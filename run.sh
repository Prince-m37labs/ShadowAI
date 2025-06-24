#!/bin/bash

echo "🚀 Starting AI Development Assistant on Replit..."

# Install Python dependencies
echo "📦 Installing Python dependencies..."
cd backend
pip install -r requirements.txt

# Install Node.js dependencies
echo "📦 Installing Node.js dependencies..."
cd ../frontend
npm install

# Build the Next.js frontend
echo "🔨 Building Next.js frontend..."
npm run build

# Start the FastAPI backend
echo "🐍 Starting FastAPI backend on port 8000..."
cd ../backend
python -m uvicorn main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Start the Next.js frontend
echo "⚛️ Starting Next.js frontend on port 3000..."
cd ../frontend
npm start &
FRONTEND_PID=$!

echo "✅ Both servers are starting up..."
echo "🌐 Frontend will be available at: https://$REPL_SLUG.$REPL_OWNER.repl.co"
echo "🔧 Backend API will be available at: https://$REPL_SLUG.$REPL_OWNER.repl.co:8000"

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID 