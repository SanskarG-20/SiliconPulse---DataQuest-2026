# Activate venv and run FastAPI backend
Write-Host "🚀 Starting SiliconPulse Backend..." -ForegroundColor Green
if (Test-Path "venv\Scripts\Activate.ps1") {
    . venv\Scripts\Activate.ps1
    uvicorn app.main:app --reload --port 8000
} else {
    Write-Host "❌ Virtual environment not found. Please run setup instructions first." -ForegroundColor Red
}
