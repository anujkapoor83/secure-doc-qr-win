
# src/verifier.py
import argparse
import json
from datetime import datetime
from pathlib import Path

from utils import sha256_hex, canonical_payload, b64url_decode
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from cryptography.hazmat.primitives import serialization

ISO_FMT = '%Y-%m-%dT%H:%M:%SZ'

def load_public_key(pem_path: Path):
    with pem_path.open('rb') as f:
        return serialization.load_pem_public_key(f.read())

def canonical_payload_for_verify(d: dict):
    d = dict(d)             # shallow copy
    sig = d.pop('sig', None)
    return json.dumps(d, separators=(',', ':'), sort_keys=True).encode('utf-8'), sig

def verify_signature(d: dict, pk: Ed25519PublicKey):
    msg, sig_b64 = canonical_payload_for_verify(d)
    if not sig_b64:
        return False, 'Missing signature'
    sig = b64url_decode(sig_b64)
    try:
        pk.verify(sig, msg)
        return True, 'Signature valid'
    except Exception as e:
        return False, f'Invalid signature: {e}'

def is_expired(d: dict):
    exp = d.get('exp')
    if not exp:
        return False
    return datetime.utcnow() > datetime.strptime(exp, ISO_FMT)

def check_revocation(d: dict, rev_path: Path | None):
    if not rev_path:
        return False
    try:
        with rev_path.open('r', encoding='utf-8') as f:
            rev = json.load(f)
        key = {
            'doc_hash': d.get('doc_hash'),
            'issuer': d.get('issuer'),
            'created': d.get('created')
        }
        return key in rev.get('revoked', [])
    except Exception:
        return False

def verify_offline(doc_path: Path, payload_json_path: Path, pubkey_pem: Path,
                   revocations_path: Path | None = None, expected_kid: str | None = None):
    pk = load_public_key(pubkey_pem)

    with payload_json_path.open('r', encoding='utf-8') as f:
        payload = json.load(f)

    if expected_kid and payload.get('kid') != expected_kid:
        return False, 'Unexpected kid in payload'

    ok, msg = verify_signature(payload, pk)
    if not ok:
        return False, msg

    # Hash binding
    actual = sha256_hex(str(doc_path))
    expected = payload.get('doc_hash', '')
    if expected != f'SHA256:{actual}':
        return False, 'Hash mismatch: QR does not belong to this file'

    # Expiry
    if is_expired(payload):
        return False, 'Payload expired'

    # Revocation (offline)
    if check_revocation(payload, revocations_path):
        return False, 'Document revoked'

    return True, 'Document authentic & unmodified'

if __name__ == '__main__':
    ap = argparse.ArgumentParser(description='Offline verifier for Secure Document QR')
    ap.add_argument('--doc', required=True, help='Path to original document')
    ap.add_argument('--payload', required=True, help='Path to payload JSON (from QR or stamped PDF metadata)')
    ap.add_argument('--pk', required=True, help='Public key PEM path')
    ap.add_argument('--rev', default=None, help='Path to revocations.json')
    ap.add_argument('--kid', default=None, help='Expected key id')
    args = ap.parse_args()

    # Resolve all incoming paths to absolute filesystem paths
    doc_path = Path(args.doc).resolve()
    payload_json_path = Path(args.payload).resolve()
    pubkey_pem = Path(args.pk).resolve()
    revocations_path = Path(args.rev).resolve() if args.rev else None

    ok, msg = verify_offline(doc_path, payload_json_path, pubkey_pem, revocations_path, args.kid)
