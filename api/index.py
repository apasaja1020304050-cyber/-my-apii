from http.server import BaseHTTPRequestHandler
import json
import os
from datetime import datetime
from supabase import create_client

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

supabase = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)

def check_license(key):

    result = (
        supabase.table("licenses")
        .select("*")
        .eq("license_key", key)
        .execute()
    )

    if not result.data:
        return False

    row = result.data[0]

    # status harus active
    if row["status"] != "active":
        return False

    # cek expired
    expires_at = row.get("expires_at")

    if expires_at:
        expire_date = datetime.fromisoformat(
            expires_at.replace("Z", "+00:00")
        )

        if expire_date < datetime.now(expire_date.tzinfo):
            return False

    return True


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
                "valid": check_license(key)
            })

        elif self.path == "/api/check_trial":

            key = data.get("trial_key")

            self.send_json({
                "valid": check_license(key),
                "duration": "Database"
            })

        else:

            self.send_json({
                "message": "Endpoint tidak ditemukan"
            })

    def send_json(self, data):

        self.send_response(200)
        self.send_header(
            "Content-type",
            "application/json"
        )
        self.end_headers()

        self.wfile.write(
            json.dumps(data).encode()
    )
