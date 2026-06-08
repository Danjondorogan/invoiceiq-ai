from collections import Counter


def calculate_fraud_risk(
    invoice_data,
    historical_invoices
):

    reasons = []

    score = 0

    invoice_number = str(
        invoice_data.get(
            "invoice_number",
            ""
        )
    ).strip()

    vendor_name = str(
        invoice_data.get(
            "vendor_name",
            ""
        )
    ).strip()

    amount = str(
        invoice_data.get(
            "amount",
            ""
        )
    ).strip()

    gst_number = str(
        invoice_data.get(
            "gst_number",
            ""
        )
    ).strip()

    # -------------------------
    # Missing GST
    # -------------------------

    if not gst_number:

        reasons.append(
            "GST number missing"
        )

        score += 15

    # -------------------------
    # Missing Invoice Number
    # -------------------------

    if not invoice_number:

        reasons.append(
            "Invoice number missing"
        )

        score += 25

    # -------------------------
    # Historical Data
    # -------------------------

    invoice_numbers = []

    vendor_names = []

    amounts = []

    for row in historical_invoices:

        invoice_numbers.append(
            str(row[0]).strip()
        )

        vendor_names.append(
            str(row[1]).strip()
        )

        amounts.append(
            str(row[2]).strip()
        )

    # -------------------------
    # Duplicate Invoice
    # -------------------------

    if (
        invoice_number
        and
        invoice_number in invoice_numbers
    ):

        reasons.append(
            "Invoice number already exists"
        )

        score += 40

    # -------------------------
    # Vendor Frequency
    # -------------------------

    vendor_count = Counter(
        vendor_names
    )

    vendor_frequency = vendor_count.get(
        vendor_name,
        0
    )

    if vendor_frequency > 20:

        reasons.append(
            "Vendor appears unusually often"
        )

        score += 10

    # -------------------------
    # Amount Frequency
    # -------------------------

    amount_count = Counter(
        amounts
    )

    amount_frequency = amount_count.get(
        amount,
        0
    )

    if amount_frequency > 10:

        reasons.append(
            "Amount repeated many times"
        )

        score += 15

    # -------------------------
    # Empty Invoice Protection
    # -------------------------

    if (
        not invoice_number
        and
        not gst_number
        and
        not amount
    ):

        reasons.append(
            "Insufficient invoice data"
        )

        score += 20

    # -------------------------
    # Risk Level
    # -------------------------

    if score >= 70:

        risk = "HIGH"

    elif score >= 40:

        risk = "MEDIUM"

    else:

        risk = "LOW"

    return {

        "fraud_score": score,

        "risk_level": risk,

        "reasons": reasons
    }