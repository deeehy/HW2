import logging
from PIL import Image
from transformers import pipeline

logger = logging.getLogger(__name__)

# Hugging Face 모델 정의
AGE_MODEL_NAME = "nateraw/vit-age-classifier"
GENDER_MODEL_NAME = "rizvandwiki/gender-classification"

try:
    logger.info(f"Loading '{AGE_MODEL_NAME}' and '{GENDER_MODEL_NAME}' models...")
    age_classifier = pipeline("image-classification", model=AGE_MODEL_NAME)
    gender_classifier = pipeline("image-classification", model=GENDER_MODEL_NAME)
    logger.info("Models loaded successfully.")
except Exception as e:
    logger.error(f"Failed to load models: {e}")
    age_classifier = None
    gender_classifier = None

def predict_demographics(image: Image.Image) -> dict:
    if age_classifier is None or gender_classifier is None:
        raise RuntimeError("Models are not initialized.")
    
    # 모델 추론
    age_results = age_classifier(image)
    gender_results = gender_classifier(image)
    
    return {
        "age": age_results[0]['label'] if age_results else "Unknown",
        "gender": gender_results[0]['label'] if gender_results else "Unknown"
    }
