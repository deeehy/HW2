# 최적화된 Single-stage 빌드
FROM python:3.10-slim

# Python 및 MLOps 최적화 환경 변수 설정
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    # Hugging Face 모델 다운로드 및 캐시 경로 명시
    HF_HOME=/app/.cache/huggingface

# 1. 보안을 위한 Non-root 시스템 유저 추가 (중요 MLOps 보안 원칙)
RUN addgroup --system appgroup && adduser --system --group appuser

WORKDIR /app

# 2. 필수 시스템 패키지 설치 및 패키지 리스트 삭제를 통한 크기 최소화
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 3. 레이어 캐싱을 극대화하기 위해 종속성 파일만 먼저 복사
COPY requirements.txt .

# 4. pip 캐시를 비활성화(--no-cache-dir)하여 이미지 경량화 달성
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 5. 캐시 및 앱 디렉토리의 소유권을 appuser로 변경
RUN mkdir -p $HF_HOME && chown -R appuser:appgroup /app

# 6. 이후 모든 명령은 권한이 제한된 appuser로 실행됨
USER appuser

# 7. 빌드 과정에서 모델을 미리 다운로드 (Docker Image Layer에 캐싱됨)
# 이를 통해 컨테이너 시동(Cold Start)시 모델 다운로드로 인한 느린 응답 시간(지연)을 방지
RUN python -c "from transformers import pipeline; pipeline('image-classification', model='nateraw/vit-age-classifier')"

# 8. 변경이 잦은 애플리케이션 코드를 맨 마지막에 복사하여 앞의 레이어 캐시를 최대한 보호
COPY --chown=appuser:appgroup ./app ./app

# 외부 노출 포트 명시
EXPOSE 8000

# 애플리케이션 서버 실행
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
