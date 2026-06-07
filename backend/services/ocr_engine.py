import fitz
import pytesseract
import cv2
import numpy as np

from PIL import Image
from pdf2image import convert_from_path


POPPLER_PATH = r"C:\Program Files\poppler-26.02.0\Library\bin"


# =====================================
# IMAGE PREPROCESSING
# =====================================

def preprocess_image(image):

    image_np = np.array(image)

    gray = cv2.cvtColor(
        image_np,
        cv2.COLOR_RGB2GRAY
    )

    gray = cv2.GaussianBlur(
        gray,
        (3, 3),
        0
    )

    thresh = cv2.threshold(
        gray,
        0,
        255,
        cv2.THRESH_BINARY +
        cv2.THRESH_OTSU
    )[1]

    return thresh


# =====================================
# OCR IMAGE
# =====================================

def extract_text_from_image(image):

    processed = preprocess_image(
        image
    )

    text = pytesseract.image_to_string(
        processed,
        config="--oem 3 --psm 6"
    )

    return text


# =====================================
# OCR PDF
# =====================================

def extract_text_from_scanned_pdf(
    pdf_path
):

    pages = convert_from_path(
        pdf_path,
        poppler_path=POPPLER_PATH
    )

    full_text = ""

    for page in pages:

        text = extract_text_from_image(
            page
        )

        full_text += text + "\n"

    return full_text


# =====================================
# HYBRID PDF EXTRACTION
# =====================================

def extract_pdf_hybrid(
    pdf_path
):

    text = ""

    doc = fitz.open(pdf_path)

    for page in doc:

        page_text = page.get_text()

        if isinstance(page_text, str):

            text += page_text

    doc.close()

    if len(text.strip()) > 100:

        print(
            "Using native PDF extraction"
        )

        return text

    print(
        "Using OCR fallback"
    )

    return extract_text_from_scanned_pdf(
        pdf_path
    )