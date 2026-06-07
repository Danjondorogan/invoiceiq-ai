from datetime import datetime


BLOCKED_VENDORS = [
    "Fake Vendor",
    "Blacklisted Vendor",
]


MAX_INVOICE_AMOUNT = 100000


def verify_invoice(invoice_data):

    issues = []

    score = 0

    # Amount validation

    try:

        amount = float(
            str(invoice_data.get("amount", "0"))
            .replace(",", "")
        )

        if amount <= 0:
            issues.append(
                "Invalid invoice amount"
            )
            score += 30

        if amount > MAX_INVOICE_AMOUNT:
            issues.append(
                "Amount exceeds threshold"
            )
            score += 20

    except:
        issues.append(
            "Unable to validate amount"
        )
        score += 20

    # Future date validation

    invoice_date = invoice_data.get(
        "invoice_date",
        ""
    )

    if invoice_date:

        try:

            date_obj = datetime.strptime(
                invoice_date,
                "%d/%m/%Y"
            )

            if date_obj > datetime.now():

                issues.append(
                    "Future invoice date"
                )

                score += 20

        except:
            pass

    # Vendor blacklist

    vendor = str(
        invoice_data.get(
            "vendor_name",
            ""
        )
    )

    if vendor in BLOCKED_VENDORS:

        issues.append(
            "Blocked vendor"
        )

        score += 40

    return {
        "issues": issues,
        "risk_score": score
    }