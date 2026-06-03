# Project Log

## Day 1

### Dataset Work
- Collected medicine images manually
- Annotated images in Roboflow
- Exported YOLOv8 datasets

### Training
- Trained baseline model on phone dataset
- Merged annotated datasets
- Trained merged dataset model

### Results
- medicine_package learned reasonably well
- drug_name and expiry_region require a different approach

### Architectural Decision
Use:
YOLO → Medicine Package Detection

OCR → Drug Name + Expiry Date Extraction

instead of relying on YOLO for tiny text regions.