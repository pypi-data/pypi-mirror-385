"""
Data models for Cosmos DB prompt data validation and serialization.
"""

from typing import Dict, Any

class PromptModel:
    """
    Flexible data model representing a Cosmos DB prompt document.

    Required fields:
        id: Unique identifier for the prompt (same as prompt_name)
        prompt_name: Name of the prompt (typically same as id)
        prompt_template: The actual prompt template content

    Optional fields:
        All other fields are stored dynamically and can be any valid Cosmos DB data type.
        Common optional fields include: description, version, timestamp, category, tags, etc.

    Example:
        model = PromptModel(
            id="greeting",
            prompt_name="greeting",
            prompt_template="Hello {name}!",
            description="A friendly greeting",
            custom_field="any value"
        )
    """

    def __init__(
        self,
        id: str,
        prompt_name: str,
        prompt_template: str,
        **kwargs: Any
    ):
        """
        Initialize a PromptModel with required fields and arbitrary optional fields.

        Args:
            id: Unique identifier for the prompt
            prompt_name: Name of the prompt (typically same as id)
            prompt_template: The actual prompt template content
            **kwargs: Any additional optional fields to store in the model
        """
        if not id:
            raise ValueError("id is required and cannot be empty")
        if not prompt_name:
            raise ValueError("prompt_name is required and cannot be empty")
        if not prompt_template:
            raise ValueError("prompt_template is required and cannot be empty")

        self.id = id
        self.prompt_name = prompt_name
        self.prompt_template = prompt_template

        for key, value in kwargs.items():
            setattr(self, key, value)

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the model to a dictionary suitable for Cosmos DB storage.

        Returns:
            Dictionary containing all model fields including required and optional fields
        """
        result = {
            "id": self.id,
            "prompt_name": self.prompt_name,
            "prompt_template": self.prompt_template,
        }

        for key, value in self.__dict__.items():
            if key not in result:
                result[key] = value

        return result

    @classmethod
    def from_cosmos_doc(cls, doc: Dict[str, Any]) -> 'PromptModel':
        """
        Create a PromptModel instance from a raw Cosmos DB document.

        Args:
            doc: Raw dictionary from Cosmos DB

        Returns:
            PromptModel instance

        Raises:
            ValueError: If required fields (id, prompt_template) are missing
        """
        if not doc.get('id'):
            raise ValueError("Invalid prompt document: missing required field 'id'")
        if not doc.get('prompt_template'):
            raise ValueError("Invalid prompt document: missing required field 'prompt_template'")

        prompt_name = doc.get('prompt_name', doc.get('name', doc['id']))

        kwargs = {k: v for k, v in doc.items() if k not in {'id', 'prompt_name', 'prompt_template'}}

        return cls(
            id=doc['id'],
            prompt_name=prompt_name,
            prompt_template=doc['prompt_template'],
            **kwargs
        )

    def __repr__(self) -> str:
        """String representation of the PromptModel."""
        attrs = ", ".join(f"{k}={v!r}" for k, v in self.__dict__.items())
        return f"PromptModel({attrs})"

    def __eq__(self, other: Any) -> bool:
        """Check equality based on all attributes."""
        if not isinstance(other, PromptModel):
            return False
        return self.__dict__ == other.__dict__