import os

import requests
from PIL import Image
from io import BytesIO

from fpdf import FPDF
from treepoem import generate_barcode

TEMP_DIR = "tmp"
FONTS_DIR = "fonts"


def barcode(code):
    filename = os.path.join(TEMP_DIR, "barcode.png")
    i = generate_barcode(
        barcode_type="code128",
        data=code
    )
    i = i.resize((i.width * 10, i.height * 10))
    i.save(filename)
    return filename


def barcode_pdf(code):
    barcode_filename = barcode(code)
    pdf = FPDF(orientation='P', unit='mm', format=(54, 17))
    pdf.add_page()
    pdf.add_font("Roboto Condensed", fname=os.path.join(FONTS_DIR, "RobotoCondensed-Regular.ttf"), uni=True)
    pdf.set_font('Roboto Condensed', size=6)
    pdf.text(3, 3, 'Eigentum der Technik-AG, Katharineum zu Lübeck')
    pdf.image(barcode_filename, 3, 3.5, 48, 14)
    pdf.set_fill_color(255, 255, 255)
    pdf.rect(0, 13, 54, 4, style="F")
    pdf.text(3, 15, "ID: {}".format(code))
    filename = os.path.join(TEMP_DIR, "{}.pdf".format(code))
    pdf.output(filename, 'F')
    return filename
