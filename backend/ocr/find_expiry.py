import re

with open("ocr_output.txt", "r", encoding="utf-8") as f:
    text = f.read()

expiry_patterns = [
    r"EXP[: ]*([A-Z]{3}[-/]\d{4})",
    r"EXP[: ]*([A-Z]{3}\s+\d{4})",
    r"([A-Z]{3}[-/]\d{4})",
    r"([A-Z]{3}\s+\d{4})",
    r"(\d{2}/\d{4})"
]

expiry_date = None

for pattern in expiry_patterns:
    match = re.search(pattern, text, re.IGNORECASE)

    if match:
        expiry_date = match.group(1)
        break

print("\nExpiry Date Found:")
print(expiry_date)