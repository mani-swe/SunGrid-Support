# SunGrid Support - AI Assistant

An AI-powered customer support application developed for **SunGrid**. The application features a clean user interface where users can ask questions regarding SunGrid services and receive instant, automated answers powered by the **Groq API** using the `openai/gpt-oss-20b` model.

---

## 🚀 Features

- **Customer Support AI:** Custom system prompt tuned to assist users with SunGrid support queries.
- **Fast Response Generation:** Leverages Groq's low-latency inference with the `openai/gpt-oss-20b` model.
- **RESTful API Backend:** Lightweight Flask server with CORS enabled to seamlessly communicate with the frontend.
- **Interactive UI:** Simple, clean, and responsive interface with real-time feedback (loading state & error handling).

---

## 🛠️ Tech Stack

- **Frontend:** HTML5, CSS3, JavaScript (Fetch API)
- **Backend:** Python, Flask, Flask-CORS
- **AI Engine:** Groq Cloud SDK (`groq`)
- **Environment Management:** `python-dotenv`

---

## ⚙️️ Prerequisites

Before you begin, ensure you have the following installed on your system:

- [Python 3.8+](https://www.python.org/downloads/)
- [Git](https://git-scm.com/)
- A **Groq API Key** (Obtain from [Groq Console](https://console.groq.com/))

---

## 📥 Installation & Setup Instructions

Follow these instructions and run these commands step-by-step on your terminal of VSCode to get the project running locally:

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

### 6. Launch the Application

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
├── .venv/              # Virtual environment directory
├── .env                # Environment variables (API keys)
├── .env.example        # Template for enviroments variables
├── .gitignore          # Git ignore rules
├── index.html          # Frontend interface
├── main.py             # Flask server & Groq integration
├── requirements.txt    # Project dependencies
└── README.md           # Project documentation
```
