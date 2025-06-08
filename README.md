# 🧠 ShadowAI – AI-Powered Dev Onboarding & Code Intelligence Assistant

ShadowAI is a full-stack AI assistant designed to help **new developers and interns** quickly get productive with unfamiliar codebases. It combines smart language models, real-time screen awareness, and Git integration to reduce onboarding friction and boost confidence from day one.

---

## 🚀 Features

### ✅ Code Intelligence & Refactoring
- Upload or paste any code and receive **clean, modern refactors**
- Supports Groq-hosted models like `LLaMA3`, `Mixtral`, or `Claude 3 Opus`

### ✅ Legacy Doc Generator
- Automatically generate clear docstrings and usage examples from legacy code

### ✅ Tech Stack Familiarizer
- Analyzes `package.json`, `requirements.txt`, Dockerfiles etc. to explain what tools the project uses

### ✅ Ask-Anything Chat for Developers
- Ask questions like “What’s a rebase?” or “How do I run this project?”
- Smart responses tailored to your current stack and context

### ✅ GitOps Guardrails
- Warns you before force-pushing to `main`, skipping tests, or making risky PRs

### ✅ Security & Hygiene Checks
- Scan pasted code for vulnerabilities like hardcoded secrets or unsafe regex

### ✅ Smart Learning from Dev Questions
- Learns from what developers frequently ask
- Stores queries in MongoDB for future answers and analytics

### ✅ Screen-Aware Assistant
- Start screen recording → ShadowAI reads visible code via OCR and scrolls automatically
- No image/video is stored — only extracted text is saved
- Claude/Groq analyzes the screen and gives fixes or guidance without the user typing a thing

---

## 🧰 Tech Stack

| Layer       | Tech                                  |
|------------|----------------------------------------|
| Frontend    | Next.js, Tailwind CSS, TypeScript     |
| Backend     | FastAPI (Python), Pydantic, Uvicorn   |
| AI Models   | Groq API (Claude 3 / LLaMA3 / Mixtral)|
| OCR         | EasyOCR, OpenCV                       |
| Database    | MongoDB (via PyMongo)                 |
| Paraphraser | LangChain (simplifies AI output)      |
| Auth (opt.) | GitHub OAuth, JWT (optional roadmap)  |

---

## ⚙️ Getting Started

### 1. Clone the repo
```bash
git clone https://github.com/Prince-m37labs/ShadowAI.git
cd ShadowAI

2. Setup virtual environment (backend)

cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

Create a .env file:
GROQ_API_KEY=your-groq-api-key
MONGODB_URI=mongodb://localhost:27017

Run the server:
uvicorn main:app --reload

3. Setup frontend

cd frontend
npm install
npm run dev

🛡 Privacy by Design
ShadowAI never stores screenshots or videos.
All screen-assist analysis is done live in memory — only extracted OCR text is saved for learning.
