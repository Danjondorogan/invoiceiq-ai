import re


BLACKLIST = [
    "invoice",
    "tax invoice",
    "bill",
    "gst",
    "cgst",
    "sgst",
    "igst",
    "phone",
    "mobile",
    "email",
    "website",
    "address",
    "bank",
    "ifsc",
    "account",
    "customer",
    "billing",
    "shipping",
    "authorised",
    "authorized",
    "transporter",
    "terms",
    "total",
    "amount",
    "qty",
    "quantity",
    "particulars",
    "hsn",
    "date"
]


# =====================================
# VENDOR
# =====================================

def extract_vendor_advanced(text):

    # Amazon
    amazon_match = re.search(
        r"Amazon Seller Services Private Limited",
        text,
        re.IGNORECASE
    )

    if amazon_match:
        return "Amazon Seller Services Private Limited"

    lines = text.split("\n")

    candidates = []

    for line in lines[:50]:

        line = line.strip()

        if len(line) < 4:
            continue

        lower = line.lower()

        if any(word in lower for word in BLACKLIST):
            continue

        if re.search(r"\d{5,}", line):
            continue

        if len(line) > 100:
            continue

        score = 0

        if line.isupper():
            score += 5

        if len(line.split()) >= 2:
            score += 3

        company_keywords = [
            "PVT",
            "PRIVATE",
            "LIMITED",
            "LLP",
            "ELECTRONICS",
            "TECHNOLOGIES",
            "TRADERS",
            "ENTERPRISES",
            "INDUSTRIES",
            "SERVICES",
            "CORPORATION",
            "COMPANY"
        ]

        if any(
            word in line.upper()
            for word in company_keywords
        ):
            score += 15

        candidates.append(
            (score, line)
        )

    if not candidates:
        return ""

    candidates.sort(
        reverse=True
    )

    return candidates[0][1]


# =====================================
# INVOICE NUMBER
# =====================================

def extract_invoice_number_advanced(text):

    special_patterns = [

        r"EPP-\d{4}-\d+",
        r"PRINV\d+",
        r"MKT-\d+"

    ]

    for pattern in special_patterns:

        match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if match:
            return match.group(0)

    patterns = [

        r"Invoice\s*Number\s*[:\-]?\s*([A-Z0-9\-\/]+)",
        r"Invoice\s*No\.?\s*[:\-]?\s*([A-Z0-9\-\/]+)",
        r"Inv\s*No\.?\s*[:\-]?\s*([A-Z0-9\-\/]+)",
        r"Tax\s*Inv\.?\s*No\.?\s*[:\-]?\s*([A-Z0-9\-\/]+)",
        r"Bill\s*No\.?\s*[:\-]?\s*([A-Z0-9\-\/]+)"
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if match:

            value = match.group(1).strip()

            if value.lower().startswith("address"):
                continue

            return value

    return ""


# =====================================
# AMOUNT
# =====================================

def extract_amount_advanced(text):

    patterns = [

        r"Total\s*Invoice\s*Amount\s*Rs\.?\s*([0-9,.]+)",
        r"G\.\s*TOTAL\s*([0-9,.]+)",
        r"Grand\s*Total\s*[:₹ ]*([0-9,.]+)",
        r"Invoice\s*Value\s*[:₹ ]*([0-9,.]+)",
        r"Net\s*Amount\s*[:₹ ]*([0-9,.]+)",
        r"Amount\s*Due\s*[:₹ ]*([0-9,.]+)",
        r"Final\s*Amount\s*[:₹ ]*([0-9,.]+)"
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if match:
            return match.group(1)

    return ""


# =====================================
# GST
# =====================================

def extract_gst_advanced(text):

    matches = re.findall(
        r"\b[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z][A-Z0-9]Z[A-Z0-9]\b",
        text
    )

    if not matches:
        return ""

    return matches[0]


# =====================================
# DATE
# =====================================

def extract_date_advanced(text):

    patterns = [

        r"\d{2}/\d{2}/\d{4}",
        r"\d{2}-\d{2}-\d{4}",
        r"\d{4}-\d{2}-\d{2}",
        r"\d{2}\.\d{2}\.\d{4}"
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text
        )

        if match:
            return match.group(0)

    return ""


# =====================================
# MAIN PARSER
# =====================================

def parse_invoice_advanced(text):

    return {

        "invoice_number":
            extract_invoice_number_advanced(text),

        "vendor_name":
            extract_vendor_advanced(text),

        "invoice_date":
            extract_date_advanced(text),

        "amount":
            extract_amount_advanced(text),

        "gst_number":
            extract_gst_advanced(text)
    }