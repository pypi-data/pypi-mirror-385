"""LLM API module for GHAI CLI."""

from pathlib import Path
from typing import Dict, Optional

import llm

from ghai.util import KeyUtil


class ModelClassMapper:
    """Maps LLM model classes to their corresponding API key names."""

    # Mapping of model class names to API key names
    CLASS_KEY_MAPPING: Dict[str, str] = {
        # Anthropic Models
        "llm_anthropic": "ANTHROPIC_API_KEY",

        # GitHub Models
        "llm_github_models": "GITHUB_TOKEN",

        # OpenAI Models
        "llm.default_plugins.openai_models": "OPENAI_API_KEY",
    }

    @classmethod
    def get_key_name_for_model_obj(cls, model_obj: llm.Model) -> Optional[str]:
        """Get the appropriate API key name for a given model object.

        Args:
            model_obj: The LLM model object

        Returns:
            The API key name to use, or None if no key required
        """
        model_class_name = model_obj.__class__.__module__

        if model_class_name in cls.CLASS_KEY_MAPPING:
            return cls.CLASS_KEY_MAPPING[model_class_name]

        return None

    @classmethod
    def get_key_name_for_model_name(cls, model_name: str) -> Optional[str]:
        """Get the appropriate API key name for a given model name.

        Args:
            model_name: The model name/ID

        Returns:
            The API key name to use, or None if no key required
        """
        try:
            model_obj = llm.get_model(model_name)
            return cls.get_key_name_for_model_obj(model_obj)
        except Exception as e:
            raise ValueError(f"Error loading model '{model_name}': {e}")


class LLMClient:
    """A simple client for interacting with LLM models."""

    def __init__(self, model_name: Optional[str] = None):
        """Initialize the LLM client.

        Args:
            model_name: Name of the LLM model to use. If None, will use the default model from keys.json
            api_key: API key for the model. If not provided, will try to get from GHAI's key storage
        """

        if model_name is None:
            model_name = KeyUtil.get_default_model()  # Default name from set keys

        if model_name is None:
            model_name = "github/o1"  # Fallback default

        self.model_name = model_name
        self.model = llm.get_model(model_name)

        # If no API key provided, try to get it from GHAI keys
        api_key_name = ModelClassMapper.get_key_name_for_model_name(model_name)
        if api_key_name is None:
            raise ValueError(f"Model '{model_name}' is not recognised.")

        api_key = KeyUtil.get_key_by_name(api_key_name)
        if api_key is None:
            raise ValueError(
                f"Please set the required API key '{api_key_name}' for model '{model_name}'."
            )

        self.model.key = api_key

    def generate_response(self, prompt_content: str, context_files: list[str]) -> str:
        """Generate a response using a prompt file and optional attachment files.

        Args:
            prompt_content: The prompt text to send to the model
            context_files: List of file paths to attach to the prompt

        Returns:
            The LLM response as a string

        Raises:
            FileNotFoundError: If any context file doesn't exist
        """
        print(f"Using model: {self.model_name}")
        fragments: list[str] = []
        for file_path in context_files:
            path = Path(file_path)
            if not path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")
            with open(path) as f:
                fragments.append(f.read())

        # Use positional argument for prompt to avoid type issues
        response = self.model.prompt(  # pyright: ignore[reportUnknownMemberType]
            prompt=prompt_content, fragments=fragments)
        result = response.text()
        return str(result)

    @staticmethod
    def get_available_models() -> list[str]:
        """Get list of available LLM models.

        Returns:
            List of available model IDs
        """
        models: list[str] = []
        for model in llm.get_models():
            models.append(model.model_id)
        return models


if __name__ == "__main__":
    llm_client = LLMClient()
    model = llm.get_model("github/o1")
    modelMapper = ModelClassMapper()
    print(modelMapper.get_key_name_for_model_obj(model))
    print(llm_client.get_available_models())
