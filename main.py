import os
import json
import time
import traceback
import faiss
import numpy as np
from dotenv import load_dotenv
from groq import Groq
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from sentence_transformers import SentenceTransformer

load_dotenv()

app = Flask(__name__)
CORS(app)

api_key = os.getenv("APIKey")

if not api_key:
    print("❌ Error: 'APIKey' is not found in .env")
else:
    print("🔑 'APIKey' found in .env... Server setup ready! \n")
    client = Groq(api_key=api_key)

try:
    faiss_index = faiss.read_index("solar_docs.index")
    with open("solar_metadata.json", "r", encoding="utf-8") as f:
        chunks_data = json.load(f)
    print("✅ FAISS index and JSON metadata loaded successfully!")
except Exception as e:
    print(f"⚠️ Warning: Could not load FAISS or JSON files: {e}")
    faiss_index = None
    chunks_data = {}

embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

def retrieve_chunks(query, k=3):
    if faiss_index is None or not chunks_data:
        return [], ["Default Knowledge Base"]
    
    query_vector = embedding_model.encode([query]).astype('float32')
    distances, indices = faiss_index.search(query_vector, k)
    
    retrieved_texts = []
    sources = []
    
    for idx in indices[0]:
        clean_idx = int(idx)
        if clean_idx != -1:
            chunk = chunks_data.get(str(clean_idx))
            if chunk:
                retrieved_texts.append(chunk.get("text", ""))
                raw_source = chunk.get("source", "solar_doc.pdf")
                # Sirf file ka naam extract karne ke liye (path hata kar)
                clean_source = os.path.basename(raw_source)
                if clean_source not in sources:
                    sources.append(clean_source)
            
    return retrieved_texts, sources

@app.route('/prompt-test', methods=['GET'])
def serve_index():
    return send_file('index.html')

@app.route('/api/ask', methods=['GET', 'POST'])
def ask_ai():
    start_time = time.time()
    
    if request.method == 'GET':
        user_prompt = request.args.get('question', '')
    else:
        data = request.get_json() or {}
        user_prompt = data.get("prompt", "") or data.get("question", "")

    if not user_prompt:
        return jsonify({
            "answer": "Prompt cannot be empty.",
            "sources": [],
            "tokens_used": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
            "latency_ms": 0
        }), 400

    try:
        relevant_chunks, sources = retrieve_chunks(user_prompt, k=3)
        context_text = "\n\n".join(relevant_chunks)

        system_instructions = (
            "You are a customer support AI assistant for SunGrid solar installations. "
            "Use the provided context information to answer the user's question accurately. "
            "If the answer is not in the context, use your general solar knowledge safely."
        )

        user_content = f"Context:\n{context_text}\n\nQuestion: {user_prompt}"

        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_instructions},
                {"role": "user", "content": user_content}
            ],
            model="openai/gpt-oss-20b",
        )

        ai_raw_content = response.choices[0].message.content.strip()
        
        usage = getattr(response, 'usage', None)
        tokens_used = {
            "prompt_tokens": getattr(usage, 'prompt_tokens', 0) if usage else 0,
            "completion_tokens": getattr(usage, 'completion_tokens', 0) if usage else 0,
            "total_tokens": getattr(usage, 'total_tokens', 0) if usage else 0
        }

        latency_ms = int((time.time() - start_time) * 1000)

        return jsonify({
            "answer": ai_raw_content,
            "sources": sources,
            "tokens_used": tokens_used,
            "latency_ms": latency_ms
        })

    except Exception as e:
        print("❌ Detailed API Error Traceback:")
        traceback.print_exc()
        
        return jsonify({
            "error": "Something went wrong while contacting the AI API.",
            "details": str(e)
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)