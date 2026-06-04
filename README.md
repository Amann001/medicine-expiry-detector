# AI-Powered Medicine Expiry Detection

## Overview

This project aims to automatically detect and extract medicine expiry information from medicine package images using Computer Vision and OCR.

## Features

* Custom medicine image dataset collection
* Manual annotation using Roboflow
* YOLOv8-based expiry region detection
* OpenCV image preprocessing
* OCR-based text extraction
* Expiry date identification pipeline

## Tech Stack

* Python
* YOLOv8
* OpenCV
* EasyOCR
* Roboflow
* Kaggle

## Current Pipeline

Image → YOLO Detection → Expiry Region Crop → OCR → Expiry Date Extraction

## Dataset

The model was trained on a custom dataset consisting of manually collected and annotated medicine package images.

## Future Improvements

* PaddleOCR integration
* Gemini Vision integration
* FastAPI backend
* React frontend
* Real-time mobile camera support
* Inventory management integration
