import os
import cv2 as cv
import numpy as np
import pytesseract
import json
import re
from spellchecker import SpellChecker
import textdistance
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
import tempfile

app = FastAPI()

def process_image(image_path):
    image = cv.imread(image_path, cv.IMREAD_GRAYSCALE)
    if image is None:
        return {"error": "Invalid image file"}

    # Preprocess image
    img = cv.bilateralFilter(image, 9, 75, 75)
    thresh = cv.adaptiveThreshold(img, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY, 11, 2)

    # Extract text using OCR
    raw_text = pytesseract.image_to_string(thresh)

    # Patterns for extracting values
    patterns = {
        "calories": r"(?i)(?:calories|cal|energy|total energy|calories per serving)[\s:]*([\d]+)\s*(?:kcal|cal)?",
        "sugar": r"(?i)(?:sugar|sugars|total sugars)[\s:]*([\d]+)\s*(?:g|mg)?",
        "sodium": r"(?i)(?:sodium|sod|na)[\s:]*([\d]+)\s*(?:mg|g)?"
    }

    unit_mapping = {"calories": "kcal", "sugar": "g", "sodium": "mg"}

    def extract_nutrition(text):
        extracted = {}
        for key, pattern in patterns.items():
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                value = match.group(1)
                extracted[key] = f"{value} {unit_mapping[key]}"
        return extracted

    nutrition_data = extract_nutrition(raw_text)
    return nutrition_data

@app.post("/upload/")
async def upload_image(file: UploadFile = File(...)):
    # Save temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_file:
        temp_file.write(await file.read())
        temp_path = temp_file.name

    # Process the image
    result = process_image(temp_path)

    # Clean up
    os.remove(temp_path)

    return JSONResponse(content=result)
