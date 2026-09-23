import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

api_key = os.getenv("APIKey")

# Checking whether APIKey is in .env file
if not api_key:
    print("❌ Error: 'APIKey' is not found in .env")
else:
    print("🔑 'APIKey' founded in .env... Sending test request \n")
    
    try:
        # Initializing Groq client 
        client = Groq(api_key=api_key)

        # Sending Testing Prompt to API
        response = client.chat.completions.create(
            messages=[
                {"role": "user", "content": "Hello! Testing API connection."}
            ],
            model="openai/gpt-oss-20b",
        )

        # Successfull Prompt 
        print("✅ SUCCESS! API working fine.")
        print("🤖 Response:", response.choices[0].message.content)

    except Exception as e:
        # In case of any Error (Invalid Key or Network Error)
        print("❌ API Error: Key is not working as exoected")
        print("Details:", e)