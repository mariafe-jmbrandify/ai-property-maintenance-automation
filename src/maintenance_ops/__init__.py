"""Reference implementation of the business rules behind the
AI-Powered Property Maintenance Operations automation.

The n8n workflows orchestrate the systems (email, Housecall Pro,
Google Sheets, SMS). This package holds the deterministic logic those
scenarios depend on, so it can be unit-tested and reused in a Code module,
a webhook, or an n8n Function node.
"""

__version__ = "1.2.0"
