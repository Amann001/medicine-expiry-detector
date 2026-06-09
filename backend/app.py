from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
import shutil, cv2, os
import numpy as np
import easyocr
from backend.ocr.find_expiry import extract_expiry_date

app = FastAPI(title="Medicine Expiry Detector API", version="1.0.0")
reader = easyocr.Reader(['en'])


def preprocess_variants(img_color):
    """
    Generate multiple preprocessed versions of the image.
    More variants = higher chance of OCR reading the expiry date correctly.
    """
    variants = []
    h, w = img_color.shape[:2]

    # Resize if image is too large (speeds up OCR significantly)
    if max(h, w) > 1920:
        scale = 1920 / max(h, w)
        img_color = cv2.resize(img_color, (int(w * scale), int(h * scale)))

    gray = cv2.cvtColor(img_color, cv2.COLOR_BGR2GRAY)

    # Variant 1: Clean grayscale
    variants.append(gray)

    # Variant 2: CLAHE enhanced (helps with low contrast)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)
    variants.append(enhanced)

    # Variant 3: Sharpened
    kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
    sharpened = cv2.filter2D(gray, -1, kernel)
    variants.append(sharpened)

    # Variant 4: Denoised
    denoised = cv2.fastNlMeansDenoising(gray, h=10)
    variants.append(denoised)

    # Variant 5: Adaptive threshold (good for stamped text on bottles)
    thresh = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY, 11, 2
    )
    variants.append(thresh)

    # Variant 6: Otsu threshold
    _, otsu = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    variants.append(otsu)

    # Variant 7: Inverted (some medicines have white text on dark background)
    inverted = cv2.bitwise_not(gray)
    variants.append(inverted)

    return variants


def run_ocr_all_variants(img_color):
    """
    Try OCR on all rotations × all preprocessing variants.
    Return first successful expiry date found.
    """
    rotations = [
        None,
        cv2.ROTATE_180,
        cv2.ROTATE_90_CLOCKWISE,
        cv2.ROTATE_90_COUNTERCLOCKWISE,
    ]

    for rotate_flag in rotations:
        if rotate_flag is not None:
            rotated = cv2.rotate(img_color, rotate_flag)
        else:
            rotated = img_color.copy()

        variants = preprocess_variants(rotated)

        for variant in variants:
            try:
                result = reader.readtext(variant)
                expiry, status = extract_expiry_date(result)
                if expiry:
                    return expiry, status
            except Exception:
                continue

    return None, None


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

    # Try YOLO detection first
    try:
        from ultralytics import YOLO
        model = YOLO("backend/models/best.pt")
        results = model.predict(upload_path, conf=0.25, verbose=False)
        boxes = results[0].boxes
        if len(boxes) > 0:
            img = cv2.imread(upload_path)
            box = boxes[0]
            x1, y1, x2, y2 = [int(v) for v in box.xyxy[0].tolist()]
            # Add padding around crop
            pad = 20
            x1 = max(0, x1 - pad)
            y1 = max(0, y1 - pad)
            x2 = min(img.shape[1], x2 + pad)
            y2 = min(img.shape[0], y2 + pad)
            crop = img[y1:y2, x1:x2]
            crop_path = "backend/ocr/expiry_crop.jpeg"
            cv2.imwrite(crop_path, crop)
            ocr_source = crop_path
            detection_method = "yolo"
    except Exception:
        ocr_source = upload_path

    # Run OCR with all variants
    img_color = cv2.imread(ocr_source)
    best_expiry, best_status = run_ocr_all_variants(img_color)

    # If YOLO crop failed, retry on full image
    if not best_expiry and ocr_source != upload_path:
        img_color_full = cv2.imread(upload_path)
        best_expiry, best_status = run_ocr_all_variants(img_color_full)
        if best_expiry:
            detection_method = "fallback_full_image"

    if best_expiry:
        return JSONResponse({
            "success": True,
            "expiry_date": best_expiry,
            "status": best_status,
            "detection_method": detection_method,
            "message": f"Expiry date found: {best_expiry} — {best_status}"
        })

    return JSONResponse({
        "success": False,
        "expiry_date": None,
        "status": "Could not extract expiry date",
        "detection_method": detection_method,
        "message": "No expiry date found. Ensure expiry text is clearly visible in good lighting."
    })