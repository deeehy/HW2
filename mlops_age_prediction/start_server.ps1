<#
.SYNOPSIS
    가상환경을 생성하고 MLOps 파이프라인 개발 환경을 세팅합니다.
#>

$EnvName = ".venv"

Write-Host "1. 가상환경 생성 중 ($EnvName)..." -ForegroundColor Cyan
python -m venv $EnvName

Write-Host "2. 종속성 설치 중..." -ForegroundColor Cyan
& ".\$EnvName\Scripts\pip.exe" install -r requirements.txt

Write-Host "3. FastAPI 서버 시작 중..." -ForegroundColor Green
Write-Host "종료하려면 Ctrl+C를 누르세요." -ForegroundColor Yellow
& ".\$EnvName\Scripts\python.exe" -m uvicorn app.main:app --reload
