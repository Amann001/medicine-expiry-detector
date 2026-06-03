# Medicine Expiry Detector

AI-powered medicine expiry detection system using YOLOv8 and OCR.

## Current Progress

### Completed
- Custom medicine dataset collection
- Image annotation using Roboflow
- YOLOv8 training pipeline setup
- Baseline model training on Kaggle
- Dataset evaluation

### Findings
- Medicine package detection works reasonably well
- Small text regions (drug name and expiry region) are difficult to detect reliably
- Project architecture updated to YOLO + OCR approach

### Next Steps
- Integrate EasyOCR
- Extract expiry dates
- Build Streamlit web application

## Tech Stack

- Python
- YOLOv8
- EasyOCR
- OpenCV
- Streamlit
- Roboflow
- Kaggle