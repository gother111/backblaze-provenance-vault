"""Vercel Services entrypoint.

Vercel removes the configured ``/api`` service prefix before dispatch, so
this app exposes prefix-free internal routes while the public API remains
``/api/*``. Cold starts never generate a demo run or write to B2.
"""

from app.main import create_app

app = create_app(seed_demo=False, api_prefix="", serve_frontend=False)
