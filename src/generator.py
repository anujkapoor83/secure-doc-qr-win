
# src/generator.py
import argparse, json, datetime
from pathlib import Path

from utils import sha256_hex, canonical_payload, b64url, now_utc_iso
from cryptography.hazmat.primitives import serialization
import qrcode
from pdf_stamp import stamp_qr_on_pdf, write_payload_metadata

def load_private_key(pem_path: Path, password: str | None = None):
    with pem_path.open('rb') as f:
        return serialization.load_pem_private_key(
            f.read(),
            password=password.encode('utf-8') if password else None
        )

def sign_document(doc_path: Path, issuer: str, kid: str, sk_pem: Path,
                  expires_days: int = 365*3, password: str | None = None,
                  outdir: Path | None = None):
    doc_path = doc_path.resolve()
    outdir = (outdir or doc_path.parent).resolve()

    # Build output paths safely using pathlib
    payload_path = outdir / f"{doc_path.stem}.payload.json"
    qr_png      = outdir / f"{doc_path.name}.secure_qr.png"   # e.g., hello.pdf.secure_qr.png

    # Create payload
    doc_hash = sha256_hex(str(doc_path))
    payload = {
        "v": 1,
        "doc_hash": f"SHA256:{doc_hash}",
        "doc_type": doc_path.suffix.lstrip('.').lower(),
        "issuer": issuer,
        "kid": kid,
        "created": now_utc_iso(),
        "exp": (datetime.datetime.utcnow() + datetime.timedelta(days=expires_days)).replace(microsecond=0).strftime('%Y-%m-%dT%H:%M:%SZ')
    }

    sk = load_private_key(sk_pem, password)
    msg = canonical_payload(payload)
    payload["sig"] = b64url(sk.sign(msg))

    # Write payload JSON
    payload_path.parent.mkdir(parents=True, exist_ok=True)
    with payload_path.open('w', encoding='utf-8') as f:
        json.dump(payload, f, indent=2)

    # Generate QR image
    qr_text = json.dumps(payload, separators=(',', ':'))
    img = qrcode.make(qr_text)
    img.save(str(qr_png))

    return payload_path, qr_png

if __name__ == '__main__':
    ap = argparse.ArgumentParser(description='Generate signed QR for a document and optionally stamp into PDF.')
    ap.add_argument('--doc', required=True, help='Path to document (PDF recommended)')
    ap.add_argument('--issuer', required=True)
    ap.add_argument('--kid', required=True)
    ap.add_argument('--sk', required=True, help='Path to Ed25519 private key PEM')
    ap.add_argument('--passphrase', default=None, help='Private key passphrase')
    ap.add_argument('--stamp', action='store_true', help='Stamp the QR into the PDF and embed payload metadata')
    ap.add_argument('--outdir', default=None, help='Optional output directory for payload/QR (defaults to document folder)')
    args = ap.parse_args()

    doc_path = Path(args.doc)
    sk_pem   = Path(args.sk)
    outdir   = Path(args.outdir) if args.outdir else None

    payload_json, qr_png = sign_document(doc_path, args.issuer, args.kid, sk_pem, password=args.passphrase, outdir=outdir)
    print('Payload saved:', payload_json)
    print('QR saved:', qr_png)

    if args.stamp and doc_path.suffix.lower() == '.pdf':
        stamped = (outdir or doc_path.parent) / f"{doc_path.stem}.stamped.pdf"
        stamp_qr_on_pdf(str(doc_path), str(qr_png), str(stamped))
        write_payload_metadata(str(stamped), str(payload_json))
