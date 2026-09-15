"""Bounded Wyoming client. No model, Docker daemon or HA credentials required."""
import io
import ipaddress
import json
import socket
import time
import wave

PHRASE = "Hello from OmniVoice. Your local voice server is ready to help."
MAX_FRAME = 65536
MAX_AUDIO = 8 * 1024 * 1024


class CheckError(Exception):
    def __init__(self, code):
        super().__init__(code)
        self.code = code


def validate_target(host, port):
    if not isinstance(host, str) or not host or len(host) > 253:
        raise CheckError("address")
    if any(c not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.-:" for c in host):
        raise CheckError("address")
    if type(port) is not int or not 1 <= port <= 65535:
        raise CheckError("port")
    return host, port


def resolve_target(host, port):
    validate_target(host, port)
    try:
        addresses = socket.getaddrinfo(host, port, type=socket.SOCK_STREAM)
    except OSError:
        raise CheckError("dns") from None
    safe = []
    for family, kind, proto, _, address in addresses:
        ip = ipaddress.ip_address(address[0])
        if isinstance(ip, ipaddress.IPv6Address) and ip.ipv4_mapped:
            ip = ip.ipv4_mapped
        lan = (ip in ipaddress.ip_network("10.0.0.0/8") or
               ip in ipaddress.ip_network("172.16.0.0/12") or
               ip in ipaddress.ip_network("192.168.0.0/16") or
               ip in ipaddress.ip_network("fc00::/7"))
        if not lan or ip in ipaddress.ip_network("172.30.32.0/23"):
            raise CheckError("lan_only")
        safe.append((family, kind, proto, address))
    if not safe:
        raise CheckError("dns")
    return safe


class Wire:
    def __init__(self, sock, seconds):
        self.sock = sock
        self.deadline = time.monotonic() + seconds

    def exact(self, count):
        data = bytearray()
        while len(data) < count:
            remaining = self.deadline - time.monotonic()
            if remaining <= 0:
                raise CheckError("timeout")
            self.sock.settimeout(remaining)
            piece = self.sock.recv(min(count - len(data), 65536))
            if not piece:
                raise CheckError("closed")
            data.extend(piece)
        return bytes(data)

    def event(self):
        line = bytearray()
        while len(line) <= MAX_FRAME:
            piece = self.exact(1)
            if piece == b"\n":
                break
            line.extend(piece)
        else:
            raise CheckError("protocol")
        try:
            head = json.loads(line)
            if not isinstance(head, dict) or not isinstance(head.get("type"), str):
                raise ValueError()
            dn, pn = head.get("data_length", 0), head.get("payload_length", 0)
            if any(type(n) is not int or n < 0 for n in (dn, pn)) or dn > MAX_FRAME or pn > 1024 * 1024:
                raise ValueError()
            data = head.get("data", {})
            if not isinstance(data, dict):
                raise ValueError()
            if dn:
                extra = json.loads(self.exact(dn))
                if not isinstance(extra, dict):
                    raise ValueError()
                data.update(extra)
            return head["type"], data, self.exact(pn)
        except (ValueError, TypeError, UnicodeError):
            raise CheckError("protocol") from None

    def send(self, kind, data=None):
        self.sock.sendall((json.dumps({"type": kind, "data": data or {}}) + "\n").encode())


def check(host, port, sample=False):
    started = time.monotonic()
    candidates = resolve_target(host, port)
    sock = None
    for family, kind, proto, address in candidates[:4]:
        candidate = socket.socket(family, kind, proto)
        try:
            candidate.settimeout(3)
            candidate.connect(address)  # Use the vetted numeric address; do not resolve again.
            sock = candidate
            break
        except OSError:
            candidate.close()
    if sock is None:
        raise CheckError("connect")
    try:
        with sock:
            wire = Wire(sock, 90 if sample else 8)
            wire.send("describe")
            kind, data, _ = wire.event()
            if kind != "info":
                raise CheckError("not_wyoming")
            programs = data.get("tts")
            if not isinstance(programs, list):
                raise CheckError("no_tts")
            voices = []
            for program in programs[:16]:
                if isinstance(program, dict) and isinstance(program.get("voices"), list):
                    for voice in program["voices"][:32]:
                        if isinstance(voice, dict) and isinstance(voice.get("name"), str):
                            voices.append(voice["name"][:100])
            if not voices:
                raise CheckError("no_tts")
            result = {"reachable": True, "voice_count": len(voices), "voices": voices,
                      "speech": False, "assist": "not_verified"}
            if not sample:
                return result, None
            speech_started = time.monotonic()
            wire.send("synthesize", {"text": PHRASE})
            audio = bytearray()
            rate = None
            first = None
            for _ in range(10000):
                kind, data, payload = wire.event()
                if kind == "error":
                    raise CheckError("synthesis")
                if kind == "audio-start":
                    if rate is not None or data.get("width") != 2 or data.get("channels") != 1:
                        raise CheckError("audio_format")
                    rate = data.get("rate")
                    if type(rate) is not int or not 8000 <= rate <= 96000:
                        raise CheckError("audio_format")
                elif kind == "audio-chunk":
                    if rate is None or len(payload) % 2 or len(audio) + len(payload) > MAX_AUDIO:
                        raise CheckError("audio_format")
                    if payload and first is None:
                        first = time.monotonic() - speech_started
                    audio.extend(payload)
                elif kind == "audio-stop":
                    if not rate or not audio or not any(audio):
                        raise CheckError("no_audio")
                    out = io.BytesIO()
                    with wave.open(out, "wb") as wav:
                        wav.setnchannels(1)
                        wav.setsampwidth(2)
                        wav.setframerate(rate)
                        wav.writeframes(audio)
                    result.update(speech=True, first_audio_seconds=round(first, 3),
                                  audio_seconds=round(len(audio) / 2 / rate, 3),
                                  total_seconds=round(time.monotonic() - started, 3))
                    return result, out.getvalue()
                else:
                    raise CheckError("protocol")
            raise CheckError("protocol")
    except (socket.timeout, TimeoutError):
        raise CheckError("timeout") from None
    except OSError:
        raise CheckError("closed") from None
