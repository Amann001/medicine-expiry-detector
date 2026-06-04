import easyocr
import cv2
from pathlib import Path

print("Loading OCR model...")

reader = easyocr.Reader(['en'])

image_path = Path(__file__).parent / "test_image.jpeg"

print("Image path:", image_path)

image = cv2.imread(str(image_path))

print("Image loaded:", image is not None)

rotated = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)

temp_path = Path(__file__).parent / "rotated.jpeg"

cv2.imwrite(str(temp_path), rotated)

print("Rotated image saved:", temp_path)

print("Reading image...")

results = reader.readtext(str(temp_path))

print("\nDetected Text:\n")

for result in results:
    print(result[1])