
import os
import tempfile

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from rag import create_rag_chain


app = FastAPI(
    title="Document AI API",
    description="Backend API for Document AI",
    version="1.0"
)


# ============================================================
# CORS
# ============================================================

origins = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:5173"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in origins],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# GLOBAL RAG CHAIN
# ============================================================

rag_chain = None


# ============================================================
# REQUEST MODEL
# ============================================================

class ChatRequest(BaseModel):
    question: str
    session_id: str


# ============================================================
# HOME
# ============================================================

@app.get("/")
def home():
    return {
        "message": "Document AI backend is running"
    }


# ============================================================
# HEALTH
# ============================================================

@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


# ============================================================
# CHAT - STREAMING
# ============================================================

@app.post("/chat")
async def chat(request: ChatRequest):
    global rag_chain

    if rag_chain is None:
        raise HTTPException(
            status_code=400,
            detail="Please upload a PDF first."
        )

    if not request.question.strip():
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty."
        )

    async def generate():
        try:
            print(f"Session ID: {request.session_id}")

            async for chunk in rag_chain.astream(
                {"input": request.question},
                config={
                    "configurable": {
                        "session_id": request.session_id
                    }
                }
            ):
                if chunk:
                    yield chunk

        except Exception as e:
            print("Streaming error:", e)
            yield f"\nError: {str(e)}"

    return StreamingResponse(
        generate(),
        media_type="text/plain"
    )


# ============================================================
# UPLOAD PDF
# ============================================================

@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    global rag_chain

    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Please upload a valid PDF file."
        )

    temp_path = None

    try:
        pdf_bytes = await file.read()

        if not pdf_bytes:
            raise HTTPException(
                status_code=400,
                detail="The uploaded PDF is empty."
            )

        # Save PDF temporarily
        with tempfile.NamedTemporaryFile(
            suffix=".pdf",
            delete=False
        ) as temp_file:
            temp_file.write(pdf_bytes)
            temp_path = temp_file.name

        # Load PDF
        loader = PyPDFLoader(temp_path)
        documents = loader.load()

        if not documents:
            raise HTTPException(
                status_code=400,
                detail="No readable content found in the PDF."
            )

        # Split document
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )

        chunks = text_splitter.split_documents(documents)

        if not chunks:
            raise HTTPException(
                status_code=400,
                detail="Could not extract text chunks from the PDF."
            )

        # Create RAG chain
        rag_chain = create_rag_chain(chunks)

        return {
            "filename": file.filename,
            "pages": len(documents),
            "chunks": len(chunks),
            "message": "PDF uploaded and RAG chain created successfully"
        }

    except HTTPException:
        raise

    except Exception as e:
        print("PDF upload error:", e)
        raise HTTPException(
            status_code=500,
            detail="Failed to process PDF."
        )

    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)