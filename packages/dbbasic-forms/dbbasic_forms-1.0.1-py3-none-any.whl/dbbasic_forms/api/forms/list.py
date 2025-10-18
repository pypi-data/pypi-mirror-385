"""
List all forms (admin interface)
GET /admin/forms
"""

from pathlib import Path
from dbbasic_forms import FormBuilder


def handle(request):
    """List all forms with stats"""
    builder = FormBuilder()
    forms = builder.list_forms()

    # Render template
    template_path = Path(__file__).parent.parent.parent / "templates" / "forms" / "list.html"
    with open(template_path) as f:
        html = f.read()

    # Simple template rendering (replace with proper template engine in production)
    # For now, return static HTML with data injected via JavaScript
    return {
        "status": 200,
        "headers": {"Content-Type": "text/html"},
        "body": html,
    }
