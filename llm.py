
import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Load API key from .env
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError(
        "GEMINI_API_KEY missing hai. .env file check karo."
    )

client = genai.Client(api_key=api_key)

SYSTEM_PROMPT = """
You are the AI customer support assistant for ZentroMart,
an Indian online store selling groceries and electronics.

Rules:
1. Introduce yourself as an AI assistant when appropriate.
2. Be polite, clear, and concise.
3. Never invent order details, refund amounts, or company policies.
4. If you do not know an answer, say so honestly.
5. Never claim to have checked an order or created a ticket
   unless the relevant tool actually succeeded.
6. This is the baseline chatbot. You do not have access to
   company knowledge documents or order tools yet.
"""

print("=== ZentroMart AI Support Agent ===")
print("Powered by Gemini")
print("Type 'exit' to stop.\n")

# Keep conversation history for multi-turn testing
history = []

while True:
    question = input("You: ").strip()

    if question.lower() == "exit":
        print("Bot: Goodbye!")
        break

    if not question:
        continue

    history.append({
        "role": "user",
        "parts": [{"text": question}]
    })

    try:
        response = client.models.generate_content(
            model="gemini-3.8-flash",
            contents=history,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT
                
            )
        )

        answer = response.text

        if not answer:
            print("\nBot: No text response received.\n")
            history.pop()
            continue

        print("\nBot:", answer, "\n")

        history.append({
            "role": "model",
            "parts": [{"text": answer}]
        })

    except Exception as error:
        # Remove failed user message from history
        history.pop()

        print("\nAPI request failed:", str(error))
        print("Check API key, model availability, quota and internet.\n")
