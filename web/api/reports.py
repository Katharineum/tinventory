import os

from django.utils import formats
import fpdf
from treepoem import generate_barcode

from api.models import Item
from tinventory.settings import BASE_DIR

TEMP_DIR = "tmp"
FONTS_DIR = "fonts"

fpdf.FPDF_FONT_DIR = os.path.join(BASE_DIR, FONTS_DIR)
fpdf.set_global("FPDF_FONT_DIR", os.path.join(BASE_DIR, FONTS_DIR))
print(fpdf.FPDF_FONT_DIR)
FPDF_FONT_DIR = os.path.join(BASE_DIR, FONTS_DIR)


def barcode(code):
    filename = os.path.join(BASE_DIR, TEMP_DIR, "barcode.png")
    i = generate_barcode(
        barcode_type="code128",
        data=code
    )
    i = i.resize((i.width * 10, i.height * 10))
    i.save(filename)
    return filename


class Report(fpdf.FPDF):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.add_font("Roboto Condensed", fname="RobotoCondensed-Regular.ttf",
                      uni=True)
        self.add_font("Roboto Condensed Bold", fname="RobotoCondensed-Bold.ttf",
                      uni=True)
        self.add_font("Roboto Condensed Light", fname="RobotoCondensed-Light.ttf",
                      uni=True)
        self.add_font("mono", fname="RobotoMono-Regular.ttf", uni=True)
        self.add_font("line", fname="Montserrat-Regular.ttf", uni=True)
        self.add_font("code39", fname="code39.ttf", uni=True)
        self.add_font("code39-s", fname="code39_S.ttf", uni=True)

        print("RobotoMono-Regular.ttf")

    def heading(self):
        self.normal_font()
        self.image(os.path.join(BASE_DIR, "logo.png"), h=20)
        # self.cell(w=0, h=1, ln=1)

    def normal_font(self, size=14):
        self.set_font('Roboto Condensed', size=size)

    def mono_font(self, size=14):
        self.set_font("mono", size=size)

    def small_font(self):
        self.set_font('Roboto Condensed Light', size=9)

    def barcode_font(self, size=23):
        self.set_font("code39", size=size)

    def barcode_font_small(self, size=15):
        self.set_font("code39-s", size=size)

    def normal_color(self):
        self.set_text_color(0, 0, 0)

    def dark_grey_color(self):
        self.set_text_color(66, 66, 66)

    def save_in_tmp(self, filename):
        filename = os.path.join(BASE_DIR, TEMP_DIR, filename)
        self.output(filename, 'F')
        return filename


def barcode_pdf(item: Item):
    pdf = Report(orientation='P', unit='mm', format=(54, 17))
    pdf.add_page()
    pdf.set_font('Roboto Condensed', size=6)
    pdf.text(3, 3, 'Eigentum der Technik-AG, Katharineum zu Lübeck')
    pdf.barcode_font()
    pdf.text(3, 12, txt="*{}*".format(item.barcode))
    pdf.set_font('Roboto Condensed', size=6)
    pdf.set_fill_color(255, 255, 255)
    pdf.rect(0, 13, 54, 4, style="F")
    pdf.text(3, 15, "ID: {}".format(item.id))

    return pdf.save_in_tmp("barcode-{}.pdf".format(item.id))


def loan_form_pdf(process):
    pdf = Report(orientation='P', unit='mm', format="A4")

    for i in range(2):
        pdf.add_page()
        pdf.heading()

        pdf.set_font('Roboto Condensed', size=15)
        pdf.dark_grey_color()
        if i == 0:
            txt = "AUSFERTIGUNG FÜR DIE TECHNIK-AG"
            x = 120
        else:
            txt = "AUSFERTIGUNG FÜR DEN AUSLEIHENDEN"
            x = 110
        pdf.text(x=x, y=20, txt=txt)

        pdf.set_font('Roboto Condensed Bold', size=20)
        pdf.normal_color()
        pdf.cell(w=0, h=30, txt="Ausleihformular der Technik-AG", align="C", ln=1)

        pdf.mono_font()
        pdf.cell(w=55, txt=process.borrowing_person.name)

        pdf.normal_font()
        pdf.cell(w=17, txt=" hat am ")

        pdf.mono_font()
        pdf.cell(w=35, txt=formats.date_format(process.checked_out_at, "d.m.Y"))

        pdf.normal_font()
        pdf.cell(w=9, txt=" bei ", )

        pdf.mono_font()
        pdf.cell(w=55, txt=process.lending_user.get_full_name(), ln=1)

        pdf.cell(w=0, h=5, ln=1)

        pdf.small_font()
        pdf.cell(w=55, txt="Name des Ausleihenden")
        pdf.cell(w=17)
        pdf.cell(w=35, txt="Datum")
        pdf.cell(w=9)
        pdf.cell(w=55, txt="Name des Technik-AG-Mitglieds", ln=1)
        pdf.cell(w=0, h=8, ln=1)

        pdf.normal_font()
        pdf.cell(w=0, txt="folgendes ausgeliehen:", ln=1)
        pdf.cell(w=0, h=8, ln=1)

        for check in process.checks.all():

            if check.item.preset:
                txt = "- {} ({}, #{})".format(check.item.name, check.item.preset.name, check.item.id)
            else:
                txt = "- {} (#{})".format(check.item.name, check.item.id)
            pdf.mono_font()
            pdf.cell(w=0, h=8, txt=txt, ln=1)

            # pdf.barcode_font_small(size=15)
            # pdf.cell(w=10, h=8, txt="*{}*".format(check.item.barcode), ln=1)


        pdf.cell(w=0, h=20, ln=1)

        pdf.set_font("line", size=12)
        pdf.cell(w=50, txt="________________________________")
        pdf.cell(w=65)
        pdf.cell(w=50, txt="________________________________", ln=1)
        pdf.cell(w=0, h=5, ln=1)

        pdf.small_font()
        pdf.cell(w=50, txt="Unterschrift des Ausleihenden")
        pdf.cell(w=65)
        pdf.cell(w=30, txt="Unterschrift des Technik-AG-Mitglieds", ln=1)

        pdf.text(x=10, y=285,
                 txt="Ausleihvorgang {}–{} #{}".format(process.borrowing_person.name, process.checked_out_at,
                                                       process.id))

        pdf.barcode_font(30)
        pdf.text(x=150, y=287, txt="*{}*".format(process.id))

    return pdf.save_in_tmp("loan-form-{}.pdf".format(process.id))


def check_in_confirmation_pdf(process):
    pdf = Report(orientation='P', unit='mm', format="A4")

    for i in range(2):
        pdf.add_page()
        pdf.heading()

        pdf.set_font('Roboto Condensed', size=15)
        pdf.dark_grey_color()
        if i == 0:
            txt = "AUSFERTIGUNG FÜR DIE TECHNIK-AG"
            x = 120
        else:
            txt = "AUSFERTIGUNG FÜR DEN AUSLEIHENDEN"
            x = 110
        pdf.text(x=x, y=20, txt=txt)

        pdf.set_font('Roboto Condensed Bold', size=20)
        pdf.normal_color()
        pdf.cell(w=0, h=30, txt="Rückgabebestätigung", align="C", ln=1)

        pdf.mono_font()
        pdf.cell(w=55, txt=process.borrowing_person.name)

        pdf.normal_font()
        pdf.cell(w=17, txt=" hat folgendes zurückgegeben:")

        pdf.cell(w=0, h=5, ln=1)

        pdf.small_font()
        pdf.cell(w=55, txt="Name des Ausleihenden")

        pdf.cell(w=0, h=8, ln=1)

        for check in process.checks.all().filter(checked_in=True):
            pdf.normal_font()
            pdf.cell(w=3, txt="-")
            pdf.mono_font()
            if check.item.preset:
                txt = "{} ({}, #{})".format(check.item.name, check.item.preset.name, check.item.id)
            else:
                txt = "{} (#{})".format(check.item.name, check.item.id)
            print(len(txt))
            if len(txt) > 30:
                pdf.cell(w=0, txt=txt, ln=1)
                pdf.cell(w=0, h=5, ln=1)
                pdf.cell(w=93)
            else:
                pdf.cell(w=90, txt=txt)

            pdf.normal_font(10)
            pdf.cell(w=8, txt=" am ")

            pdf.mono_font(12)
            pdf.cell(w=30, txt=formats.date_format(check.checked_in_at, "d.m.Y"))

            pdf.normal_font(10)
            pdf.cell(w=7, txt=" bei ", )

            pdf.mono_font(12)
            pdf.cell(w=55, txt=check.checked_in_by.get_full_name(), ln=1)

            pdf.cell(w=0, h=5, ln=1)

            pdf.small_font()
            pdf.cell(w=101)

            pdf.cell(w=30, txt="Datum")
            pdf.cell(w=7)
            pdf.cell(w=55, txt="Name des Technik-AG-Mitglieds", ln=1)
            pdf.cell(w=0, h=10, ln=1)
        pdf.cell(w=0, h=20, ln=1)

        pdf.set_font("line", size=12)
        pdf.cell(w=50, txt="________________________________")
        pdf.cell(w=65)
        pdf.cell(w=50, txt="________________________________", ln=1)
        pdf.cell(w=0, h=5, ln=1)

        pdf.small_font()
        pdf.cell(w=50, txt="Unterschrift des Ausleihenden")
        pdf.cell(w=65)
        pdf.cell(w=50, txt="Unterschrift des Technik-AG-Mitglieds", ln=1)

        pdf.text(x=10, y=285,
                 txt="Ausleihvorgang {}–{} #{}".format(process.borrowing_person.name, process.checked_out_at,
                                                       process.id))

        pdf.barcode_font(30)
        pdf.text(x=150, y=287, txt="*{}*".format(process.id))

    return pdf.save_in_tmp("check-in-{}.pdf".format(process.id))
