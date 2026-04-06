from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import io
import os
from PIL import Image
from app.model import predict_demographics
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Age & Gender Prediction API", 
    description="MLOps Pipeline - Multi-model Prediction Server",
    version="2.0.0"
)

static_dir = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/")
def read_root():
    return FileResponse(os.path.join(static_dir, "index.html"))

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload an image.")

    try:
        content = await file.read()
        image = Image.open(io.BytesIO(content)).convert("RGB")
        logger.info(f"Received image: {file.filename}, size: {image.size}")
        
        demographics = predict_demographics(image)
        
        return JSONResponse(content={
            "filename": file.filename, 
            "predicted_age_range": demographics["age"], 
            "predicted_gender": demographics["gender"],
            "status": "success"
        })
    except Exception as e:
        logger.error(f"Prediction failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")
