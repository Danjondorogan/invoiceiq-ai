import sqlite3
import pandas as pd

DATABASE = "database.db"


def vendor_analytics():

    conn = sqlite3.connect(DATABASE)

    query = """
    SELECT
        vendor_name,
        COUNT(*) as total_invoices,
        AVG(fraud_score) as avg_risk
    FROM invoices
    WHERE vendor_name != ''
    GROUP BY vendor_name
    ORDER BY total_invoices DESC
    """

    df = pd.read_sql_query(
        query,
        conn
    )

    conn.close()

    return df.to_dict(
        orient="records"
    )


def monthly_analytics():

    conn = sqlite3.connect(DATABASE)

    query = """
    SELECT
        substr(uploaded_at,1,7) as month,
        COUNT(*) as invoices,
        AVG(fraud_score) as avg_risk
    FROM invoices
    GROUP BY month
    ORDER BY month
    """

    df = pd.read_sql_query(
        query,
        conn
    )

    conn.close()

    return df.to_dict(
        orient="records"
    )


def risk_distribution():

    conn = sqlite3.connect(DATABASE)

    cursor = conn.cursor()

    cursor.execute(
        "SELECT COUNT(*) FROM invoices WHERE status='VERIFIED'"
    )

    verified = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM invoices WHERE status='SUSPICIOUS'"
    )

    suspicious = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM invoices WHERE status='HIGH RISK'"
    )

    high_risk = cursor.fetchone()[0]

    conn.close()

    return {
        "verified": verified,
        "suspicious": suspicious,
        "high_risk": high_risk
    }