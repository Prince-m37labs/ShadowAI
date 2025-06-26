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

# Start the FastAPI backend on port 8000
echo "🐍 Starting FastAPI backend on port 8000..."
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

# Install Node.js dependencies
echo "📦 Installing Node.js dependencies..."
cd ../frontend

# Fix the postcss configuration
echo "🔧 Fixing postcss configuration..."
cat > postcss.config.mjs << 'EOL'
export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
EOL

# Create a basic tailwind config if it doesn't exist
if [ ! -f "tailwind.config.js" ]; then
    echo "🔧 Creating tailwind configuration..."
    cat > tailwind.config.js << 'EOL'
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
EOL
fi

# Fix the globals.css file
if [ -f "src/app/globals.css" ]; then
    echo "🔧 Fixing globals.css..."
    sed -i '1s/^@import "tailwindcss";/@tailwind base;\n@tailwind components;\n@tailwind utilities;/' src/app/globals.css
    # Remove the @theme inline block if it exists
    sed -i '/@theme inline/,/}/d' src/app/globals.css
fi

# Update package.json to fix dependencies
echo "🔧 Updating package.json..."
npm uninstall @tailwindcss/postcss
npm install tailwindcss@latest postcss@latest autoprefixer@latest --save-dev

# Check Node.js and npm versions
echo "📋 Node.js version: $(node --version)"
echo "📋 npm version: $(npm --version)"

# Build the Next.js frontend
echo "🔨 Building Next.js frontend..."
npm run build

# Check if build was successful
if [ $? -ne 0 ]; then
    echo "❌ Frontend build failed!"
    echo "Trying development mode instead..."
    npm run dev > frontend.log 2>&1 &
    FRONTEND_PID=$!
else
    echo "✅ Frontend build completed successfully"
    # Start the Next.js frontend on port 3000
    echo "⚛️ Starting Next.js frontend on port 3000..."
    PORT=3000 npm start > frontend.log 2>&1 &
    FRONTEND_PID=$!
fi

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

echo "✅ Both servers are running..."
echo "🌐 Frontend will be available at: https://$REPL_SLUG.$REPL_OWNER.repl.co"
echo "🔧 Backend API will be available at: $BACKEND_URL"

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID 