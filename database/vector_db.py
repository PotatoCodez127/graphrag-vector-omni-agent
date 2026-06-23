# database/vector_db.py
import chromadb
from chromadb.utils import embedding_functions


def setup_mock_vector_db():
    print("🚀 Initializing Company Vector Database...")
    chroma_client = chromadb.Client()  # Using an in-memory client for the capstone

    sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )

    collection = chroma_client.get_or_create_collection(
        name="company_handbook", embedding_function=sentence_transformer_ef
    )

    # Mock Document Data
    documents = [
        "RUST CODING STANDARDS (eng_handbook_v2.pdf): All Rust projects must use strict memory management logging. Unsafe blocks are heavily discouraged unless reviewed by a Lead Engineer.",
        "PYTHON STANDARDS (eng_handbook_v2.pdf): Python code must adhere to PEP 8 and use type hinting for all function arguments.",
        "PTO POLICY (hr_handbook_v1.pdf): Employees are entitled to 20 days of paid time off per year. PTO requests must be submitted 2 weeks in advance.",
    ]
    ids = ["doc_rust", "doc_python", "doc_pto"]

    collection.upsert(documents=documents, ids=ids)
    return collection


# Initialize it
vector_collection = setup_mock_vector_db()
