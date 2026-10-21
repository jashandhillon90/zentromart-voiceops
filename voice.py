import os
import json
from pathlib import Path
from dotenv import load_dotenv
from gnani.stt import GnaniSTTClient
from gnani.tts import GnaniTTSClient
from llm import respond
from rag import retrieve_evidence

load_dotenv()

api_key = os.getenv("GNANI_API_KEY")

if not api_key:
    raise ValueError("GNANI_API_KEY .env file mein add karo.")

stt = GnaniSTTClient(api_key=api_key)
tts = GnaniTTSClient(api_key=api_key)

OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(exist_ok=True)


def process_audio(audio_path):
    audio_path = Path(audio_path)

    if not audio_path.exists():
        raise FileNotFoundError(f"Audio file nahi mili: {audio_path}")

    name = audio_path.stem

    # Convert audio speech into text.
    result = stt.transcribe(
        str(audio_path),
        language_code="en-IN"
    )

    print("DEBUG STT RESULT:", repr(result))

    if isinstance(result, dict):
        transcript = (
            result.get("transcript")
            or result.get("text")
            or ""
        ).strip()
    else:
        transcript = str(result).strip()

    if not transcript:
        raise ValueError(
            f"Transcript nahi mila. STT result: {result!r}"
        )

    # Retrieve knowledge-base evidence.
    chunks = retrieve_evidence(transcript)

    # Get the answer from the existing chatbot.
    answer = respond(transcript)

    # Convert the chatbot answer into speech.
    audio = tts.synthesize(
        answer,
        voice="Kaveri",
        model="timbre-v2.5",
        language="en-IN"
    )

    audio_path_out = OUTPUT_DIR / f"{name}_reply.wav"

    with open(audio_path_out, "wb") as file:
        file.write(audio)

    record = {
        "audio_file": str(audio_path),
        "transcript": transcript,
        "reply": answer,
        "retrieved_chunks": [
            {
                "source": chunk["source"],
                "score": chunk["score"],
                "text": chunk["text"]
            }
            for chunk in chunks
        ],
        "reply_audio": str(audio_path_out)
    }

    json_path = OUTPUT_DIR / f"{name}_result.json"

    with open(json_path, "w", encoding="utf-8") as file:
        json.dump(record, file, indent=2, ensure_ascii=False)

    print(f"\nAudio: {audio_path.name}")
    print(f"Customer: {transcript}")
    print(f"Bot: {answer}")
    print(f"Saved: {audio_path_out}")
    print(f"Saved: {json_path}")

    return record


if __name__ == "__main__":
    audio_file = input("Enter WAV audio file path: ").strip().strip('"')

    try:
        process_audio(audio_file)
    except Exception as error:
        print("Voice processing failed:", error)
