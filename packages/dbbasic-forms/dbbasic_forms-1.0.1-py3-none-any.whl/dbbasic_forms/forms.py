"""
Form builder and response handler for dbbasic-forms
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from dbbasic.tsv import TSV


class FormBuilder:
    """Build and manage forms with TSV storage"""

    def __init__(self, data_dir: str = "data"):
        """Initialize form builder

        Args:
            data_dir: Directory to store form definitions and responses
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)

        # Initialize TSV tables
        self.forms = TSV(
            "forms",
            ["id", "name", "description", "fields", "settings", "created_at", "updated_at"],
            data_dir=self.data_dir,
            indexes=["id"],
        )

    def create_form(
        self,
        form_id: str,
        name: str,
        description: str = "",
        fields: Optional[List[Dict[str, Any]]] = None,
        settings: Optional[Dict[str, Any]] = None,
    ) -> "Form":
        """Create a new form

        Args:
            form_id: Unique identifier for the form
            name: Form name
            description: Form description
            fields: List of field definitions
            settings: Form settings (success message, button text, etc.)

        Returns:
            Form instance
        """
        if fields is None:
            fields = []
        if settings is None:
            settings = {
                "success_message": "Thanks! We'll get back to you soon.",
                "button_text": "Submit",
            }

        now = datetime.utcnow().isoformat()

        self.forms.insert(
            {
                "id": form_id,
                "name": name,
                "description": description,
                "fields": json.dumps(fields),
                "settings": json.dumps(settings),
                "created_at": now,
                "updated_at": now,
            }
        )

        return Form(form_id, self.data_dir)

    def get_form(self, form_id: str) -> Optional["Form"]:
        """Get a form by ID

        Args:
            form_id: Form identifier

        Returns:
            Form instance or None if not found
        """
        form_data = self.forms.query_one(id=form_id)
        if not form_data:
            return None
        return Form(form_id, self.data_dir)

    def list_forms(self) -> List[Dict[str, Any]]:
        """List all forms

        Returns:
            List of form data dictionaries
        """
        forms = []
        for form_data in self.forms.all():
            # Get response count
            form = Form(form_data["id"], self.data_dir)
            response_count = form.count_responses()

            forms.append(
                {
                    "id": form_data["id"],
                    "name": form_data["name"],
                    "description": form_data["description"],
                    "created_at": form_data["created_at"],
                    "response_count": response_count,
                }
            )
        return forms

    def delete_form(self, form_id: str) -> bool:
        """Delete a form and all its responses

        Args:
            form_id: Form identifier

        Returns:
            True if deleted, False if not found
        """
        # Delete responses first
        form = self.get_form(form_id)
        if form:
            form._delete_responses_table()

        # Delete form
        deleted = self.forms.delete(id=form_id)
        return deleted > 0


class Form:
    """Individual form with response handling"""

    def __init__(self, form_id: str, data_dir: Path = Path("data")):
        """Initialize form

        Args:
            form_id: Form identifier
            data_dir: Data directory path
        """
        self.form_id = form_id
        self.data_dir = Path(data_dir)

        # Load form data
        forms_table = TSV("forms", data_dir=self.data_dir, indexes=["id"])
        self.form_data = forms_table.query_one(id=form_id)

        if not self.form_data:
            raise ValueError(f"Form '{form_id}' not found")

        # Parse JSON fields
        self.fields = json.loads(self.form_data["fields"])
        self.settings = json.loads(self.form_data["settings"])

        # Initialize responses table
        self._init_responses_table()

    def _init_responses_table(self):
        """Initialize the responses TSV table"""
        # Extract field names from form definition
        field_names = [field["name"] for field in self.fields]

        # Standard columns plus dynamic fields
        columns = ["id", "submitted_at"] + field_names + ["metadata"]

        self.responses = TSV(
            f"responses_{self.form_id}",
            columns,
            data_dir=self.data_dir,
            indexes=["id"],
        )

    def _delete_responses_table(self):
        """Delete the responses table file"""
        tsv_file = self.data_dir / f"responses_{self.form_id}.tsv"
        if tsv_file.exists():
            tsv_file.unlink()

    def submit_response(self, response_data: Dict[str, Any]) -> str:
        """Submit a response to this form

        Args:
            response_data: Dictionary of field names to values

        Returns:
            Response ID
        """
        # Generate response ID
        response_id = f"resp_{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}"

        # Prepare record
        record = {
            "id": response_id,
            "submitted_at": datetime.utcnow().isoformat(),
        }

        # Add field values
        for field in self.fields:
            field_name = field["name"]
            value = response_data.get(field_name, "")

            # Convert lists to JSON for multi-select fields
            if isinstance(value, list):
                value = json.dumps(value)

            record[field_name] = str(value)

        # Add metadata (IP, user agent, etc.)
        metadata = response_data.get("_metadata", {})
        record["metadata"] = json.dumps(metadata)

        # Insert response
        self.responses.insert(record)

        return response_id

    def get_responses(
        self, limit: Optional[int] = None, offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Get form responses

        Args:
            limit: Maximum number of responses to return
            offset: Number of responses to skip

        Returns:
            List of response dictionaries
        """
        responses = list(self.responses.all())

        # Sort by submitted_at descending
        responses.sort(key=lambda x: x["submitted_at"], reverse=True)

        # Apply pagination
        if offset:
            responses = responses[offset:]
        if limit:
            responses = responses[:limit]

        # Parse JSON fields
        for response in responses:
            if "metadata" in response:
                try:
                    response["metadata"] = json.loads(response["metadata"])
                except (json.JSONDecodeError, TypeError):
                    response["metadata"] = {}

        return responses

    def count_responses(self) -> int:
        """Count total responses

        Returns:
            Number of responses
        """
        return self.responses.count()

    def get_response(self, response_id: str) -> Optional[Dict[str, Any]]:
        """Get a single response by ID

        Args:
            response_id: Response identifier

        Returns:
            Response dictionary or None
        """
        response = self.responses.query_one(id=response_id)
        if response and "metadata" in response:
            try:
                response["metadata"] = json.loads(response["metadata"])
            except (json.JSONDecodeError, TypeError):
                response["metadata"] = {}
        return response

    def delete_response(self, response_id: str) -> bool:
        """Delete a response

        Args:
            response_id: Response identifier

        Returns:
            True if deleted, False if not found
        """
        deleted = self.responses.delete(id=response_id)
        return deleted > 0

    def update_form(
        self,
        name: Optional[str] = None,
        description: Optional[str] = None,
        fields: Optional[List[Dict[str, Any]]] = None,
        settings: Optional[Dict[str, Any]]] = None,
    ) -> bool:
        """Update form configuration

        Args:
            name: New form name
            description: New description
            fields: New fields definition
            settings: New settings

        Returns:
            True if updated
        """
        forms_table = TSV("forms", data_dir=self.data_dir, indexes=["id"])

        updates = {"updated_at": datetime.utcnow().isoformat()}

        if name is not None:
            updates["name"] = name
            self.form_data["name"] = name

        if description is not None:
            updates["description"] = description
            self.form_data["description"] = description

        if fields is not None:
            updates["fields"] = json.dumps(fields)
            self.form_data["fields"] = json.dumps(fields)
            self.fields = fields

        if settings is not None:
            updates["settings"] = json.dumps(settings)
            self.form_data["settings"] = json.dumps(settings)
            self.settings = settings

        updated = forms_table.update({"id": self.form_id}, updates)
        return updated > 0

    def export_responses_csv(self) -> str:
        """Export responses as CSV

        Returns:
            CSV string
        """
        import csv
        from io import StringIO

        output = StringIO()

        # Get all responses
        responses = self.get_responses()
        if not responses:
            return ""

        # Write CSV
        field_names = ["id", "submitted_at"] + [field["name"] for field in self.fields]
        writer = csv.DictWriter(output, fieldnames=field_names)

        writer.writeheader()
        for response in responses:
            # Filter to only include relevant fields
            row = {k: response.get(k, "") for k in field_names}
            writer.writerow(row)

        return output.getvalue()

    def to_dict(self) -> Dict[str, Any]:
        """Convert form to dictionary

        Returns:
            Form data dictionary
        """
        return {
            "id": self.form_id,
            "name": self.form_data["name"],
            "description": self.form_data["description"],
            "fields": self.fields,
            "settings": self.settings,
            "created_at": self.form_data["created_at"],
            "updated_at": self.form_data["updated_at"],
            "response_count": self.count_responses(),
        }
