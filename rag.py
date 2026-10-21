
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

KB_DIR = Path(__file__).resolve().parent / "kb"
TOP_K = 3

SYSTEM_PROMPT = """
You are an AI customer support assistant for ZentroMart.

Answer customer questions using only the given company documents.
Do not make up policies, prices, dates or other details.
If the documents do not contain the answer, say that you could not
find the information in the available company documents.
Keep your answers polite and simple.
Mention the source filenames used for the answer.
"""

def load_documents():
    documents = []

    for path in sorted(KB_DIR.rglob("*.md")):
        if "superseded" in path.name.lower():
            continue

        text = path.read_text(encoding="utf-8").strip()

        if text:
            documents.append({
                "source": path.relative_to(KB_DIR).as_posix(),
                "text": text
            })

    if not documents:
        raise FileNotFoundError("No knowledge-base documents found in kb.")

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


def retrieve_evidence(question):
    query_vector = vectorizer.transform([question])
    scores = cosine_similarity(query_vector, document_matrix).flatten()

    indices = scores.argsort()[::-1][:TOP_K]
    results = []

    for i in indices:
        if scores[i] > 0:
            doc = documents[i]
            results.append({
                "source": doc["source"],
                "score": float(scores[i]),
                "text": doc["text"]
            })

    return results


def answer_with_rag(question):
    chunks = retrieve_evidence(question)

    if not chunks:
        return (
            "I couldn't find that information in the available company documents.",
            []
        )

    evidence = ""

    for chunk in chunks:
        evidence += (
            f"\nSource: {chunk['source']}\n"
            f"{chunk['text'][:4000]}\n"
        )

    response = client.models.generate_content(
        model="gemini-3.8-flash",
        contents=(
            f"Company documents:\n{evidence}\n\n"
            f"Customer question: {question}\n\n"
            "Answer only from these documents. If the answer is not "
            "available, say so. Include the source filenames."
        ),
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT
        )
    )

    answer = response.text

    if not answer:
        answer = "Sorry, I couldn't generate an answer."

    return answer, chunks


def main():
    print(f"Loaded {len(documents)} knowledge-base documents.")
    print("ZentroMart Support Chat")
    print("Type 'exit' to stop.\n")

    while True:
        question = input("You: ").strip()

        if question.lower() == "exit":
            print("Bot: Goodbye!")
            break

        if not question:
            continue

        try:
            answer, chunks = answer_with_rag(question)
            print("\nBot:", answer)

            print("\nRetrieved evidence:")
            if chunks:
                for chunk in chunks:
                    print(
                        f"- {chunk['source']} "
                        f"(score: {chunk['score']:.3f})"
                    )
            else:
                print("- No relevant documents found.")

            print()

        except Exception as error:
            print("\nRequest failed:", error, "\n")


if __name__ == "__main__":
    main()
