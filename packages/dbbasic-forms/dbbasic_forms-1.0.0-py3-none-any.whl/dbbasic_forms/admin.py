"""
Admin interface configuration for dbbasic-forms

This module is auto-discovered by dbbasic-admin.
Customize the configuration below to change the menu appearance.
"""

ADMIN_CONFIG = [
    {
        'icon': '📋',  # Change to any emoji you like
        'label': 'Forms',  # Plural noun (e.g., "Contacts", "Tasks")
        'href': '/admin/forms',  # Replace "forms" with your module name
        'order': 20,  # Menu position (10 = top, 100 = bottom)
    }
]
