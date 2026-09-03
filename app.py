import os
import tempfile
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

    /* ========================================================
       REMOVE CHAT AVATARS
       ======================================================== */

    [data-testid="stChatMessageAvatarUser"],
    [data-testid="stChatMessageAvatarAssistant"] {

        display: none;

    }


    /* ========================================================
       MAIN TITLE
       ======================================================== */

    .main-title {

        text-align: center;

        font-size: 46px;

        font-weight: 700;

        margin-top: 25px;

        margin-bottom: 5px;

    }


    /* ========================================================
       SUBTITLE
       ======================================================== */

    .subtitle {

        text-align: center;

        font-size: 16px;

        color: #9ca3af;

        margin-bottom: 30px;

    }


    /* ========================================================
       STATUS CARD
       ======================================================== */

    .status-card {

        padding: 15px;

        border-radius: 10px;

        margin-top: 15px;

        margin-bottom: 15px;

        border: 1px solid rgba(128,128,128,0.2);

    }


    /* ========================================================
       FOOTER
       ======================================================== */

    .footer {
    position: fixed;
    bottom: 8px;
    width: 100%;
    text-align: center;
    font-size: 11px;
    color: #999;
    font-weight: normal;
}


    /* ========================================================
       CHAT INPUT
       ======================================================== */

    [data-testid="stChatInput"] {

        bottom: 35px;

    }


    /* ========================================================
       BOTTOM SPACE
       ======================================================== */

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

    st.markdown("## 📄 Documents")

    st.write(
        "Upload one or more PDF documents "
        "to start chatting."
    )


    # ========================================================
    # FILE UPLOADER
    # ========================================================

    uploaded_files = st.file_uploader(
        "Upload PDF files",
        type=["pdf"],
        accept_multiple_files=True
    )


    # ========================================================
    # PROCESS BUTTON
    # ========================================================

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


            # =================================================
            # LOAD PDFs
            # =================================================

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

                    # Remove temporary file
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


# ============================================================
# SIDEBAR STATUS
# ============================================================

with st.sidebar:

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
    # CLEAR CHAT
    # ========================================================

    st.divider()

    if st.button(
        "🗑️ Clear Conversation",
        use_container_width=True
    ):

        st.session_state.messages = []

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
                    .invoke(input_text)
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

# Footer
st.markdown(
    """
    <div class="footer">
        Created by Koushik Asrith Mulavisala
    </div>
    """,
    unsafe_allow_html=True
)