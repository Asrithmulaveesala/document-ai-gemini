# 📚 Document RAG Chatbot

A document-based question-answering chatbot built using **LangChain, LCEL, Gemini, FAISS, and Streamlit**.

The application allows users to upload PDF documents and ask questions about their content. The system retrieves the most relevant document chunks and uses a Gemini LLM to generate answers based only on the retrieved context.

## 🚀 Features

- Upload one or multiple PDF documents
- Extract text from PDF files
- Split documents into manageable chunks
- Generate embeddings using Gemini
- Store document embeddings using FAISS
- Retrieve relevant document chunks
- Generate answers using Gemini
- Built using LangChain LCEL
- Interactive Streamlit chat interface
- Maintains chat history during the session

## 🛠️ Technologies Used

- Python
- Streamlit
- LangChain
- LangChain Expression Language (LCEL)
- Google Gemini
- Gemini Embeddings
- FAISS
- PyPDF
- Python-dotenv

## 📂 Project Structure

```text
document-retrieved-gemini/
│
├── app.py
├── rag.py
├── requirements.txt
├── gemini-ai.ipynb
├── .env.example
├── .gitignore
└── README.md