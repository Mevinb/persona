# ARK Fine-tuning README
# ======================

This directory contains tools and resources for fine-tuning ARK's language model to better match your personal preferences and communication style.

## Overview

ARK uses LoRA (Low-Rank Adaptation) for efficient fine-tuning, which allows you to customize the assistant's responses without requiring massive computational resources.

## Files

- `dataset.jsonl` - Training dataset with conversation examples
- `fine_tuner.py` - Main fine-tuning script and utilities
- `models/` - Directory where fine-tuned models will be saved (created automatically)

## How to Use

### 1. Prepare Your Dataset

Edit `dataset.jsonl` to include examples of how you want ARK to respond. The format is:

```json
{
  "conversations": [
    {
      "input": "User says this",
      "output": "ARK should respond like this"
    }
  ]
}
```

### 2. Add Custom Examples

You can add examples through the script:

```bash
python fine_tuner.py
# Select option 2 to add conversation examples
```

### 3. Start Fine-tuning

```bash
python fine_tuner.py
# Select option 3 to start fine-tuning
```

**Note:** Fine-tuning requires significant GPU memory and time. Make sure you have:
- CUDA-capable GPU with at least 8GB VRAM
- All required dependencies installed (see main requirements.txt)

### 4. Use Fine-tuned Model

After fine-tuning completes, update your `data/config.yaml` to use the fine-tuned model:

```yaml
model:
  name: "fine_tune/models"  # Point to your fine-tuned model directory
```

## Tips for Good Training Data

1. **Quality over Quantity**: 20-50 high-quality examples are better than 200 poor ones
2. **Consistency**: Make sure your examples reflect the tone and style you want
3. **Variety**: Include different types of conversations and scenarios
4. **Natural Language**: Use realistic conversation patterns
5. **Your Voice**: Include examples that reflect how you personally communicate

## Example Training Scenarios

- Personalizing greeting styles
- Adjusting formality level
- Adding domain-specific knowledge
- Customizing humor and personality
- Teaching preferred response formats

## Future Enhancements

This fine-tuning system will be expanded to support:
- Automatic dataset generation from conversations
- Multiple fine-tuning targets (different personalities/modes)
- Continuous learning from user feedback
- Advanced LoRA configurations
- Model merging and evaluation tools