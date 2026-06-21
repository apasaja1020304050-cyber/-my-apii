from http.server import BaseHTTPRequestHandler
import json
import os
from supabase import create_client

VALID_KEYS = [
    "UCGGFREE111"
]

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

supabase = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)

class handler(BaseHTTPRequestHandler):

    def do_GET(self):
        if self.path == "/":
            self.send_json({
                "message": "Server Online"
            })

        else:
            self.send_json({
                "message": "Endpoint tidak ditemukan"
            })


    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)

        try:
            data = json.loads(body)
        except:
            data = {}

        if self.path == "/api/check":
            key = data.get("key")

            self.send_json({
                "valid": key in VALID_KEYS
            })


        elif self.path == "/api/check_trial":
            key = data.get("trial_key")

            self.send_json({
                "valid": key in VALID_KEYS,
                "duration": "Unlimited"
            })


        else:
            self.send_json({
                "message": "Endpoint tidak ditemukan"
            })


    def send_json(self, data):
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()

        self.wfile.write(
            json.dumps(data).encode()
                    )
