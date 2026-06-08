import sqlite3
import pandas as pd
import joblib

from sklearn.ensemble import RandomForestClassifier


DATABASE = "database.db"


def load_data():

    conn = sqlite3.connect(DATABASE)

    query = """
    SELECT
        invoice_number,
        vendor_name,
        amount,
        fraud_score
    FROM invoices
    """

    df = pd.read_sql_query(
        query,
        conn
    )

    conn.close()

    return df


def prepare_features(df):

    X = []
    y = []

    vendor_counts = (
        df["vendor_name"]
        .fillna("")
        .astype(str)
        .value_counts()
        .to_dict()
    )

    amount_counts = (
        df["amount"]
        .fillna(0)
        .astype(str)
        .value_counts()
        .to_dict()
    )

    invoice_counts = (
        df["invoice_number"]
        .fillna("")
        .astype(str)
        .value_counts()
        .to_dict()
    )

    for _, row in df.iterrows():

        invoice_number = str(
            row["invoice_number"]
            if pd.notna(row["invoice_number"])
            else ""
        )

        vendor_name = str(
            row["vendor_name"]
            if pd.notna(row["vendor_name"])
            else ""
        )

        amount_raw = str(
            row["amount"]
            if pd.notna(row["amount"])
            else "0"
        )

        try:
            amount = float(amount_raw)
        except:
            amount = 0.0

        invoice_present = int(
            invoice_number.strip() != ""
        )

        vendor_present = int(
            vendor_name.strip() != ""
        )

        duplicate_flag = int(
            invoice_counts.get(
                invoice_number,
                0
            ) > 1
        )

        vendor_frequency = (
            vendor_counts.get(
                vendor_name,
                0
            )
        )

        amount_frequency = (
            amount_counts.get(
                amount_raw,
                0
            )
        )

        score = int(
            row["fraud_score"]
        )

        label = 1 if score >= 40 else 0

        X.append([
            invoice_present,
            vendor_present,
            duplicate_flag,
            vendor_frequency,
            amount_frequency,
            amount
        ])

        y.append(label)

    return X, y


def train_model():

    df = load_data()

    print(
        f"Loaded {len(df)} invoices"
    )

    if len(df) < 20:

        print(
            "Need at least 20 invoices"
        )

        return

    X, y = prepare_features(df)

    model = RandomForestClassifier(
        n_estimators=200,
        max_depth=8,
        random_state=42
    )

    model.fit(X, y)

    joblib.dump(
        model,
        "models/fraud_model.pkl"
    )

    print(
        "\nModel trained successfully"
    )

    print(
        f"Samples: {len(X)}"
    )


if __name__ == "__main__":

    train_model()