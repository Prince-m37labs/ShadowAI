#!/bin/bash

echo "🚀 Starting AI Development Assistant on Replit..."

# Set environment variables for Replit
export NODE_ENV="production"
export BACKEND_URL="https://$REPL_SLUG.$REPL_OWNER.repl.co:8000"

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

# Start the FastAPI backend on port 8000
echo "🐍 Starting FastAPI backend on port 8000..."
cd ../backend
python -m uvicorn main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 5

# Start the Next.js frontend on the main port
echo "⚛️ Starting Next.js frontend on main port..."
cd ../frontend
PORT=443 npm start &
FRONTEND_PID=$!

echo "✅ Both servers are starting up..."
echo "🌐 Frontend will be available at: https://$REPL_SLUG.$REPL_OWNER.repl.co"
echo "🔧 Backend API will be available at: $BACKEND_URL"

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID 