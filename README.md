# 🎓 AI Learning & Study Assistant

[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit 1.35+](https://img.shields.io/badge/Streamlit-1.35%2B-FF4B4B.svg?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![FAISS Vector Search](https://img.shields.io/badge/FAISS-CPU%20Vector%20Store-green.svg)](https://github.com/facebookresearch/faiss)
[![Sentence Transformers](https://img.shields.io/badge/Embeddings-all--MiniLM--L6--v2-yellow.svg)](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2)
[![Google Gemini API](https://img.shields.io/badge/LLM-Gemini%202.5%20Flash-orange.svg?logo=google&logoColor=white)](https://aistudio.google.com/)
[![Architecture](https://img.shields.io/badge/Architecture-Zero%20LangChain-success.svg)](#-architecture--design-philosophy)

A lightweight, high-performance, and intelligent AI study companion built specifically for students and educators. Upload your course materials, lecture notes, or textbooks in PDF format, ask questions grounded strictly in your documents using **Retrieval-Augmented Generation (RAG)**, generate personalized multiple-choice quizzes with instant interactive grading, track learning progress and weak topics over time, and build actionable day-by-day exam preparation schedules.

Built with a custom **Modern SaaS Design System** (`ui_components.py`) featuring Plus Jakarta Sans typography, sleek card layouts, micro-interactions, and real-time feedback.

---

## 🚀 Key Features

### 1. 🏠 Executive Learning Dashboard
- **Real-Time Study Metrics:** View total questions asked, quizzes completed, current mastery average score, and active weak areas at a glance.
- **Quick-Start Actions:** Instant one-click shortcuts to start asking questions, launch a quiz, upload PDFs, or build a study schedule.
- **Recent Topics & History:** Visual badges highlighting recently studied subjects and prompt shortcuts.
- **Engine Status Indicators:** Live status badge showing Gemini API connectivity, embedding model health, and indexed chunk counts.

### 2. 📚 PDF Ingestion & Semantic Vector Store
- **Multi-File PDF Upload:** Upload multiple course PDFs simultaneously with drag-and-drop support.
- **Intelligent Page-by-Page Extraction:** Uses `pypdf` to extract text while tracking exact page numbers and document origins.
- **Graceful Scanner Detection:** Automatically detects empty or image-only scanned PDFs with clear user warnings.
- **Semantic Chunking:** Splits text into 700-character passages with a 100-character sliding overlap to maintain contextual continuity.
- **Local Dense Embeddings:** Generates 384-dimensional dense vectors using `sentence-transformers/all-MiniLM-L6-v2` (fast and CPU-friendly).
- **Persistent FAISS Vector Index:** Fast cosine similarity search (`IndexFlatIP` on unit-normalized vectors) stored persistently in `data/vector_store/`.
- **Built-in Demo Generator:** Generates a ready-to-use sample Cloud Computing lecture PDF with one click for immediate testing.

### 3. 💬 Grounded RAG Question Answering ("Ask AI")
- **Semantic Retrieval:** Queries the FAISS index for the top-k most relevant passages.
- **Strict Anti-Hallucination Guardrails:** Formulates strictly grounded prompts for Google Gemini (`gemini-2.5-flash`).
- **Absence Handling:** If information is missing from the uploaded documents, the assistant cleanly states:
  > *"I couldn't find this information in the uploaded study material."*
- **Transparent Source Citations:** Expandable citation cards under every response showing source filename, page number, similarity confidence percentage, and extracted text snippet.
- **Quick Prompt Chips:** One-click sample questions (e.g., *"Provide a 3-bullet summary"*, *"Explain the core concept in simple terms"*).

### 4. 📝 Interactive MCQ Quiz Generator & Evaluator
- **Customizable Configuration:** Choose target topic, question count (5 or 10 questions), and difficulty level (Easy, Medium, Hard).
- **Material-Grounded Questions:** Generated directly from the indexed PDF content or specified course subject.
- **Interactive Quiz Taker:** Radio-button question form with step-by-step or full quiz submission.
- **Instant Detailed Grading:** Immediate score calculation, percentage progress bar, and badge feedback (Needs Practice, Good Effort, Mastery Achieved).
- **Question Breakdown Cards:** Color-coded cards showing your selected answer, the correct answer, and an in-depth conceptual explanation.
- **Automatic Weak Area Diagnosis:** Incorrect questions are automatically categorized and logged into the student memory system.

### 5. 📊 Student Memory & Analytics ("My Progress")
- **Persistent Local Memory:** Stored in `data/memory.json` without requiring external databases.
- **Inquiry & Study Logging:** Automatically logs queries, timestamps, and studied topics.
- **Dynamic Mastery Tracking:**
  - Quiz scores `< 70%` flag the topic under **Priority Focus Areas**.
  - Quiz scores `≥ 85%` promote the topic to **Mastered** and resolve prior weak areas.
- **Quiz Performance Table:** Full historical log displaying dates, topics, question counts, and percentage scores.
- **One-Click Memory Management:** Provides a safe reset button to clear learning history when starting a new course.

### 6. 📅 Dynamic Study Plan Generator
- **Personalized Inputs:** Configurable exam date, daily available study hours (0.5 to 8 hrs), current knowledge level (Beginner, Intermediate, Advanced), and targeted weak areas.
- **Phased Exam Schedule:** Generates an actionable day-by-day timetable broken down into:
  - *Phase 1:* Core Concept Mastery & Theory
  - *Phase 2:* Practice & Active Recall
  - *Phase 3:* Weak Area Drilling & Mock Quizzes
  - *Phase 4:* Final Revision & Rapid Review
- **Interactive Day-by-Day Checklist:** Check off study days as you complete them with real-time completion percentage tracking.
- **Instant Export:** Download your personalized plan as a formatted Markdown (`.md`) file with one click.

---

## 🏛️ Architecture & Design Philosophy

```
                              +-----------------------------+
                              |     User / Streamlit UI     |
                              |     (ui_components.py)      |
                              +--------------+--------------+
                                             |
                     +-----------------------+-----------------------+
                     |                       |                       |
             [Study Materials]           [Ask AI]              [Quiz / Plan]
                     |                       |                       |
             PyPDF Extraction                |                       |
                     |                 Intent Router                 |
              Text Chunking                  |                       |
                     |           +-----------+-----------+           |
           SentenceTransformers  |                       |           |
            (all-MiniLM-L6-v2)   v                       v           v
                     |      Vector Search          Direct Tools    Gemini API
                     v      (FAISS Index)        (quiz, memory,   (Flash Model)
               FAISS Index       |                study plan)         |
                     |           v                       |            |
                     +---> Retrieved Context             +------------+
                                  |
                                  v
                          Google Gemini LLM
                                  |
                                  v
                        Grounded Answer + Citations
                                  |
                                  v
                      Local Memory (data/memory.json)
```

### Why Zero LangChain?
This application intentionally avoids heavy orchestration frameworks (LangChain, LangGraph, LlamaIndex):
1. **Total Transparency:** Full control over prompts, token budgets, retrieval thresholds, and data structures.
2. **Deterministic Speed:** Instant startup times with minimal import overhead and fast execution.
3. **No Breaking Upgrades:** Direct integration with Google's official `google-generativeai` SDK and Facebook's `faiss-cpu`.
4. **Clean Debugging:** Standard Python functions with predictable stack traces and clear error messages.

---

## 🛠️ Tech Stack

| Component | Technology | Description |
|---|---|---|
| **Frontend Framework** | Streamlit `1.35.0+` | Interactive multi-page educational web dashboard |
| **Design System** | Custom CSS (`ui_components.py`) | Plus Jakarta Sans font, modern SaaS card layout, badges |
| **LLM Provider** | Google Gemini (`gemini-2.5-flash`) | Fast, cost-efficient reasoning and question answering |
| **Embeddings** | `sentence-transformers` (`all-MiniLM-L6-v2`) | 384-dimensional dense semantic vector representations |
| **Vector Database** | `faiss-cpu` `1.8.0+` | CPU-optimized dense vector index with cosine similarity |
| **PDF Extraction** | `pypdf` `4.0.0+` | Fast text and metadata extraction from PDF files |
| **Local Persistence** | Local JSON & Binary FAISS | `data/memory.json` and `data/vector_store/index.faiss` |
| **Environment** | `python-dotenv` | Clean, secure API key and model configuration |

---

## 📁 Project Structure

```
ai-study-assistant/
│
├── app.py                   # Main Streamlit application & 6-page navigation
├── ui_components.py         # Modern SaaS design system, CSS, badges & cards
├── rag.py                   # PDF extraction, chunking, FAISS index & RAG QA
├── quiz.py                  # MCQ generation, fallback generation & scoring
├── memory.py                # Persistent student memory (data/memory.json)
├── study_plan.py            # Day-by-day exam schedule generator & export
├── tools.py                 # Modular tools & deterministic keyword intent router
├── config.py                # Environment variables, paths, and Gemini client
├── requirements.txt         # Minimal, pinned Python dependencies
├── .env.example             # Template for API keys and model parameters
├── .gitignore               # Complete git ignore rules (venv, secrets, cache)
├── README.md                # Full documentation, architecture & demo guide
│
├── test_verification.py     # Backend verification test suite (RAG, FAISS, Tools)
├── test_app_flows.py        # Streamlit AppTest automated functional UI tests
│
├── data/
│   ├── .gitkeep             # Directory placeholder
│   ├── memory.json          # Persistent student history and metrics
│   └── vector_store/
│       ├── .gitkeep         # Directory placeholder
│       ├── index.faiss      # Saved FAISS vector index
│       └── chunks_metadata.json # Chunk text and citation metadata
│
└── uploads/
    └── .gitkeep             # Directory placeholder for user-uploaded PDFs
```

---

## ⚙️ Installation & Setup

### 1. Prerequisites
- **Python 3.11** or **Python 3.12** installed on your system.
- A free **Google Gemini API Key** from [Google AI Studio](https://aistudio.google.com/).

### 2. Clone or Navigate to the Directory
```bash
cd d:\inten\ai-study-assistant
```

### 3. Create & Activate a Virtual Environment

**Windows (PowerShell):**
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**Windows (Command Prompt):**
```cmd
python -m venv .venv
.venv\Scripts\activate.bat
```

**macOS / Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Configure Your Gemini API Key
Copy the sample environment file:
```bash
# Windows
copy .env.example .env

# macOS / Linux
cp .env.example .env
```

Open `.env` and set your API key:
```env
# Google Gemini API Key
GEMINI_API_KEY=AIzaSy...your_real_api_key_here

# Model Selection
GEMINI_MODEL=gemini-2.5-flash

# Embeddings & Vector Search
EMBEDDING_MODEL=all-MiniLM-L6-v2
CHUNK_SIZE=700
CHUNK_OVERLAP=100
TOP_K_RESULTS=4
```

---

## 🚀 Running the Application

Ensure your virtual environment is active, then run:

```bash
streamlit run app.py
```

The application will open automatically in your browser at:
👉 **`http://localhost:8501`**

---

## 🧪 Running Automated Tests

The repository includes comprehensive automated verification suites:

### 1. Backend Integration Tests
Tests PDF processing, FAISS vector search, student memory updates, fallback quiz evaluation, and tool intent routing:
```bash
# Using active virtual environment
python test_verification.py
```

### 2. Streamlit UI Flow Tests
Tests page transitions, widget keys, session state persistence, and button actions using Streamlit's official `AppTest` framework:
```bash
python test_app_flows.py
```

---

## 🔍 Deep-Dive: How It Works

### 1. Retrieval-Augmented Generation (RAG)
1. **Extraction:** `pypdf.PdfReader` extracts text page-by-page. Blank or non-extractable scanned pages are identified and reported.
2. **Chunking:** Extracted text is normalized and split into 700-character segments with a 100-character sliding overlap. Each chunk retains its filename, page number, and unique chunk ID.
3. **Dense Embedding:** Chunks are converted into 384-dimensional dense vectors using `all-MiniLM-L6-v2`. Vectors are L2-normalized so that inner products compute exact cosine similarity.
4. **FAISS Indexing:** Normalized vectors are inserted into `faiss.IndexFlatIP`.
5. **Retrieval & Guardrails:** User queries are embedded, normalized, and searched against FAISS for the top-4 closest chunks. If similarity scores fall below the threshold or the topic is not covered, the assistant prevents hallucinations by responding with:
   *"I couldn't find this information in the uploaded study material."*
6. **Transparent Citations:** Citations are rendered below the answer showing file, page, score, and snippet.

### 2. Student Learning Memory
- Stored locally in `data/memory.json`.
- Automatically logs user questions and timestamps.
- Logs every quiz submission: topic, score, percentage, date, and difficulty.
- Automatically diagnoses weak concepts when quiz scores drop below `70%`.
- Automatically marks mastery when quiz scores reach `85%` or higher.

### 3. Agentic Intent Router
`tools.py` implements a fast, deterministic keyword router:
- Queries with *"quiz"*, *"test me"*, *"generate a test"* ➔ `generate_quiz()`
- Queries with *"how am i doing"*, *"my score"*, *"progress"* ➔ `get_student_memory()`
- Queries with *"study plan"*, *"exam timetable"*, *"schedule"* ➔ `create_study_plan()`
- All subject-matter queries ➔ `search_study_material()` (RAG)

---

## 🎬 Step-by-Step Demo Flow

Follow this exact walkthrough during demonstrations:

1. **Launch the Dashboard:**
   - Run `streamlit run app.py`.
   - Explore the **🏠 Dashboard**: view real-time metrics cards, system status, recent topics, and quick-start action buttons.
2. **Upload Study Materials:**
   - Navigate to **📚 Study Materials**.
   - Either upload your own course PDF or click **✨ Generate Sample Lecture PDF** to test immediately.
   - Click **🚀 Process & Index Materials**. Show the live progress bar and metrics (Pages Extracted, Chunks Created, Total Vectors).
3. **Ask Grounded RAG Questions:**
   - Navigate to **💬 Ask AI**.
   - Click a quick chip or type: `"What is the primary concept discussed in this material?"`
   - Observe the grounded answer and expand **🔍 View Sources & Citations** to highlight the source file, page number, and exact text snippet.
4. **Demonstrate Anti-Hallucination Guardrails:**
   - Ask an out-of-domain question (e.g., *"Who won the 2022 FIFA World Cup?"*).
   - Observe the strictly guarded response: *"I couldn't find this information in the uploaded study material."*
5. **Generate an Interactive Quiz:**
   - Navigate to **📝 Quiz**.
   - Select your topic, choose 5 questions, and set difficulty to Medium.
   - Click **⚡ Generate Quiz**.
6. **Take & Submit Quiz:**
   - Answer the multiple-choice questions interactively.
   - Click **📊 Submit Quiz & See Results**.
   - Review your score badge, percentage progress bar, and the explanation card for each question.
7. **Inspect Learning Progress:**
   - Navigate to **📊 My Progress**.
   - Show that your quiz score, questions asked, and diagnosed weak topics were immediately updated in memory.
8. **Generate & Track Personalized Study Plan:**
   - Navigate to **📅 Study Plan**.
   - Pick your exam date (e.g., 7 days ahead), set daily hours (e.g., 2.5 hrs), select your knowledge level, and click **📅 Generate Study Plan**.
   - Review the day-by-day plan, check off Day 1 in the interactive checklist, and click **📥 Download Study Plan (.md)**.

---

## ❓ Troubleshooting

| Issue | Likely Cause | Solution |
|---|---|---|
| `GEMINI_API_KEY is not set` | Missing API key in environment | Set `GEMINI_API_KEY` in `.env` or system environment variables. |
| `Gemini model not found (404)` | Deprecated or unavailable model | Set `GEMINI_MODEL=gemini-2.5-flash` in `.env`. |
| `PyTorch / DLL initialization failed (Win32)` | Windows C-extension DLL path resolution | Addressed automatically in `config.py`. Ensure torch is installed in `.venv`. |
| `PDF contains no extractable text` | PDF contains only scanned images | Upload a searchable PDF containing selectable text. |
| `No study materials uploaded yet` | Querying an empty vector index | Ingest at least one PDF in **📚 Study Materials** before querying. |
| Corrupted or invalid student memory | Broken JSON syntax in `memory.json` | Click **🗑️ Reset All Student Memory** in **📊 My Progress** to regenerate. |

---

## 📄 License & Attribution

Developed as an educational AI project. Free for personal, academic, and open-source learning. Powered by Google Gemini, FAISS, and Streamlit.

## Developer

 **Yogesh** — [GitHub](https://github.com/ug8yogesh)

---

<div align="center">
  🌟 If you found this project useful, consider giving it a star on GitHub!
</div>