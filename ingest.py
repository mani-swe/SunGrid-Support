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
  """Clean raw text: remove excessive whitespaces, broken lines, and redundant line breaks."""
  # Multiple spaces ko single space banao
  text = re.sub(r"[ \t]+", " ", text)
  # 3 ya us se zyada newlines ko double newline me convert karo
  text = re.sub(r"\n{3,}", "\n\n", text)
  return text.strip()


def load_documents(data_path: str):
  """Data folder me se .md aur .pdf files load aur clean karta ha."""
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
  """Documents ko approx 500-token chunks me divide karta ha using tiktoken."""
  text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
      chunk_size=chunk_size, chunk_overlap=chunk_overlap
  )

  chunks = text_splitter.split_documents(documents)
  return chunks


if __name__ == "__main__":
  print("--- Starting Document Ingestion Pipeline ---")

  # 1. Load & Clean
  raw_docs = load_documents(DATA_DIR)
  print(f"Total raw document pages loaded: {len(raw_docs)}")

  # 2. Chunking
  chunks = chunk_documents(raw_docs, chunk_size=500, chunk_overlap=50)
  print(f"Total 500-token chunks created: {len(chunks)}")

  # Testing/Debugging output: First chunk ka preview
  if chunks:
    print("\n--- Sample Chunk Preview (Chunk 1) ---")
    print(f"Source: {chunks[0].metadata.get('source')}")
    print(f"Content Length: {len(chunks[0].page_content)} characters")
    print(f"Content:\n{chunks[0].page_content[:300]}...\n")

    # 3. Embeddings & FAISS Index Saving (Naya Add Kiya Gaya Hissa)
    print("3. Embedding model (all-MiniLM-L6-v2) load ho raha hai...")
    model = SentenceTransformer("all-MiniLM-L6-v2")

    print("4. Text chunks ko vectors mein convert kiya ja raha hai...")
    texts = [chunk.page_content for chunk in chunks]
    embeddings = model.encode(texts, convert_to_numpy=True)

    dimension = embeddings.shape[1]

    print("5. FAISS Index banaya ja raha hai...")
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)

    # Disk par FAISS index save karna
    faiss_file_path = "solar_docs.index"
    faiss.write_index(index, faiss_file_path)
    print(f"FAISS index successfully save ho gaya: {faiss_file_path}")

    # 6. Metadata JSON Mapping banana aur save karna
    metadata = {}
    for i, chunk in enumerate(chunks):
      metadata[str(i)] = {
          "text": chunk.page_content,
          "source": chunk.metadata.get("source", "Unknown"),
      }

    json_file_path = "solar_metadata.json"
    with open(json_file_path, "w", encoding="utf-8") as f:
      json.dump(metadata, f, ensure_ascii=False, indent=4)

    print(f"Metadata JSON successfully save ho gaya: {json_file_path}")
    print(
        "\n Mubarak ho! Ingestion pipeline mukammal ho gayi aur files save"
        " ho chuki hain."
    )