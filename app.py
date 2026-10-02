import os
import tempfile
import uuid
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from rag import create_rag_chain


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

    st.error(
        f"""
        Gemini API key not found.

        Please check your .env file:

        {ENV_FILE}
        """
    )

    st.stop()

os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Document AI",
    page_icon="📚",
    layout="centered",
    initial_sidebar_state="expanded"
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    .main-title {
        text-align: center;
        font-size: 46px;
        font-weight: 700;
        margin-top: 25px;
        margin-bottom: 5px;
    }

    .subtitle {
        text-align: center;
        font-size: 16px;
        color: #9ca3af;
        margin-bottom: 30px;
    }

    .status-card {
        padding: 15px;
        border-radius: 10px;
        margin-top: 15px;
        margin-bottom: 15px;
        border: 1px solid rgba(128,128,128,0.2);
    }

    .footer {
        position: fixed;
        bottom: 8px;
        width: 100%;
        text-align: center;
        font-size: 11px;
        color: #999;
        font-weight: normal;
    }

    [data-testid="stChatInput"] {
        bottom: 35px;
    }

    [data-testid="stAppViewContainer"] {
        padding-bottom: 90px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# SESSION STATE
# ============================================================

if "messages" not in st.session_state:
    st.session_state.messages = []


if "rag_chain" not in st.session_state:
    st.session_state.rag_chain = None


if "documents_processed" not in st.session_state:
    st.session_state.documents_processed = False


if "document_names" not in st.session_state:
    st.session_state.document_names = []


if "chunk_count" not in st.session_state:
    st.session_state.chunk_count = 0


# ============================================================
# CHAT SESSIONS
# ============================================================

if "sessions" not in st.session_state:

    st.session_state.sessions = {
        "chat_1": {
            "name": "New Chat",
            "messages": []
        }
    }


if "current_session_id" not in st.session_state:

    st.session_state.current_session_id = "chat_1"


# ============================================================
# GET CURRENT SESSION
# ============================================================

current_session_id = st.session_state.current_session_id

if current_session_id not in st.session_state.sessions:

    st.session_state.sessions[current_session_id] = {
        "name": "New Chat",
        "messages": []
    }


# Make messages point to current session
st.session_state.messages = (
    st.session_state.sessions[current_session_id]["messages"]
)


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="main-title">📚 Document AI</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Upload your documents and ask questions using AI'
    '</div>',
    unsafe_allow_html=True
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown("## 💬 Chat Sessions")


    # --------------------------------------------------------
    # NEW CHAT
    # --------------------------------------------------------

    if st.button(
        "➕ New Chat",
        use_container_width=True
    ):

        new_session_id = f"chat_{uuid.uuid4().hex[:8]}"

        st.session_state.sessions[new_session_id] = {
            "name": "New Chat",
            "messages": []
        }

        st.session_state.current_session_id = new_session_id

        st.rerun()


    # --------------------------------------------------------
    # SESSION SELECTOR
    # --------------------------------------------------------

    session_ids = list(
        st.session_state.sessions.keys()
    )

    session_names = [
        st.session_state.sessions[session_id]["name"]
        for session_id in session_ids
    ]

    selected_index = session_ids.index(
        st.session_state.current_session_id
    )


    selected_session_name = st.selectbox(
        "Select conversation",
        session_names,
        index=selected_index
    )


    selected_session_id = session_ids[
        session_names.index(selected_session_name)
    ]


    if selected_session_id != st.session_state.current_session_id:

        st.session_state.current_session_id = selected_session_id

        st.rerun()


    # ========================================================
    # DOCUMENTS
    # ========================================================

    st.divider()

    st.markdown("## 📄 Documents")

    st.write(
        "Upload one or more PDF documents "
        "to start chatting."
    )


    # --------------------------------------------------------
    # FILE UPLOADER
    # --------------------------------------------------------

    uploaded_files = st.file_uploader(
        "Upload PDF files",
        type=["pdf"],
        accept_multiple_files=True
    )


    # --------------------------------------------------------
    # PROCESS BUTTON
    # --------------------------------------------------------

    process_button = st.button(
        "🚀 Process Documents",
        use_container_width=True
    )


    # ========================================================
    # PROCESS DOCUMENTS
    # ========================================================

    if process_button:

        if not uploaded_files:

            st.warning(
                "Please upload at least one PDF document."
            )

        else:

            all_documents = []

            progress_bar = st.progress(0)
            status_text = st.empty()


            # ------------------------------------------------
            # LOAD PDFs
            # ------------------------------------------------

            total_files = len(uploaded_files)

            for index, uploaded_file in enumerate(
                uploaded_files
            ):

                status_text.info(
                    f"Loading {uploaded_file.name}..."
                )


                # ------------------------------------------------
                # Create temporary PDF
                # ------------------------------------------------

                with tempfile.NamedTemporaryFile(
                    delete=False,
                    suffix=".pdf"
                ) as temp_file:

                    temp_file.write(
                        uploaded_file.getbuffer()
                    )

                    temp_path = temp_file.name


                # ------------------------------------------------
                # Load PDF
                # ------------------------------------------------

                try:

                    loader = PyPDFLoader(
                        temp_path
                    )

                    documents = loader.load()

                    all_documents.extend(
                        documents
                    )

                finally:

                    if os.path.exists(temp_path):

                        os.remove(temp_path)


                # ------------------------------------------------
                # Update progress
                # ------------------------------------------------

                progress = int(
                    ((index + 1) / total_files) * 40
                )

                progress_bar.progress(
                    progress
                )


            # =================================================
            # SPLIT DOCUMENTS
            # =================================================

            status_text.info(
                "Splitting documents into chunks..."
            )


            text_splitter = RecursiveCharacterTextSplitter(

                chunk_size=1000,

                chunk_overlap=200

            )


            chunks = text_splitter.split_documents(
                all_documents
            )


            progress_bar.progress(60)


            # =================================================
            # CREATE RAG SYSTEM
            # =================================================

            status_text.info(
                "Creating embeddings and FAISS vector database..."
            )


            try:

                rag_chain = create_rag_chain(
                    chunks
                )


                # ------------------------------------------------
                # Store RAG chain
                # ------------------------------------------------

                st.session_state.rag_chain = rag_chain


                # ------------------------------------------------
                # Store document information
                # ------------------------------------------------

                st.session_state.documents_processed = True

                st.session_state.document_names = [
                    file.name
                    for file in uploaded_files
                ]

                st.session_state.chunk_count = len(
                    chunks
                )


                progress_bar.progress(100)


                status_text.success(
                    "Documents processed successfully! ✅"
                )


            except Exception as e:

                st.error(
                    f"Error while creating RAG system:\n\n{e}"
                )


    # ========================================================
    # SIDEBAR STATUS
    # ========================================================

    st.divider()


    if st.session_state.documents_processed:

        st.success(
            "🟢 Documents Ready"
        )


        st.write(
            f"📄 Files: "
            f"{len(st.session_state.document_names)}"
        )


        st.write(
            f"🧩 Chunks: "
            f"{st.session_state.chunk_count}"
        )


        st.markdown("### Uploaded Files")


        for file_name in st.session_state.document_names:

            st.caption(
                f"📄 {file_name}"
            )


    else:

        st.info(
            "Upload documents and click "
            "**Process Documents**."
        )


    # ========================================================
    # DELETE CURRENT CHAT
    # ========================================================

    st.divider()


    if st.button(
        "🗑️ Delete Current Chat",
        use_container_width=True
    ):

        if len(st.session_state.sessions) > 1:

            del st.session_state.sessions[
                st.session_state.current_session_id
            ]

            st.session_state.current_session_id = (
                list(st.session_state.sessions.keys())[0]
            )

        else:

            st.session_state.sessions[
                st.session_state.current_session_id
            ]["messages"] = []


        st.rerun()


# ============================================================
# DOCUMENT READY MESSAGE
# ============================================================

if st.session_state.documents_processed:

    st.markdown(
        """
        <div class="status-card">

        🟢 <strong>Document knowledge base ready.</strong>

        Ask questions about your uploaded files below.

        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# DISPLAY CHAT HISTORY
# ============================================================

for message in st.session_state.messages:

    with st.chat_message(
        message["role"]
    ):

        st.markdown(
            message["content"]
        )


# ============================================================
# CHAT INPUT
# ============================================================

input_text = st.chat_input(
    "Ask something about your documents..."
)


# ============================================================
# PROCESS QUESTION
# ============================================================

if input_text:

    # ========================================================
    # CHECK DOCUMENTS
    # ========================================================

    if not st.session_state.documents_processed:

        st.warning(
            "Please upload and process your documents first."
        )

        st.stop()


    # ========================================================
    # DISPLAY USER MESSAGE
    # ========================================================

    with st.chat_message("user"):

        st.markdown(
            input_text
        )


    # ========================================================
    # STORE USER MESSAGE
    # ========================================================

    st.session_state.messages.append(
        {
            "role": "user",
            "content": input_text
        }
    )


    # ========================================================
    # GIVE FIRST QUESTION AS CHAT NAME
    # ========================================================

    if (
        st.session_state.sessions[
            st.session_state.current_session_id
        ]["name"] == "New Chat"
    ):

        short_name = input_text[:30]

        if len(input_text) > 30:
            short_name += "..."

        st.session_state.sessions[
            st.session_state.current_session_id
        ]["name"] = short_name


    # ========================================================
    # GENERATE RESPONSE
    # ========================================================

    with st.chat_message("assistant"):

        with st.spinner(
            "Searching your documents..."
        ):

            try:

                response = (
                    st.session_state
                    .rag_chain
                    .invoke(
                        {
                            "input": input_text
                        },
                        config={
                            "configurable": {
                                "session_id":
                                st.session_state.current_session_id
                            }
                        }
                    )
                )


                st.markdown(
                    response
                )


            except Exception as e:

                response = (
                    "Sorry, I encountered an error "
                    "while processing your question."
                )

                st.error(
                    str(e)
                )


    # ========================================================
    # STORE RESPONSE
    # ========================================================

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": response
        }
    )


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
    <div class="footer">
        Created by Koushik Asrith Mulavisala
    </div>
    """,
    unsafe_allow_html=True
)

