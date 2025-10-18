# dbbasic-forms: Git-Native Form Builder

[![PyPI version](https://badge.fury.io/py/dbbasic-forms.svg)](https://badge.fury.io/py/dbbasic-forms)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A simple, git-friendly form builder that stores everything in TSV files. Build forms, collect responses, export to CSV—all without a database.

## Why This Exists

Form builders shouldn't cost $29/month. Your data shouldn't be locked in a SaaS platform. Forms are just tables, and tables are just TSV files.

## Features

- **Visual Form Builder**: Drag-drop interface for creating forms
- **TSV Storage**: All data in human-readable text files
- **Git-Friendly**: Version control your forms and responses
- **Admin Interface**: Auto-discovered by dbbasic-admin
- **CSV Export**: One-click export to spreadsheet
- **Zero Setup**: No database, no configuration, just works

## Installation

```bash
pip install dbbasic-forms
```

Requires Python 3.8+ and `dbbasic-tsv`.

## Quick Start

### Create a Form

```python
from dbbasic_forms import FormBuilder

builder = FormBuilder()

contact_form = builder.create_form(
    form_id="contact",
    name="Contact Form",
    description="Get in touch with us",
    fields=[
        {
            "name": "name",
            "type": "text",
            "label": "Name",
            "required": True
        },
        {
            "name": "email",
            "type": "email",
            "label": "Email",
            "required": True
        },
        {
            "name": "message",
            "type": "textarea",
            "label": "Message"
        }
    ]
)
```

### Submit Responses

```python
# From your web handler
form = builder.get_form("contact")
response_id = form.submit_response({
    "name": "Alice Johnson",
    "email": "alice@example.com",
    "message": "Love your product!"
})
```

### View Responses

```python
# Get all responses
responses = form.get_responses(limit=10)

for response in responses:
    print(f"{response['submitted_at']}: {response['email']}")

# Export to CSV
csv_data = form.export_responses_csv()
with open("responses.csv", "w") as f:
    f.write(csv_data)
```

## Data Format

Your forms and responses are stored in TSV files:

```bash
$ cat data/forms.tsv
id      name            description             fields                  created_at
contact Contact Form    Get in touch with us    [{"name":"email"...}]  2024-01-15T10:30:00

$ cat data/responses_contact.tsv
id                  submitted_at            name            email               message
resp_20240115...    2024-01-15T14:22:00    Alice Johnson   alice@example.com   Love your product!
```

This means you can:
- Debug with `tail -f data/responses_contact.tsv`
- Search with `grep alice data/responses_contact.tsv`
- Edit in Excel, Google Sheets, or vim
- Track changes in Git with meaningful diffs

## Field Types

- `text` - Single-line text input
- `email` - Email with validation
- `textarea` - Multi-line text
- `number` - Numeric input
- `date` - Date picker
- `select` - Dropdown menu
- `radio` - Radio buttons (single choice)
- `checkbox` - Checkboxes (multiple choice)
- `file` - File upload (coming soon)

## Admin Interface

dbbasic-forms integrates with [dbbasic-admin](https://github.com/askrobots/dbbasic-admin) for visual management.

The admin interface includes:
- Form builder with drag-drop fields
- Response viewer with filtering
- CSV export
- Form analytics

Install dbbasic-admin:

```bash
pip install dbbasic-admin
```

The forms interface is auto-discovered at `/admin/forms`.

## Web Framework Integration

### Flask Example

```python
from flask import Flask, request, jsonify
from dbbasic_forms import FormBuilder

app = Flask(__name__)
builder = FormBuilder()

@app.route('/api/forms/<form_id>/submit', methods=['POST'])
def submit_form(form_id):
    form = builder.get_form(form_id)
    if not form:
        return jsonify({"error": "Form not found"}), 404

    response_id = form.submit_response(request.json)
    return jsonify({
        "success": True,
        "response_id": response_id,
        "message": form.settings["success_message"]
    })
```

### FastAPI Example

```python
from fastapi import FastAPI, HTTPException
from dbbasic_forms import FormBuilder

app = FastAPI()
builder = FormBuilder()

@app.post("/api/forms/{form_id}/submit")
async def submit_form(form_id: str, data: dict):
    form = builder.get_form(form_id)
    if not form:
        raise HTTPException(status_code=404, detail="Form not found")

    response_id = form.submit_response(data)
    return {
        "success": True,
        "response_id": response_id,
        "message": form.settings["success_message"]
    }
```

## API Reference

### FormBuilder

```python
builder = FormBuilder(data_dir="data")
```

**Methods:**

- `create_form(form_id, name, description, fields, settings)` → Form
- `get_form(form_id)` → Form | None
- `list_forms()` → List[Dict]
- `delete_form(form_id)` → bool

### Form

```python
form = builder.get_form("contact")
```

**Methods:**

- `submit_response(response_data)` → str (response_id)
- `get_responses(limit, offset)` → List[Dict]
- `count_responses()` → int
- `get_response(response_id)` → Dict | None
- `delete_response(response_id)` → bool
- `update_form(name, description, fields, settings)` → bool
- `export_responses_csv()` → str
- `to_dict()` → Dict

## When to Use This

✅ **Perfect for:**
- Contact forms on static sites
- Feedback forms
- Event registrations
- Surveys and polls
- Internal tools (HR forms, IT requests)
- Prototypes and MVPs

❌ **Not suitable for:**
- High-volume transactional forms (>1K submissions/day)
- Payment forms (use Stripe Checkout)
- Multi-tenant SaaS applications
- Real-time collaboration

**Rule of thumb:** If your form responses can safely live in Git (because they're content, not transactions), use dbbasic-forms.

## Deployment

### Development

```bash
pip install dbbasic-forms
# Data is stored in ./data directory
# Commit to git: git add data/ && git commit -m "Add form data"
```

### Production (Git-Based)

```bash
git clone https://github.com/yourorg/yourapp.git
cd yourapp
pip install -r requirements.txt

# Data is in the repo
# New responses append to TSV files
# Push updates: git add data/ && git commit && git push
```

## Performance

- **Form Creation:** <1ms
- **Response Submission:** <5ms
- **Query 10K Responses:** ~100ms
- **CSV Export (10K rows):** ~200ms

**Limits:**
- Responses per form: 100K recommended, 1M maximum
- Fields per form: 50 recommended

## Comparison

| Feature | dbbasic-forms | Google Forms | Typeform |
|---------|---------------|--------------|----------|
| Cost | Free | Free/Limited | $25+/mo |
| Data Ownership | ✅ | ❌ | ❌ |
| Git-Friendly | ✅ | ❌ | ❌ |
| Self-Hosted | ✅ | ❌ | ❌ |
| Visual Builder | ✅ | ✅ | ✅ |
| File Uploads | 🚧 | ✅ | ✅ |

## Documentation

- [Full Specification](SPEC.md) - Complete technical spec
- [API Reference](#api-reference) - Method documentation
- [Examples](examples/) - Code examples and demos

## Contributing

Contributions welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT License - see [LICENSE](LICENSE) for details.

## Credits

Created by the AskRobots team as part of the dbbasic ecosystem.

Inspired by the philosophy that forms shouldn't require infrastructure.

---

**Remember:** The best form builder is the one you control.
