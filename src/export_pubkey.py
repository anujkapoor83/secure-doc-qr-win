
import argparse
from cryptography.hazmat.primitives import serialization

def export_public_key(private_pem, passphrase, public_pem):
    with open(private_pem, 'rb') as f:
        sk = serialization.load_pem_private_key(f.read(), password=passphrase.encode('utf-8') if passphrase else None)
    pk = sk.public_key()
    pem = pk.public_bytes(encoding=serialization.Encoding.PEM, format=serialization.PublicFormat.SubjectPublicKeyInfo)
    with open(public_pem, 'wb') as f:
        f.write(pem)

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--sk', required=True)
    ap.add_argument('--passphrase', default=None)
    ap.add_argument('--pk', required=True)
    a = ap.parse_args()
    export_public_key(a.sk, a.passphrase, a.pk)
    print('Public key exported to', a.pk)
