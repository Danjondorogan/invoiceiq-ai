import os
import requests

DATASET_FOLDER = "../dataset/cleaned"

API_URL = "http://127.0.0.1:8000/upload"

success = 0
failed = 0

for filename in os.listdir(DATASET_FOLDER):

    filepath = os.path.join(
        DATASET_FOLDER,
        filename
    )

    if not os.path.isfile(filepath):
        continue

    try:

        with open(filepath, "rb") as f:

            files = {
                "file": (
                    filename,
                    f
                )
            }

            response = requests.post(
                API_URL,
                files=files
            )

        if response.status_code == 200:

            success += 1

            print(
                f"[OK] {filename}"
            )

        else:

            failed += 1

            print(
                f"[FAILED] {filename}"
            )

    except Exception as e:

        failed += 1

        print(
            f"[ERROR] {filename} -> {e}"
        )

print("\n========== DONE ==========")
print("Success:", success)
print("Failed :", failed)