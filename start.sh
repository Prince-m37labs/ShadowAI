#!/bin/bash

# Start FastAPI backend
cd backend
source venv/bin/activate
echo "Starting FastAPI backend on http://localhost:8000 ..."
uvicorn main:app --reload &
BACKEND_PID=$!
cd ..

# Start Next.js frontend
cd frontend
echo "Starting Next.js frontend on http://localhost:3000 ..."
npm run dev &
FRONTEND_PID=$!
cd ..

# Wait for both to finish (Ctrl+C to stop)
trap "kill $BACKEND_PID $FRONTEND_PID" EXIT
wait