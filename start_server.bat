@echo off
echo ========================================
echo Starting FastAPI Server...
echo ========================================
echo.
echo The server will run on http://127.0.0.1:8000
echo Open another terminal and run: python ws_test.py
echo.
echo Press CTRL+C to stop the server
echo ========================================
echo.
uvicorn app.main:app --reload
