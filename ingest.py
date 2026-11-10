import json
import os
import re
import faiss
import numpy as np
from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    UnstructuredMarkdownLoader,
)
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer

DATA_DIR = "./data"

def clean_text(text: str) -> str:
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()

def load_documents(data_path: str):
    documents = []

    for file in os.listdir(data_path):
        file_path = os.path.join(data_path, file)

        if file.endswith(".md"):
            print(f"Loading Markdown file: {file}")
            loader = TextLoader(file_path, encoding="utf-8")
            loaded_docs = loader.load()
            for doc in loaded_docs:
                doc.page_content = clean_text(doc.page_content)
                documents.append(doc)

        elif file.endswith(".pdf"):
            print(f"Loading PDF file: {file}")
            loader = PyPDFLoader(file_path)
            loaded_docs = loader.load()
            for doc in loaded_docs:
                doc.page_content = clean_text(doc.page_content)
                documents.append(doc)

    return documents

def chunk_documents(documents, chunk_size=500, chunk_overlap=50):
    text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        chunk_size=chunk_size, chunk_overlap=chunk_overlap
    )
    chunks = text_splitter.split_documents(documents)
    return chunks

if __name__ == "__main__":
    print("--- Starting Document Ingestion Pipeline ---")

    raw_docs = load_documents(DATA_DIR)
    print(f"Total raw document pages loaded: {len(raw_docs)}")

    chunks = chunk_documents(raw_docs, chunk_size=500, chunk_overlap=50)
    print(f"Total 500-token chunks created: {len(chunks)}")

    if chunks:
        print("\n--- Sample Chunk Preview (Chunk 1) ---")
        print(f"Source: {chunks[0].metadata.get('source')}")
        print(f"Content Length: {len(chunks[0].page_content)} characters")
        print(f"Content:\n{chunks[0].page_content[:300]}...\n")

        print("Initializing embedding model (all-MiniLM-L6-v2)...")
        model = SentenceTransformer("all-MiniLM-L6-v2")

        print("Converting text chunks into vector embeddings...")
        texts = [chunk.page_content for chunk in chunks]
        embeddings = model.encode(texts, convert_to_numpy=True)

        dimension = embeddings.shape[1]

        print("Building FAISS index...")
        index = faiss.IndexFlatL2(dimension)
        index.add(embeddings)

        faiss_file_path = "solar_docs.index"
        faiss.write_index(index, faiss_file_path)
        print(f"FAISS index successfully saved: {faiss_file_path}")

        metadata = {}
        for i, chunk in enumerate(chunks):
            metadata[str(i)] = {
                "text": chunk.page_content,
                "source": chunk.metadata.get("source", "Unknown"),
            }

        json_file_path = "solar_metadata.json"
        with open(json_file_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, ensure_ascii=False, indent=4)

        print(f"Metadata JSON successfully saved: {json_file_path}")
        print("\nPipeline execution completed successfully. All artifacts stored.")