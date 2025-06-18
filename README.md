# AI Development Assistant

A comprehensive AI-powered development assistant that combines a modern Next.js frontend with a FastAPI backend to provide intelligent code refactoring, Q&A capabilities, Git operations, and screen assistance features.

## 🚀 Features

### Frontend (Next.js)
- **Modern UI**: Built with Next.js 15, React 19, and Tailwind CSS
- **Interactive Dashboard**: Real-time code analysis and suggestions
- **Code Explorer**: Browse and analyze code repositories
- **Git Operations**: Manage Git workflows with AI assistance
- **Refactoring Tools**: AI-powered code refactoring interface
- **Screen Assistant**: Visual code assistance and analysis
- **Markdown Support**: Rich text rendering with syntax highlighting
- **Responsive Design**: Optimized for desktop and mobile devices

### Backend (FastAPI)
- **AI Integration**: Claude API integration for intelligent responses
- **Code Refactoring**: Advanced code analysis and refactoring engine
- **Q&A System**: Intelligent question-answering about code
- **Git Operations**: Automated Git workflow management
- **Screen Assistance**: Computer vision and OCR capabilities
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

### Backend
- **Framework**: FastAPI
- **Language**: Python
- **Database**: MongoDB with PyMongo
- **AI**: Claude API (Anthropic)
- **Computer Vision**: OpenCV, PaddleOCR
- **Image Processing**: Pillow, NumPy
- **Server**: Uvicorn

## 📦 Installation

### Prerequisites
- Node.js 18+ and npm/yarn
- Python 3.8+
- MongoDB instance
- Claude API key

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

4. **Set up environment variables**:
   Create a `.env` file in the backend directory:
   ```env
   ANTHROPIC_API_KEY=your_claude_api_key_here
   MONGODB_URI=your_mongodb_connection_string
   ```

5. **Run the backend server**:
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

3. **Run the development server**:
   ```bash
   npm run dev
   # or
   yarn dev
   ```

4. **Open your browser**:
   Navigate to [http://localhost:3000](http://localhost:3000)

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
│   │   │   ├── dashboard/   # Dashboard page
│   │   │   ├── explorer/    # Code explorer page
│   │   │   ├── gitops/      # Git operations page
│   │   │   ├── refactor/    # Refactoring page
│   │   │   ├── screen-assist/ # Screen assistant page
│   │   │   ├── layout.tsx   # Root layout
│   │   │   ├── page.tsx     # Home page
│   │   │   └── globals.css  # Global styles
│   │   └── components/      # React components
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
- `POST /screen-assist/` - Screen assistance
- `GET /history/` - Get interaction history
- `POST /history/` - Save interaction

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

### Backend (.env)
```env
ANTHROPIC_API_KEY=your_claude_api_key_here
MONGODB_URI=mongodb://localhost:27017/ai_assistant
```

### Frontend (.env.local)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 📝 Usage

1. **Start both servers** (backend on port 8000, frontend on port 3000)
2. **Open the application** in your browser at `http://localhost:3000`
3. **Navigate through different modules**:
   - Dashboard: Overview and quick actions
   - Explorer: Browse and analyze code
   - GitOps: Manage Git workflows
   - Refactor: AI-powered code refactoring
   - Screen Assistant: Visual code assistance

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

- [ ] Enhanced code analysis capabilities
- [ ] Integration with more AI models
- [ ] Advanced Git workflow automation
- [ ] Real-time collaboration features
- [ ] Mobile app development
- [ ] Plugin system for extensibility 