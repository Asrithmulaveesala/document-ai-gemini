# 📄 Document AI — RAG-Based Document Question Answering System

A modern **React.js frontend** for an AI-powered document question-answering application built using **Retrieval-Augmented Generation (RAG)**.

Users can upload PDF documents and interact with them through a conversational chat interface. The frontend communicates with a **FastAPI backend**, which handles document processing, retrieval, Gemini embeddings, FAISS vector search, and LLM-based response generation.

## 🚀 Live Demo

🌐 **Frontend:**
https://document-ai-gemini.vercel.app/

⚙️ **Backend API:**
https://document-ai-gemini.onrender.com/

> ⚠️ **Demo Note:** The application depends on the available Google Gemini API quota. If the API quota is temporarily exhausted, new requests may not be processed until the quota becomes available again.

## ✨ Features

* 📄 Upload PDF documents
* 🔍 Document-based question answering
* 🧠 Retrieval-Augmented Generation (RAG)
* 🔢 Gemini-powered embeddings
* 🗃️ FAISS vector search
* 💬 Conversational chat interface
* ⚡ Streaming AI responses
* 📊 Document processing information
* 🎨 Responsive and interactive React UI
* 🔗 FastAPI backend integration
* ☁️ Deployed application

## 🏗️ Architecture

```text
                ┌──────────────────────┐
                │      React.js        │
                │      Frontend        │
                └──────────┬───────────┘
                           │
                    HTTP / Streaming
                           │
                           ▼
                ┌──────────────────────┐
                │       FastAPI        │
                │       Backend        │
                └──────────┬───────────┘
                           │
                           ▼
                ┌──────────────────────┐
                │     RAG Pipeline     │
                │      LangChain       │
                └──────────┬───────────┘
                           │
             ┌─────────────┴─────────────┐
             ▼                           ▼
      Gemini Embeddings              FAISS
             │                           │
             └─────────────┬─────────────┘
                           ▼
                    Relevant Chunks
                           │
                           ▼
                    Google Gemini
                           │
                           ▼
                    Generated Answer
                           │
                           ▼
                     React UI
```

## 🛠️ Tech Stack

### Frontend

* React.js
* Vite
* JavaScript
* CSS
* Lucide React

### Backend

* Python
* FastAPI
* LangChain
* LCEL
* Google Gemini API
* Gemini Embeddings
* FAISS
* PyPDF

### Deployment

* Vercel — Frontend
* Render — Backend
* GitHub — Version Control

## 🔄 RAG Workflow

1. User uploads a PDF document.
2. The backend extracts the document content.
3. The content is split into smaller chunks.
4. Gemini Embeddings are generated for the chunks.
5. Embeddings are stored in FAISS.
6. User submits a question.
7. The question is converted into an embedding.
8. FAISS retrieves the most relevant document chunks.
9. Retrieved context is passed to Google Gemini.
10. Gemini generates a context-based answer.
11. The response is streamed back to the React frontend.

## 📊 RAG Evaluation

The project was also extended beyond basic RAG implementation to explore **RAG evaluation techniques**.

The evaluation focuses on aspects such as:

* Retrieval relevance
* Retrieved context quality
* Answer quality
* Context-based response generation

This helped in understanding that building an effective RAG system involves not only retrieval and generation, but also measuring the quality of the overall pipeline.

## 📁 Project Structure

```text
document-ai/
│
├── public/
│
├── src/
│   ├── assets/
│   ├── App.jsx
│   ├── App.css
│   ├── main.jsx
│   └── ...
│
├── index.html
├── package.json
├── vite.config.js
└── README.md
```

## ⚙️ Local Setup

### 1. Clone the repository

```bash
git clone <your-github-repository-url>
cd <your-project-folder>
```

### 2. Install dependencies

```bash
npm install
```

### 3. Configure the backend URL

Create a `.env` file in the frontend project:

```env
VITE_API_URL=http://127.0.0.1:8000
```

For the deployed application, configure the environment variable with the deployed FastAPI backend URL.

### 4. Start the development server

```bash
npm run dev
```

The application will be available at:

```text
http://localhost:5173
```

## 🎯 Project Focus

The main focus of this project was to gain practical experience in building an end-to-end **RAG application**, including:

* Document processing
* Embeddings
* Vector databases
* Semantic retrieval
* LLM integration
* RAG evaluation
* API development
* Streaming responses
* Frontend integration
* Application deployment

Authentication and database-backed chat persistence were intentionally kept outside the scope of this version so the project could remain focused on the **core RAG pipeline, evaluation, user experience, and deployment**.

## 🔮 Future Work

The next focus is to explore **AI Agents and Agentic AI**, including:

* Tool calling
* Agent workflows
* Multi-step reasoning
* Agent memory
* Autonomous task execution
* Building practical AI agent applications

## 👨‍💻 Author

**Koushik Asrith Mulavisala**

Interested in **Generative AI, RAG, LLM Applications, and Agentic AI**.

---

⭐ If you find this project useful, feel free to explore the repository and try the live application.
