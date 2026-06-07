import re
import fitz
import pandas as pd
import pytesseract
from PIL import Image


# =====================================
# FILE TYPE DETECTION
# =====================================

def detect_file_type(filename):

    filename = filename.lower()

    if filename.endswith(".pdf"):
        return "pdf"

    elif filename.endswith(".xlsx"):
        return "excel"

    elif filename.endswith(".xls"):
        return "excel"

    elif filename.endswith(".png"):
        return "image"

    elif filename.endswith(".jpg"):
        return "image"

    elif filename.endswith(".jpeg"):
        return "image"

    return "unknown"


# =====================================
# PDF EXTRACTION
# =====================================

def extract_from_pdf(pdf_path):

    text = ""

    doc = fitz.open(pdf_path)

    for page in doc:

        page_text = page.get_text()

        if page_text:
            text += str(page_text) + "\n"

    doc.close()

    return text


# =====================================
# EXCEL EXTRACTION
# =====================================

def extract_from_excel(excel_path):

    try:

        df = pd.read_excel(
            excel_path,
            header=None
        )

        return df.to_string()

    except Exception:

        return ""


# =====================================
# IMAGE OCR
# =====================================

def extract_from_image(image_path):

    try:

        image = Image.open(image_path)

        text = pytesseract.image_to_string(
            image
        )

        return text

    except Exception:

        return ""


# =====================================
# INVOICE FIELD EXTRACTION
# =====================================

def extract_invoice_fields(text):

    data = {
        "invoice_number": "",
        "vendor_name": "",
        "invoice_date": "",
        "amount": "",
        "gst_number": ""
    }

    # -------------------------
    # Invoice Number
    # -------------------------

    invoice_patterns = [

        r"Invoice\s*No[:\-\s]*([A-Z0-9\/\-]+)",
        r"Invoice\s*Number[:\-\s]*([A-Z0-9\/\-]+)",
        r"Invoice\s*#[:\-\s]*([A-Z0-9\/\-]+)",
        r"Invoice\s*ID[:\-\s]*([A-Z0-9\/\-]+)",
        r"Tax\s*Invoice\s*No[:\-\s]*([A-Z0-9\/\-]+)",
        r"Inv\s*No[:\-\s]*([A-Z0-9\/\-]+)",
        r"Bill\s*No[:\-\s]*([A-Z0-9\/\-]+)",
        r"Reference\s*No[:\-\s]*([A-Z0-9\/\-]+)"
        ]

    for pattern in invoice_patterns:

        match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if match:

            data["invoice_number"] = (
                match.group(1)
            )

            break

    # -------------------------
    # GST Number
    # -------------------------

    gst_match = re.search(

        r"\b[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z][A-Z0-9]Z[A-Z0-9]\b",

        text

    )

    if gst_match:

        data["gst_number"] = (
            gst_match.group(0)
        )

    # -------------------------
    # Invoice Date
    # -------------------------

    date_patterns = [

        r"\d{2}/\d{2}/\d{4}",
        r"\d{2}-\d{2}-\d{4}",
        r"\d{4}-\d{2}-\d{2}",
        r"\d{2}\.\d{2}\.\d{4}",

        r"\d{1,2}\s+[A-Za-z]{3,9}\s+\d{4}",
        r"[A-Za-z]{3,9}\s+\d{1,2},\s+\d{4}"
    ]

    for pattern in date_patterns:

        match = re.search(
            pattern,
            text
        )

        if match:

            data["invoice_date"] = (
                match.group(0)
            )

            break

    # -------------------------
    # Amount
    # -------------------------

    amount_patterns = [

        r"Grand\s*Total[:\s₹]*([\d,]+\.\d{2})",
        r"Total\s*Amount[:\s₹]*([\d,]+\.\d{2})",
        r"Invoice\s*Total[:\s₹]*([\d,]+\.\d{2})",
        r"Amount\s*Due[:\s₹]*([\d,]+\.\d{2})",
        r"Net\s*Amount[:\s₹]*([\d,]+\.\d{2})",
        r"Payable\s*Amount[:\s₹]*([\d,]+\.\d{2})",
        r"Final\s*Amount[:\s₹]*([\d,]+\.\d{2})",
        r"Total[:\s₹]*([\d,]+\.\d{2})"
        
        ]       

    for pattern in amount_patterns:

        match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if match:

            data["amount"] = (
                match.group(1)
            )

            break

    # -------------------------
    # Vendor Name
    # -------------------------

    lines = text.split("\n")

    cleaned_lines = []

    for line in lines:

        line = line.strip()

        if len(line) > 3:

            cleaned_lines.append(
                line
            )

    blacklist = [

        "invoice",
        "tax invoice",
        "gst",
        "cgst",
        "sgst",
        "igst",
        "amount",
        "quantity",
        "description",
        "date",
        "bill",
        "phone",
        "mobile",
        "address",
        "hsn",
        "state code"
    ]

    for line in cleaned_lines[:10]:

        lower_line = line.lower()

        if any(
            word in lower_line
            for word in blacklist
        ):
            continue

        if 4 < len(line) < 80:

            data["vendor_name"] = line

            break

    return data