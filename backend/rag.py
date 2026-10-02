import os
from pathlib import Path

from dotenv import load_dotenv

from langchain_google_genai import (
    GoogleGenerativeAIEmbeddings,
    ChatGoogleGenerativeAI
)

from langchain_community.vectorstores import FAISS

from langchain_core.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder
)

from langchain_core.output_parsers import StrOutputParser

from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables import RunnableWithMessageHistory


# ============================================================
# ENVIRONMENT VARIABLES
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent
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
    model="gemini-3.5-flash-lite",
    streaming=True
)


# ============================================================
# IN-MEMORY MESSAGE HISTORY
# ============================================================

store = {}


def get_session_history(
    session_id: str
) -> BaseChatMessageHistory:

    if session_id not in store:
        store[session_id] = ChatMessageHistory()

        print(
            f"Created new chat session: {session_id}"
        )

    return store[session_id]


# ============================================================
# GET SESSION MESSAGES
# ============================================================

def get_session_messages(session_id: str):

    history = store.get(session_id)

    if history is None:
        return []

    return [
        {
            "role": message.type,
            "content": message.content
        }
        for message in history.messages
    ]


# ============================================================
# GET ALL SESSIONS
# ============================================================

def get_all_sessions():

    return list(store.keys())


# ============================================================
# CREATE RAG CHAIN
# ============================================================

def create_rag_chain(chunks):

    print("Creating new RAG chain...")

    # ========================================================
    # REMOVE EMPTY CHUNKS
    # ========================================================

    valid_chunks = [
        chunk
        for chunk in chunks
        if chunk.page_content
        and chunk.page_content.strip()
    ]

    print("Total chunks:", len(chunks))
    print("Valid chunks:", len(valid_chunks))

    if not valid_chunks:
        raise ValueError(
            "No readable text was extracted from the uploaded PDF. "
            "The PDF may be scanned/image-based or contain no text."
        )

    # ========================================================
    # CREATE FAISS VECTOR STORE
    # ========================================================

    print("Creating FAISS vector store...")

    vectorstore = FAISS.from_documents(
        documents=valid_chunks,
        embedding=embeddings
    )

    print("FAISS vector store created successfully.")

    # ========================================================
    # CREATE RETRIEVER
    # ========================================================

    retriever = vectorstore.as_retriever(
        search_kwargs={
            "k": 4
        }
    )

    # ========================================================
    # PROMPT
    # ========================================================

    system_prompt = (
        "You are a helpful document question-answering assistant. "
        "Use the retrieved context to answer the user's question. "
        "Use the conversation history when necessary to understand "
        "follow-up questions. "
        "Answer using ONLY the information available in the "
        "uploaded documents. "
        "If the answer cannot be found in the uploaded documents, "
        "say: I don't know based on the uploaded documents. "
        "Do not make up information.\n\n"
        "Retrieved Context:\n"
        "{context}"
    )

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),

            MessagesPlaceholder(
                variable_name="history"
            ),

            ("human", "{input}")
        ]
    )

    # ========================================================
    # RAG CHAIN
    # ========================================================

    rag_chain = (
        {
            "context": lambda x: retriever.invoke(
                x["input"]
            ),
            "input": lambda x: x["input"],
            "history": lambda x: x["history"]
        }
        | prompt
        | llm
        | StrOutputParser()
    )

    # ========================================================
    # ADD MESSAGE HISTORY
    # ========================================================

    rag_with_runnable_history = RunnableWithMessageHistory(
        rag_chain,
        get_session_history,
        input_messages_key="input",
        history_messages_key="history"
    )

    print("RAG chain created successfully.")

    return rag_with_runnable_history