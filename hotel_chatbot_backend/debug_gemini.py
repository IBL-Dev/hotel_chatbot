
import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("Error: GEMINI_API_KEY not found in environment variables.")
    exit(1)

genai.configure(api_key=api_key)

print("Listing available models...")
try:
    with open("models_list.txt", "w") as f:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                f.write(f"Name: {m.name}\n")
    print("Models written to models_list.txt")
except Exception as e:
    with open("models_list.txt", "w") as f:
        f.write(f"Error listing models: {e}")
    print(f"Error: {e}")
