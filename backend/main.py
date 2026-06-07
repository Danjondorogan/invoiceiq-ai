from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from services.verifier import verify_invoice
from services.fraud_detector import calculate_fraud_risk
from services.ml_detector import predict_invoice_risk

import sqlite3
import pandas as pd

from services.extractor import (
    detect_file_type,
    extract_from_pdf,
    extract_from_excel,
    extract_from_image,
    extract_invoice_fields
)

from datetime import datetime
import os

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

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


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

    conn.commit()
    conn.close()


init_db()


# =====================================
# HOME ROUTE
# =====================================

@app.get("/")
def home():

    return {
        "project": "InvoiceIQ",
        "status": "running",
        "version": "1.0.0"
    }

# =====================================
# DUPLICATE CHECK
# =====================================

def check_duplicate(invoice_number):

    conn = sqlite3.connect(DATABASE)

    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM invoices WHERE invoice_number=?",
        (invoice_number,)
    )

    result = cursor.fetchone()

    conn.close()

    return result is not None

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
# UPLOAD INVOICE
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
    # Detect File Type
    # -------------------------

    file_type = detect_file_type(filename)

    raw_text = ""

    if file_type == "pdf":
        raw_text = extract_from_pdf(filepath)

    elif file_type == "excel":
        raw_text = extract_from_excel(filepath)

    elif file_type == "image":
        raw_text = extract_from_image(filepath)

    # -------------------------
    # Extract Fields
    # -------------------------

    fields = extract_invoice_fields(
        raw_text
    )

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
    # Status Calculation
    # -------------------------

    fraud_score = (
        fraud_result["fraud_score"]
        +
        verification["risk_score"]
        +
        ml_result["ml_score"]
    )

    status = "VERIFIED"

    if fraud_score >= 40:
        status = "SUSPICIOUS"

    if fraud_score >= 70:
        status = "HIGH RISK"

    # -------------------------
    # Save Database
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

        "fraud_analysis": fraud_result,

        "ml_analysis": ml_result,

        "preview": raw_text[:1000]
    }


# =====================================
# DASHBOARD
# =====================================

@app.get("/dashboard")
def dashboard():

    conn = sqlite3.connect(DATABASE)

    df = pd.read_sql_query(
        "SELECT * FROM invoices",
        conn
    )

    conn.close()

    return df.to_dict(orient="records")

@app.get("/stats")
def get_stats():

    conn = sqlite3.connect(DATABASE)

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
        "average_fraud_score": round(avg_score or 0, 2)
    }

