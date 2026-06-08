import sqlite3

DATABASE = "database.db"

vendors = [

    (
        "Amazon Seller Services Private Limited",
        "29AAICA3918J1ZE",
        "ACTIVE"
    ),

    (
        "Eclectech Power Packs LLP",
        "33AAHFE6927B1ZQ",
        "ACTIVE"
    ),

    (
        "MAHALASA ELECTRONICS",
        "29AKTPP5258Q1ZT",
        "ACTIVE"
    )
]

conn = sqlite3.connect(DATABASE)

cursor = conn.cursor()

for vendor in vendors:

    cursor.execute("""
    INSERT OR IGNORE INTO vendors(
        vendor_name,
        gst_number,
        status
    )
    VALUES(?,?,?)
    """, vendor)

conn.commit()
conn.close()

print("Vendor database seeded")