# AI Development Assistant

A comprehensive AI-powered development assistant that combines a modern Next.js frontend with a FastAPI backend to provide intelligent code refactoring, Q&A capabilities, Git operations, and advanced screen assistance features.

## 🚀 Features

### Frontend (Next.js)
- **Modern UI**: Built with Next.js 15, React 19, and Tailwind CSS
- **Interactive Dashboard**: Real-time code analysis and suggestions
- **Code Explorer**: Browse and analyze code repositories
- **Git Operations**: Manage Git workflows with AI assistance
- **Refactoring Tools**: AI-powered code refactoring interface
- **Screen Assistant**: Advanced screen capture and analysis system
- **Markdown Support**: Rich text rendering with syntax highlighting
- **Responsive Design**: Optimized for desktop and mobile devices

### Backend (FastAPI)
- **AI Integration**: Claude API integration for intelligent responses
- **Code Refactoring**: Advanced code analysis and refactoring engine
- **Q&A System**: Intelligent question-answering about code
- **Git Operations**: Automated Git workflow management
- **Screen Assistance**: Multi-frame screen capture with OCR analysis
- **History Management**: Track and manage user interactions
- **MongoDB Integration**: Persistent data storage
- **CORS Support**: Cross-origin resource sharing for frontend integration

## 🛠 Tech Stack

### Frontend
- **Framework**: Next.js 15.3.3
- **Language**: TypeScript 5
- **Styling**: Tailwind CSS 4
- **UI Components**: Framer Motion
- **Markdown**: React Markdown with syntax highlighting
- **Security**: DOMPurify for XSS protection
- **Screen Capture**: HTML5 Canvas API with MediaDevices

### Backend
- **Framework**: FastAPI
- **Language**: Python
- **Database**: MongoDB with PyMongo
- **AI**: Claude API (Anthropic)
- **Computer Vision**: OpenCV, PaddleOCR, Tesseract OCR
- **Image Processing**: Pillow, NumPy
- **Server**: Uvicorn

## 📦 Installation

### Prerequisites
- Node.js 18+ and npm/yarn
- Python 3.8+
- MongoDB instance
- Claude API key
- Tesseract OCR (for screen analysis)

### Backend Setup

1. **Navigate to backend directory**:
   ```bash
   cd backend
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Install Tesseract OCR** (for screen analysis):
   ```bash
   # macOS
   brew install tesseract
   
   # Ubuntu/Debian
   sudo apt-get install tesseract-ocr
   
   # Windows
   # Download from https://github.com/UB-Mannheim/tesseract/wiki
   ```

5. **Set up environment variables**:
   Create a `.env` file in the `backend` directory with the following variables. This file should **not** be committed to version control.

   ```env
   # Your Anthropic/Claude API key
   ANTHROPIC_API_KEY=your_claode_api_key_here

   # Your MongoDB connection string
   MONGODB_URI=your_mongodb_connection_string

   # Comma-separated list of allowed frontend origins for CORS
   # For local development, this should be your Next.js dev server
   CORS_ORIGINS=http://localhost:3000
   ```

6. **Run the backend server**:
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

### Frontend Setup

1. **Navigate to frontend directory**:
   ```bash
   cd frontend
   ```

2. **Install dependencies**:
   ```bash
   npm install
   # or
   yarn install
   ```

3. **Set up environment variables**:
   Create a `.env.local` file in the `frontend` directory. This file should **not** be committed to version control.

   ```env
   # Base URL for the backend API
   # For local development, this points to your local FastAPI server
   NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
   ```

4. **Run the development server**:
   ```bash
   npm run dev
   # or
   yarn dev
   ```

5. **Open your browser**:
   Navigate to [http://localhost:3000](http://localhost:3000)

## 🔥 Quick Start with `start.sh`

To start both the backend (FastAPI) and frontend (Next.js) servers at once, use the provided `start.sh` script:

```bash
./start.sh
```

- This script will:
  - Activate the Python virtual environment and start the FastAPI backend on port 8000
  - Start the Next.js frontend on port 3000
  - Automatically stop both servers when you press Ctrl+C

> **Note:**
> - Make sure you have run all installation steps for both backend and frontend before using this script.
> - On macOS/Linux, you may need to make the script executable: `chmod +x start.sh`

## 🏗 Project Structure

```
├── backend/
│   ├── main.py              # FastAPI application entry point
│   ├── db.py                # MongoDB database configuration
│   ├── simplify.py          # Code simplification utilities
│   ├── requirements.txt     # Python dependencies
│   ├── routes/              # API route modules
│   │   ├── refactor.py      # Code refactoring endpoints
│   │   ├── ask_qa.py        # Q&A system endpoints
│   │   ├── gitops.py        # Git operations endpoints
│   │   ├── screen_assist.py # Screen assistance endpoints
│   │   └── history.py       # History management endpoints
│   └── venv/                # Python virtual environment
├── frontend/
│   ├── src/
│   │   ├── app/             # Next.js app directory
│   │   │   ├── dashboard/   # Dashboard pages
│   │   │   │   ├── ask-qa/  # Q&A interface
│   │   │   │   ├── refactor/ # Refactoring interface
│   │   │   │   ├── gitops/  # Git operations interface
│   │   │   │   └── screen-assist/ # Screen assistant interface
│   │   │   ├── explorer/    # Code explorer page
│   │   │   ├── components/  # Shared components
│   │   │   ├── layout.tsx   # Root layout
│   │   │   ├── page.tsx     # Home page
│   │   │   └── globals.css  # Global styles
│   ├── public/              # Static assets
│   ├── package.json         # Node.js dependencies
│   └── next.config.ts       # Next.js configuration
├── .gitignore              # Git ignore rules
└── README.md               # This file
```

## 🔧 API Endpoints

### Core Endpoints
- `GET /modules` - Get available modules
- `POST /refactor/` - Code refactoring
- `POST /qa/` - Question answering
- `POST /gitops/` - Git operations
- `POST /screen-assist/` - Screen assistance with OCR
- `GET /history/` - Get interaction history
- `POST /history/` - Save interaction

## 🖥️ Screen Assistant Features

The Screen Assistant is a sophisticated tool that provides:

### **Multi-Frame Capture**
- Captures 5 frames at 2-second intervals
- Automatic screen sharing detection
- Canvas-based image processing
- High-quality PNG export

### **Advanced OCR Processing**
- **Tesseract OCR**: Primary text extraction
- **PaddleOCR**: Alternative OCR engine
- **Image Preprocessing**: 
  - Adaptive thresholding for varying brightness
  - Morphological operations for text clarity
  - Bilateral filtering for noise reduction
  - CLAHE (Contrast Limited Adaptive Histogram Equalization)

### **AI-Powered Analysis**
- Sends processed screenshots to Claude API
- Context-aware code analysis
- Bug detection and suggestions
- Code improvement recommendations

### **User Experience**
- Real-time progress tracking
- Error handling for screen sharing permissions
- Cross-browser compatibility
- Automatic session management

## 🚀 Development

### Backend Development
```bash
cd backend
source venv/bin/activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Development
```bash
cd frontend
npm run dev
```

### Building for Production

**Frontend**:
```bash
cd frontend
npm run build
npm start
```

**Backend**:
```bash
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000
```

## 🔒 Environment Variables

### Backend (`backend/.env`)
Create a `.env` file in the `backend` directory.

```env
# Your Anthropic/Claude API key
ANTHROPIC_API_KEY=your_claude_api_key_here

# Your MongoDB connection string
MONGODB_URI=your_mongodb_connection_string

# For local development, allow requests from the Next.js dev server
CORS_ORIGINS=http://localhost:3000
```

### Frontend (`frontend/.env.local`)
Create a `.env.local` file in the `frontend` directory.

```env
# For local development, point to the local FastAPI server
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

## 📝 Usage

1. **Start both servers** (backend on port 8000, frontend on port 3000)
2. **Open the application** in your browser at `http://localhost:3000`
3. **Navigate through different modules**:
   - **Dashboard**: Overview and quick actions
   - **Explorer**: Browse and analyze code
   - **GitOps**: Manage Git workflows
   - **Refactor**: AI-powered code refactoring
   - **Screen Assistant**: Capture and analyze code screenshots

### Screen Assistant Workflow
1. Click "Start Screen Capture"
2. Select the screen/window to share
3. Bring your code editor to the front
4. System captures 5 frames automatically
5. AI analyzes the code and provides insights
6. View detailed analysis and recommendations

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

If you encounter any issues or have questions:
1. Check the documentation
2. Search existing issues
3. Create a new issue with detailed information

## 🔮 Roadmap

- [ ] Enhanced OCR accuracy for different code themes
- [ ] Real-time screen analysis streaming
- [ ] Integration with more AI models
- [ ] Advanced Git workflow automation
- [ ] Real-time collaboration features
- [ ] Mobile app development
- [ ] Plugin system for extensibility
- [ ] Code snippet extraction and sharing

## ☁️ Deployment

This project is designed to be deployed with a Vercel frontend and a Render backend.

### 1. Backend (FastAPI on Render)

1.  **Push to GitHub**: Ensure your latest backend code is on GitHub.
2.  **Create a Web Service on Render**:
    *   Connect your GitHub repository.
    *   Set the **Root Directory** to `backend`.
    *   **Build Command**: `pip install -r requirements.txt`
    *   **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
3.  **Add Environment Variables on Render**:
    *   `ANTHROPIC_API_KEY`: Your Claude API key.
    *   `MONGODB_URI`: Your MongoDB connection string.
    *   `PYTHON_VERSION`: A specific Python version (e.g., `3.11.0`).
    *   `CORS_ORIGINS`: Your Vercel frontend URL (e.g., `https://your-frontend.vercel.app`).

### 2. Frontend (Next.js on Vercel)

1.  **Push to GitHub**: Ensure your latest frontend code is on GitHub.
2.  **Create a Project on Vercel**:
    *   Connect your GitHub repository.
    *   The build settings are typically detected automatically.
3.  **Add Environment Variable on Vercel**:
    *   `NEXT_PUBLIC_API_BASE_URL`: Your deployed Render backend URL (e.g., `https://your-backend.onrender.com`).

Once both are deployed, the frontend on Vercel will make API calls to your backend on Render.