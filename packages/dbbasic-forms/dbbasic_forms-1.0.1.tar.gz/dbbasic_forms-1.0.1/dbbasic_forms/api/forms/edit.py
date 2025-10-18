"""
Edit existing form (admin interface)
GET /admin/forms/{form_id}/edit - Show form editor
POST /admin/forms/{form_id}/edit - Update form
"""

import json
from pathlib import Path
from dbbasic_forms import FormBuilder


def handle(request):
    """Handle form editing - GET shows editor, POST updates form"""

    # Extract form_id from path
    # Path format: /admin/forms/{form_id}/edit
    path_parts = request.path.strip("/").split("/")
    if len(path_parts) < 3:
        return {
            "status": 400,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": "Invalid path"}),
        }

    form_id = path_parts[2]  # forms/{form_id}/edit

    if request.method == 'POST':
        # Update form
        # Parse request body
        try:
            data = json.loads(request.body)
        except (json.JSONDecodeError, AttributeError):
            return {
                "status": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": "Invalid JSON"}),
            }

        # Load form
        builder = FormBuilder()
        form = builder.get_form(form_id)

        if not form:
            return {
                "status": 404,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": "Form not found"}),
            }

        # Update form
        try:
            form.update_form(
                name=data.get("name"),
                description=data.get("description"),
                fields=data.get("fields"),
                settings=data.get("settings"),
            )

            return {
                "status": 200,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"success": True, "form_id": form_id}),
            }
        except Exception as e:
            return {
                "status": 500,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": str(e)}),
            }

    # GET - Show form editor interface
    builder = FormBuilder()
    form = builder.get_form(form_id)

    if not form:
        return {
            "status": 404,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": "Form not found"}),
        }

    # Load editor template
    template_path = Path(__file__).parent.parent.parent / "templates" / "forms" / "editor.html"
    with open(template_path) as f:
        html = f.read()

    # In production, inject form data into template
    # For now, return static HTML (data loaded via API)
    return {
        "status": 200,
        "headers": {"Content-Type": "text/html"},
        "body": html,
    }
