from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
import shutil, cv2, os
import numpy as np
import easyocr
from backend.ocr.find_expiry import extract_expiry_date

app = FastAPI(title="Medicine Expiry Detector API", version="1.0.0")

reader = easyocr.Reader(['en'])

@app.get("/")
def home():
    return {"message": "Medicine Expiry Detector API is running"}

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.post("/detect-expiry")
async def detect_expiry(file: UploadFile = File(...)):
    upload_path = "backend/ocr/uploaded_image.jpeg"
    with open(upload_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    detection_method = "fallback_full_image"
    ocr_source = upload_path

    try:
        from ultralytics import YOLO
        model = YOLO("backend/models/best.pt")
        results = model.predict(upload_path, conf=0.25, verbose=False)
        boxes = results[0].boxes
        if len(boxes) > 0:
            img = cv2.imread(upload_path)
            box = boxes[0]
            x1, y1, x2, y2 = [int(v) for v in box.xyxy[0].tolist()]
            crop = img[y1:y2, x1:x2]
            crop_path = "backend/ocr/expiry_crop.jpeg"
            cv2.imwrite(crop_path, crop)
            ocr_source = crop_path
            detection_method = "yolo"
    except Exception:
        ocr_source = upload_path

    best_expiry = None
    best_status = None

    img_color = cv2.imread(ocr_source)

    for rotate_flag in [None, cv2.ROTATE_180, cv2.ROTATE_90_CLOCKWISE, cv2.ROTATE_90_COUNTERCLOCKWISE]:
        if rotate_flag is not None:
            rotated = cv2.rotate(img_color, rotate_flag)
        else:
            rotated = img_color.copy()

        # Pass numpy array directly — not file path
        gray = cv2.cvtColor(rotated, cv2.COLOR_BGR2GRAY)

        result = reader.readtext(gray)
        # Pass raw EasyOCR output directly — find_expiry handles all formats
        expiry, status = extract_expiry_date(result)

        if expiry:
            best_expiry = expiry
            best_status = status
            break

    if best_expiry:
        return JSONResponse({
            "success": True,
            "expiry_date": best_expiry,
            "status": best_status,
            "detection_method": detection_method,
            "message": f"Expiry date found: {best_expiry} — {best_status}"
        })
    else:
        return JSONResponse({
            "success": False,
            "expiry_date": None,
            "status": "Could not extract expiry date",
            "detection_method": detection_method,
            "message": "No expiry date found. Ensure expiry text is visible."
        })