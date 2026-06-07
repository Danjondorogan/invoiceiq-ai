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

    for _, row in df.iterrows():

        invoice_present = int(
            bool(row["invoice_number"])
        )

        vendor_present = int(
            bool(row["vendor_name"])
        )

        try:

            amount = float(
                row["amount"]
            )

        except:

            amount = 0

        score = int(
            row["fraud_score"]
        )

        label = 1 if score >= 40 else 0

        X.append([
            invoice_present,
            vendor_present,
            amount
        ])

        y.append(label)

    return X, y


def train_model():

    df = load_data()

    if len(df) < 5:

        print(
            "Need at least 5 invoices."
        )

        return

    X, y = prepare_features(df)

    model = RandomForestClassifier(
        n_estimators=100,
        random_state=42
    )

    model.fit(X, y)

    joblib.dump(
        model,
        "models/fraud_model.pkl"
    )

    print(
        "Model trained successfully."
    )


if __name__ == "__main__":

    train_model()