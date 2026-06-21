from http.server import BaseHTTPRequestHandler
import json
import os
from datetime import datetime
from supabase import create_client

# =========================
# ENV CONFIG
# =========================
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
ADMIN_SECRET = os.environ.get("ADMIN_SECRET")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# =========================
# LICENSE CHECK FUNCTION
# =========================
def check_license(key):

    if not key:
        return False

    key = key.strip()

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
    if row.get("status") != "active":
        return False

    # cek expired
    expired_at = row.get("expired_at")

    if expired_at:
        try:
            expired_date = datetime.fromisoformat(
                expired_at.replace("Z", "+00:00")
            )

            if expired_date < datetime.now(expired_date.tzinfo):
                return False

        except:
            return False

    return True


# =========================
# ADMIN AUTH CHECK
# =========================
def is_admin(headers):
    auth = headers.get("Authorization")

    if not auth:
        return False

    token = auth.replace("Bearer ", "").strip()
    return token == ADMIN_SECRET


# =========================
# HANDLER
# =========================
class handler(BaseHTTPRequestHandler):

    # =====================
    # GET REQUEST
    # =====================
    def do_GET(self):

        if self.path == "/":
            self.send_json({
                "message": "Server Online"
            })

        else:
            self.send_json({
                "message": "Endpoint tidak ditemukan"
            })

    # =====================
    # POST REQUEST
    # =====================
    def do_POST(self):

        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)

        try:
            data = json.loads(body)
        except:
            data = {}

        # =====================
        # PUBLIC: CHECK LICENSE
        # =====================
        if self.path == "/api/check":

            key = data.get("key")

            self.send_json({
                "valid": check_license(key)
            })

        # =====================
        # PUBLIC: CHECK TRIAL
        # =====================
        elif self.path == "/api/check_trial":

            key = data.get("trial_key")

            self.send_json({
                "valid": check_license(key),
                "duration": "Database"
            })

        # =====================
        # ADMIN: CREATE KEY
        # =====================
        elif self.path == "/api/admin/create_key":

            if not is_admin(self.headers):
                return self.send_json({"error": "unauthorized"})

            key = data.get("key")
            expired_at = data.get("expired_at")

            supabase.table("licenses").insert({
                "license_key": key,
                "status": "active",
                "expired_at": expired_at
            }).execute()

            self.send_json({
                "success": True,
                "message": "Key created"
            })

        # =====================
        # ADMIN: DISABLE KEY
        # =====================
        elif self.path == "/api/admin/disable_key":

            if not is_admin(self.headers):
                return self.send_json({"error": "unauthorized"})

            key = data.get("key")

            supabase.table("licenses") \
                .update({"status": "disabled"}) \
                .eq("license_key", key) \
                .execute()

            self.send_json({
                "success": True,
                "message": "Key disabled"
            })

        # =====================
        # ADMIN: ENABLE KEY
        # =====================
        elif self.path == "/api/admin/enable_key":

            if not is_admin(self.headers):
                return self.send_json({"error": "unauthorized"})

            key = data.get("key")

            supabase.table("licenses") \
                .update({"status": "active"}) \
                .eq("license_key", key) \
                .execute()

            self.send_json({
                "success": True,
                "message": "Key enabled"
            })

        # =====================
        # ADMIN: LIST ALL KEYS
        # =====================
        elif self.path == "/api/admin/list_keys":

            if not is_admin(self.headers):
                return self.send_json({"error": "unauthorized"})

            result = supabase.table("licenses").select("*").execute()

            self.send_json({
                "success": True,
                "data": result.data
            })

        else:
            self.send_json({
                "message": "Endpoint tidak ditemukan"
            })

    # =========================
    # JSON RESPONSE HELPER
    # =========================
    def send_json(self, data):

        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()

        self.wfile.write(
            json.dumps(data).encode()
    )
