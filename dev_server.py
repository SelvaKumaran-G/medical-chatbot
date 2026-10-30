"""
MediGuide AI — Local Development Server
Serves static frontend and /api/* endpoints on http://localhost:3000
"""

import os
import sys
import json
import urllib.parse
from http.server import HTTPServer
from api.index import handler as ApiHandler

class DevHandler(ApiHandler):
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        if path.startswith("/api"):
            super().do_GET()
        else:
            filepath = "index.html" if path in ("", "/") else path.lstrip("/")
            self._send_file(filepath)

if __name__ == "__main__":
    PORT = 3000
    server_address = ("", PORT)
    httpd = HTTPServer(server_address, DevHandler)
    print(f"MediGuide AI local dev server running on http://localhost:{PORT}")
    httpd.serve_forever()
