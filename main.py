import os
import json
from dotenv import load_dotenv
from groq import Groq
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS

load_dotenv()

app = Flask(__name__)
CORS(app)

api_key = os.getenv("APIKey")

if not api_key:
    print("❌ Error: 'APIKey' is not found in .env")
else:
    print("🔑 'APIKey' found in .env... Server setup ready! \n")
    client = Groq(api_key=api_key)

# 1. Route to serve index.html page (Requirement for /prompt-test)
@app.route('/prompt-test', methods=['GET'])
def serve_index():
    return send_file('index.html')

# 2. API Endpoint for asking questions
@app.route('/api/ask', methods=['POST'])
def ask_ai():
    try:
        data = request.get_json()
        user_prompt = data.get("prompt", "")

        if not user_prompt:
            return jsonify({
                "answer": "Prompt cannot be empty.",
                "source": "System Validation",
                "confidence": 0.0
            }), 400

        # System prompt instructing Groq to return JSON with required fields
        system_instructions = (
            "You are a customer support AI assistant for SunGrid. "
            "You MUST reply ONLY in raw JSON format with three exact keys:\n"
            "1. 'answer': (string) Clear, helpful response to the user query.\n"
            "2. 'source': (string) Indicate source, e.g., 'Groq Model'.\n"
            "3. 'confidence': (float) A realistic score between 0.00 and 1.00 based on how confident you are in your answer.\n\n"
            "Do not include any extra markdown formatting (like ```json), just raw valid JSON."
        )

        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_instructions},
                {"role": "user", "content": user_prompt}
            ],
            model="openai/gpt-oss-20b",
            response_format={"type": "json_object"} # Groq JSON Mode enable kiya
        )

        ai_raw_content = response.choices[0].message.content.strip()

        # Try parsing JSON from Groq
        try:
            parsed_data = json.loads(ai_raw_content)
            return jsonify({
                "answer": parsed_data.get("answer", ai_raw_content),
                "source": parsed_data.get("source", "Groq Model Data"),
                "confidence": float(parsed_data.get("confidence", 0.90))
            })
        except json.JSONDecodeError:
            # Fallback if AI output formatting slightly misses
            return jsonify({
                "answer": ai_raw_content,
                "source": "Groq Model Knowledge Base",
                "confidence": 0.88
            })

    except Exception as e:
        print("❌ API Error:", e)
        return jsonify({
            "answer": "Something went wrong while contacting the AI API.",
            "source": "Server Error Logs",
            "confidence": 0.0
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)