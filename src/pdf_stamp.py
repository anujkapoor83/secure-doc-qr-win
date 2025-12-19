
import io, json
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader

def make_overlay_with_png(png_path, page_size=letter, pos=(36,36), scale=1.0):
    packet = io.BytesIO()
    c = canvas.Canvas(packet, pagesize=page_size)
    img = ImageReader(png_path)
    iw, ih = img.getSize()
    c.drawImage(img, pos[0], pos[1], width=iw*scale, height=ih*scale, mask='auto')
    c.save()
    packet.seek(0)
    return PdfReader(packet)

def stamp_qr_on_pdf(pdf_in, png_qr, pdf_out, pos=(36,36), scale=0.5):
    base = PdfReader(pdf_in)
    writer = PdfWriter()
    overlay = make_overlay_with_png(png_qr, page_size=base.pages[0].mediabox[2:4], pos=pos, scale=scale)
    for i, page in enumerate(base.pages):
        if i == 0:
            page.merge_page(overlay.pages[0])
        writer.add_page(page)
    with open(pdf_out, 'wb') as f:
        writer.write(f)

def write_payload_metadata(pdf_path, payload_json_path):
    reader = PdfReader(pdf_path)
    writer = PdfWriter()
    for p in reader.pages:
        writer.add_page(p)
    with open(payload_json_path, 'r') as f:
        payload = json.load(f)
    md = reader.metadata or {}
    md.update({"/QRPayload": json.dumps(payload, separators=(',', ':'))})
    with open(pdf_path, 'wb') as f:
        writer.add_metadata(md)
        writer.write(f)
