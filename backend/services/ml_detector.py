from collections import Counter


def generate_ml_features(
    invoice_data,
    historical_invoices
):

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

    duplicate_flag = 0
    vendor_frequency = 0
    amount_frequency = 0

    invoice_numbers = []
    vendors = []
    amounts = []

    for row in historical_invoices:

        invoice_numbers.append(
            str(row[0])
        )

        vendors.append(
            str(row[1])
        )

        amounts.append(
            str(row[2])
        )

    if invoice_number in invoice_numbers:
        duplicate_flag = 1

    vendor_counter = Counter(
        vendors
    )

    amount_counter = Counter(
        amounts
    )

    vendor_frequency = (
        vendor_counter.get(
            vendor_name,
            0
        )
    )

    amount_frequency = (
        amount_counter.get(
            amount,
            0
        )
    )

    return {
        "duplicate_flag": duplicate_flag,
        "vendor_frequency": vendor_frequency,
        "amount_frequency": amount_frequency,
        "has_gst": int(bool(gst_number)),
        "has_invoice_number": int(bool(invoice_number))
    }


def predict_invoice_risk(
    invoice_data,
    historical_invoices
):

    features = generate_ml_features(
        invoice_data,
        historical_invoices
    )

    score = 0

    if features["duplicate_flag"]:
        score += 10

    if features["vendor_frequency"] > 10:
        score += 15

    if features["amount_frequency"] > 5:
        score += 10

    if not features["has_gst"]:
        score += 15

    if not features["has_invoice_number"]:
        score += 20

    if score >= 70:

        prediction = "HIGH_RISK"

    elif score >= 40:

        prediction = "MEDIUM_RISK"

    else:

        prediction = "LOW_RISK"

    return {
        "ml_score": score,
        "prediction": prediction,
        "features": features
    }