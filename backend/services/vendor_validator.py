import sqlite3

DATABASE = "database.db"


def validate_vendor(
    vendor_name,
    gst_number
):

    conn = sqlite3.connect(
        DATABASE
    )

    cursor = conn.cursor()

    cursor.execute("""
    SELECT
        gst_number,
        status
    FROM vendors
    WHERE vendor_name=?
    """, (vendor_name,))

    result = cursor.fetchone()

    conn.close()

    # Unknown vendor
    if not result:

        return {

            "valid": True,

            "known_vendor": False,

            "reason": "New vendor"
        }

    db_gst = result[0]

    status = result[1]

    if status == "BLOCKED":

        return {

            "valid": False,

            "known_vendor": True,

            "reason": "Vendor blocked"
        }

    if gst_number and db_gst and gst_number != db_gst:

        return {

            "valid": False,

            "known_vendor": True,

            "reason": "GST mismatch"
        }

    return {

        "valid": True,

        "known_vendor": True,

        "reason": ""
    }