
import argparse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

def make_sample(out):
    c = canvas.Canvas(out, pagesize=letter)
    c.setFont("Helvetica", 14)
    c.drawString(72, 720, "Sample Document - Secure QR Demo")
    c.setFont("Helvetica", 10)
    c.drawString(72, 700, "This document will be stamped with a tamper-proof QR code.")
    c.showPage()
    c.save()

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True)
    a = ap.parse_args()
    make_sample(a.out)
    print('Sample PDF created:', a.out)
