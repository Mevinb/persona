"""
NOVA Fine-tuning Module
=======================
Tools and scripts for fine-tuning NOVA's language model with LoRA.
This module will allow you to customize NOVA's responses based on your preferences.
"""

import json
import logging
import torch
from pathlib import Path
from typing import List, Dict, Any, Optional
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling
)
from peft import (
    LoraConfig,
    get_peft_model,
    TaskType,
    PeftModel
)
from datasets import Dataset


class NovaFineTuner:
    """
    Fine-tuning manager for NOVA using LoRA (Low-Rank Adaptation).
    Allows customization of the assistant's responses while maintaining efficiency.
    """
    
    def __init__(self, 
                 base_model: str = "mistralai/Mistral-7B-v0.1",
                 dataset_path: str = "fine_tune/dataset.jsonl",
                 output_dir: str = "fine_tune/models"):
        """
        Initialize the fine-tuner.
        
        Args:
            base_model: Base model to fine-tune
            dataset_path: Path to training dataset
            output_dir: Directory to save fine-tuned models
        """
        self.logger = logging.getLogger(__name__)
        self.base_model = base_model
        self.dataset_path = Path(dataset_path)
        self.output_dir = Path(output_dir)
        
        # LoRA configuration
        self.lora_config = LoraConfig(
            task_type=TaskType.CAUSAL_LM,
            inference_mode=False,
            r=16,                    # Rank
            lora_alpha=32,           # Alpha
            lora_dropout=0.1,        # Dropout
            target_modules=["q_proj", "v_proj"]  # Target attention modules
        )
        
        # Training configuration
        self.training_args = TrainingArguments(
            output_dir=str(self.output_dir),
            num_train_epochs=3,
            per_device_train_batch_size=4,
            gradient_accumulation_steps=4,
            warmup_ratio=0.03,
            max_steps=-1,
            learning_rate=2e-4,
            fp16=True,
            logging_steps=10,
            optim="adamw_torch",
            seed=42,
            save_strategy="epoch",
            evaluation_strategy="no",
            remove_unused_columns=False,
            dataloader_pin_memory=False
        )
        
        self.tokenizer = None
        self.model = None
        
        self.logger.info("Fine-tuner initialized")
    
    def load_dataset(self) -> List[Dict[str, str]]:
        """
        Load training dataset from JSONL file.
        
        Returns:
            List of conversation examples
        """
        try:
            with open(self.dataset_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                conversations = data.get('conversations', [])
                
                self.logger.info(f"Loaded {len(conversations)} conversation examples")
                return conversations
                
        except Exception as e:
            self.logger.error(f"Error loading dataset: {e}")
            return []
    
    def prepare_training_data(self, conversations: List[Dict[str, str]]) -> Dataset:
        """
        Prepare training data for the model.
        
        Args:
            conversations: List of input-output conversation pairs
            
        Returns:
            Prepared dataset
        """
        # Format conversations for training
        formatted_data = []
        
        for conv in conversations:
            # Create a prompt-response format
            prompt = f"Human: {conv['input']}\nNova:"
            response = conv['output']
            full_text = f"{prompt} {response}<|endoftext|>"
            
            formatted_data.append({"text": full_text})
        
        # Create dataset
        dataset = Dataset.from_list(formatted_data)
        
        self.logger.info(f"Prepared {len(formatted_data)} training examples")
        return dataset
    
    def tokenize_dataset(self, dataset: Dataset) -> Dataset:
        """
        Tokenize the dataset for training.
        
        Args:
            dataset: Raw text dataset
            
        Returns:
            Tokenized dataset
        """
        def tokenize_function(examples):
            # Tokenize the text
            tokenized = self.tokenizer(
                examples["text"],
                truncation=True,
                padding=False,
                max_length=512,
                return_tensors=None
            )
            
            # Set labels for causal language modeling
            tokenized["labels"] = tokenized["input_ids"].copy()
            return tokenized
        
        tokenized_dataset = dataset.map(
            tokenize_function,
            batched=True,
            remove_columns=dataset.column_names
        )
        
        self.logger.info("Dataset tokenized successfully")
        return tokenized_dataset
    
    def setup_model_and_tokenizer(self):
        """Setup the base model and tokenizer for fine-tuning."""
        try:
            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(self.base_model)
            
            # Add padding token if missing
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            # Load model
            self.model = AutoModelForCausalLM.from_pretrained(
                self.base_model,
                torch_dtype=torch.float16,
                device_map="auto",
                trust_remote_code=True
            )
            
            # Apply LoRA
            self.model = get_peft_model(self.model, self.lora_config)
            self.model.print_trainable_parameters()
            
            self.logger.info("Model and tokenizer setup complete")
            
        except Exception as e:
            self.logger.error(f"Error setting up model: {e}")
            raise
    
    def fine_tune(self) -> bool:
        """
        Execute the fine-tuning process.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Create output directory
            self.output_dir.mkdir(parents=True, exist_ok=True)
            
            # Load and prepare data
            conversations = self.load_dataset()
            if not conversations:
                self.logger.error("No training data available")
                return False
            
            # Setup model
            self.setup_model_and_tokenizer()
            
            # Prepare dataset
            dataset = self.prepare_training_data(conversations)
            tokenized_dataset = self.tokenize_dataset(dataset)
            
            # Data collator
            data_collator = DataCollatorForLanguageModeling(
                tokenizer=self.tokenizer,
                mlm=False,
                pad_to_multiple_of=8
            )
            
            # Initialize trainer
            trainer = Trainer(
                model=self.model,
                args=self.training_args,
                train_dataset=tokenized_dataset,
                data_collator=data_collator,
                tokenizer=self.tokenizer
            )
            
            # Start fine-tuning
            self.logger.info("Starting fine-tuning...")
            trainer.train()
            
            # Save the model
            trainer.save_model()
            self.tokenizer.save_pretrained(self.output_dir)
            
            self.logger.info(f"Fine-tuning complete! Model saved to {self.output_dir}")
            return True
            
        except Exception as e:
            self.logger.error(f"Fine-tuning failed: {e}")
            return False
    
    def load_fine_tuned_model(self, model_path: str = None):
        """
        Load a fine-tuned model for inference.
        
        Args:
            model_path: Path to fine-tuned model (default: latest in output_dir)
        """
        try:
            model_path = model_path or str(self.output_dir)
            
            # Load base model
            base_model = AutoModelForCausalLM.from_pretrained(
                self.base_model,
                torch_dtype=torch.float16,
                device_map="auto"
            )
            
            # Load LoRA weights
            self.model = PeftModel.from_pretrained(base_model, model_path)
            
            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(model_path)
            
            self.logger.info(f"Fine-tuned model loaded from {model_path}")
            
        except Exception as e:
            self.logger.error(f"Error loading fine-tuned model: {e}")
            raise
    
    def add_conversation_example(self, user_input: str, assistant_output: str):
        """
        Add a new conversation example to the dataset.
        
        Args:
            user_input: User's input
            assistant_output: Desired assistant output
        """
        try:
            # Load existing data
            if self.dataset_path.exists():
                with open(self.dataset_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            else:
                data = {"conversations": []}
            
            # Add new example
            new_example = {
                "input": user_input,
                "output": assistant_output
            }
            
            data["conversations"].append(new_example)
            
            # Save back to file
            with open(self.dataset_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            self.logger.info("Added new conversation example to dataset")
            
        except Exception as e:
            self.logger.error(f"Error adding conversation example: {e}")
    
    def create_sample_dataset(self):
        """Create a sample dataset with basic conversation examples."""
        sample_conversations = [
            {
                "input": "Hello Nova!",
                "output": "Hello! I'm Nova, your personal AI assistant. How can I help you today?"
            },
            {
                "input": "What can you do?",
                "output": "I can help you with many tasks! I can open applications, search the web, set reminders, answer questions, and have conversations. What would you like to try?"
            },
            {
                "input": "Open calculator",
                "output": "I'll open the calculator for you right now! *opens calculator application* There you go!"
            },
            {
                "input": "Thanks for your help",
                "output": "You're very welcome! I'm always here to help whenever you need assistance. Is there anything else I can do for you?"
            }
        ]
        
        data = {"conversations": sample_conversations}
        
        # Ensure directory exists
        self.dataset_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(self.dataset_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Created sample dataset at {self.dataset_path}")


def main():
    """Example usage of the fine-tuning system."""
    logging.basicConfig(level=logging.INFO)
    
    fine_tuner = NovaFineTuner()
    
    # Create sample dataset if it doesn't exist
    if not fine_tuner.dataset_path.exists():
        fine_tuner.create_sample_dataset()
    
    print("NOVA Fine-tuning System")
    print("======================")
    print("1. Create sample dataset")
    print("2. Add conversation example")
    print("3. Start fine-tuning")
    print("4. Test fine-tuned model")
    
    choice = input("Select option (1-4): ")
    
    if choice == "1":
        fine_tuner.create_sample_dataset()
        print("Sample dataset created!")
    
    elif choice == "2":
        user_input = input("User input: ")
        assistant_output = input("Desired assistant response: ")
        fine_tuner.add_conversation_example(user_input, assistant_output)
        print("Example added to dataset!")
    
    elif choice == "3":
        print("Starting fine-tuning... This may take a while.")
        if fine_tuner.fine_tune():
            print("Fine-tuning completed successfully!")
        else:
            print("Fine-tuning failed.")
    
    elif choice == "4":
        print("Testing functionality not yet implemented.")
    
    else:
        print("Invalid choice.")


if __name__ == "__main__":
    main()