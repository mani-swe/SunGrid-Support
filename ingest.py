import os
import re
from langchain_community.document_loaders import PyPDFLoader, UnstructuredMarkdownLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

DATA_DIR = "./data"

def clean_text(text: str) -> str:
    """
    Clean raw text: remove excessive whitespaces, broken lines, and redundant line breaks.
    """
    # Multiple spaces ko single space banao
    text = re.sub(r'[ \t]+', ' ', text)
    # 3 ya us se zyada newlines ko double newline me convert karo
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()

def load_documents(data_path: str):
    """
    Data folder me se .md aur .pdf files load aur clean karta ha.
    """
    documents = []
    
    for file in os.listdir(data_path):
        file_path = os.path.join(data_path, file)
        
        if file.endswith(".md"):
            print(f"Loading Markdown file: {file}")
            # TextLoader ya UnstructuredMarkdownLoader use kar sakte ho
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
    """
    Documents ko approx 500-token chunks me divide karta ha using tiktoken.
    """
    # RecursiveCharacterTextSplitter token-based splitting handle karta ha
    text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        chunk_size=chunk_size,      # Target: 500 tokens
        chunk_overlap=chunk_overlap # Overlap context miss hone se bachata ha
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