
from pathlib import Path
from voice import process_audio


ROOT_DIR = Path(__file__).resolve().parent
AUDIO_DIR = ROOT_DIR / "audio"
OUTPUT_DIR = ROOT_DIR / "outputs"


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    if not AUDIO_DIR.exists():
        print(f"Audio folder nahi mila: {AUDIO_DIR}")
        return

    files = sorted(AUDIO_DIR.glob("*.wav"))

    if not files:
        print("audio folder mein koi WAV file nahi mili.")
        return

    successful = 0
    failed = 0

    print(f"Total WAV files: {len(files)}")

    for index, audio_file in enumerate(files, start=1):
        print(f"\n[{index}/{len(files)}] Processing: {audio_file.name}")

        try:
            process_audio(audio_file)
            successful += 1
        except Exception as error:
            failed += 1
            print(f"Failed: {audio_file.name} - {error}")

    print("\nBatch processing complete.")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    print(f"Output folder: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
