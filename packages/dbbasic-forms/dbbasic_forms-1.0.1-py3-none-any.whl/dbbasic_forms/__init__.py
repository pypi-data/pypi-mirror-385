"""
dbbasic-forms: A simple, git-friendly form builder using TSV storage

Build forms, collect responses, all stored in human-readable TSV files.
"""

from .forms import FormBuilder, Form

__version__ = "1.0.1"
__all__ = ["FormBuilder", "Form"]
