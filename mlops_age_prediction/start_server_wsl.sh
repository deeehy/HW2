#!/bin/bash
echo "🚀 [WSL 환경] MLOps 나이 예측 API 서버 가동을 시작합니다..."

# python3-venv가 없을 경우를 대비해 가상환경 대신 로컬 유저 영역에 설치하는 방법도 있지만, 깔끔하게 venv를 씁니다.
python3 -m venv .venv

echo "📦 종속성을 설치하는 중입니다..."
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo "🌐 서버를 띄우는 중입니다 (종료: Ctrl+C)..."
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
