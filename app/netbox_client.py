import os
import requests


class NetBox:
    def __init__(self):
        self.url = os.getenv("NETBOX_URL", "http://localhost:8000").rstrip("/")
        token = os.getenv("NETBOX_TOKEN", "").removeprefix("Bearer ").strip()
        self.s = requests.Session()
        self.s.headers.update({
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        })

    def _req(self, method, path, **kw):
        r = self.s.request(method, f"{self.url}/api/{path.lstrip('/')}", timeout=30, **kw)
        if not r.ok:
            raise RuntimeError(f"{method} {path} -> {r.status_code}: {r.text[:300]}")
        return r.json() if r.text else None

    def get_all(self, path, params=None):
        out, offset = [], 0
        while True:
            data = self._req("GET", path, params={"limit": 200, "offset": offset, **(params or {})})
            out += data["results"]
            if not data["next"]:
                return out
            offset += 200
            