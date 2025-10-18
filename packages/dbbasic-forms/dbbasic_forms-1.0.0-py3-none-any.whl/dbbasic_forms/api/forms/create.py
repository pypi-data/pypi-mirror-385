"""
Create new form (admin interface)
GET /admin/forms/create - Show form builder
POST /admin/forms/create - Save new form
"""

import json
from pathlib import Path
from dbbasic_forms import FormBuilder


def GET(request):
    """Show form builder interface"""
    template_path = Path(__file__).parent.parent.parent / "templates" / "forms" / "editor.html"
    with open(template_path) as f:
        html = f.read()

    return {
        "status": 200,
        "headers": {"Content-Type": "text/html"},
        "body": html,
    }


def POST(request):
    """Create new form"""
    builder = FormBuilder()

    # Parse request body
    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, AttributeError):
        return {
            "status": 400,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": "Invalid JSON"}),
        }

    # Validate required fields
    if not data.get("id") or not data.get("name"):
        return {
            "status": 400,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": "Missing required fields: id, name"}),
        }

    # Create form
    try:
        form = builder.create_form(
            form_id=data["id"],
            name=data["name"],
            description=data.get("description", ""),
            fields=data.get("fields", []),
            settings=data.get("settings", {}),
        )

        return {
            "status": 201,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(
                {"success": True, "form_id": form.form_id, "redirect": f"/admin/forms/{form.form_id}/edit"}
            ),
        }
    except Exception as e:
        return {
            "status": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": str(e)}),
        }
