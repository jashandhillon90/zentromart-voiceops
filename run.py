
import argparse
from pathlib import Path

from llm import main as chat_main
from voice import process_audio


def main():
    parser = argparse.ArgumentParser(
        description="ZentroMart VoiceOps customer-support assistant"
    )

    parser.add_argument(
        "--mode",
        choices=["chat", "voice", "batch"],
        default="chat",
        help="chat: text conversation, voice: process one audio file, batch: process audio folder"
    )

    parser.add_argument(
        "--audio",
        type=str,
        help="Path to an audio file for voice mode"
    )

    args = parser.parse_args()

    if args.mode == "chat":
        chat_main()

    elif args.mode == "voice":
        if not args.audio:
            parser.error("Voice mode ke liye --audio path dena zaroori hai.")

        audio_path = Path(args.audio)

        if not audio_path.is_file():
            parser.error(f"Audio file nahi mili: {audio_path}")

        process_audio(audio_path)

    elif args.mode == "batch":
        from batch_runner import main as batch_main
        batch_main()


if __name__ == "__main__":
    main()
