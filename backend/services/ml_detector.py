import joblib
from collections import Counter

MODEL_PATH = "models/fraud_model.pkl"

try:

    model = joblib.load(
        MODEL_PATH
    )

except Exception:

    model = None


def generate_ml_features(
    invoice_data,
    historical_invoices
):

    invoice_number = str(
        invoice_data.get(
            "invoice_number",
            ""
        ) or ""
    ).strip()

    vendor_name = str(
        invoice_data.get(
            "vendor_name",
            ""
        ) or ""
    ).strip()

    gst_number = str(
        invoice_data.get(
            "gst_number",
            ""
        ) or ""
    ).strip()

    amount = str(
        invoice_data.get(
            "amount",
            ""
        ) or ""
    ).strip()

    invoice_numbers = []
    vendor_names = []
    amounts = []

    for row in historical_invoices:

        invoice_numbers.append(
            str(row[0] or "").strip()
        )

        vendor_names.append(
            str(row[1] or "").strip()
        )

        amounts.append(
            str(row[2] or "").strip()
        )

    duplicate_flag = int(
        invoice_number != ""
        and
        invoice_number in invoice_numbers
    )

    vendor_frequency = (
        Counter(vendor_names).get(
            vendor_name,
            0
        )
    )

    amount_frequency = (
        Counter(amounts).get(
            amount,
            0
        )
    )

    has_gst = int(
        gst_number != ""
    )

    has_invoice_number = int(
        invoice_number != ""
    )

    try:

        amount_value = float(
            amount.replace(",", "")
        )

    except Exception:

        amount_value = 0.0

    features = [

        has_invoice_number,
        int(vendor_name != ""),
        duplicate_flag,
        vendor_frequency,
        amount_frequency,
        amount_value
    ]

    feature_details = {

        "duplicate_flag":
            duplicate_flag,

        "vendor_frequency":
            vendor_frequency,

        "amount_frequency":
            amount_frequency,

        "has_gst":
            has_gst,

        "has_invoice_number":
            has_invoice_number,

        "amount":
            amount_value
    }

    return features, feature_details


def predict_invoice_risk(
    invoice_data,
    historical_invoices
):

    if model is None:

        return {

            "ml_score": 0,

            "prediction":
                "MODEL_NOT_FOUND",

            "probability": 0,

            "features": {}
        }

    try:

        features, feature_details = (
            generate_ml_features(
                invoice_data,
                historical_invoices
            )
        )

        prediction = model.predict(
            [features]
        )[0]

        probability = model.predict_proba(
            [features]
        )[0][1]

        ml_score = int(
            probability * 100
        )

        return {

            "ml_score":
                ml_score,

            "prediction":
                "HIGH_RISK"
                if prediction == 1
                else "LOW_RISK",

            "probability":
                round(
                    float(probability),
                    3
                ),

            "features":
                feature_details
        }

    except Exception as e:

        return {

            "ml_score": 0,

            "prediction":
                "ML_ERROR",

            "probability": 0,

            "error":
                str(e),

            "features": {}
        }