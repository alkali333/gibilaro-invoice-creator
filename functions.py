import requests
from io import BytesIO
import pypdf
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer, LTChar

pdfmetrics.registerFont(TTFont("Ovo", "fonts/Ovo-Regular.ttf"))


def limit_file_name(product_name: str) -> str:
    # Remove trailing slash if present

    words = product_name.split("-")[:4]  # Split by '-' and take the first 4 words
    limited_name = "-".join(words)  # Join them back together with '-'
    return limited_name


def fetch_pdf(product_url: str) -> tuple[BytesIO, str]:
    pdf_url = product_url + "?print-products=pdf"

    response = requests.get(pdf_url)
    response.raise_for_status()  # this will raise error if the request failed

    # Convert to a BytesIO object
    pdf_bytes = BytesIO(response.content)

    # Use the name of the file for the download button
    if product_url.endswith("/"):
        product_url = product_url[:-1]
    product_name = product_url.split("/")[-1]  # Extract product name for file name
    limited_product_name = limit_file_name(product_name)
    file_name = limited_product_name + "-invoice.pdf"

    return pdf_bytes, file_name


def append_text_to_pdf(pdf_bytes: BytesIO, text: str, x: int, y: int) -> BytesIO:
    # Create a PDF file to overlay
    packet = BytesIO()
    c = canvas.Canvas(packet, pagesize=letter)

    c.setFont("Ovo", 12)

    # Split the text by newlines and draw each line separately
    lines = text.split("\n")
    line_height = 26  # Set line height for the text
    for line in lines:
        c.drawString(x, y, line)
        y -= line_height  # Move to the next line by decreasing the y-coordinate

    c.save()

    # Move the buffer to the beginning so pypdf can read it
    packet.seek(0)
    new_pdf = pypdf.PdfReader(packet)
    existing_pdf = pypdf.PdfReader(pdf_bytes)

    # Add the "watermark" (which is the new PDF) on the existing page
    page = existing_pdf.pages[0]
    page.merge_page(new_pdf.pages[0])
    output = BytesIO()
    output_pdf = pypdf.PdfWriter()

    # Add the modified first page and then the rest of the pages
    output_pdf.add_page(page)
    for i in range(1, len(existing_pdf.pages)):
        output_pdf.add_page(existing_pdf.pages[i])

    output_pdf.write(output)
    output.seek(0)
    return output


from pdfminer.high_level import extract_pages
import fitz  # PyMuPDF


def find_string_coordinates(pdf_bytes, search_str):
    # Open the PDF file from the BytesIO object
    pdf = fitz.open(stream=pdf_bytes, filetype="pdf")

    # Iterate through each page of the PDF until the string is found
    for page_num in range(len(pdf)):
        page = pdf[page_num]
        # Search for the string (case insensitive)
        text_instances = page.search_for(search_str, hit_max=16)

        # If the string is found, return the first instance's coordinates
        if text_instances:
            rect = text_instances[0]
            x1, y1, x2, y2 = rect
            # Adjust y coordinate to top-origin system
            y1_adjusted = page.rect.height - y1
            # Round the coordinates to the nearest integer
            return int(round(x1)), int(round(y1_adjusted))

    # If the string was not found in any page, return None
    return None, None
