"""
Delete form (admin interface)
POST /admin/forms/{form_id}/delete - Delete form and all responses
"""

import json
from dbbasic_forms import FormBuilder


def handle(request):
    """Delete a form and all its responses"""
    # Extract form_id from path
    # Path format: /admin/forms/{form_id}/delete
    path_parts = request.path.strip("/").split("/")
    if len(path_parts) < 3:
        return {
            "status": 400,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": "Invalid path"}),
        }

    form_id = path_parts[2]  # forms/{form_id}/delete

    # Delete form
    builder = FormBuilder()
    deleted = builder.delete_form(form_id)

    if deleted:
        return {
            "status": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"success": True, "message": f"Form '{form_id}' deleted"}),
        }
    else:
        return {
            "status": 404,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": "Form not found"}),
        }
