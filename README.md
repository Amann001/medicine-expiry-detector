# MedScan — AI Medicine Expiry Detector

> Scan any medicine photo. Get the expiry date instantly.

![Python](https://img.shields.io/badge/Python-3.10-blue?style=flat-square)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688?style=flat-square)
![YOLOv8](https://img.shields.io/badge/YOLOv8-Object%20Detection-FF4B4B?style=flat-square)
![EasyOCR](https://img.shields.io/badge/EasyOCR-Text%20Extraction-4CAF50?style=flat-square)
![Streamlit](https://img.shields.io/badge/Streamlit-Frontend-FF4B4B?style=flat-square)

**[Live Demo](#-coming-soon)** · **[API Docs](#-coming-soon)** · **[GitHub](https://github.com/Amann001/medicine-expiry-detector)**

---

## The Problem

Millions of patients in India — especially elderly and semi-literate individuals — unknowingly consume expired medicines. No accessible tool exists that works directly from a phone camera without any typing.

MedScan solves this with a zero-typing AI pipeline that reads expiry dates from real Indian medicine packaging in any orientation.

---

## What Makes This Project Different

### Custom-Trained YOLOv8 Object Detector
- Built and annotated a custom dataset of **50+ real Indian medicine images** from scratch using Roboflow
- Trained on **Kaggle T4 GPU** — single class `expiry_region` for maximum precision
- Diagnosed and fixed an undertrained multi-class model by simplifying to one class — a real debugging decision that improved mAP50 to **0.995**

### 28-Attempt OCR Pipeline
Most OCR demos use clean, flat images. Medicine packaging is curved, foil-stamped, and photographed at random angles. MedScan uses:

```
4 rotations  ×  7 preprocessing variants  =  28 OCR attempts per image
```

| Variant | Problem it solves |
|---|---|
| CLAHE enhancement | Dark / low-contrast stamped labels |
| Adaptive thresholding | Foil blister strips |
| Sharpening filter | Blurry phone camera shots |
| NL Means denoising | Grainy / noisy images |
| Otsu thresholding | Printed text on white boxes |
| Inverted image | White text on dark backgrounds |

### 3-Strategy Expiry Extraction Engine
A single regex fails on Indian medicine labels which use 10+ date formats. Built a 3-pass system:

- **Pass 1** — Regex on full joined OCR text (14 keyword patterns)
- **Pass 2** — Token-window search for split OCR lines
- **Pass 3** — Keyword position search as a last resort

Handles every real-world format: `EXP. 01/2026` · `Expiry Date JUL.2028` · `EXP SEP 2027` · `USE BEFORE MAR 2027`

### Production-Grade FastAPI Backend
- REST API with auto-generated Swagger documentation
- YOLO → OCR fallback chain: if detection fails, retries on full image automatically
- Multipart file upload, health endpoint, clean JSON responses

---

## System Architecture

```
Phone Camera / Image Upload
         │
         ▼
  ┌─────────────┐
  │  YOLOv8n   │  ──── Detects expiry region bounding box
  └─────────────┘
         │
         ▼
  ┌──────────────────────────────────┐
  │  OpenCV Preprocessing Pipeline  │
  │  4 rotations × 7 variants       │
  │  = 28 OCR attempts              │
  └──────────────────────────────────┘
         │
         ▼
  ┌─────────────┐
  │   EasyOCR  │  ──── Extracts raw text from image
  └─────────────┘
         │
         ▼
  ┌───────────────────────────┐
  │  Expiry Extraction Engine │
  │  Pass 1: Regex patterns   │
  │  Pass 2: Token window     │
  │  Pass 3: Position search  │
  └───────────────────────────┘
         │
         ▼
  JSON Response  →  Streamlit UI
  { expiry_date, status, detection_method }
```

---

## Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| Object Detection | YOLOv8n | Custom-trained label region detector |
| OCR | EasyOCR | Real-world text extraction |
| Image Processing | OpenCV 4.13 | 7 preprocessing variants |
| Backend | FastAPI + Uvicorn | Async REST API, Swagger docs |
| Frontend | Streamlit | Healthcare-grade UI |
| Training | Kaggle T4 GPU | Free GPU training |
| Annotation | Roboflow | Dataset creation + 3× augmentation |

---

## API

### `POST /detect-expiry`

Upload any medicine image, receive the expiry date.

```json
{
  "success": true,
  "expiry_date": "JUL 2028",
  "status": "VALID (754 days remaining)",
  "detection_method": "yolo",
  "message": "Expiry date found: JUL 2028 — VALID (754 days remaining)"
}
```

### `GET /health`
```json
{ "status": "healthy" }
```

---

## Run Locally

```bash
git clone https://github.com/yourusername/medicine-expiry-detector
cd medicine-expiry-detector
pip install -r requirements.txt

# Terminal 1 — Backend
uvicorn backend.app:app --reload
# Swagger UI → http://127.0.0.1:8000/docs

# Terminal 2 — Frontend
streamlit run frontend/streamlit_app.py
# UI → http://localhost:8501
```

---

## Project Structure

```
medicine-expiry-detector/
├── backend/
│   ├── app.py                  ← FastAPI application
│   ├── models/best.pt          ← Trained YOLOv8n weights
│   └── ocr/
│       ├── find_expiry.py      ← 3-strategy extraction engine
│       └── medicine_pipeline.py
├── frontend/
│   └── streamlit_app.py        ← Streamlit UI
├── dataset/                    ← Training images + annotations
├── notebooks/                  ← Kaggle training notebook
└── requirements.txt
```

---

## Key Engineering Decisions

**Why single class instead of 3?**
Initial training with `drug_name`, `expiry_region`, `medicine_package` caused zero detections — dataset too small for multi-class learning. Refactored to single class, mAP50 reached 0.995.

**Why 28 OCR attempts?**
A single preprocessing pass fails on 60%+ of real-world medicine photos due to curved surfaces, glare, and random orientations. 28 attempts costs negligible latency but dramatically improves success rate.

**Why build a custom dataset?**
No public dataset exists for Indian medicine packaging with expiry annotations. Self-collected and crowd-sourced 69 images — explicitly cited as a research contribution.

**Why FastAPI over Flask?**
Async handling, auto Swagger docs, Pydantic validation, and production-ready ASGI server out of the box.

---

## Future Scope

- Drug interaction checking via OpenFDA API
- Hindi/regional language support via AI4Bharat
- Android APK via ONNX offline deployment
- WhatsApp bot interface — send photo, receive warning

---

## About

Built by **Amann001** — 2nd Year CS Student

End-to-end project built from scratch over 2 weeks — dataset collection, model training, backend, frontend, and deployment.

---

*If this project helped or impressed you, please ⭐ the repo*