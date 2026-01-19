# Activate venv and run mock pathway pipeline
Write-Host "🚀 Starting Pathway Pipeline (Mock Mode for Windows)..." -ForegroundColor Cyan
if (Test-Path "venv\Scripts\Activate.ps1") {
    . venv\Scripts\Activate.ps1
    python mock_pathway_pipeline.py
} else {
    Write-Host "❌ Virtual environment not found. Please run setup instructions first." -ForegroundColor Red
}
