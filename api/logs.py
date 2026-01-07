from http.server import BaseHTTPRequestHandler
import json
import os
import urllib.request

LAMBDA_URL = os.environ.get(
    "LAMBDA_URL",
    "https://auwb72k75qnn3ncgrchc6qpyv40kvdaa.lambda-url.sa-east-1.on.aws/",
)


class handler(BaseHTTPRequestHandler):
    """Vercel serverless function that proxies the Lambda and adds CORS."""
    
    def do_GET(self):
        try:
            req = urllib.request.Request(LAMBDA_URL, headers={"Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                body = resp.read()
                status = 200
        except Exception as exc:
            status = 500
            body = json.dumps({"error": str(exc)}).encode('utf-8')

        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(body)
        return

