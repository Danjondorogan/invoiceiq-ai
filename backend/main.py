from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware

from services.vendor_validator import validate_vendor
from services.verifier import verify_invoice
from services.fraud_detector import calculate_fraud_risk
from services.ml_detector import predict_invoice_risk
from services.invoice_parser import parse_invoice_advanced

from services.analytics import (
    vendor_analytics,
    monthly_analytics,
    risk_distribution
)
from services.extractor import (
    detect_file_type,
    extract_from_pdf,
    extract_from_excel,
    extract_from_image,
    extract_invoice_fields
)

import sqlite3
import pandas as pd
import os

from datetime import datetime

app = FastAPI(title="InvoiceIQ")


# =====================================
# CORS
# =====================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =====================================
# CONFIG
# =====================================

UPLOAD_FOLDER = "uploads"
DATABASE = "database.db"

os.makedirs(
    UPLOAD_FOLDER,
    exist_ok=True
)


# =====================================
# DATABASE
# =====================================

def init_db():

    conn = sqlite3.connect(DATABASE)

    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS invoices (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        filename TEXT,
        invoice_number TEXT,
        vendor_name TEXT,
        invoice_date TEXT,
        amount REAL,

        status TEXT,
        fraud_score INTEGER,

        uploaded_at TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS vendors (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        vendor_name TEXT UNIQUE,
        gst_number TEXT,
        status TEXT
    )
    """)

    conn.commit()
    conn.close()


init_db()


# =====================================
# HOME
# =====================================

@app.get("/")
def home():

    return {
        "project": "InvoiceIQ",
        "status": "running",
        "version": "1.0.0"
    }


# =====================================
# HISTORY
# =====================================

def get_historical_invoices():

    conn = sqlite3.connect(DATABASE)

    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            invoice_number,
            vendor_name,
            amount
        FROM invoices
    """)

    rows = cursor.fetchall()

    conn.close()

    return rows


# =====================================
# UPLOAD
# =====================================

@app.post("/upload")
async def upload_invoice(file: UploadFile = File(...)):

    filename = file.filename or "uploaded_file"

    filepath = os.path.join(
        UPLOAD_FOLDER,
        filename
    )

    with open(filepath, "wb") as f:
        f.write(await file.read())

    # -------------------------
    # File Type Detection
    # -------------------------

    file_type = detect_file_type(
        filename
    )

    raw_text = ""

    if file_type == "pdf":

        raw_text = extract_from_pdf(
            filepath
        )

    elif file_type == "excel":

        raw_text = extract_from_excel(
            filepath
        )

    elif file_type == "image":

        raw_text = extract_from_image(
            filepath
        )

    # -------------------------
    # Extraction
    # -------------------------

    basic_fields = extract_invoice_fields(
        raw_text
    )

    advanced_fields = parse_invoice_advanced(
        raw_text
    )

    fields = basic_fields.copy()

    for key, value in advanced_fields.items():

        if value:

            fields[key] = value

    if fields is None:

        fields = {
            "invoice_number": "",
            "vendor_name": "",
            "invoice_date": "",
            "amount": "",
            "gst_number": ""
        }

    print("\nFIELDS EXTRACTED:")
    print(fields)
    print()

    # -------------------------
    # Verification
    # -------------------------

    verification = verify_invoice(
        fields
    )

    vendor_check = validate_vendor(
        fields["vendor_name"],
        fields["gst_number"]
    )

    # -------------------------
    # Fraud Detection
    # -------------------------

    historical_invoices = (
        get_historical_invoices()
    )

    fraud_result = (
        calculate_fraud_risk(
            fields,
            historical_invoices
        )
    )

    ml_result = (
        predict_invoice_risk(
            fields,
            historical_invoices
        )
    )

    # -------------------------
    # Final Score
    # -------------------------

    fraud_score = (
        fraud_result["fraud_score"]
        +
        verification["risk_score"]
        +
        ml_result["ml_score"]
    )

    if (
        not vendor_check["valid"]
        and
        vendor_check["reason"] != "New vendor"
    ):
        fraud_score += 20

    status = "VERIFIED"

    if fraud_score >= 40:
        status = "SUSPICIOUS"

    if fraud_score >= 70:
        status = "HIGH RISK"

    # -------------------------
    # Save
    # -------------------------

    conn = sqlite3.connect(
        DATABASE
    )

    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO invoices(
            filename,
            invoice_number,
            vendor_name,
            invoice_date,
            amount,
            status,
            fraud_score,
            uploaded_at
        )
        VALUES(?,?,?,?,?,?,?,?)
    """,
    (
        filename,
        fields["invoice_number"],
        fields["vendor_name"],
        fields["invoice_date"],
        fields["amount"],
        status,
        fraud_score,
        str(datetime.now())
    ))

    cursor.execute("""
    INSERT OR IGNORE INTO vendors(
        vendor_name,
        gst_number,
        status
    )
    VALUES(?,?,?)
    """,
    (
        fields["vendor_name"],
        fields["gst_number"],
        "ACTIVE"
    ))

    conn.commit()
    conn.close()

    # -------------------------
    # Response
    # -------------------------

    return {

        "filename": filename,

        "file_type": file_type,

        "status": status,

        "fraud_score": fraud_score,

        "invoice_data": fields,

        "verification": verification,

        "vendor_validation": vendor_check,

        "fraud_analysis": fraud_result,

        "ml_analysis": ml_result,

        "preview": raw_text[:1000]
    }


# =====================================
# DASHBOARD
# =====================================

@app.get("/dashboard")
def dashboard():

    conn = sqlite3.connect(
        DATABASE
    )

    df = pd.read_sql_query(
        "SELECT * FROM invoices",
        conn
    )

    conn.close()

    return df.to_dict(
        orient="records"
    )


# =====================================
# STATS
# =====================================
# =====================================
# ANALYTICS
# =====================================

@app.get("/analytics/vendors")
def analytics_vendors():

    return vendor_analytics()


@app.get("/analytics/monthly")
def analytics_monthly():

    return monthly_analytics()


@app.get("/analytics/risk-distribution")
def analytics_risk_distribution():

    return risk_distribution()

@app.get("/stats")
def get_stats():

    conn = sqlite3.connect(
        DATABASE
    )

    cursor = conn.cursor()

    cursor.execute(
        "SELECT COUNT(*) FROM invoices"
    )

    total = cursor.fetchone()[0]

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

    cursor.execute(
        "SELECT AVG(fraud_score) FROM invoices"
    )

    avg_score = cursor.fetchone()[0]

    conn.close()

    return {

        "total_invoices": total,

        "verified": verified,

        "suspicious": suspicious,

        "high_risk": high_risk,

        "average_fraud_score": round(
            avg_score or 0,
            2
        )
    }