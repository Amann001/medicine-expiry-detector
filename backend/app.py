from fastapi import FastAPI, UploadFile, File

app = FastAPI(
    title="Medicine Expiry Detector API",
    version="1.0.0"
)

@app.get("/")
def home():
    return {
        "message": "Medicine Expiry Detector API is running"
    }

@app.get("/health")
def health():
    return {
        "status": "healthy"
    }

@app.post("/detect-expiry")
async def detect_expiry(file: UploadFile = File(...)):

    save_path = "backend/ocr/uploaded_image.jpeg"

    with open(save_path, "wb") as buffer:
        buffer.write(await file.read())

    return {
        "message": "Image uploaded successfully",
        "saved_to": save_path
    }