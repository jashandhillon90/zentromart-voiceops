import time
import os
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY .env file mein nahi mili.")

client = genai.Client(api_key=api_key)

KB_DIR = Path("kb")
TOP_K = 3

SYSTEM_PROMPT = """
You are ZentroMart's AI customer support assistant.

Answer using ONLY the supplied knowledge-base evidence.
If the evidence does not answer the question, clearly say:
"I couldn't find that information in the available company documents."
Do not invent policies, prices, dates, or order details.
Be polite and concise.
Cite the source filenames you used in your answer.
"""

def load_documents():
    documents = []

    for path in sorted(KB_DIR.rglob("*.md")):
        if "superseded" in path.name.lower():
            continue

        text = path.read_text(encoding="utf-8").strip()

        if text:
            documents.append({
                "source": str(path),
                "text": text
            })

    if not documents:
        raise FileNotFoundError(
            "kb folder mein koi Markdown (.md) document nahi mila."
        )

    return documents
documents = load_documents()

vectorizer = TfidfVectorizer(
    lowercase=True,
    stop_words="english",
    ngram_range=(1, 2)
)

document_matrix = vectorizer.fit_transform(
    [doc["text"] for doc in documents]
)

print(f"Loaded {len(documents)} knowledge-base documents.")
print("=== ZentroMart RAG Support Agent ===")
print("Type 'exit' to stop.\n")


while True:
    question = input("You: ").strip()

    if question.lower() == "exit":
        print("Bot: Goodbye!")
        break

    if not question:
        continue

    query_vector = vectorizer.transform([question])
    scores = cosine_similarity(
        query_vector, document_matrix
    ).flatten()

    top_indices = scores.argsort()[::-1][:TOP_K]

    # Ignore results with no lexical match
    retrieved = [
        (int(i), float(scores[i]))
        for i in top_indices
        if scores[i] > 0
    ]

    if not retrieved:
        print(
            "\nBot: I couldn't find relevant information "
            "in the available company documents.\n"
        )
        print("Retrieved chunks: none\n")
        continue

    evidence_parts = []

    print("\nRetrieved evidence:")
    for index, score in retrieved:
        doc = documents[index]
        print(f"- {doc['source']} (score: {score:.3f})")

        evidence_parts.append(
            f"SOURCE: {doc['source']}\n"
            f"CONTENT:\n{doc['text'][:4000]}"
        )

    evidence = "\n\n---\n\n".join(evidence_parts)

    try:
        response = client.models.generate_content(
            model="gemini-3.8-flash",
            contents=(
                "Knowledge-base evidence:\n\n"
                f"{evidence}\n\n"
                f"Customer question: {question}"
            ),
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT
            )
        )

        print("\nBot:", response.text or "No text response.")
        print()

    except Exception as error:
        print("\nAPI request failed:", str(error), "\n")
