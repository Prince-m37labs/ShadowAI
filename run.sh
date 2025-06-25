#!/bin/bash

echo "🚀 Starting AI Development Assistant on Replit..."

# Set environment variables for Replit
export NODE_ENV="production"
export BACKEND_URL="https://$REPL_SLUG.$REPL_OWNER.repl.co:8000"

echo "🔧 Environment variables set:"
echo "  NODE_ENV: $NODE_ENV"
echo "  BACKEND_URL: $BACKEND_URL"
echo "  Current directory: $(pwd)"

# Install Python dependencies
echo "📦 Installing Python dependencies..."
cd backend
pip install -r requirements.txt

# Install Node.js dependencies
echo "📦 Installing Node.js dependencies..."
cd ../frontend
npm install

# Check Node.js and npm versions
echo "📋 Node.js version: $(node --version)"
echo "📋 npm version: $(npm --version)"

# Build the Next.js frontend
echo "🔨 Building Next.js frontend..."
npm run build

# Check if build was successful
if [ $? -ne 0 ]; then
    echo "❌ Frontend build failed!"
    exit 1
fi

echo "✅ Frontend build completed successfully"

# Start the FastAPI backend on port 8000
echo "🐍 Starting FastAPI backend on port 8000..."
cd ../backend
python -m uvicorn main:app --host 0.0.0.0 --port 8000 > backend.log 2>&1 &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 5

# Check if backend is running
if ! kill -0 $BACKEND_PID 2>/dev/null; then
    echo "❌ Backend failed to start!"
    echo "Backend logs:"
    cat backend.log
    exit 1
fi

echo "✅ Backend is running on port 8000"

# Start the Next.js frontend on port 3000 with detailed logging
echo "⚛️ Starting Next.js frontend on port 3000..."
cd ../frontend
echo "Current directory: $(pwd)"
echo "Checking if .next directory exists:"
ls -la .next/ 2>/dev/null || echo "No .next directory found!"

PORT=3000 npm start > frontend.log 2>&1 &
FRONTEND_PID=$!

# Wait a moment for frontend to start
sleep 10

# Check if frontend is running
if ! kill -0 $FRONTEND_PID 2>/dev/null; then
    echo "❌ Frontend failed to start!"
    echo "Frontend logs:"
    cat frontend.log
    exit 1
fi

echo "✅ Frontend is running on port 3000"

# Check what's listening on port 3000
echo "🔍 Checking what's listening on port 3000:"
netstat -tlnp 2>/dev/null | grep :3000 || echo "Nothing found on port 3000"

echo "✅ Both servers are starting up..."
echo "🌐 Frontend will be available at: https://$REPL_SLUG.$REPL_OWNER.repl.co"
echo "🔧 Backend API will be available at: $BACKEND_URL"

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID 