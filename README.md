# SunGrid Support - AI Assistant

An AI-powered customer support application developed for **SunGrid**. The application features a clean user interface where users can ask questions regarding SunGrid services and receive instant, automated answers powered by the **Groq API** using a local RAG (Retrieval-Augmented Generation) pipeline.

---

## 🚀 Features

- **Customer Support AI:** Custom system prompt tuned to assist users with SunGrid support queries.
- **RAG Pipeline & Vector Search:** Uses FAISS and Sentence Transformers for fast, context-aware document retrieval.
- **Automated Ingestion Script:** Processes local documents, cleans text, creates optimized chunks, and builds vector indices.
- **Fast Response Generation:** Leverages Groq's low-latency inference.
- **RESTful API Backend:** Lightweight Flask server with CORS enabled to seamlessly communicate with the frontend.
- **Interactive UI:** Simple, clean, and responsive interface with real-time feedback (loading state & error handling).

---

## 🛠️ Tech Stack

- **Frontend:** HTML5, CSS3, JavaScript (Fetch API)
- **Backend:** Python, Flask, Flask-CORS
- **AI & Embeddings Engine:** Groq Cloud SDK (`groq`), SentenceTransformers (`all-MiniLM-L6-v2`), FAISS-CPU
- **Document Processing:** LangChain (`PyPDFLoader`, `TextLoader`, `RecursiveCharacterTextSplitter`)
- **Environment Management:** `python-dotenv`

---

## ⚙️ Prerequisites

Before you begin, ensure you have the following installed on your system:

- [Python 3.8+](https://www.python.org/downloads/)
- [Git](https://git-scm.com/)
- A **Groq API Key** (Obtain from [Groq Console](https://console.groq.com/))

---

## 📥 Installation & Setup Instructions

Follow these instructions and run these commands step-by-step on your terminal in VS Code to get the project running locally:

### 1. Clone the Repository

git clone [https://github.com/mani-swe/SunGrid-Support.git](https://github.com/mani-swe/SunGrid-Support.git)

### 2. Setup a Virtual Enviroment

- **On Windows:**
  python -m venv .venv
  .venv\Scripts\activate

- **On MacOS/Linux:**
  python3 -m venv .venv
  source .venv/bin/activate

### 3. Install Dependencies

pip install -r requirements.txt

### 4. Confiure Enviroments Variables

- **On Windows (Command Prompt)**
  copy .env.example .env

- **On Windows (PowerShell) / macOS / Linux**
  cp .env.example .env

### 5. Open .env and Insert your APIKey

APIKey = "Paste Your APIKey Here"

---

## 📚 Document Ingestion Pipeline (ingest.py)

The application relies on a local document store to fetch accurate answers. The ingestion script processes your files through the following pipeline:

  ### 1.Supported Formats
  Place your documentation files inside the **Data/** folder. The script automatically supports:
  - Markdown (.md)
  - Portable Document Format (.pdf)
  
  ### 2. Cleaning & Chunking:
  - Raw text is cleaned to remove excessive whitespaces and redundant line breaks.
  - Documents are split into chunks of approx. 500 tokens with a 50-token overlap using LangChain's **RecursiveCharacterTextSplitter**.

  ### 3. Embeddings & Indexing:
  - Converts chunks into numerical vector embeddings using the **all-MiniLM-L6-v2** model.
  - Builds a FAISS index **(IndexFlatL2)** for high-speed similarity search.
  - Generates a metadata map linking chunks to their source files.

  ## How to Add New Documents & Re-run Ingestion:
  If you add new documents or update existing ones, follow these steps:
    1. Drop your new *.md* or *.pdf* files inside the **Data/** directory.
    2. Run the ingestion script in your terminal:

        python ingest.py

    3. This will process the files and automatically update/overwrite:
      - solar_docs.index (The FAISS vector database) 
      - solar_metadata.json (The source-to-text metadata mapping)

---

## 🚀 Launch the Application

- **Start the Flask Server**
  pyhton main.py

- **Open this Link on Web browser**
  http://127.0.0.1:5000/prompt-test

            **OR**

  Open index.html on web browser

- **Here, the application is successfully running on your computer**

---

## 📁 Project Structure

```SunGrid-Support
.
├── .vscode/               # VS Code configuration settings
├── Data/                  # Folder storing source documentation (.md and .pdf files)
├── .env                   # Environment variables (API keys)
├── .env.example           # Template for environment variables
├── .gitignore             # Git ignore rules
├── index.html             # Frontend user interface
├── ingest.py              # Automated RAG document ingestion script
├── main.py                # Flask server & AI integration backend
├── requirements.txt       # Project dependencies
├── solar_docs.index       # Generated FAISS vector index file
├── solar_metadata.json    # Generated text and source metadata mapping
└── README.md              # Project documentation
```
