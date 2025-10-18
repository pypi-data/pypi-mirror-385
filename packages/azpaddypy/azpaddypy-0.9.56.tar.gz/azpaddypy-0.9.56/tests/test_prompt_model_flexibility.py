"""
Tests for the flexible PromptModel class.

This module tests the new flexible PromptModel that allows arbitrary optional fields
while enforcing only three required fields: id, prompt_name, and prompt_template.
"""

import pytest
from azpaddypy.tools.prompt_models import PromptModel


class TestPromptModelFlexibility:
    """Test the flexible PromptModel with minimal required fields and arbitrary optional fields."""

    def test_required_fields_only(self):
        """Test creating PromptModel with only required fields."""
        model = PromptModel(
            id="test_id",
            prompt_name="test_prompt",
            prompt_template="Hello {name}!"
        )

        assert model.id == "test_id"
        assert model.prompt_name == "test_prompt"
        assert model.prompt_template == "Hello {name}!"

    def test_with_standard_optional_fields(self):
        """Test creating PromptModel with common optional fields."""
        model = PromptModel(
            id="greeting",
            prompt_name="greeting",
            prompt_template="Hello {name}!",
            description="A friendly greeting",
            version="1.0.0",
            timestamp="2023-01-01T00:00:00.000000Z"
        )

        assert model.id == "greeting"
        assert model.prompt_name == "greeting"
        assert model.prompt_template == "Hello {name}!"
        assert model.description == "A friendly greeting"
        assert model.version == "1.0.0"
        assert model.timestamp == "2023-01-01T00:00:00.000000Z"

    def test_with_custom_optional_fields(self):
        """Test creating PromptModel with arbitrary custom fields."""
        model = PromptModel(
            id="custom_prompt",
            prompt_name="custom_prompt",
            prompt_template="Custom template",
            category="ai_chat",
            tags=["greeting", "friendly"],
            author="user123",
            rating=4.5,
            is_public=True,
            metadata={"key": "value"},
            custom_field_1="anything",
            custom_field_2=42
        )

        assert model.id == "custom_prompt"
        assert model.prompt_name == "custom_prompt"
        assert model.prompt_template == "Custom template"
        assert model.category == "ai_chat"
        assert model.tags == ["greeting", "friendly"]
        assert model.author == "user123"
        assert model.rating == 4.5
        assert model.is_public is True
        assert model.metadata == {"key": "value"}
        assert model.custom_field_1 == "anything"
        assert model.custom_field_2 == 42

    def test_to_dict_includes_all_fields(self):
        """Test that to_dict includes all fields including custom ones."""
        model = PromptModel(
            id="test",
            prompt_name="test",
            prompt_template="template",
            custom1="value1",
            custom2=123
        )

        result = model.to_dict()

        assert result["id"] == "test"
        assert result["prompt_name"] == "test"
        assert result["prompt_template"] == "template"
        assert result["custom1"] == "value1"
        assert result["custom2"] == 123

    def test_from_cosmos_doc_with_standard_fields(self):
        """Test creating PromptModel from Cosmos DB document with standard fields."""
        doc = {
            "id": "doc_prompt",
            "prompt_name": "doc_prompt",
            "prompt_template": "Document template",
            "description": "From Cosmos",
            "version": "2.0.0"
        }

        model = PromptModel.from_cosmos_doc(doc)

        assert model.id == "doc_prompt"
        assert model.prompt_name == "doc_prompt"
        assert model.prompt_template == "Document template"
        assert model.description == "From Cosmos"
        assert model.version == "2.0.0"

    def test_from_cosmos_doc_with_custom_fields(self):
        """Test creating PromptModel from Cosmos DB document with custom fields."""
        doc = {
            "id": "custom_doc",
            "prompt_name": "custom_doc",
            "prompt_template": "Custom template",
            "tenant_id": "tenant123",
            "language": "en",
            "priority": 5,
            "enabled": True
        }

        model = PromptModel.from_cosmos_doc(doc)

        assert model.id == "custom_doc"
        assert model.prompt_name == "custom_doc"
        assert model.prompt_template == "Custom template"
        assert model.tenant_id == "tenant123"
        assert model.language == "en"
        assert model.priority == 5
        assert model.enabled is True

    def test_from_cosmos_doc_fallback_prompt_name(self):
        """Test that from_cosmos_doc uses 'name' or 'id' as fallback for prompt_name."""
        # Test with 'name' field
        doc1 = {
            "id": "test1",
            "name": "test_name",
            "prompt_template": "template"
        }
        model1 = PromptModel.from_cosmos_doc(doc1)
        assert model1.prompt_name == "test_name"

        # Test with only 'id' field (no name or prompt_name)
        doc2 = {
            "id": "test2",
            "prompt_template": "template"
        }
        model2 = PromptModel.from_cosmos_doc(doc2)
        assert model2.prompt_name == "test2"

    def test_from_cosmos_doc_missing_id_raises_error(self):
        """Test that missing 'id' field raises ValueError."""
        doc = {
            "prompt_name": "test",
            "prompt_template": "template"
        }

        with pytest.raises(ValueError, match="missing required field 'id'"):
            PromptModel.from_cosmos_doc(doc)

    def test_from_cosmos_doc_missing_prompt_template_raises_error(self):
        """Test that missing 'prompt_template' field raises ValueError."""
        doc = {
            "id": "test",
            "prompt_name": "test"
        }

        with pytest.raises(ValueError, match="missing required field 'prompt_template'"):
            PromptModel.from_cosmos_doc(doc)

    def test_init_empty_id_raises_error(self):
        """Test that empty 'id' raises ValueError."""
        with pytest.raises(ValueError, match="id is required and cannot be empty"):
            PromptModel(
                id="",
                prompt_name="test",
                prompt_template="template"
            )

    def test_init_empty_prompt_name_raises_error(self):
        """Test that empty 'prompt_name' raises ValueError."""
        with pytest.raises(ValueError, match="prompt_name is required and cannot be empty"):
            PromptModel(
                id="test",
                prompt_name="",
                prompt_template="template"
            )

    def test_init_empty_prompt_template_raises_error(self):
        """Test that empty 'prompt_template' raises ValueError."""
        with pytest.raises(ValueError, match="prompt_template is required and cannot be empty"):
            PromptModel(
                id="test",
                prompt_name="test",
                prompt_template=""
            )

    def test_repr(self):
        """Test string representation of PromptModel."""
        model = PromptModel(
            id="test",
            prompt_name="test",
            prompt_template="template",
            custom="value"
        )

        repr_str = repr(model)
        assert "PromptModel(" in repr_str
        assert "id='test'" in repr_str
        assert "prompt_name='test'" in repr_str
        assert "prompt_template='template'" in repr_str
        assert "custom='value'" in repr_str

    def test_equality(self):
        """Test equality comparison between PromptModel instances."""
        model1 = PromptModel(
            id="test",
            prompt_name="test",
            prompt_template="template",
            custom="value"
        )
        model2 = PromptModel(
            id="test",
            prompt_name="test",
            prompt_template="template",
            custom="value"
        )
        model3 = PromptModel(
            id="test",
            prompt_name="test",
            prompt_template="different",
            custom="value"
        )

        assert model1 == model2
        assert model1 != model3
        assert model1 != "not a model"

    def test_roundtrip_to_dict_from_cosmos_doc(self):
        """Test that to_dict and from_cosmos_doc are inverses."""
        original = PromptModel(
            id="roundtrip",
            prompt_name="roundtrip",
            prompt_template="template",
            custom1="value1",
            custom2=123,
            nested={"key": "value"}
        )

        # Convert to dict
        doc = original.to_dict()

        # Convert back to model
        restored = PromptModel.from_cosmos_doc(doc)

        # Should be equal
        assert restored == original
        assert restored.id == original.id
        assert restored.prompt_name == original.prompt_name
        assert restored.prompt_template == original.prompt_template
        assert restored.custom1 == original.custom1
        assert restored.custom2 == original.custom2
        assert restored.nested == original.nested
