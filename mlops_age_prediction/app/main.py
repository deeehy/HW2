from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import io
import os
from PIL import Image
from app.model import predict_age
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Age Prediction API", 
    description="MLOps Pipeline - Lightweight Age Prediction Server",
    version="1.0.0"
)

static_dir = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/")
def read_root():
    return FileResponse(os.path.join(static_dir, "index.html"))

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    # 1. 파일 확장자/타입 검증
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload an image.")

    try:
        # 2. 이미지 읽기
        content = await file.read()
        image = Image.open(io.BytesIO(content)).convert("RGB")
        logger.info(f"Received image: {file.filename}, size: {image.size}")
        
        # 3. 모델 예측 (추론)
        predicted_age_range = predict_age(image)
        
        # 4. 결과 반환
        return JSONResponse(content={
            "filename": file.filename, 
            "predicted_age_range": predicted_age_range, 
            "status": "success"
        })
    except Exception as e:
        logger.error(f"Prediction failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")
