from PIL import Image
from transformers import pipeline
import logging
import os

logger = logging.getLogger(__name__)

# Hugging Face의 가벼운 ViT 기반 나이 예측 모델 (ViT Age Classifier)
# 모델 크기가 약 300MB 정도로 비교적 가벼우며 빠릅니다.
MODEL_NAME = "nateraw/vit-age-classifier"

# 전역 변수로 모델 파이프라인 초기화 (서버 구동 시 1회 메모리 로드)
try:
    logger.info(f"Loading '{MODEL_NAME}' model. This may take a moment downlading weights on first run...")
    # 파이프라인 초기화 (CPU 사용)
    age_classifier = pipeline("image-classification", model=MODEL_NAME)
    logger.info("Model loaded successfully.")
except Exception as e:
    logger.error(f"Failed to load model: {e}")
    age_classifier = None

def predict_age(image: Image.Image) -> str:
    """
    이미지를 받아 모델을 통해 예측된 나이대 문자열(예: '20-29')을 반환합니다.
    """
    if age_classifier is None:
        raise RuntimeError("Model is not initialized.")
    
    # 모델 추론 진행
    results = age_classifier(image)
    
    # 확률(score)이 가장 높은 라벨 반환
    if results:
        best_match = results[0]
        # best_match['label']은 '0-2', '3-9', '10-19', '20-29' 형태로 반환됨
        return best_match['label']
    
    return "Unknown"
