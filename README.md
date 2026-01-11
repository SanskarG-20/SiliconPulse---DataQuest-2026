# SiliconPulse

Strategic Intelligence Platform - Real-time semiconductor and tech ecosystem monitoring.

## Project Structure

```
DATAQUEST/
├── frontend/          # React + TypeScript + Vite UI
├── backend/           # FastAPI + Pathway backend
├── data/              # Data files (stream.jsonl)
└── docs/              # Documentation
```

## Prerequisites

- **Node.js** 18+ and npm
- **Python** 3.10+
- **pip** and **virtualenv** (recommended)

## Quick Start

### Backend Setup

1. Navigate to backend directory:
   ```bash
   cd backend
   ```

2. Create virtual environment (recommended):
   ```bash
   python -m venv venv
   ```

3. Activate virtual environment:
   - **Windows (PowerShell):**
     ```powershell
     .\venv\Scripts\Activate.ps1
     ```
   - **Windows (CMD):**
     ```cmd
     venv\Scripts\activate.bat
     ```
   - **Linux/Mac:**
     ```bash
     source venv/bin/activate
     ```

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

5. Create `.env` file in `backend/`:
   ```env
   GEMINI_API_KEY=your_api_key_here
   ```

6. Run backend server:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

   Backend runs at: `http://localhost:8000`
   - API docs: `http://localhost:8000/docs`
   - Health check: `http://localhost:8000/health`

### Frontend Setup

1. Navigate to frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Create `.env` file in `frontend/` (if needed):
   ```env
   VITE_GEMINI_API_KEY=your_api_key_here
   ```

4. Run development server:
   ```bash
   npm run dev
   ```

   Frontend runs at: `http://localhost:3000`

## Development Workflow

### Run Both Services

**Terminal 1 - Backend:**
```bash
cd backend
# Activate venv if using one
uvicorn app.main:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

### Verify Setup

1. Check backend health:
   ```bash
   curl http://localhost:8000/health
   ```

2. Open browser:
   - Frontend: http://localhost:3000
   - Backend API docs: http://localhost:8000/docs

## API Endpoints

- `GET /` - Welcome message
- `GET /health` - Health check
- `GET /docs` - Interactive API documentation (Swagger)
- `GET /redoc` - Alternative API documentation

## Configuration

### Backend Port
Default: `8000`
Change in run command: `--port <port_number>`

### Frontend Port
Default: `3000`
Configured in `frontend/vite.config.ts`

### CORS
Backend CORS is configured for:
- `http://localhost:3000`
- `http://127.0.0.1:3000`

## Troubleshooting

**Backend won't start:**
- Ensure virtual environment is activated
- Check Python version: `python --version` (need 3.10+)
- Verify dependencies: `pip list`

**Frontend won't start:**
- Clear node_modules and reinstall: `rm -rf node_modules && npm install`
- Check Node version: `node --version` (need 18+)

**CORS errors:**
- Verify backend CORS origins match frontend URL
- Check both services are running

**Port already in use:**
- Backend: Change port with `--port <port>` flag
- Frontend: Vite will auto-select next available port

## Production Build

**Frontend:**
```bash
cd frontend
npm run build
```

**Backend:**
```bash
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000
```
