import fitz
import pandas as pd
import pytesseract
import re

from PIL import Image


def extract_from_pdf(file_path: str) -> str:

    text = ""

    pdf = fitz.open(file_path)

    for page in pdf:
        page_text = page.get_text()

        if page_text:
            text += str(page_text)

    pdf.close()

    return text


def extract_from_excel(file_path: str) -> str:

    df = pd.read_excel(file_path)

    return df.to_string()


def extract_from_image(file_path: str) -> str:

    image = Image.open(file_path)

    text = pytesseract.image_to_string(image)

    return str(text)


def detect_file_type(filename: str) -> str:

    filename = filename.lower()

    if filename.endswith(".pdf"):
        return "pdf"

    if filename.endswith(".xlsx") or filename.endswith(".xls"):
        return "excel"

    if (
        filename.endswith(".png")
        or filename.endswith(".jpg")
        or filename.endswith(".jpeg")
    ):
        return "image"

    return "unknown"


def extract_invoice_fields(text: str):

    data = {
        "invoice_number": "",
        "amount": "",
        "gst_number": "",
        "invoice_date": "",
        "vendor_name": "",
    }

    invoice_match = re.search(
        r"(invoice[\s\-#:]*)([A-Za-z0-9\-\/]+)",
        text,
        re.IGNORECASE,
    )

    if invoice_match:
        data["invoice_number"] = str(invoice_match.group(2))

    amount_match = re.search(
        r"(?:₹|Rs\.?|INR)?\s?(\d+(?:,\d+)*(?:\.\d+)?)",
        text,
        re.IGNORECASE,
    )

    if amount_match:
        data["amount"] = str(amount_match.group(1))

    gst_match = re.search(
        r"\b[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[A-Z0-9]{3}\b",
        text,
    )

    if gst_match:
        data["gst_number"] = str(gst_match.group())

    return data