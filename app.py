"""
MediGuide AI — Multi-Platform Entrypoint
Supports local Streamlit UI, local HTTP development server, and WSGI runners.
"""

import os
import sys

# WSGI & Serverless Callable (proxies to api.index)
try:
    from api.index import app, handler
except Exception:
    def app(environ, start_response):
        start_response("200 OK", [("Content-Type", "text/plain")])
        return [b"MediGuide AI"]
    handler = app

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

if __name__ == "__main__":
    from dev_server import DevHandler, HTTPServer
    port = int(os.environ.get("PORT", 3000))
    server_address = ("", port)
    httpd = HTTPServer(server_address, DevHandler)
    print(f"MediGuide AI server running on http://localhost:{port}")
    httpd.serve_forever()
