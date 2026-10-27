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
            full_path = os.path.join(os.path.dirname(__file__), filepath)
            
            if os.path.exists(full_path) and os.path.isfile(full_path):
                content_type = "text/html; charset=utf-8"
                if filepath.endswith(".css"): content_type = "text/css; charset=utf-8"
                elif filepath.endswith(".js"): content_type = "application/javascript; charset=utf-8"
                elif filepath.endswith(".json"): content_type = "application/json; charset=utf-8"
                elif filepath.endswith(".png"): content_type = "image/png"
                elif filepath.endswith(".jpg"): content_type = "image/jpeg"
                elif filepath.endswith(".svg"): content_type = "image/svg+xml"

                with open(full_path, "rb") as f:
                    content = f.read()

                self.send_response(200)
                self.send_header("Content-Type", content_type)
                self.send_header("Content-Length", str(len(content)))
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(content)
            else:
                self.send_response(404)
                self.send_header("Content-Type", "text/plain")
                self.end_headers()
                self.wfile.write(b"404 Not Found")

if __name__ == "__main__":
    PORT = 3000
    server_address = ("", PORT)
    httpd = HTTPServer(server_address, DevHandler)
    print(f"MediGuide AI local dev server running on http://localhost:{PORT}")
    httpd.serve_forever()
