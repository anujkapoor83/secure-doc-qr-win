
# import argparse
# from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
# from cryptography.hazmat.primitives import serialization
# import json, base64, os

# def gen(out_sk, out_pk, kid, passphrase=None):
#     sk = Ed25519PrivateKey.generate()
#     enc = serialization.BestAvailableEncryption(passphrase.encode('utf-8')) if passphrase else serialization.NoEncryption()
#     sk_pem = sk.private_bytes(encoding=serialization.Encoding.PEM, format=serialization.PrivateFormat.PKCS8, encryption_algorithm=enc)
#     with open(out_sk, 'wb') as f:
#         f.write(sk_pem)
#     pk = sk.public_key()
#     pk_pem = pk.public_bytes(encoding=serialization.Encoding.PEM, format=serialization.PublicFormat.SubjectPublicKeyInfo)
#     with open(out_pk, 'wb') as f:
#         f.write(pk_pem)
#     raw = pk.public_bytes(encoding=serialization.Encoding.Raw, format=serialization.PublicFormat.Raw)
#     jwk = {"kty":"OKP","crv":"Ed25519","kid":kid,"x":base64.urlsafe_b64encode(raw).decode('ascii').rstrip('=')}
#     return jwk

# if __name__ == '__main__':
#     ap = argparse.ArgumentParser()
#     ap.add_argument('--out', dest='out_sk', required=True)
#     ap.add_argument('--pub', dest='out_pk', required=True)
#     ap.add_argument('--kid', required=True)
#     ap.add_argument('--passphrase', default=None)
#     a = ap.parse_args()
#     jwk = gen(a.out_sk, a.out_pk, a.kid, a.passphrase)
#     print('Private key saved to', a.out_sk)
#     print('Public key saved to', a.out_pk)
#     jwks_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'policy', 'jwks.json')
#     try:
#         with open(jwks_path, 'r') as f:
#             jwks = json.load(f)
#     except Exception:
#         jwks = {"keys": []}
#     jwks['keys'] = [k for k in jwks.get('keys', []) if k.get('kid') != a.kid]
#     jwks['keys'].append(jwk)
#     with open(jwks_path, 'w') as f:
#         json.dump(jwks, f, indent=2)
#     print('JWKS updated at', jwks_path)

# src/scripts/genkey.py
import argparse
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization
import json, base64, os
from pathlib import Path

def gen(out_sk, out_pk, kid, passphrase=None):
    sk = Ed25519PrivateKey.generate()
    enc = serialization.BestAvailableEncryption(passphrase.encode('utf-8')) if passphrase else serialization.NoEncryption()
    sk_pem = sk.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=enc
    )
    # Ensure parent folders exist for key outputs
    Path(out_sk).parent.mkdir(parents=True, exist_ok=True)
    Path(out_pk).parent.mkdir(parents=True, exist_ok=True)

    with open(out_sk, 'wb') as f:
        f.write(sk_pem)

    pk = sk.public_key()
    pk_pem = pk.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    with open(out_pk, 'wb') as f:
        f.write(pk_pem)

    raw = pk.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw
    )
    jwk = {
        "kty": "OKP",
        "crv": "Ed25519",
        "kid": kid,
        "x": base64.urlsafe_b64encode(raw).decode('ascii').rstrip('=')
    }
    return jwk

if __name__ == '__main__':
    ap = argparse.ArgumentParser(description='Generate Ed25519 keypair and JWKS entry')
    ap.add_argument('--out', dest='out_sk', required=True)
    ap.add_argument('--pub', dest='out_pk', required=True)
    ap.add_argument('--kid', required=True)
    ap.add_argument('--passphrase', default=None)
    args = ap.parse_args()

    jwk = gen(args.out_sk, args.out_pk, args.kid, args.passphrase)
    print('Private key saved to', args.out_sk)
    print('Public key saved to', args.out_pk)

    # Resolve repo root (two levels up from this script file: .../<repo>/src/scripts/genkey.py)
    repo_root = Path(__file__).resolve().parents[2]  # -> <repo>
    jwks_path = repo_root / 'policy' / 'jwks.json'
    jwks_path.parent.mkdir(parents=True, exist_ok=True)  # ensure <repo>/policy exists
    print(jwks_path)
    # Create JWKS file if missing; then write/replace this kid
    if not jwks_path.exists():
        with open(jwks_path, 'w') as f:
            json.dump({"keys": []}, f)
    
    with open(jwks_path, 'r') as f:
        jwks = json.load(f)
    jwks['keys'] = [k for k in jwks.get('keys', []) if k.get('kid') != args.kid]
    jwks['keys'].append(jwk)
    with open(jwks_path, 'w') as f:
        json.dump(jwks, f, indent=2)
    print('JWKS updated at', jwks_path)

