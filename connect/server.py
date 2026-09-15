"""Ingress-only onboarding UI with one bounded Wyoming operation at a time."""
import argparse
import json
import os
from pathlib import Path
import secrets
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit

from protocol import CheckError, check, validate_target

VERSION = "0.1.0"
STATIC = Path(__file__).parent / "static"
MESSAGES = {
    "address": "Enter the server's LAN IP or hostname, without http:// or a path.",
    "port": "Enter a port between 1 and 65535.",
    "dns": "The hostname could not be resolved. Try the server's LAN IP address.",
    "lan_only": "Use an external LAN server. Loopback, public and Supervisor addresses are not accepted.",
    "connect": "Could not connect. Check the address, published port, container and LAN firewall.",
    "timeout": "The server took too long. Check its logs and wait for model loading to finish, then retry.",
    "closed": "The server closed the connection. Check its logs and available GPU memory.",
    "not_wyoming": "This port did not respond as a Wyoming server. Check the published Wyoming port.",
    "no_tts": "Wyoming responded but did not advertise a TTS voice. Check that this is the OmniVoice service.",
    "protocol": "The server returned an invalid or oversized Wyoming response.",
    "audio_format": "The server returned unsupported or oversized audio. Expected mono 16-bit PCM.",
    "no_audio": "The server finished without audible audio. Check its voice settings and logs.",
    "synthesis": "The server reported a synthesis error. Check its model, voice files and GPU logs.",
    "busy": "A check is already running. Wait for it to finish.",
    "storage": "Could not save settings in /data. Check the app's storage permissions.",
}


def compose(port, platform, path):
    if type(port) is not int or not 1 <= port <= 65535:
        raise CheckError("port")
    if platform not in ("docker", "truenas"):
        raise ValueError("Choose Docker or TrueNAS")
    if platform == "truenas":
        if not isinstance(path, str) or not path.startswith("/mnt/") or any(c in path for c in "\n\r:$") or len(path) > 512:
            raise ValueError("Use an absolute TrueNAS dataset path under /mnt/ without :, $ or newlines")
        volume = json.dumps(path + ":/data")
    else:
        volume = '"omnivoice_data:/data"'
    text = f'''services:
  wyoming-omnivoice:
    image: ghcr.io/valentinealan/wyoming-omnivoice:1.1.0
    restart: unless-stopped
    init: true
    user: "568:568"
    ports:
      - "{port}:10200"
    environment:
      OMNIVOICE_DEVICE: cuda
      OMNIVOICE_VOICE: example
      OMNIVOICE_LANGUAGE: English
      OMNIVOICE_LANGUAGE_CODE: en
      OMNIVOICE_LOG_LEVEL: WARNING
    volumes:
      - {volume}
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
    cap_drop: [ALL]
    security_opt: ["no-new-privileges:true"]
'''
    if platform == "docker":
        text += "volumes:\n  omnivoice_data:\n"
    return text


class State:
    def __init__(self, data_dir):
        self.path = Path(data_dir) / "connect.json"
        self.token = secrets.token_urlsafe(32)
        self.lock = threading.Lock()
        self.job = None
        self.settings = {"host": "", "port": 10200}
        if self.path.exists():
            try:
                stored = json.loads(self.path.read_text())
                host, port = validate_target(stored["host"], stored["port"])
                self.settings = {"host": host, "port": port}
            except (ValueError, KeyError, TypeError, OSError, CheckError):
                pass

    def start(self, host, port, sample):
        validate_target(host, port)
        with self.lock:
            if self.job and self.job["status"] == "running":
                raise CheckError("busy")
            settings = {"host": host, "port": port}
            try:
                self.path.parent.mkdir(parents=True, exist_ok=True)
                temp = self.path.with_suffix(".tmp")
                temp.write_text(json.dumps(settings), encoding="utf-8")
                os.replace(temp, self.path)
            except OSError:
                raise CheckError("storage") from None
            self.settings = settings
            self.job = {"id": secrets.token_urlsafe(24), "status": "running", "created": time.monotonic()}
            identifier = self.job["id"]
        threading.Thread(target=self.run, args=(identifier, host, port, sample), daemon=True).start()
        return identifier

    def run(self, identifier, host, port, sample):
        try:
            result, audio = check(host, port, sample)
            update = {"status": "done", "result": result, "audio": audio}
        except CheckError as error:
            update = {"status": "error", "code": error.code, "message": MESSAGES[error.code]}
        except Exception:
            update = {"status": "error", "code": "internal", "message": "The check failed unexpectedly. Restart the companion and retry."}
        with self.lock:
            if self.job and self.job["id"] == identifier:
                self.job.update(update)

    def snapshot(self, identifier, audio=False):
        with self.lock:
            if not self.job or self.job["id"] != identifier or time.monotonic() - self.job["created"] > 600:
                raise KeyError()
            if audio:
                if not self.job.get("audio"):
                    raise KeyError()
                return self.job["audio"]
            return {k: v for k, v in self.job.items() if k not in ("audio", "created")}


class Handler(BaseHTTPRequestHandler):
    server_version = "OmniVoiceConnect"

    def log_message(self, *args):
        pass  # Do not log private addresses, ingress paths or request bodies.

    def setup(self):
        super().setup()
        self.connection.settimeout(10)

    def allowed(self):
        return self.client_address[0] == self.server.allowed_peer

    def reply(self, status, data, kind="application/json"):
        if kind == "application/json":
            data = json.dumps(data).encode()
        elif isinstance(data, str):
            data = data.encode()
        self.send_response(status)
        self.send_header("Content-Type", kind)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("Content-Security-Policy", "default-src 'self'; script-src 'self'; style-src 'self'; media-src 'self' blob:; connect-src 'self'; object-src 'none'; base-uri 'self'; frame-ancestors 'self'")
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if not self.allowed():
            return self.reply(403, {"error": "Access through Home Assistant Ingress only."})
        path = urlsplit(self.path).path
        if path == "/api/state":
            return self.reply(200, {"version": VERSION, "token": self.server.state.token,
                                   "settings": self.server.state.settings})
        if path.startswith("/api/job/") or path.startswith("/api/audio/"):
            identifier = path.rsplit("/", 1)[-1]
            try:
                audio = path.startswith("/api/audio/")
                data = self.server.state.snapshot(identifier, audio)
                return self.reply(200, data, "audio/wav" if audio else "application/json")
            except KeyError:
                return self.reply(404, {"error": "This test has expired. Run a new check."})
        files = {"/": ("index.html", "text/html; charset=utf-8"),
                 "/app.js": ("app.js", "text/javascript; charset=utf-8"),
                 "/style.css": ("style.css", "text/css; charset=utf-8")}
        if path in files:
            name, kind = files[path]
            return self.reply(200, (STATIC / name).read_bytes(), kind)
        self.reply(404, {"error": "Not found"})

    def do_POST(self):
        if not self.allowed() or not secrets.compare_digest(self.headers.get("X-Connect-Token", ""), self.server.state.token):
            return self.reply(403, {"error": "Reload this page from Home Assistant and try again."})
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if not 0 < length <= 4096 or self.headers.get_content_type() != "application/json":
                return self.reply(400, {"error": "Invalid request"})
            body = json.loads(self.rfile.read(length))
            if not isinstance(body, dict):
                raise ValueError("Invalid request")
            path = urlsplit(self.path).path
            if path in ("/api/check", "/api/sample"):
                identifier = self.server.state.start(body.get("host"), body.get("port"), path == "/api/sample")
                return self.reply(202, {"id": identifier})
            if path == "/api/compose":
                return self.reply(200, {"compose": compose(body.get("port"), body.get("platform"), body.get("path"))})
            return self.reply(404, {"error": "Not found"})
        except CheckError as error:
            return self.reply(409 if error.code == "busy" else 400, {"error": MESSAGES[error.code]})
        except (ValueError, TypeError):
            return self.reply(400, {"error": "Check the fields. TrueNAS requires an absolute /mnt/ dataset path without :, $ or newlines."})


def make_server(address, data_dir, dev=False):
    server = ThreadingHTTPServer(address, Handler)
    server.daemon_threads = True
    server.allowed_peer = "127.0.0.1" if dev else "172.30.32.2"
    server.state = State(data_dir)
    return server


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dev", action="store_true", help="Bind only to loopback for local development")
    parser.add_argument("--data", default="/data")
    parser.add_argument("--port", type=int, default=8099)
    args = parser.parse_args()
    # Supervisor owns a new app data directory as root. Prepare only our directory
    # and files, then drop privileges before accepting any network connection.
    if hasattr(os, "geteuid") and os.geteuid() == 0:
        data = Path(args.data)
        data.mkdir(parents=True, exist_ok=True)
        os.chown(data, 568, 568)
        for name in ("connect.json", "connect.tmp"):
            item = data / name
            if item.exists() and not item.is_symlink():
                os.chown(item, 568, 568)
        os.setgroups([])
        os.setgid(568)
        os.setuid(568)
    server = make_server(("127.0.0.1" if args.dev else "0.0.0.0", args.port), args.data, args.dev)
    print("OmniVoice Connect", VERSION, "listening", flush=True)
    server.serve_forever()
