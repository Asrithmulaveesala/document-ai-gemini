
import sys
import json
from pathlib import Path

# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIR = BASE_DIR / "backend"

# Allow importing rag.py from backend
sys.path.insert(0, str(BACKEND_DIR))

# ============================================================
# IMPORTS
# ============================================================

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from rag import embeddings

from langchain_community.vectorstores import FAISS


# ============================================================
# FILE PATHS
# ============================================================

PDF_PATH = BACKEND_DIR / "temp_uploaded.pdf"
DATASET_PATH = Path(__file__).resolve().parent / "evalution_dataset.json"

# ============================================================
# CHECK FILES
# ============================================================

if not PDF_PATH.exists():
    raise FileNotFoundError(
        f"PDF not found: {PDF_PATH}"
    )

if not DATASET_PATH.exists():
    raise FileNotFoundError(
        f"Evaluation dataset not found: {DATASET_PATH}"
    )


# ============================================================
# LOAD PDF
# ============================================================

loader = PyPDFLoader(str(PDF_PATH))

documents = loader.load()


# ============================================================
# SPLIT DOCUMENT
# Same settings as rag.py
# ============================================================

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)

chunks = text_splitter.split_documents(documents)


# ============================================================
# ASSIGN CHUNK IDs
# ============================================================

for chunk_id, chunk in enumerate(chunks):

    chunk.metadata["chunk_id"] = chunk_id


print(f"Total chunks: {len(chunks)}")


# ============================================================
# CREATE FAISS VECTOR STORE
# ============================================================

print("\nCreating FAISS vector store...")

vectorstore = FAISS.from_documents(
    documents=chunks,
    embedding=embeddings
)


# ============================================================
# CREATE RETRIEVER
# ============================================================

retriever = vectorstore.as_retriever(
    search_kwargs={
        "k": 4
    }
)


# ============================================================
# LOAD EVALUATION DATASET
# ============================================================

with open(DATASET_PATH, "r", encoding="utf-8") as f:

    evaluation_data = json.load(f)


# ============================================================
# METRIC FUNCTIONS
# ============================================================

def hit_at_k(
    retrieved_ids,
    relevant_ids,
    k
):

    retrieved_top_k = retrieved_ids[:k]

    return int(
        any(
            chunk_id in relevant_ids
            for chunk_id in retrieved_top_k
        )
    )


def precision_at_k(
    retrieved_ids,
    relevant_ids,
    k
):

    retrieved_top_k = retrieved_ids[:k]

    if not retrieved_top_k:
        return 0.0

    relevant_count = sum(
        chunk_id in relevant_ids
        for chunk_id in retrieved_top_k
    )

    return relevant_count / len(retrieved_top_k)


def recall_at_k(
    retrieved_ids,
    relevant_ids,
    k
):

    retrieved_top_k = retrieved_ids[:k]

    if not relevant_ids:
        return 0.0

    relevant_retrieved = sum(
        chunk_id in relevant_ids
        for chunk_id in retrieved_top_k
    )

    return relevant_retrieved / len(relevant_ids)


# ============================================================
# EVALUATION
# ============================================================

K = 4

hit_scores = []
precision_scores = []
recall_scores = []


print("\n")
print("=" * 70)
print("              RETRIEVAL EVALUATION")
print("=" * 70)


for item in evaluation_data:

    question = item["question"]

    relevant_ids = item["relevant_chunk_ids"]


    # --------------------------------------------------------
    # Retrieve chunks
    # --------------------------------------------------------

    retrieved_documents = retriever.invoke(question)


    # Get chunk IDs
    retrieved_ids = [
        doc.metadata["chunk_id"]
        for doc in retrieved_documents
    ]


    # --------------------------------------------------------
    # Calculate metrics
    # --------------------------------------------------------

    hit = hit_at_k(
        retrieved_ids,
        relevant_ids,
        K
    )

    precision = precision_at_k(
        retrieved_ids,
        relevant_ids,
        K
    )

    recall = recall_at_k(
        retrieved_ids,
        relevant_ids,
        K
    )


    # Store scores
    hit_scores.append(hit)
    precision_scores.append(precision)
    recall_scores.append(recall)


    # --------------------------------------------------------
    # Display result
    # --------------------------------------------------------

    print("\nQuestion:")
    print(question)

    print(f"Expected chunks : {relevant_ids}")
    print(f"Retrieved chunks: {retrieved_ids}")

    print(f"Hit@{K}        : {hit}")
    print(f"Precision@{K}  : {precision:.2f}")
    print(f"Recall@{K}     : {recall:.2f}")

    print("-" * 70)


# ============================================================
# OVERALL METRICS
# ============================================================

total_questions = len(evaluation_data)


if total_questions > 0:

    average_hit = sum(hit_scores) / total_questions

    average_precision = (
        sum(precision_scores)
        / total_questions
    )

    average_recall = (
        sum(recall_scores)
        / total_questions
    )

else:

    average_hit = 0.0
    average_precision = 0.0
    average_recall = 0.0


# ============================================================
# FINAL RESULTS
# ============================================================

print("\n")
print("=" * 70)
print("                 FINAL RESULTS")
print("=" * 70)

print(f"Number of questions : {total_questions}")

print(
    f"Hit@{K}              : "
    f"{average_hit:.2f}"
)

print(
    f"Precision@{K}        : "
    f"{average_precision:.2f}"
)

print(
    f"Recall@{K}           : "
    f"{average_recall:.2f}"
)

print("=" * 70)

