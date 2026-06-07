import os
import hashlib
import shutil
import csv

RAW_FOLDER = "../dataset/raw"
CLEANED_FOLDER = "../dataset/cleaned"
DUPLICATE_FOLDER = "../dataset/duplicates"
REPORT_FOLDER = "../dataset/reports"

os.makedirs(CLEANED_FOLDER, exist_ok=True)
os.makedirs(DUPLICATE_FOLDER, exist_ok=True)
os.makedirs(REPORT_FOLDER, exist_ok=True)


def get_file_hash(filepath):

    md5 = hashlib.md5()

    with open(filepath, "rb") as f:

        while True:

            chunk = f.read(4096)

            if not chunk:
                break

            md5.update(chunk)

    return md5.hexdigest()


seen_hashes = set()

total_files = 0
duplicates = 0
unique_files = 0

report_rows = []

for filename in os.listdir(RAW_FOLDER):

    filepath = os.path.join(
        RAW_FOLDER,
        filename
    )

    if not os.path.isfile(filepath):
        continue

    total_files += 1

    try:

        file_hash = get_file_hash(
            filepath
        )

        if file_hash in seen_hashes:

            duplicates += 1

            shutil.copy2(
                filepath,
                os.path.join(
                    DUPLICATE_FOLDER,
                    filename
                )
            )

            report_rows.append([
                filename,
                "DUPLICATE"
            ])

        else:

            seen_hashes.add(
                file_hash
            )

            unique_files += 1

            shutil.copy2(
                filepath,
                os.path.join(
                    CLEANED_FOLDER,
                    filename
                )
            )

            report_rows.append([
                filename,
                "UNIQUE"
            ])

    except Exception:

        report_rows.append([
            filename,
            "ERROR"
        ])

report_file = os.path.join(
    REPORT_FOLDER,
    "cleaning_report.csv"
)

with open(
    report_file,
    "w",
    newline="",
    encoding="utf-8"
) as csvfile:

    writer = csv.writer(csvfile)

    writer.writerow([
        "filename",
        "status"
    ])

    writer.writerows(
        report_rows
    )

print("\n========== DATASET REPORT ==========")

print(
    f"Total Files: {total_files}"
)

print(
    f"Unique Files: {unique_files}"
)

print(
    f"Duplicates: {duplicates}"
)

print(
    f"Report Saved: {report_file}"
)