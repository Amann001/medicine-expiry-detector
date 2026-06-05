from ultralytics import YOLO
import cv2
from pathlib import Path

# Load model
model = YOLO("backend/models/best.pt")

# Test image
image_path = "backend/ocr/uploaded_image.jpeg"

# Run inference
results = model.predict(
    source=image_path,
    conf=0.05,
    save=False
)

# Load image
image = cv2.imread(image_path)

for r in results:

    print("Detected Classes:")

    for box in r.boxes:

        cls_id = int(box.cls[0])

        print(
            cls_id,
            model.names[cls_id]
        )

        x1, y1, x2, y2 = map(int, box.xyxy[0])

        crop = image[y1:y2, x1:x2]

        output_path = f"backend/ocr/crop_{cls_id}.jpg"

        cv2.imwrite(output_path, crop)

        print("Saved:", output_path)