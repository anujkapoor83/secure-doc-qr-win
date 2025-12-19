
import json, hashlib, base64
from datetime import datetime
ISO_FMT = '%Y-%m-%dT%H:%M:%SZ'

def sha256_hex(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(65536), b''):
            h.update(chunk)
    return h.hexdigest()

def canonical_payload(payload_dict):
    return json.dumps(payload_dict, separators=(',', ':'), sort_keys=True).encode('utf-8')

def b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode('ascii').rstrip('=')

def b64url_decode(s: str) -> bytes:
    return base64.urlsafe_b64decode(s + '==')

def now_utc_iso():
    return datetime.utcnow().replace(microsecond=0).strftime(ISO_FMT)
