import re


# =====================================
# BLACKLIST
# =====================================

BLACKLIST = [

    "invoice",
    "tax invoice",
    "bill",
    "gst",
    "gstin",
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
    "date",
    "recipient",
    "supplier code",
    "vendor code",
    "purchase order",
    "po number",
    "lr no",
    "dispatch",
    "description",
    "goods",
    "services",
    "unit price",
    "price",
    "taxable value"
]


# =====================================
# CLEAN TEXT
# =====================================

def clean_text(text):

    text = text.replace("\r", "\n")

    text = re.sub(
        r"\n+",
        "\n",
        text
    )

    return text


# =====================================
# GST
# =====================================

def extract_gst_advanced(text):

    matches = re.findall(
        r"\b[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z][A-Z0-9]Z[A-Z0-9]\b",
        text
    )

    if matches:
        return matches[0]

    return ""


# =====================================
# DATE
# =====================================

def extract_date_advanced(text):

    patterns = [

        r"\d{2}/\d{2}/\d{4}",
        r"\d{2}-\d{2}-\d{4}",
        r"\d{4}-\d{2}-\d{2}",
        r"\d{2}\.\d{2}\.\d{4}",

        r"\d{1,2}/\d{1,2}/\d{4}",
        r"\d{1,2}-\d{1,2}-\d{4}"
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
# INVOICE NUMBER
# =====================================

def extract_invoice_number_advanced(text):

    patterns = [

        r"Document\s*No\.?\s*[:\-]?\s*([A-Z0-9\/\-_]+)",

        r"Invoice\s*Number\s*[:\-]?\s*([A-Z0-9\/\-_]+)",

        r"Invoice\s*No\.?\s*[:\-]?\s*([A-Z0-9\/\-_]+)",

        r"Tax\s*Invoice\s*No\.?\s*[:\-]?\s*([A-Z0-9\/\-_]+)",

        r"Inv\s*No\.?\s*[:\-]?\s*([A-Z0-9\/\-_]+)",

        r"Bill\s*No\.?\s*[:\-]?\s*([A-Z0-9\/\-_]+)",

        r"Reference\s*No\.?\s*[:\-]?\s*([A-Z0-9\/\-_]+)"
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if match:

            invoice_no = match.group(1).strip()

            if len(invoice_no) >= 3:
                return invoice_no

    return ""


# =====================================
# AMOUNT
# =====================================

def extract_amount_advanced(text):

    patterns = [

        r"Total\s*Invoice\s*Amount.*?([0-9,]+\.\d{2})",

        r"Invoice\s*Value.*?([0-9,]+\.\d{2})",

        r"Grand\s*Total.*?([0-9,]+\.\d{2})",

        r"Net\s*Amount.*?([0-9,]+\.\d{2})",

        r"Amount\s*Due.*?([0-9,]+\.\d{2})",

        r"Final\s*Amount.*?([0-9,]+\.\d{2})",

        r"G\.?\s*TOTAL.*?([0-9,]+\.\d{2})"
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if match:
            return match.group(1)

    numbers = re.findall(
        r"\b\d+[,.]?\d*\.\d{2}\b",
        text
    )

    if numbers:

        try:

            values = []

            for num in numbers:

                values.append(
                    float(
                        num.replace(",", "")
                    )
                )

            return str(max(values))

        except:
            pass

    return ""


# =====================================
# VENDOR
# =====================================

def extract_vendor_advanced(text):

    lines = text.split("\n")

    # -------------------------
    # Direct Supplier/Vendor Extraction
    # -------------------------

    supplier_patterns = [

        r"Supplier\s*:\s*([^\n]+)",
        r"Vendor\s*:\s*([^\n]+)",
        r"Sold\s*By\s*:\s*([^\n]+)",
        r"From\s*:\s*([^\n]+)",
        r"Regd\s*Office\s*:\s*([^\n]+)"
    ]

    for pattern in supplier_patterns:

        match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if match:

            vendor = match.group(1).strip()

            if len(vendor) > 3:

                lower = vendor.lower()

                if not any(
                    word in lower
                    for word in BLACKLIST
                ):
                    return vendor

    # -------------------------
    # Supplier Block Detection
    # -------------------------

    supplier_found = False

    for line in lines:

        clean = line.strip()

        if "supplier" in clean.lower():

            supplier_found = True
            continue

        if supplier_found:

            if len(clean) < 4:
                continue

            if len(clean) > 120:
                continue

            lower = clean.lower()

            if any(
                word in lower
                for word in BLACKLIST
            ):
                continue

            if re.search(
                r"\d{8,}",
                clean
            ):
                continue

            return clean

    # -------------------------
    # GST Neighbour Search
    # -------------------------

    for i, line in enumerate(lines):

        if "gstin" in line.lower():

            start = max(
                0,
                i - 8
            )

            end = min(
                len(lines),
                i + 2
            )

            for j in range(start, end):

                candidate = (
                    lines[j]
                    .strip()
                )

                if len(candidate) < 4:
                    continue

                if len(candidate) > 120:
                    continue

                lower = candidate.lower()

                if any(
                    word in lower
                    for word in BLACKLIST
                ):
                    continue

                if re.search(
                    r"\d{8,}",
                    candidate
                ):
                    continue

                return candidate

    # -------------------------
    # Generic Company Scoring
    # -------------------------

    candidates = []

    company_words = [

        "PVT",
        "PRIVATE",
        "LIMITED",
        "LLP",
        "LTD",
        "ENTERPRISES",
        "INDUSTRIES",
        "SERVICES",
        "TECHNOLOGIES",
        "SYSTEMS",
        "ELECTRONICS",
        "CORPORATION",
        "COMPANY",
        "ACADEMY",
        "CENTER",
        "CENTRE",
        "TRADERS",
        "AGENCIES",
        "DISTRIBUTORS",
        "SOLUTIONS",
        "INDIA"
    ]

    for index, line in enumerate(lines[:100]):

        line = line.strip()

        if len(line) < 4:
            continue

        if len(line) > 120:
            continue

        lower = line.lower()

        if any(
            word in lower
            for word in BLACKLIST
        ):
            continue

        score = 0

        if line.isupper():
            score += 20

        if len(line.split()) >= 2:
            score += 10

        if any(
            word in line.upper()
            for word in company_words
        ):
            score += 30

        if re.search(
            r"\d{6,}",
            line
        ):
            score -= 20

        if re.search(
            r"[A-Za-z]",
            line
        ):
            score += 5

        score += max(
            0,
            70 - index
        )

        candidates.append(
            (score, line)
        )

    if not candidates:
        return ""

    candidates.sort(
        key=lambda x: x[0],
        reverse=True
    )

    return candidates[0][1]

# =====================================
# MAIN PARSER
# =====================================

def parse_invoice_advanced(text):

    text = clean_text(text)

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