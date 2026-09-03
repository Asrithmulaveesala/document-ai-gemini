import os
from pathlib import Path

from dotenv import load_dotenv

from langchain_google_genai import (
    GoogleGenerativeAIEmbeddings,
    ChatGoogleGenerativeAI
)

from langchain_community.vectorstores import FAISS

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser


# ============================================================
# ENVIRONMENT VARIABLES
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
ENV_FILE = BASE_DIR / ".env"

load_dotenv(ENV_FILE)

GOOGLE_API_KEY = (
    os.getenv("GOOGLE_API_KEY")
    or os.getenv("GEMINI_API_KEY")
)

if not GOOGLE_API_KEY:
    raise ValueError(
        f"Gemini API key not found.\n"
        f"Check your .env file:\n{ENV_FILE}"
    )

os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY


# ============================================================
# EMBEDDING MODEL
# ============================================================

embeddings = GoogleGenerativeAIEmbeddings(
    model="gemini-embedding-2-preview"
)


# ============================================================
# LLM
# ============================================================

llm = ChatGoogleGenerativeAI(
    model="gemini-3.6-flash"
)


# ============================================================
# PROMPT
# ============================================================

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
You are a helpful document question-answering assistant.

Answer the user's question using ONLY the information
provided in the context.

If the answer cannot be found in the uploaded documents,
say:

"I don't know based on the uploaded documents."

Do not make up information.

Context:
{context}
"""
        ),
        (
            "human",
            "{question}"
        )
    ]
)


# ============================================================
# CREATE RAG CHAIN
# ============================================================

def create_rag_chain(chunks):

    # --------------------------------------------------------
    # Remove empty chunks
    # --------------------------------------------------------

    valid_chunks = [
        chunk
        for chunk in chunks
        if chunk.page_content
        and chunk.page_content.strip()
    ]

    print("Total chunks:", len(chunks))
    print("Valid chunks:", len(valid_chunks))


    # --------------------------------------------------------
    # Check whether chunks exist
    # --------------------------------------------------------

    if not valid_chunks:

        raise ValueError(
            "No readable text was extracted from the uploaded PDF. "
            "The PDF may be scanned/image-based or contain no text."
        )


    # --------------------------------------------------------
    # Create FAISS Vector Store
    # --------------------------------------------------------

    vectorstore = FAISS.from_documents(
        documents=valid_chunks,
        embedding=embeddings
    )


    # --------------------------------------------------------
    # Create Retriever
    # --------------------------------------------------------

    retriever = vectorstore.as_retriever(
        search_kwargs={
            "k": 4
        }
    )


    # --------------------------------------------------------
    # Create RAG Chain
    # --------------------------------------------------------

    rag_chain = (
        {
            "context": retriever,
            "question": RunnablePassthrough()
        }
        | prompt
        | llm
        | StrOutputParser()
    )

    return rag_chain