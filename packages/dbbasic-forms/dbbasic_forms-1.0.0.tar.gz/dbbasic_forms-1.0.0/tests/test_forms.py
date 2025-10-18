"""
Tests for dbbasic-forms
"""

import json
import tempfile
from pathlib import Path
import pytest
from dbbasic_forms import FormBuilder


@pytest.fixture
def temp_data_dir():
    """Create a temporary data directory for testing"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def builder(temp_data_dir):
    """Create a FormBuilder instance for testing"""
    return FormBuilder(data_dir=temp_data_dir)


def test_create_form(builder):
    """Test creating a new form"""
    form = builder.create_form(
        form_id="test",
        name="Test Form",
        description="A test form",
        fields=[
            {"name": "email", "type": "email", "required": True},
            {"name": "message", "type": "textarea"},
        ],
    )

    assert form.form_id == "test"
    assert form.form_data["name"] == "Test Form"
    assert len(form.fields) == 2


def test_get_form(builder):
    """Test retrieving a form"""
    builder.create_form("test", "Test Form")
    form = builder.get_form("test")

    assert form is not None
    assert form.form_id == "test"

    # Non-existent form
    assert builder.get_form("nonexistent") is None


def test_list_forms(builder):
    """Test listing all forms"""
    builder.create_form("form1", "Form 1")
    builder.create_form("form2", "Form 2")

    forms = builder.list_forms()
    assert len(forms) == 2
    assert forms[0]["id"] in ["form1", "form2"]


def test_delete_form(builder):
    """Test deleting a form"""
    builder.create_form("test", "Test Form")
    assert builder.get_form("test") is not None

    deleted = builder.delete_form("test")
    assert deleted is True
    assert builder.get_form("test") is None

    # Try deleting non-existent form
    assert builder.delete_form("nonexistent") is False


def test_submit_response(builder):
    """Test submitting a response"""
    form = builder.create_form(
        "test",
        "Test Form",
        fields=[
            {"name": "email", "type": "email"},
            {"name": "message", "type": "textarea"},
        ],
    )

    response_id = form.submit_response(
        {"email": "test@example.com", "message": "Hello world"}
    )

    assert response_id.startswith("resp_")
    assert form.count_responses() == 1


def test_get_responses(builder):
    """Test retrieving responses"""
    form = builder.create_form(
        "test",
        "Test Form",
        fields=[{"name": "email", "type": "email"}],
    )

    # Submit multiple responses
    form.submit_response({"email": "user1@example.com"})
    form.submit_response({"email": "user2@example.com"})
    form.submit_response({"email": "user3@example.com"})

    # Get all responses
    responses = form.get_responses()
    assert len(responses) == 3

    # Test pagination
    responses = form.get_responses(limit=2)
    assert len(responses) == 2

    responses = form.get_responses(limit=2, offset=2)
    assert len(responses) == 1


def test_count_responses(builder):
    """Test counting responses"""
    form = builder.create_form(
        "test", "Test Form", fields=[{"name": "email", "type": "email"}]
    )

    assert form.count_responses() == 0

    form.submit_response({"email": "user1@example.com"})
    assert form.count_responses() == 1

    form.submit_response({"email": "user2@example.com"})
    assert form.count_responses() == 2


def test_get_response(builder):
    """Test retrieving a single response"""
    form = builder.create_form(
        "test", "Test Form", fields=[{"name": "email", "type": "email"}]
    )

    response_id = form.submit_response({"email": "test@example.com"})

    response = form.get_response(response_id)
    assert response is not None
    assert response["id"] == response_id
    assert response["email"] == "test@example.com"

    # Non-existent response
    assert form.get_response("nonexistent") is None


def test_delete_response(builder):
    """Test deleting a response"""
    form = builder.create_form(
        "test", "Test Form", fields=[{"name": "email", "type": "email"}]
    )

    response_id = form.submit_response({"email": "test@example.com"})
    assert form.count_responses() == 1

    deleted = form.delete_response(response_id)
    assert deleted is True
    assert form.count_responses() == 0

    # Try deleting non-existent response
    assert form.delete_response("nonexistent") is False


def test_update_form(builder):
    """Test updating a form"""
    form = builder.create_form("test", "Test Form", description="Old description")

    updated = form.update_form(
        name="Updated Form",
        description="New description",
        fields=[{"name": "new_field", "type": "text"}],
    )

    assert updated is True
    assert form.form_data["name"] == "Updated Form"
    assert form.form_data["description"] == "New description"
    assert len(form.fields) == 1


def test_export_responses_csv(builder):
    """Test exporting responses to CSV"""
    form = builder.create_form(
        "test",
        "Test Form",
        fields=[
            {"name": "email", "type": "email"},
            {"name": "message", "type": "textarea"},
        ],
    )

    form.submit_response({"email": "user1@example.com", "message": "Hello"})
    form.submit_response({"email": "user2@example.com", "message": "World"})

    csv_data = form.export_responses_csv()
    assert "email" in csv_data
    assert "message" in csv_data
    assert "user1@example.com" in csv_data
    assert "user2@example.com" in csv_data


def test_form_to_dict(builder):
    """Test converting form to dictionary"""
    form = builder.create_form(
        "test",
        "Test Form",
        description="Test description",
        fields=[{"name": "email", "type": "email"}],
    )

    form_dict = form.to_dict()
    assert form_dict["id"] == "test"
    assert form_dict["name"] == "Test Form"
    assert form_dict["description"] == "Test description"
    assert len(form_dict["fields"]) == 1
    assert form_dict["response_count"] == 0


def test_metadata_in_response(builder):
    """Test storing metadata with responses"""
    form = builder.create_form(
        "test", "Test Form", fields=[{"name": "email", "type": "email"}]
    )

    response_id = form.submit_response(
        {"email": "test@example.com", "_metadata": {"ip": "1.2.3.4", "user_agent": "Test"}}
    )

    response = form.get_response(response_id)
    assert response["metadata"]["ip"] == "1.2.3.4"
    assert response["metadata"]["user_agent"] == "Test"


def test_multiselect_fields(builder):
    """Test handling multi-select checkbox fields"""
    form = builder.create_form(
        "test",
        "Test Form",
        fields=[
            {
                "name": "interests",
                "type": "checkbox",
                "options": ["Option 1", "Option 2", "Option 3"],
            }
        ],
    )

    # Submit with array
    response_id = form.submit_response({"interests": ["Option 1", "Option 3"]})

    response = form.get_response(response_id)
    # Should be stored as JSON string
    assert isinstance(response["interests"], str)
    assert "Option 1" in response["interests"]
    assert "Option 3" in response["interests"]
