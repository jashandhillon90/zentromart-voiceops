# ZentroMart VoiceOps — AI Customer Support Agent

An AI-powered customer support agent built for the IIT Guwahati Consulting & Analytics Club × Gnani.ai VoiceOps 2026 capstone.

The system combines a Gemini-powered language model, TF-IDF-based retrieval-augmented generation (RAG), synthetic order lookup and verification tools, ticket handover, and Gnani.ai speech-to-text (STT) and text-to-speech (TTS).

## Features

- **Baseline LLM:** Answers customer questions without retrieved company evidence.
- **RAG:** Retrieves relevant Markdown knowledge-base documents using TF-IDF and cosine similarity.
- **Grounded responses:** Uses retrieved evidence for company-policy questions and cites source filenames where available.
- **Order verification:** Uses synthetic order data and requires a registered phone's last four digits or delivery pincode before revealing order details.
- **Human handover:** Creates a support ticket using the local mock ticket tool.
- **Voice support:** Transcribes audio through Gnani STT, generates a response, and produces spoken output through Gnani TTS.
- **Batch processing:** Processes WAV files in the `audio/` directory.
- **Evaluation:** Compares baseline and RAG responses against practice questions using automated keyword checks and records latency and errors.

## Project Structure

```text
.
├── audio/                  # Input WAV files
├── data/                   # Synthetic customer and order data
├── kb/                     # Company knowledge-base Markdown documents
├── outputs/                # Generated audio, JSON logs and evaluation results
├── practice/               # Questions and conversation datasets
├── tools/
│   └── tools.py             # Order lookup and ticket creation
├── batch_runner.py          # Batch audio processing
├── evaluate.py              # Baseline vs RAG evaluation
├── llm.py                   # Chat, RAG integration and conversation logic
├── rag.py                   # TF-IDF retrieval
├── run.py                   # Application entry point
├── voice.py                 # Gnani STT/TTS pipeline
├── requirements.txt
├── .env.example
└── README.md
```

## Requirements

- Python 3.10 or newer
- Gemini API key
- Gnani.ai API key for voice functionality
- Internet access for API-based features

## Setup

1. Create and activate a virtual environment.
2. Install dependencies.
3. Copy `.env.example` to `.env`.
4. Add your own API keys to `.env`.

Example PowerShell commands:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Set the following variables in `.env`:

```text
GEMINI_API_KEY=your_gemini_api_key
GNANI_API_KEY=your_gnani_api_key
```

Never commit `.env` or publish API keys.

## Running the Application

### Text chat

```powershell
python run.py --mode chat
```

Type `exit` to stop the interactive session.

### Process one audio file

```powershell
python run.py --mode voice --audio audio\customer_test.wav
```

### Batch-process WAV files

```powershell
python run.py --mode batch
```

Place input WAV files inside `audio/`. Generated replies and JSON result logs are written to `outputs/`.

### Run the evaluation

```powershell
python evaluate.py
```

The evaluation script compares baseline and RAG responses and writes:

- `outputs/evaluation_results.csv`
- `outputs/evaluation_summary.json`

Evaluation requires Gemini API access and is subject to the model's API quotas. A quota error can prevent the full question set from completing. Check the output CSV and summary before reporting metrics.

## Order Verification and Ticket Handover

Order records are synthetic. The agent should request an order ID and verify the caller using either the last four digits of the registered phone number or the delivery pincode before disclosing order details.

The local ticket tool records handover requests. The agent should only confirm that a ticket was created when the tool reports successful creation.

## Voice Pipeline

1. Read an input WAV file.
2. Transcribe the customer audio using Gnani STT.
3. Pass the transcript to the customer-support agent.
4. Generate spoken output using Gnani TTS.
5. Save the generated WAV file and a JSON result containing the transcript, response, and retrieved evidence.

The voice pipeline has been tested with a sample WAV file. Batch processing has also been tested with one WAV file. These tests do not establish performance across all audio conditions.

## Evaluation Notes

The practice dataset contains 52 questions. Automated `must_include` and `must_not_include` checks are keyword-based and should not be interpreted as a complete semantic accuracy score.

The current saved evaluation was interrupted by API quota errors. The saved results contain 7 successful baseline calls and 5 successful RAG calls out of 52 questions per mode. Therefore, the full 52-question comparison is incomplete and must not be reported as a completed benchmark.

## Limitations

- RAG uses TF-IDF retrieval, which may miss semantically related questions or relevant document sections.
- Model answers depend on the available evidence and API response.
- API quotas, network issues and service availability may affect evaluation and voice processing.
- The order and ticket tools use synthetic local data and are not production authentication or ticketing systems.
- Automated keyword checks do not replace manual answer-quality review.

## Security

- Keep `.env`, API keys, virtual environments and other secrets out of the submission archive and Git history.
- Use only synthetic customer data and authorized test recordings.
- Do not disclose order details until the mock verification flow succeeds.
