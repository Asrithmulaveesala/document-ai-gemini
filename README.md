# 📄 Document AI

An AI-powered document question-answering application that allows users to upload PDF documents and interact with them through a conversational chat interface.

The application uses **Retrieval-Augmented Generation (RAG)** to retrieve relevant information from uploaded documents and generate accurate answers using **Google Gemini**.

## 🚀 Features

* 📤 Upload one or multiple PDF documents
* 📑 Extract text from uploaded documents
* ✂️ Split documents into smaller chunks
* 🧠 Generate embeddings using Gemini
* 🔎 Semantic document retrieval using FAISS
* 🤖 Generate answers using Google Gemini
* 💬 Interactive conversational chat interface
* 🗂️ Display uploaded documents and processed chunk information
* ⚡ Built with LangChain and LCEL
* 🎨 Clean and responsive Streamlit UI

## 🛠️ Tech Stack

* **Python**
* **Streamlit**
* **LangChain**
* **LangChain Expression Language (LCEL)**
* **Google Gemini**
* **Gemini Embeddings**
* **FAISS**
* **PyPDF**
* **python-dotenv**

## 🧠 Architecture

```text
                ┌─────────────────┐
                │   PDF Upload    │
                └────────┬────────┘
                         │
                         ▼
                ┌─────────────────┐
                │  PDF Extraction │
                │   PyPDFLoader   │
                └────────┬────────┘
                         │
                         ▼
                ┌─────────────────┐
                │  Text Splitting │
                │ Recursive Split │
                └────────┬────────┘
                         │
                         ▼
                ┌─────────────────┐
                │ Gemini Embedding│
                └────────┬────────┘
                         │
                         ▼
                ┌─────────────────┐
                │      FAISS      │
                │  Vector Store   │
                └────────┬────────┘
                         │
                         ▼
                ┌─────────────────┐
                │    Retriever    │
                └────────┬────────┘
                         │
                    Relevant
                     Context
                         │
                         ▼
                ┌─────────────────┐
                │   Gemini LLM    │
                └────────┬────────┘
                         │
                         ▼
                ┌─────────────────┐
                │   AI Response   │
                └─────────────────┘
```

## 🔄 How It Works

### 1. Upload Documents

Users can upload one or multiple PDF files directly through the Streamlit interface.

### 2. Document Loading

The uploaded PDFs are processed using `PyPDFLoader` to extract their text content.

### 3. Text Chunking

The extracted content is divided into smaller chunks using `RecursiveCharacterTextSplitter`.

```python
RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)
```

### 4. Embeddings

Each document chunk is converted into a vector representation using Gemini Embeddings.

### 5. Vector Storage

The generated embeddings are stored in a **FAISS vector database**, allowing efficient similarity search.

### 6. Retrieval

When the user asks a question, the retriever searches the vector database and finds the most relevant document chunks.

### 7. Generation

The retrieved context is passed to Google Gemini through a LangChain LCEL pipeline.

The model generates an answer based on the retrieved document content.

## 📂 Project Structure

```text
Document-AI/
│
├── app.py
├── rag.py
├── requirements.txt
├── gemini-ai.ipynb
├── .env.example
├── .gitignore
└── README.md
```

## ⚙️ Installation

Clone the repository:

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
```

Navigate to the project directory:

```bash
cd Document-AI
```

Create a virtual environment:

```bash
python -m venv venv
```

Activate the virtual environment on Windows:

```bash
venv\Scripts\activate
```

Install the required dependencies:

```bash
pip install -r requirements.txt
```

## 🔑 Environment Variables

Create a `.env` file in the project directory:

```env
GOOGLE_API_KEY=your_google_gemini_api_key
```

The `.env` file should **never be committed to GitHub**.

Use `.env.example` as a template.

## ▶️ Run the Application

Start the Streamlit application:

```bash
streamlit run app.py
```

The application will open in your browser.

Upload your documents, process them, and start asking questions.

## 💡 Example Questions

After uploading a document, you can ask questions such as:

```text
What is this document about?

What are the main skills mentioned?

What is the candidate's educational qualification?

Summarize the document.

What certifications are mentioned?

What projects are included in the document?
```

## 🔐 RAG-Based Responses

The application is designed to answer questions using the information retrieved from the uploaded documents.

If the required information cannot be found, the system is instructed to respond:

```text
I don't know based on the uploaded documents.
```

This helps reduce unsupported answers and keeps the chatbot focused on the provided documents.

## 📈 Future Improvements

* Support for DOCX, TXT, and other document formats
* Persistent vector database storage
* Document source citations
* Streaming responses
* Multi-document conversations
* Conversation memory
* Improved document parsing
* OCR support for scanned PDFs
* Authentication and user-specific document storage

## 👨‍💻 Author

**Koushik Asrith Mulavisala**

B.Tech — Computer Science & Engineering

---

⭐ If you find this project useful, consider giving the repository a star.
