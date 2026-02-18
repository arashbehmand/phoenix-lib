"""YAML-based prompt loader shared across Phoenix services."""

from pathlib import Path

import yaml


class PromptLoader:
    """Loads prompt templates from YAML files."""

    def __init__(self, base_dir: Path):
        """Initialize the prompt loader with a base directory.

        Args:
            base_dir: The base directory containing prompt template files.
        """
        self.base_dir = base_dir

    def load(self, name: str) -> str:
        """Load a prompt template by name.

        Args:
            name: The name of the prompt template to load.

        Returns:
            The prompt template string.

        Raises:
            ValueError: If the template is missing or malformed.
            FileNotFoundError: If the prompt file does not exist.
        """
        file_path = self.base_dir / f"{name}.yaml"
        data = yaml.safe_load(file_path.read_text(encoding="utf-8"))
        template = data.get("template")
        if not template:
            raise ValueError(f"Prompt '{name}' missing 'template' key in {file_path}")
        return template
