# import os
# import cv2 as cv
# import numpy as np
# import pytesseract
# import json
# import re
# from spellchecker import SpellChecker
# import textdistance
# from fastapi import FastAPI, File, UploadFile, HTTPException


# app = FastAPI()

# def resize_for_display(image, max_size=1000):
#     (h, w) = image.shape[:2]
#     scale = max_size / max(h, w)  # Scale based on the longer side
#     resized = cv.resize(image, (int(w * scale), int(h * scale)), interpolation=cv.INTER_AREA)
#     return resized

# # Load and preprocess image
# img_path = 'photos/nutritional_labels/23.jpg'
# print(f"Loading image from {img_path}")
# image = cv.imread(img_path, cv.IMREAD_GRAYSCALE)
# assert image is not None, f"File could not be read, check with os.path.exists({img_path})"


# def grayscale_image(image):
#     img_path = image

# img = resize_for_display(image)

# # Apply better preprocessing
# img = cv.bilateralFilter(img, 9, 75, 75)  # Preserves text edges
# thresh = cv.adaptiveThreshold(img, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY, 11, 2)

# # Display preprocessed image (optional)
# cv.imshow('Preprocessed Image', thresh)
# cv.waitKey(0)
# cv.destroyAllWindows()

# # Extract text
# print("Extracting text using OCR...")
# raw_text = pytesseract.image_to_string(thresh)  # Original OCR extraction
# print("Raw OCR Text:\n", raw_text)

# # Define expected nutrition keywords
# expected_words = ["calories", "sugar", "sodium", "sugars", "cal", "sod", "mg", "g"]

# # Patterns for extracting values
# patterns = {
#     "calories": r"(?i)(?:calories|cal|energy|total energy|calories per serving)[\s:]*([\d]+)\s*(?:kcal|cal)?",
#     # "calories_from_fat": r"(?i)(?:calories from fat|cal from fat)[\s:]*([\d]+)\s*(?:kcal|cal)?",
#     "sugar": r"(?i)(?:sugar|sugars|total sugars)[\s:]*([\d]+)\s*(?:g|mg)?",
#     "sodium": r"(?i)(?:sodium|sod|na)[\s:]*([\d]+)\s*(?:mg|g)?"
# }

# unit_mapping = {
#     "calories": "kcal",
#     # "calories_from_fat": "kcal",
#     "sugar": "g",
#     "sodium": "mg"
# }

# # Extract values from raw OCR first
# nutrition_data = {}

# def extract_nutrition(text):
#     extracted = {}
#     for key, pattern in patterns.items():
#         match = re.search(pattern, text, re.IGNORECASE)
#         if match:
#             value = match.group(1)  # Preserve the original numeric format
#             extracted[key] = f"{value} {unit_mapping[key]}"
#     return extracted

# # Step 1: Extract from raw OCR text
# nutrition_data.update(extract_nutrition(raw_text))

# # Step 2: Process corrected text only for missing values
# spell = SpellChecker()
# words = raw_text.split()
# corrected_words = []

# for word in words:
#     if word.isdigit() or word in expected_words:  # Preserve numeric values
#         corrected_words.append(word)
#     else:
#         corrected_word = spell.correction(word)
#         corrected_words.append(corrected_word if corrected_word else word)

# corrected_text = " ".join(corrected_words)
# print("\nCorrected OCR Text:\n", corrected_text)

# def fuzzy_match(word, choices, threshold=0.8):
#     best_match = max(choices, key=lambda x: textdistance.Jaccard().similarity(word, x))
#     return best_match if textdistance.Jaccard().similarity(word, best_match) >= threshold else word

# corrected_text = " ".join([fuzzy_match(word, expected_words) for word in corrected_text.split()])

# # Step 3: Extract from corrected text only if missing in raw extraction
# corrected_nutrition = extract_nutrition(corrected_text)
# for key, value in corrected_nutrition.items():
#     if key not in nutrition_data:  # Only add missing elements
#         nutrition_data[key] = value

# # Export as JSON
# with open("nutrition_data.json", "w") as json_file:
#     json.dump(nutrition_data, json_file, indent=4)

# print("\nExtracted Nutrition Data:", nutrition_data)
