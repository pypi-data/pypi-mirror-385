"""
View form responses (admin interface)
GET /admin/forms/{form_id}/responses - Show responses page
"""

import json
from pathlib import Path
from dbbasic_forms import FormBuilder


def handle(request):
    """Show form responses interface"""
    # Extract form_id from path
    # Path format: /admin/forms/{form_id}/responses
    path_parts = request.path.strip("/").split("/")
    if len(path_parts) < 3:
        return {
            "status": 400,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": "Invalid path"}),
        }

    form_id = path_parts[2]  # forms/{form_id}/responses

    # Load form
    builder = FormBuilder()
    form = builder.get_form(form_id)

    if not form:
        return {
            "status": 404,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": "Form not found"}),
        }

    # Load responses template
    template_path = Path(__file__).parent.parent.parent / "templates" / "forms" / "responses.html"
    with open(template_path) as f:
        html = f.read()

    return {
        "status": 200,
        "headers": {"Content-Type": "text/html"},
        "body": html,
    }
