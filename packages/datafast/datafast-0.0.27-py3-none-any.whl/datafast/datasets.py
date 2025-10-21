from abc import ABC, abstractmethod
import numpy as np
from pydantic import BaseModel, Field
from pathlib import Path
from typing import Any, Optional
from datasets import Dataset, load_dataset
from huggingface_hub import HfApi
from datafast.llms import LLMProvider
from datafast.prompts import (
    classification_prompts,
    question_generation_prompts,
    mcq_prompts,
    text_prompts,
)
from datafast.schema.config import (
    ClassificationDatasetConfig,
    RawDatasetConfig,
    UltrachatDatasetConfig,
    MCQDatasetConfig,
    PreferenceDatasetConfig,
    GenericPipelineDatasetConfig,
)
from datafast.schema.data_rows import (
    ChatRow,
    TextClassificationRow,
    LabelSource,
    TextRow,
    TextSource,
    MCQRow,
    MCQSource,
    PreferenceRow,
    PreferenceSource,
    GenericPipelineRow,
    GenericPipelineSource,
)
from datafast.expanders import expand_prompts
import os
from datafast import utils
from loguru import logger


### Model for Raw Text Examples Generation

class Example(BaseModel):
    text: str = Field(..., description="Generated text example")

class TextExamples(BaseModel):
    list_of_text_examples: list[Example] = Field(..., description="List of example texts")

class TextEntries(BaseModel):
    entries: list[str] = Field(..., description="List of generated texts")

class QAEntry(BaseModel):
    question: str = Field(..., description="Question")
    answer: str = Field(..., description="Answer")

class QAEntries(BaseModel):
    entries: list[QAEntry] = Field(..., description="List of generated QAs")

class UserQuestions(BaseModel):
    questions: list[str] = Field(..., description="List of user questions")

class ReformulatedUserQuestion(BaseModel):
    question: str = Field(..., description="Reformulated user question")

class Answer(BaseModel):
    answer: str = Field(..., description="Answer to the user question")

class EvolveInstructOutput(BaseModel):
    improved_question: str = Field(...)
    improved_answer: str = Field(...)

class JudgeLLMOutput(BaseModel):
    assessment: str = Field(..., description="Assessment of the response")
    score: int = Field(..., description="Score between 1 and 10")


class DatasetBase(ABC):
    """
    Abstract base class for all dataset generators.

    Methods
    -------
    inspect():
        Launch a Gradio app to visually browse the dataset (self.data_rows).
        Requires gradio to be installed (pip install gradio).
        Provides Next/Previous navigation through dataset examples.
    """

    def __init__(self, config):
        self.config = config
        self.data_rows = []

    def inspect(self, random: bool = False) -> None:
        """
        Launch an interactive Gradio app to visually inspect the generated dataset.
        
        This method redirects to specialized inspectors in datafast.inspectors module,
        which provide tailored visualization for each dataset type.
        
        Args:
            random: If True, examples will be shown in random order instead of sequential order.
                   Default is False (sequential order).
        
        Raises:
            ImportError: If gradio is not installed.
            ValueError: If the dataset type is not supported by any specialized inspector.
        """
        import warnings
        from importlib import import_module
        
        try:
            # Test if Gradio is installed
            import gradio as gr
        except ImportError as e:
            raise ImportError("Gradio is required for .inspect(). Install with 'pip install gradio'.") from e

        if not self.data_rows:
            raise ValueError("No data rows to inspect. Generate or load data first.")
            
        try:
            # Import inspectors dynamically to prevent import cycles
            inspectors = import_module('datafast.inspectors')
            
            # Get the class name without module prefix and convert CamelCase to snake_case
            class_name = self.__class__.__name__
            
            # Convert CamelCase to snake_case (e.g., ClassificationDataset -> classification_dataset)
            import re
            snake_case = re.sub(r'(?<!^)(?=[A-Z])', '_', class_name).lower()
            inspector_name = f"inspect_{snake_case}"
            
            if hasattr(inspectors, inspector_name):
                # Call the appropriate specialized inspector
                inspector_func = getattr(inspectors, inspector_name)
                inspector_func(self, random=random)
            else:
                # Fall back to generic JSON display with a warning
                warnings.warn(
                    f"No specialized inspector found for {class_name}. "
                    "Using generic inspector. Consider adding a specialized inspector "
                    "in datafast.inspectors module.", 
                    UserWarning
                )
                self._generic_inspect(random=random)
        except Exception as e:
            # If there's any error in the process, fall back to generic inspector
            warnings.warn(f"Error using specialized inspector: {e}. Falling back to generic inspector.")
            self._generic_inspect(random=random)
            
    def _generic_inspect(self, random: bool = False) -> None:
        """Generic inspector that displays dataset rows as JSON.
        
        Args:
            random: If True, examples will be shown in random order instead of sequential. Default is False.
        """
        import gradio as gr
        import numpy as np
        
        # Convert data rows to dicts for display
        examples = [row.model_dump() if hasattr(row, 'model_dump') else row.dict() if hasattr(row, 'dict') else row for row in self.data_rows]
        total = len(examples)
        
        # Generate random order indices if random is True
        if random and total > 1:
            import numpy as np
            # Create a permutation of indices
            random_indices = np.random.permutation(total)
            display_order = list(random_indices)
            ordering_label = "(Random Order)" 
        else:
            # Sequential order
            display_order = list(range(total))
            ordering_label = ""
            
        def show_example(idx: int) -> tuple[str, dict]:
            idx = max(0, min(idx, total - 1))
            # Get the actual example based on the display order
            example_idx = display_order[idx]
            return f"Example {idx+1} / {total} {ordering_label}", examples[example_idx]

        with gr.Blocks() as demo:
            idx_state = gr.State(0)
            gr.Markdown("# Dataset Inspector (Generic)")
            idx_label = gr.Markdown()
            data_view = gr.JSON()
            with gr.Row():
                prev_btn = gr.Button("Previous")
                next_btn = gr.Button("Next")

            def update_example(idx):
                label, example = show_example(idx)
                return label, example, idx

            prev_btn.click(lambda idx: max(0, idx-1), idx_state, idx_state).then(update_example, idx_state, [idx_label, data_view, idx_state])
            next_btn.click(lambda idx: min(total-1, idx+1), idx_state, idx_state).then(update_example, idx_state, [idx_label, data_view, idx_state])

            # Initial display
            demo.load(update_example, idx_state, [idx_label, data_view, idx_state])

        demo.launch()

    @abstractmethod
    def generate(self, llms=None):
        """Main method to generate the dataset."""
        pass

    def to_csv(self, filepath: str):
        """Convert self.data_rows to CSV."""
        raise NotImplementedError

    def to_parquet(self, filepath: str):
        """Convert self.data_rows to Parquet."""
        raise NotImplementedError

    def to_jsonl(self, filepath: str, rows: list[Any] = None, append: bool = False):
        """Save rows to a JSONL file, either appending or overwriting.
        
        Args:
            filepath: Path to the output file
            rows: List of rows to save, defaults to all rows in self.data_rows if None
            append: If True, append to existing file; if False, overwrite
        """
        # Use all rows if none specified
        rows_to_save = rows if rows is not None else self.data_rows
        
        if not rows_to_save:
            return
            
        output_path = Path(filepath)
        if not output_path.parent.exists():
            output_path.parent.mkdir(parents=True)
            
        mode = "a" if append and output_path.exists() else "w"
        with open(filepath, mode) as f:
            for row in rows_to_save:
                f.write(row.model_dump_json() + "\n")

    def push_to_hub(
        self,
        repo_id: str,
        token: str | None = None,
        private: bool = True,
        commit_message: str | None = None,
        train_size: float | None = None,
        seed: int | None = None,
        shuffle: bool | None = True,
        upload_card: bool = True,
    ) -> str:
        """Push the dataset to Hugging Face Hub.

        Args:
            repo_id: The ID of the repository to push to (e.g., 'username/dataset-name')
            token: Hugging Face API token. If None, will look for token in environment
            private: Whether to create a private repository
            commit_message: Optional commit message. If None, uses a default message
            train_size: If provided, fraction of data to use for training
            (e.g., 0.8 for 80% train)
            seed: Optional random seed for train_test_split
            shuffle: Optional boolean to shuffle the data for train_test_split
            upload_card: Whether to automatically upload a dataset card after pushing

        Returns:
            str: URL of the dataset on the Hub

        Raises:
            ValueError: If no data rows exist or if token is not provided
            ValueError: If invalid split parameters are provided
        """
        if not self.data_rows:
            raise ValueError("No data rows to push. Generate data first.")

        # Convert Pydantic models to dictionaries and handle UUID serialization
        data = []
        for row in self.data_rows:
            row_dict = row.model_dump()
            # Convert UUID to string
            if "uuid" in row_dict:
                row_dict["uuid"] = str(row_dict["uuid"])
            # Remove empty dictionaries that cause Parquet issues
            if "confidence_scores" in row_dict and not row_dict["confidence_scores"]:
                del row_dict["confidence_scores"]
            if "metadata" in row_dict and not row_dict["metadata"]:
                del row_dict["metadata"]
            data.append(row_dict)

        dataset = Dataset.from_list(data)

        # Create train/test split if requested
        if train_size is not None:
            if not 0 < train_size < 1:
                raise ValueError("train_size must be between 0 and 1")

            # Create the split
            splits = dataset.train_test_split(
                train_size=train_size,
                shuffle=shuffle,
                seed=seed,
            )
            dataset = splits  # splits is now a DatasetDict with 'train' and 'test' keys

        # Get token from env if not provided
        token = token or os.getenv("HF_TOKEN")
        if token is None:
            raise ValueError(
                "No token provided and HF_TOKEN environment variable not set"
            )

        api = HfApi(token=token)

        # Create the repo if it doesn't exist
        api.create_repo(
            repo_id=repo_id, private=private, repo_type="dataset", exist_ok=True
        )

        # Push the dataset
        try:
            dataset.push_to_hub(
                repo_id,
                commit_message=commit_message or "Update dataset",
                token=token,
                private=private,
            )
        except Exception as e:
            if "did not recognize Python value type" in str(e):
                raise ValueError(
                    "Data type conversion error. Please ensure all fields "
                    "are of supported types. Original error: {str(e)}"
                )
            raise

        # Upload dataset card if requested
        if upload_card:
            try:
                from datafast.card_utils import upload_dataset_card
                upload_dataset_card(repo_id=repo_id, token=token)
                print("Dataset card uploaded successfully")
            except Exception as e:
                print(f"Warning: Failed to upload dataset card: {e}")
                # Continue even if card upload fails

        return f"https://huggingface.co/datasets/{repo_id}"


class ClassificationDataset(DatasetBase):
    def __init__(self, config: ClassificationDatasetConfig):
        super().__init__(config)
        self.config = config
    
    def get_num_expected_rows(self, llms: list[LLMProvider]) -> int:
        """Calculate the expected number of rows that will be generated.
        
        Args:
            llms: List of LLM providers that will be used for generation.
            
        Returns:
            int: The expected number of rows that will be generated.
        """
        if not self.config.classes or not llms:
            return 0
            
        return utils._get_classification_num_expected_rows(self.config, llms)
    

    def generate(self, llms: list[LLMProvider]) -> "ClassificationDataset":
        """Generate text classification data by calling multiple providers.

        Args:
            llms: List of LLM providers to use for generation. Must not be empty.

        Raises:
            ValueError: If no LLM providers are supplied or if no classes are defined.
        """
        if not llms:
            raise ValueError("At least one LLM provider must be supplied")

        if not self.config.classes:
            raise ValueError("No classification classes provided in config")

        # Get labels listing for context in prompts
        labels_listing = [label["name"] for label in self.config.classes]

        # Get languages from config, default to English if not specified
        languages = self.config.languages or {"en": "English"}

        # For each label, generate examples using all providers
        for label in self.config.classes:
            for lang_code, language_name in languages.items():
                # 1. Create base prompts for this label and language
                base_prompts = self.config.prompts or self._get_default_prompts()
                base_prompts = [
                    prompt.format(
                        num_samples=self.config.num_samples_per_prompt,
                        labels_listing=labels_listing,
                        label_name=label["name"],
                        label_description=label["description"],
                        language_name=language_name,
                    )  # Directly use language name
                    for prompt in base_prompts
                ]

                # 2. Expand prompts with configured variations
                expansions = expand_prompts(
                    prompt_templates=base_prompts, **self.config.expansion.model_dump()
                )

                # 3. For each expanded prompt, call each provider
                for expanded_prompt, meta in expansions:
                    for llm in llms:
                        try:
                            # Generate multiple examples using the LLM
                            response = llm.generate(
                                expanded_prompt, response_format=TextEntries
                            )

                            # Create and save rows for each batch
                            new_rows = []
                            for text in response.entries:
                                row = TextClassificationRow(
                                    text=text,
                                    label=label["name"],
                                    model_id=llm.model_id,
                                    label_source=LabelSource.SYNTHETIC,
                                    language=lang_code,
                                )
                                self.data_rows.append(row)
                                new_rows.append(row)
                            
                            # Save this batch
                            self.to_jsonl(self.config.output_file, new_rows, append=True)
                            print(f" Generated and saved {len(self.data_rows)} examples total")

                        except Exception as e:
                            print(f"Error with llm provider {llm.provider_name}: {e}")
        return self

    def _get_default_prompts(self) -> list[str]:
        """Return the default prompt templates for text classification."""
        return classification_prompts.DEFAULT_TEMPLATES


class RawDataset(DatasetBase):
    def __init__(self, config: RawDatasetConfig):
        super().__init__(config)
        self.config = config
    
    def get_num_expected_rows(self, llms: list[LLMProvider]) -> int:
        """Calculate the expected number of rows that will be generated.
        
        Args:
            llms: List of LLM providers that will be used for generation.
            
        Returns:
            int: The expected number of rows that will be generated.
        """
        if not llms:
            raise ValueError("At least one LLM provider must be supplied")
        return utils._get_text_num_expected_rows(self.config, llms)

    def generate(self, llms: list[LLMProvider]) -> "RawDataset":
        """Generate text data by calling multiple providers.

        Args:
            llms: List of LLM providers to use for generation.

        Raises:
            ValueError: If no LLM providers are supplied or if text_attributes are missing.
        """
        if not llms:
            raise ValueError("At least one LLM provider must be supplied")

        # Get languages from config, default to English if not specified
        languages = self.config.languages or {"en": "English"}

        # For each language, generate examples using all providers
        for document_type in self.config.document_types:
            for topic in self.config.topics:
                for lang_code, language_name in languages.items():
                    # Add language to text attributes for prompt generation
                    # text_attrs = self.config.text_attributes.copy()
                    # text_attrs['language_name'] = language_name
                    # text_attrs['num_samples'] = str(self.config.num_samples_per_prompt)

                    # 1. Create base prompts for this language
                    base_prompts = self.config.prompts or self._get_default_prompts()
                    base_prompts = [
                        prompt.format(
                            num_samples=self.config.num_samples_per_prompt,
                            language_name=language_name,
                            document_type=document_type,
                            topic=topic,
                        )
                        for prompt in base_prompts
                    ]

                    # 2. Expand prompts with configured variations
                    expansions = expand_prompts(
                        prompt_templates=base_prompts,
                        **self.config.expansion.model_dump(),
                    )

                    # 3. For each expanded prompt, call each provider
                    for expanded_prompt, meta in expansions:
                        for llm in llms:
                            try:
                                # Generate multiple examples using the LLM
                                response = llm.generate(
                                    expanded_prompt, response_format=TextExamples
                                )

                                # Create a row for each generated example
                                new_rows = []
                                for example in response.list_of_text_examples:
                                    row = TextRow(
                                        text=example.text,
                                        text_source=TextSource.SYNTHETIC,
                                        model_id=llm.model_id,
                                        language=lang_code,
                                        metadata={
                                            "document_type": document_type,
                                            "topic": topic,
                                        },
                                    )
                                    self.data_rows.append(row)
                                    new_rows.append(row)
                                
                                # Save this batch
                                self.to_jsonl(self.config.output_file, new_rows, append=True)
                                print(f" Generated and saved {len(self.data_rows)} examples total")

                            except Exception as e:
                                print(f"Error with llm provider {llm.provider_name}: {e}")

        return self

    def _get_default_prompts(self) -> list[str]:
        """Return the default prompt templates for text generation."""
        return text_prompts.DEFAULT_TEMPLATES


class UltrachatDataset(DatasetBase):
    def __init__(self, config: UltrachatDatasetConfig):
        super().__init__(config)
        self.config = config
    
    def get_num_expected_rows(self, llms: list[LLMProvider]) -> int:
        """Calculate the expected number of rows that will be generated.
        
        Args:
            llms: List of LLM providers that will be used for generation.
            
        Returns:
            int: The expected number of rows that will be generated.
        """
        if not llms:
            raise ValueError("At least one LLM provider must be supplied")
        return utils._get_ultrachat_num_expected_rows(self.config, llms)


    def generate(self, llms: list[LLMProvider]) -> "UltrachatDataset":
        if not llms:
            raise ValueError("At least one LLM provider must be supplied")

        # Get languages from config, default to English if not specified
        languages = self.config.languages or {"en": "English"}

        # For each language, generate examples using all providers
        for lang_code, language_name in languages.items():
            for topic, subtopics in self.config.topics_and_subtopics.items():
                for subtopic in subtopics:
                    # 1. Create base prompts for this language
                    base_prompts = (
                        self.config.question_generation_prompts
                        or self._get_default_question_generation_prompts()
                    )

                    base_prompts = [
                        prompt.format(
                            num_samples=self.config.num_samples,
                            language_name=language_name,
                            domain=self.config.domain,
                            topic=topic,
                            subtopic=subtopic,
                        )
                        for prompt in base_prompts
                    ]

                    # 2. Expand prompts with configured variations
                    expansions = expand_prompts(
                        prompt_templates=base_prompts,
                        **self.config.expansion.model_dump(),
                    )

                    # 3. For each expanded prompt, call each provider in UltraChat iteration
                    for i, (expanded_prompt, meta) in enumerate(expansions, 1):
                        for llm in llms:
                            try:
                                # Generate multiple examples using the LLM
                                # --- Here goes the ultraChat loop ---
                                opening_questions = llm.generate(
                                    expanded_prompt, response_format=UserQuestions
                                )

                                for opening_question in opening_questions.questions:
                                    random_persona = np.random.choice(
                                        self.config.personas
                                    )
                                    reformulation_prompt = self._get_default_persona_question_reformulation_prompt()
                                    reformulated_question = llm.generate(
                                        prompt=reformulation_prompt.format(
                                            question=opening_question,
                                            persona=random_persona,
                                            topic=topic,
                                            subtopic=subtopic,
                                        ),
                                        response_format=ReformulatedUserQuestion,
                                    )

                                    # simulate the assistant response to the opening question
                                    assistant_prompt = (
                                        self._get_default_simulated_assistant_prompt()
                                    )
                                    assistant_response = llm.generate(
                                        prompt=assistant_prompt.format(
                                            domain=self.config.domain,
                                            topic=topic,
                                            subtopic=subtopic,
                                            question=reformulated_question.question,
                                        ),
                                        response_format=Answer,
                                    )

                                    # choose to continue the conversation or not (proba 0.5)
                                    count = 1
                                    messages = [
                                        {
                                            "role": "user",
                                            "content": reformulated_question.question,
                                        },
                                        {
                                            "role": "assistant",
                                            "content": assistant_response.answer,
                                        },
                                    ]

                                    # assemble the dialog to prompt the user
                                    dialog_summary = f"{reformulated_question.question}\n{assistant_response.answer}"

                                    while (count < self.config.max_turns) and (
                                        np.random.random()
                                        < self.config.conversation_continuation_prob
                                    ):
                                        # simulate the user follow-up question
                                        followup_prompt = (
                                            self._get_default_user_followup_prompt()
                                        )
                                        followup_question = llm.generate(
                                            prompt=followup_prompt.format(
                                                dialog_summary=dialog_summary,
                                                persona=random_persona,
                                                subtopic=subtopic,
                                                domain=self.config.domain,
                                            ),
                                            response_format=ReformulatedUserQuestion,
                                        )
                                        # simulate the assistant response
                                        messages.append(
                                            {
                                                "role": "user",
                                                "content": followup_question.question,
                                            }
                                        )
                                        ai_response = llm.generate(
                                            messages=messages, response_format=Answer
                                        )

                                        dialog_summary += f"\n{followup_question.question}\n{ai_response.answer}"
                                        messages.append(
                                            {
                                                "role": "assistant",
                                                "content": ai_response.answer,
                                            }
                                        )

                                        count += 1
                                        if count >= self.config.max_turns:
                                            break

                                    # Create a row for each generated example
                                    row = ChatRow(
                                        opening_question=messages[0]["content"],
                                        messages=messages,
                                        model_id=llm.model_id,
                                        language=lang_code,
                                        metadata={
                                            "domain": self.config.domain,
                                            "topic": topic,
                                            "subtopic": subtopic,
                                        },
                                        persona=random_persona,
                                    )
                                    self.data_rows.append(row)
                                    # Save each chat conversation as it's generated
                                    self.to_jsonl(self.config.output_file, [row], append=True)
                                    print(f" Generated and saved {len(self.data_rows)} chat conversations total")

                            except Exception as e:
                                import traceback
                                error_trace = traceback.format_exc()
                                print(f"\nError with llm provider {llm.provider_name}:\n{error_trace}")
                                print(f"Error occurred at response type: {response_format.__name__ if 'response_format' in locals() else 'unknown'}")
                                if 'reformulated_question' in locals():
                                    print(f"Last reformulated_question: {reformulated_question}")

        return self

    def _get_default_question_generation_prompts(self) -> list[str]:
        return question_generation_prompts.DOMAIN_TOPIC_SUBTOPIC_N_QUESTION_GENERATION_DEFAULT_TEMPLATES

    def _get_default_persona_question_reformulation_prompt(self) -> str:
        return (
            question_generation_prompts.PERSONA_QUESTION_REFORMULATION_DEFAULT_TEMPLATE
        )

    def _get_default_simulated_assistant_prompt(self) -> str:
        return question_generation_prompts.SIMULATED_ASSISTANT_DEFAULT_TEMPLATE

    # def _get_default_user_system_prompt(self) -> str:
    #     return question_generation_prompts.USER_SYSTEM_PROMPT_TEMPLATE

    def _get_default_user_followup_prompt(self) -> str:
        return question_generation_prompts.USER_FOLLOWUP_PROMPT_TEMPLATE


class MCQDataset(DatasetBase):
    def __init__(self, config: MCQDatasetConfig):
        super().__init__(config)
        self.config = config
    
    def get_num_expected_rows(self, llms: list[LLMProvider], source_data_num_rows: int) -> int:
        """Calculate the expected number of rows that will be generated.
        
        Args:
            llms: List of LLM providers that will be used for generation.
            
        Returns:
            int: The expected number of rows that will be generated.
        """
        if not llms:
            raise ValueError("At least one LLM provider must be supplied")
        return utils._get_mcq_num_expected_rows(self.config, llms, source_data_num_rows)


    def generate(self, llms: list[LLMProvider]) -> "MCQDataset":
        """
        Generate multiple choice questions by calling providers for questions and then for incorrect answers.
        
        Args:
            llms: List of LLM providers to use for generation. Must not be empty.
            
        Raises:
            ValueError: If no LLM providers are supplied or if required configuration is missing.
        """
        if not llms:
            raise ValueError("At least one LLM provider must be supplied")
            
        # Load the dataset using shared utility
        try:
            dataset = utils.load_dataset_from_source(
                hf_dataset_name=self.config.hf_dataset_name,
                local_file_path=self.config.local_file_path,
                sample_count=self.config.sample_count,
                text_column=self.config.text_column
            )
                
        except Exception as e:
            source = self.config.hf_dataset_name or self.config.local_file_path
            raise ValueError(f"Error loading data from {source}: {e}")
            
        # Get languages from config, default to English if not specified
        languages = self.config.languages or {"en": "English"}
        
        # For each document, generate questions and answers
        for sample in dataset:
            if self.config.text_column not in sample:
                print(f"Warning: Column {self.config.text_column} not found in sample, skipping")
                continue
                
            document = sample[self.config.text_column]
            if not document or len(document.strip()) < self.config.min_document_length:  # Skip very short documents
                continue
            if len(document.strip()) > self.config.max_document_length: # Skip very long documents
                continue
                
            # Check if context_column exists and extract context if available
            context = None
            if self.config.context_column and self.config.context_column in sample:
                context = sample[self.config.context_column]

            for lang_code, language_name in languages.items():
                # 1. First call: Generate questions and correct answers
                if context and isinstance(context, str):
                    # Use contextualized templates if context is available
                    from datafast.prompts.mcq_prompts import CONTEXTUALISED_TEMPLATES
                    question_prompts = self.config.prompts or CONTEXTUALISED_TEMPLATES
                    question_prompts = [
                        prompt.format(
                            num_samples=self.config.num_samples_per_prompt,
                            language_name=language_name,
                            document=document,
                            context=context
                        )
                        for prompt in question_prompts
                    ]
                else:
                    # Use default templates if no context is available
                    question_prompts = self.config.prompts or self._get_default_prompts()
                    question_prompts = [
                        prompt.format(
                            num_samples=self.config.num_samples_per_prompt,
                            language_name=language_name,
                            document=document,
                        )
                        for prompt in question_prompts
                    ]
                
                # Expand prompts with configured variations
                question_expansions = expand_prompts(
                    prompt_templates=question_prompts,
                    **self.config.expansion.model_dump(),
                )
                
                # Process each expanded prompt
                for expanded_prompt, meta in question_expansions:
                    for llm in llms:
                        # Use the first LLM provider to generate questions and correct answers
                        try:
                            # Generate questions with the correct answers
                            response = llm.generate(expanded_prompt, response_format=QAEntries)
                            
                            for qa_entry in response.entries:
                                # Extract question and correct answer from the QAEntry
                                try:
                                    # QAEntry already has question and answer fields
                                    question_part = qa_entry.question
                                    correct_answer = qa_entry.answer
                                    
                                    # 2. Second call: Generate incorrect answers
                                    distractor_prompt = self.config.distractor_prompt or self._get_distractor_prompt().format(
                                        question=question_part,
                                        correct_answer=correct_answer,
                                        language_name=language_name,
                                    )
                                    
                                    try:
                                        # Use TextEntries for the distractor response since we need a list of incorrect answers
                                        distractor_response = llm.generate(
                                            distractor_prompt, response_format=TextEntries
                                        )
                                        
                                        # Parse the incorrect answers
                                        incorrect_answers = []
                                        for entry in distractor_response.entries:
                                            incorrect_answers.append(entry.strip())
                                        
                                        if len(incorrect_answers) >= 3:
                                            # Create MCQ row with the question, correct answer, and incorrect answers
                                            row = MCQRow(
                                                source_document=document,
                                                question=question_part,
                                                correct_answer=correct_answer,
                                                incorrect_answer_1=incorrect_answers[0],
                                                incorrect_answer_2=incorrect_answers[1],
                                                incorrect_answer_3=incorrect_answers[2],
                                                model_id=llm.model_id,
                                                mcq_source=MCQSource.SYNTHETIC,
                                                language=lang_code,
                                                metadata={
                                                    "source_dataset": self._get_source_dataset_name(),
                                                },
                                            )
                                            self.data_rows.append(row)
                                            # Save each MCQ as it's generated
                                            self.to_jsonl(self.config.output_file, [row], append=True)
                                        else:
                                            print(f"Warning: Not enough incorrect answers generated (got {len(incorrect_answers)}, need 3)")
                                    except Exception as e:
                                        print(f"Error generating distractors: {e}")
                                except Exception as e:
                                    print(f"Error processing entry: {e}")
                            print(f" Generated and saved {len(self.data_rows)} MCQs total")
                        except Exception as e:
                            print(f"Error with llm provider {llm.provider_name}: {e}")
        
        return self
    
    def _get_default_prompts(self) -> list[str]:
        """Return the default prompt templates for MCQ generation."""
        return mcq_prompts.DEFAULT_TEMPLATES
        
    def _get_distractor_prompt(self) -> str:
        """Return the prompt template for generating incorrect answers."""
        return mcq_prompts.DISTRACTOR_TEMPLATE
        
    def _get_source_dataset_name(self) -> str:
        """Get a source dataset name for metadata.
        
        Returns a descriptive name for the dataset source, either from the HF dataset
        name or derived from the local file path if using a local file.
        
        Returns:
            str: Source dataset name for metadata.
        """
        if self.config.hf_dataset_name:
            return self.config.hf_dataset_name
        
        if self.config.local_file_path:
            # Extract a reasonable name from the file path
            file_name = self.config.local_file_path.split('/')[-1]
            return f"local_file:{file_name}"
        
        # Fallback if somehow neither is set
        return "unknown_source"
        


class PreferenceDataset(DatasetBase):
    def __init__(self, config: PreferenceDatasetConfig):
        super().__init__(config)
        self.config = config
    

    def get_num_expected_rows(self, llms: list[LLMProvider]) -> int:
        """Calculate the expected number of rows that will be generated.
        
        Args:
            llms: List of LLM providers that will be used for generation.
            
        Returns:
            int: The expected number of rows that will be generated.
        """
        if not llms:
            raise ValueError("At least one LLM provider must be supplied")
        return utils._get_preference_num_expected_rows(self.config, llms)
    
    def generate(self, 
                question_gen_llm: LLMProvider,
                chosen_response_gen_llm: LLMProvider,
                rejected_response_gen_llm: LLMProvider,
                evolution_llm: LLMProvider = None,
                judge_llm: LLMProvider = None) -> "PreferenceDataset":
        """
        Generate preference data with chosen and rejected responses.
        
        Args:
            question_gen_llm: LLM provider for generating questions/instructions.
            chosen_response_gen_llm: LLM provider for generating high-quality (chosen) responses.
            rejected_response_gen_llm: LLM provider for generating lower-quality (rejected) responses.
            evolution_llm: LLM provider for evolving questions and generating improved responses.
            judge_llm: LLM provider for scoring responses when llm_as_judge is True.
            
        Raises:
            ValueError: If input_documents are missing in the configuration.
        """
        if not self.config.input_documents:
            raise ValueError("input_documents must be provided in the configuration")
        
        # Get languages from config, default to English if not specified
        languages = self.config.languages or {"en": "English"}
        
        # For each language, generate examples
        for lang_code, language_name in languages.items():
            # Process each input document
            for doc in self.config.input_documents:
                # Generate questions for each document
                questions = self._generate_questions(doc, question_gen_llm, language_name)
                
                # For each question, generate chosen and rejected responses
                for question in questions:
                    # Generate chosen response
                    chosen_response = self._generate_chosen_response(
                        doc, 
                        question, 
                        chosen_response_gen_llm, 
                        language_name
                    )
                    
                    # Generate rejected response
                    rejected_response = self._generate_rejected_response(
                        doc,
                        question,
                        rejected_response_gen_llm, 
                        language_name
                    )

                    # If evolutionary instruction is enabled, refine the instruction and response
                    if self.config.evol_instruct and evolution_llm:
                        raise NotImplementedError
                        # evol_result = self._evolve_question_and_answer(
                        #     doc, 
                        #     question, 
                        #     chosen_response, 
                        #     evolution_llm
                        # )
                        # question = evol_result.improved_question
                        # chosen_response = evol_result.improved_answer

                    
                    # Initialize model IDs and judge-related variables
                    chosen_model_id = chosen_response_gen_llm.model_id
                    rejected_model_id = rejected_response_gen_llm.model_id
                    chosen_response_score = None
                    rejected_response_score = None
                    chosen_response_assessment = None
                    rejected_response_assessment = None
                    
                    # If LLM as judge is enabled, use the judge LLM to evaluate the preference pair
                    if self.config.llm_as_judge and judge_llm:
                        # Get judge scores for chosen response
                        chosen_response_result = self._judge_scoring(
                            doc, question, chosen_response, judge_llm
                        )
                        chosen_response_score = chosen_response_result.score
                        chosen_response_assessment = chosen_response_result.assessment

                        # Get judge scores for rejected response
                        rejected_response_result = self._judge_scoring(
                            doc, question, rejected_response, judge_llm
                        )
                        rejected_response_score = rejected_response_result.score
                        rejected_response_assessment = rejected_response_result.assessment

                        # Swap chosen and rejected responses based on scores if needed
                        # This ensures the higher-scored response is always the chosen one
                        if rejected_response_score > chosen_response_score:
                            # Swap responses
                            chosen_response, rejected_response = rejected_response, chosen_response
                            # Swap scores
                            chosen_response_score, rejected_response_score = rejected_response_score, chosen_response_score
                            # Swap assessments
                            chosen_response_assessment, rejected_response_assessment = rejected_response_assessment, chosen_response_assessment
                            # Swap model IDs
                            chosen_model_id, rejected_model_id = rejected_model_id, chosen_model_id
                    
                    # Create and store the preference row
                    row_data = {
                        "input_document": doc,
                        "question": question,
                        "chosen_response": chosen_response,
                        "rejected_response": rejected_response,
                        "preference_source": PreferenceSource.SYNTHETIC,
                        "chosen_model_id": chosen_model_id,
                        "rejected_model_id": rejected_model_id,
                        "language": lang_code,
                        "metadata": {
                            "instruction_model": question_gen_llm.model_id,
                        }
                    }
                    
                    # Add judge-related fields only if we have a judge
                    if self.config.llm_as_judge and judge_llm:
                        row_data.update({
                            "chosen_response_score": chosen_response_score,
                            "rejected_response_score": rejected_response_score,
                            "chosen_response_assessment": chosen_response_assessment,
                            "rejected_response_assessment": rejected_response_assessment
                        })
                    
                    row = PreferenceRow(**row_data)
                    self.data_rows.append(row)
                    
                    # Save each preference pair immediately
                    self.to_jsonl(self.config.output_file, [row], append=True)
                    print(f" Generated and saved {len(self.data_rows)} preference pairs total")
            
        return self
        
    def _generate_questions(self, document: str, llm: LLMProvider, language_name: str) -> list[str]:
        """
        Generate questions based on the input document.
        
        Args:
            document: The input document text.
            llm: LLM provider for generating questions.
            language_name: The language to generate questions in.
            
        Returns:
            List of generated questions.
        """
        # Get prompt templates
        templates = self.config.question_generation_prompts or self._get_default_question_prompts()
        
        # Select a template randomly
        template = np.random.choice(templates)
        
        # Format the prompt
        prompt = template.format(
            document=document,
            num_samples=self.config.num_samples_per_prompt,
            language_name=language_name
        )
        
        # Generate questions using structured output
        response = llm.generate(
            prompt=prompt,
            response_format=UserQuestions
        )
        
        return response.questions
    
    def _generate_chosen_response(self, document: str, question: str, llm: LLMProvider, language_name: str) -> str:
        """
        Generate a high-quality (chosen) response.
        
        Args:
            document: The input document text.
            question: The question to answer.
            llm: LLM provider for generating the response.
            language_name: The language to generate the response in.
            
        Returns:
            The generated response.
        """
        # Get prompt template
        template = self.config.chosen_response_generation_prompt or self._get_default_chosen_response_prompt()
        
        # Format the prompt
        prompt = template.format(
            document=document,
            question=question,
            language_name=language_name
        )
        
        # Generate response
        response = llm.generate(
            prompt=prompt,
            response_format=Answer
        )
        
        return response.answer
    
    def _generate_rejected_response(self, document: str, question: str, llm: LLMProvider, language_name: str) -> str:
        """
        Generate a lower-quality (rejected) response.
        
        Args:
            document: The input document text.
            question: The question to answer.
            llm: LLM provider for generating the response.
            language_name: The language to generate the response in.
            
        Returns:
            The generated response.
        """
        # Get prompt template
        template = self.config.rejected_response_generation_prompt or self._get_default_rejected_response_prompt()
        
        # Format the prompt
        prompt = template.format(
            document=document,
            question=question,
            language_name=language_name
        )
        
        # Generate response
        response = llm.generate(
            prompt=prompt,
            response_format=Answer
        )
        
        return response.answer
    
    def _evolve_question_and_answer(self, document: str, question: str, answer: str, llm: LLMProvider) -> EvolveInstructOutput:
        """
        Evolve the question and answer.
        
        Args:
            document: The input document text.
            question: The original question.
            answer: The original answer.
            llm: LLM provider for evolving the question and answer.
            
        Returns:
            EvolveInstructOutput with improved question and answer.
        """
        raise NotImplementedError
        # # Get prompt template
        # template = self.config.evolution_prompt or self._get_default_evolution_prompt()
        
        # # Format the prompt
        # prompt = template.format(
        #     document=document,
        #     question=question,
        #     answer=answer
        # )
        
        # # Generate evolved question and answer
        # response = llm.generate(
        #     prompt=prompt,
        #     response_format=EvolveInstructOutput,
        # )
        
        # return response
    
    def _judge_scoring(self, document: str, question: str, response: str, llm: LLMProvider) -> JudgeLLMOutput:
        """
        Score a response using an LLM judge.
        
        Args:
            document: The input document text.
            question: The question.
            response: The response to evaluate.
            llm: LLM provider for judging.
            
        Returns:
            JudgeLLMOutput with assessment and score.
        """
        # Get prompt template
        template = self.config.judge_prompt or self._get_default_judge_prompt()
        
        # Format the prompt
        prompt = template.format(
            document=document,
            question=question,
            response=response
        )
        
        # Generate score using the judge LLM
        # The JudgeLLMOutput class handles validation and clipping of scores
        result = llm.generate(
            prompt=prompt,
            response_format=JudgeLLMOutput,
        )
        
        return result
    
    def _get_default_question_prompts(self) -> list[str]:
        """Return the default prompt templates for question generation."""
        from datafast.prompts import preference_prompts
        return preference_prompts.QUESTION_GENERATION_TEMPLATES
    
    def _get_default_chosen_response_prompt(self) -> str:
        """Return the default prompt template for chosen response generation."""
        from datafast.prompts import preference_prompts
        return preference_prompts.CHOSEN_RESPONSE_TEMPLATE
    
    def _get_default_rejected_response_prompt(self) -> str:
        """Return the default prompt template for rejected response generation."""
        from datafast.prompts import preference_prompts
        return preference_prompts.REJECTED_RESPONSE_TEMPLATE
    
    def _get_default_evolution_prompt(self) -> str:
        """Return the default prompt template for evolutionary instruction refinement."""
        from datafast.prompts import preference_prompts
        return preference_prompts.EVOLUTION_PROMPT
    
    def _get_default_judge_prompt(self) -> str:
        """Return the default prompt template for LLM judge scoring."""
        from datafast.prompts import preference_prompts
        return preference_prompts.JUDGE_PROMPT


class GenericPipelineDataset(DatasetBase):
    def __init__(self, config: GenericPipelineDatasetConfig):
        super().__init__(config)
        self.config = config
    
    def get_num_expected_rows(self, llms: list[LLMProvider]) -> int:
        """Calculate the expected number of rows that will be generated.
        
        Args:
            llms: List of LLM providers that will be used for generation.
            
        Returns:
            int: The expected number of rows that will be generated.
        """
        if not llms:
            raise ValueError("At least one LLM provider must be supplied")
        return utils._get_generic_pipeline_num_expected_rows(self.config, llms)
    
    def _load_source_dataset(self):
        """Load dataset from Hugging Face or local file using shared utility."""
        return utils.load_dataset_from_source(
            hf_dataset_name=self.config.hf_dataset_name,
            local_file_path=self.config.local_file_path,
            sample_count=self.config.sample_count
        )
    
    def generate(self, llms: list[LLMProvider]) -> "GenericPipelineDataset":
        """Generate data by processing source dataset through custom prompts.
        
        Args:
            llms: List of LLM providers to use for generation.
            
        Returns:
            Self for method chaining.
        """
        if not llms:
            raise ValueError("At least one LLM provider must be supplied")
        
        # Load source dataset
        source_dataset = self._load_source_dataset()
        print(f"Loaded source dataset with {len(source_dataset)} rows")
        
        # Apply sample limit if specified
        if self.config.sample_count:
            source_dataset = source_dataset[:min(self.config.sample_count, len(source_dataset))]
            print(f"Limited to {len(source_dataset)} rows")
        
        # Get languages from config
        languages = self.config.languages or {"en": "English"}
        
        # Process each row in the source dataset
        for row_idx, source_row in enumerate(source_dataset):
            # Apply skip function if provided
            if self.config.skip_function and self.config.skip_function(source_row):
                print(f"Skipping row {row_idx} due to skip_function")
                continue
            
            # Extract input data based on input_columns
            input_data = {col: str(source_row.get(col, "")) for col in self.config.input_columns}
            
            # Extract forward data if specified
            forward_data = {}
            if self.config.forward_columns:
                forward_data = {col: str(source_row.get(col, "")) for col in self.config.forward_columns}
            
            # Process for each language
            for lang_code, language_name in languages.items():
                # Process each prompt
                for prompt_idx, prompt_template in enumerate(self.config.prompts):
                    # Format prompt with input data and required placeholders
                    formatted_prompt = prompt_template.format(
                        num_samples=self.config.num_samples_per_prompt,
                        language=language_name,
                        **input_data
                    )
                    
                    # Expand prompts with configured variations
                    expansions = expand_prompts(
                        prompt_templates=[formatted_prompt],
                        **self.config.expansion.model_dump()
                    )
                    
                    # Process each expanded prompt
                    for expanded_prompt, meta in expansions:
                        # Process with each LLM
                        for llm in llms:
                            try:
                                # Create dynamic response model based on output_columns configuration
                                response_model = utils.create_response_model(self.config)
                                
                                # Create dynamic row model based on output_columns configuration
                                row_model = utils.create_generic_pipeline_row_model(self.config)
                                
                                # Generate response using the LLM with proper response format
                                response = llm.generate(expanded_prompt, response_format=response_model)
                                
                                # Create rows for each generated sample
                                new_rows = []
                                for entry in response.entries:
                                    # Prepare row data with all columns as separate top-level fields
                                    row_data = {
                                        "model_id": llm.model_id,
                                        "pipeline_source": GenericPipelineSource.SYNTHETIC,
                                        "language": lang_code,
                                        "metadata": {
                                            "prompt_index": str(prompt_idx),
                                            "source_row_index": str(row_idx),
                                        }
                                    }
                                    
                                    # Add input data as individual top-level fields
                                    for column, value in input_data.items():
                                        row_data[column] = value
                                    
                                    # Add forward data as individual top-level fields
                                    for column, value in forward_data.items():
                                        row_data[column] = value
                                    
                                    # Add each output column as a separate field
                                    if self.config.output_columns:
                                        for column in self.config.output_columns:
                                            row_data[column] = getattr(entry, column, "")
                                    else:
                                        row_data["generated_text"] = getattr(entry, "generated_text", "")
                                    
                                    # Create the dynamic row
                                    row = row_model(**row_data)
                                    self.data_rows.append(row)
                                    new_rows.append(row)
                                
                                # Save this batch
                                self.to_jsonl(self.config.output_file, new_rows, append=True)
                                logger.success(f"Generated and saved {len(self.data_rows)} examples total")
                                
                            except Exception as e:
                                logger.error(f"Error with llm provider {llm.provider_name} on row {row_idx}: {e}")
                                continue
        
        return self