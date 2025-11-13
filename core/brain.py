"""
NOVA Brain Module
================
Handles model loading, inference, and response generation using open-source LLMs.
Supports local models via Transformers library with memory-efficient loading.
"""

import torch
from transformers import (
    AutoTokenizer, 
    AutoModelForCausalLM, 
    BitsAndBytesConfig,
    pipeline
)
import yaml
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path

class Brain:
    """
    Core AI brain for NOVA assistant.
    Manages LLM loading, inference, and response generation.
    """
    
    def __init__(self, config_path: str = "data/config.yaml"):
        """
        Initialize the Brain with configuration.
        
        Args:
            config_path: Path to configuration file
        """
        self.logger = logging.getLogger(__name__)
        self.config = self._load_config(config_path)
        self.tokenizer = None
        self.model = None
        self.pipeline = None
        self.personality = self._load_personality()
        
        # Model configuration
        self.model_name = self.config.get('model', {}).get('name', 'mistralai/Mistral-7B-v0.1')
        self.max_tokens = self.config.get('model', {}).get('max_tokens', 512)
        self.temperature = self.config.get('model', {}).get('temperature', 0.7)
        self.use_quantization = self.config.get('model', {}).get('quantization', True)
        
        self.logger.info(f"Brain initialized with model: {self.model_name}")
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            self.logger.warning(f"Config file not found: {config_path}, using defaults")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Return default configuration."""
        return {
            'model': {
                'name': 'mistralai/Mistral-7B-v0.1',
                'max_tokens': 512,
                'temperature': 0.7,
                'quantization': True
            }
        }
    
    def _load_personality(self) -> Dict[str, Any]:
        """Load personality configuration."""
        try:
            with open("core/personality.yaml", 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            self.logger.warning("Personality file not found, using default")
            return self._get_default_personality()
    
    def _get_default_personality(self) -> Dict[str, Any]:
        """Return default personality traits."""
        return {
            'name': 'Nova',
            'traits': ['friendly', 'witty', 'loyal', 'curious'],
            'tone': 'conversational',
            'style': 'helpful but not overly formal'
        }
    
    def load_model(self) -> bool:
        """
        Load the language model and tokenizer.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            self.logger.info(f"Loading model: {self.model_name}")
            
            # Configure quantization for memory efficiency
            quantization_config = None
            if self.use_quantization:
                quantization_config = BitsAndBytesConfig(
                    load_in_4bit=True,
                    bnb_4bit_compute_dtype=torch.float16,
                    bnb_4bit_use_double_quant=True,
                    bnb_4bit_quant_type="nf4"
                )
            
            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_name,
                padding_side="left"
            )
            
            # Add pad token if missing
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            # Load model
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                quantization_config=quantization_config,
                device_map="auto",
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                trust_remote_code=True
            )
            
            # Create text generation pipeline
            self.pipeline = pipeline(
                "text-generation",
                model=self.model,
                tokenizer=self.tokenizer,
                max_new_tokens=self.max_tokens,
                temperature=self.temperature,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id
            )
            
            self.logger.info("Model loaded successfully!")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to load model: {e}")
            return False
    
    def generate_response(self, prompt: str, context: List[Dict] = None) -> str:
        """
        Generate a response to the given prompt.
        
        Args:
            prompt: User input prompt
            context: Previous conversation context
            
        Returns:
            Generated response string
        """
        if not self.model or not self.pipeline:
            return "I'm sorry, my brain isn't fully loaded yet. Please wait a moment."
        
        try:
            # Build context-aware prompt
            full_prompt = self._build_prompt(prompt, context)
            
            # Generate response
            outputs = self.pipeline(
                full_prompt,
                max_new_tokens=self.max_tokens,
                temperature=self.temperature,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id
            )
            
            # Extract the generated text
            generated_text = outputs[0]['generated_text']
            
            # Remove the input prompt from the response
            response = generated_text[len(full_prompt):].strip()
            
            # Clean up the response
            response = self._clean_response(response)
            
            self.logger.info(f"Generated response of {len(response)} characters")
            return response
            
        except Exception as e:
            self.logger.error(f"Error generating response: {e}")
            return "I'm having trouble thinking right now. Could you try again?"
    
    def _build_prompt(self, user_input: str, context: List[Dict] = None) -> str:
        """
        Build a complete prompt with personality and context.
        
        Args:
            user_input: Current user input
            context: Previous conversation history
            
        Returns:
            Complete formatted prompt
        """
        # System prompt with personality
        system_prompt = f"""You are {self.personality['name']}, a personal AI assistant.
Your personality traits: {', '.join(self.personality['traits'])}
Tone: {self.personality['tone']}
Style: {self.personality['style']}

You are helpful, remember user preferences, and maintain context across conversations.
Keep responses concise but warm and engaging."""

        # Add conversation history if available
        conversation = ""
        if context:
            for entry in context[-5:]:  # Last 5 exchanges
                conversation += f"Human: {entry.get('user', '')}\n"
                conversation += f"Nova: {entry.get('assistant', '')}\n"
        
        # Build complete prompt
        full_prompt = f"{system_prompt}\n\n{conversation}Human: {user_input}\nNova:"
        
        return full_prompt
    
    def _clean_response(self, response: str) -> str:
        """
        Clean and format the generated response.
        
        Args:
            response: Raw generated response
            
        Returns:
            Cleaned response
        """
        # Remove common artifacts
        response = response.replace("Nova:", "").strip()
        response = response.replace("Human:", "").strip()
        
        # Stop at natural conversation boundaries
        stop_patterns = ["\nHuman:", "\nUser:", "\n\n"]
        for pattern in stop_patterns:
            if pattern in response:
                response = response.split(pattern)[0]
        
        # Ensure reasonable length
        if len(response) > 500:
            sentences = response.split('. ')
            response = '. '.join(sentences[:3]) + '.'
        
        return response.strip()
    
    def is_loaded(self) -> bool:
        """Check if the model is loaded and ready."""
        return self.model is not None and self.pipeline is not None
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model."""
        return {
            'model_name': self.model_name,
            'max_tokens': self.max_tokens,
            'temperature': self.temperature,
            'quantization': self.use_quantization,
            'loaded': self.is_loaded(),
            'personality': self.personality
        }
    
    def unload_model(self):
        """Unload the model to free memory."""
        try:
            if self.model:
                del self.model
            if self.pipeline:
                del self.pipeline
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            
            self.model = None
            self.pipeline = None
            self.logger.info("Model unloaded successfully")
            
        except Exception as e:
            self.logger.error(f"Error unloading model: {e}")


if __name__ == "__main__":
    # Test the Brain module
    logging.basicConfig(level=logging.INFO)
    
    brain = Brain()
    
    print("Loading model...")
    if brain.load_model():
        print("Model loaded successfully!")
        
        # Test conversation
        response = brain.generate_response("Hello, what's your name?")
        print(f"Nova: {response}")
        
        # Test with context
        context = [{"user": "Hello, what's your name?", "assistant": response}]
        response2 = brain.generate_response("What can you help me with?", context)
        print(f"Nova: {response2}")
        
    else:
        print("Failed to load model")