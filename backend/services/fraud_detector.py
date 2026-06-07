from collections import Counter


def calculate_fraud_risk(invoice_data, historical_invoices):

    reasons = []

    score = 0

    invoice_number = str(
        invoice_data.get(
            "invoice_number",
            ""
        )
    )

    vendor_name = str(
        invoice_data.get(
            "vendor_name",
            ""
        )
    )

    amount = str(
        invoice_data.get(
            "amount",
            ""
        )
    )

    gst_number = str(
        invoice_data.get(
            "gst_number",
            ""
        )
    )

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
    # Historical Analysis
    # -------------------------

    invoice_numbers = []
    vendor_names = []
    amounts = []

    for row in historical_invoices:

        invoice_numbers.append(
            str(row[0])
        )

        vendor_names.append(
            str(row[1])
        )

        amounts.append(
            str(row[2])
        )

    # -------------------------
    # Duplicate Invoice Number
    # -------------------------

    if invoice_number in invoice_numbers:

        reasons.append(
            "Invoice number already exists"
        )

        score += 40

    # -------------------------
    # Repeated Vendor
    # -------------------------

    vendor_count = Counter(
        vendor_names
    )

    if (
        vendor_name
        and vendor_count.get(vendor_name, 0)
        > 10
    ):

        reasons.append(
            "Vendor appears unusually often"
        )

        score += 10

    # -------------------------
    # Repeated Amount
    # -------------------------

    amount_count = Counter(
        amounts
    )

    if (
        amount
        and amount_count.get(amount, 0)
        > 5
    ):

        reasons.append(
            "Amount repeated many times"
        )

        score += 15

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