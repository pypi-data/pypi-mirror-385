"""
Prompt templates for LLM interactions
"""
import os
from pathlib import Path

# Get the directory where this __init__.py is located
PROMPTS_DIR = Path(__file__).parent.absolute()

def get_prompt_path(prompt_name):
    """Get the full path to a prompt file"""
    return PROMPTS_DIR / prompt_name
