"""
MediGuide AI — Multi-Platform Entrypoint
Supports Vercel Serverless Functions, WSGI/ASGI servers, and local/Cloud Streamlit.
"""

import os
import sys

# ---------------------------------------------------------------------------
# 1. Vercel & WSGI Deployment Entrypoints
# Export 'app' and 'handler' callable for Vercel Serverless Runtime
# ---------------------------------------------------------------------------
try:
    from api.index import app, handler
except Exception:
    def app(environ, start_response):
        start_response("200 OK", [("Content-Type", "application/json")])
        return [b'{"status": "ok", "app": "MediGuide AI"}']
    handler = app

# ---------------------------------------------------------------------------
# 2. Streamlit Runtime Execution
# Only runs Streamlit UI when invoked via 'streamlit run app.py'
# ---------------------------------------------------------------------------
def _is_streamlit_running():
    try:
        from streamlit.runtime.scriptrunner_utils.script_run_context import get_script_run_ctx
        return get_script_run_ctx() is not None
    except Exception:
        return False

if _is_streamlit_running():
    import runpy
    _target = os.path.join(os.path.dirname(os.path.abspath(__file__)), "streamlit_app.py")
    if os.path.exists(_target):
        runpy.run_path(_target, run_name="__main__")
