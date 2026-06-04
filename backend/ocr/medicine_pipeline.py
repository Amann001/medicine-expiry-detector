import easyocr
import cv2
from pathlib import Path

print("Loading OCR...")

reader = easyocr.Reader(['en'])

# Load image
image_path = Path(__file__).parent / "expiry_crop.jpeg"

img = cv2.imread(str(image_path))

if img is None:
    print("Could not load image!")
    exit()

# Convert to grayscale
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# Slight sharpening
gray = cv2.GaussianBlur(gray, (0, 0), 3)
gray = cv2.addWeighted(gray, 1.5, gray, -0.5, 0)

# Crop only the expiry text area
h, w = gray.shape[:2]

text_region = gray[
    int(h * 0.25):int(h * 0.65),
    int(w * 0.45):int(w * 0.95)
]

# Save for inspection
cv2.imwrite("expiry_text_region.jpeg", text_region)

# OCR
results = reader.readtext(text_region)

full_text = " ".join([r[1] for r in results])

print("\nOCR TEXT:\n")
print(full_text)

with open("ocr_output.txt", "w", encoding="utf-8") as f:
    f.write(full_text)

print("\nSaved OCR output to ocr_output.txt")