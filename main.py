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
            "CRITICAL FORMATTING RULE: Write your response entirely in clean, readable plain text. "
            "Do NOT use markdown bolding (asterisks like **), bullet points, escape sequences (like /n, /n/n etc.) with special symbols, or raw escape formatting. "
            "Write in smooth, natural sentences and paragraphs. "
            "You must output a valid JSON object with a single key 'answer' containing your response text, like this: "
            '{"answer": "Your clean and polished response here"}'
        )

        user_content = f"Context:\n{context_text}\n\nQuestion: {user_prompt}"

        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_instructions},
                {"role": "user", "content": user_content}
            ],
            model="openai/gpt-oss-20b",
            response_format={"type": "json_object"}
        )

        ai_raw_content = response.choices[0].message.content.strip()
        
        try:
            parsed_json = json.loads(ai_raw_content)
            clean_answer = parsed_json.get("answer", ai_raw_content)
        except json.JSONDecodeError:
            clean_answer = ai_raw_content

        usage = getattr(response, 'usage', None)
        tokens_used = {
            "prompt_tokens": getattr(usage, 'prompt_tokens', 0) if usage else 0,
            "completion_tokens": getattr(usage, 'completion_tokens', 0) if usage else 0,
            "total_tokens": getattr(usage, 'total_tokens', 0) if usage else 0
        }

        latency_ms = int((time.time() - start_time) * 1000)

        return jsonify({
            "Answer": clean_answer,
            "Sources": sources,
            "Tokens Used": tokens_used,
            "Latency(ms)": latency_ms
        })

    except Exception as e:
        print("❌ Detailed API Error Traceback:")
        traceback.print_exc()
        
        latency_ms = int((time.time() - start_time) * 1000)
        
        return jsonify({
            "Answer": "I am currently experiencing technical difficulties connecting to the AI service. Please try again in a moment.",
            "Sources": [],
            "Tokens Used": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
            "Latency(ms)": latency_ms
        }), 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)