
import argparse
import json
import re
import time
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from google import genai
from google.genai import types
from rag import retrieve_evidence

load_dotenv()

client = genai.Client()
MODEL = "gemini-3.8-flash"

ROOT = Path(__file__).resolve().parent
QUESTIONS_FILE = ROOT / "practice" / "questions.csv"
OUTPUT_DIR = ROOT / "outputs"
RESULTS_FILE = OUTPUT_DIR / "evaluation_results.csv"
SUMMARY_FILE = OUTPUT_DIR / "evaluation_summary.json"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

SYSTEM_PROMPT = """
You are ZentroMart's customer-support assistant.
Be polite and concise.
Never invent company policies, prices, dates, or facts.
If information is unavailable, clearly say you do not have
enough information in the available company documents.
"""


def normalize(text):
    return re.sub(r"\s+", " ", str(text).lower()).strip()


def split_terms(value):
    if pd.isna(value) or not str(value).strip():
        return []

    return [
        term.strip().lower()
        for term in str(value).split(";")
        if term.strip()
    ]


def generate_answer(question, evidence=None):
    if evidence is None:
        prompt = f"""
Customer question:
{question}

Answer as a general customer-support chatbot without access to
ZentroMart's knowledge base. Do not invent company-specific facts.
If unsure, clearly say that you do not know.
"""
    else:
        evidence_text = "\n\n".join(
            f"Source: {chunk['source']}\n{chunk['text'][:3500]}"
            for chunk in evidence
        )

        if not evidence_text:
            evidence_text = "No relevant evidence retrieved."

        prompt = f"""
Company document evidence:
{evidence_text}

Customer question:
{question}

Answer using only the evidence above.
If the evidence does not support an answer, say the information
is unavailable. Cite the source filenames when using evidence.
"""

    response = client.models.generate_content(
        model=MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            temperature=0
        )
    )

    answer = (response.text or "").strip()

    if not answer:
        raise RuntimeError("EMPTY_MODEL_RESPONSE")

    return answer


def evaluate_terms(answer, must_include, must_not_include):
    text = normalize(answer)

    required = split_terms(must_include)
    forbidden = split_terms(must_not_include)

    required_found = [
        term for term in required
        if normalize(term) in text
    ]

    forbidden_found = [
        term for term in forbidden
        if normalize(term) in text
    ]

    required_ok = (
        len(required_found) == len(required)
        if required else None
    )

    forbidden_ok = len(forbidden_found) == 0

    return required_ok, forbidden_ok, required_found, forbidden_found


def is_quota_error(error_text):
    message = str(error_text).lower()

    quota_markers = [
        "resource_exhausted",
        "429",
        "quota exceeded",
        "quota failure",
        "rate limit",
        "requests per day",
        "limit: 0"
    ]

    return any(marker in message for marker in quota_markers)


def evaluate_one(row, mode):
    question = str(row.get("question", ""))
    start = time.perf_counter()

    answer = ""
    sources = []
    error = ""

    try:
        if mode == "baseline":
            answer = generate_answer(question)
        else:
            chunks = retrieve_evidence(question)
            sources = [chunk["source"] for chunk in chunks]
            answer = generate_answer(question, chunks)

    except Exception as exc:
        error = str(exc)

    latency = round(time.perf_counter() - start, 3)

    required_ok, forbidden_ok, found, forbidden_found = (
        evaluate_terms(
            answer,
            row.get("must_include", ""),
            row.get("must_not_include", "")
        )
    )

    answerable = (
        str(row.get("answerable", "")).strip().lower() == "true"
    )

    refusal_markers = [
        "couldn't find",
        "could not find",
        "don't have information",
        "do not have information",
        "not available",
        "not enough information",
        "can't find",
        "cannot find",
        "connect you",
        "colleague",
        "human agent"
    ]

    refusal = any(
        marker in normalize(answer)
        for marker in refusal_markers
    )

    if error:
        refusal_flag = "api_error"
    elif answerable and refusal:
        refusal_flag = "unexpected_refusal"
    elif not answerable and not refusal:
        refusal_flag = "possible_missing_refusal"
    else:
        refusal_flag = "not_flagged"

    return {
        "id": str(row.get("id", "")),
        "mode": mode,
        "question": question,
        "intent": row.get("intent", ""),
        "answerable": answerable,
        "answer": answer,
        "reference_answer": row.get("reference_answer", ""),
        "must_include_pass": required_ok,
        "must_include_found": "; ".join(found),
        "must_not_include_pass": forbidden_ok,
        "forbidden_terms_found": "; ".join(forbidden_found),
        "refusal_detected": refusal,
        "answerable_refusal_flag": refusal_flag,
        "retrieved_sources": "; ".join(sources),
        "retrieved_count": len(sources),
        "latency_seconds": latency,
        "error": error
    }


def load_existing_results():
    if not RESULTS_FILE.exists():
        return []

    try:
        df = pd.read_csv(
            RESULTS_FILE,
            dtype=str,
            keep_default_na=False
        )

        if "id" not in df.columns or "mode" not in df.columns:
            print("Existing CSV has an unexpected format; starting fresh.")
            return []

        return df.to_dict("records")

    except (pd.errors.EmptyDataError, pd.errors.ParserError, OSError):
        print("Could not read existing results; starting fresh.")
        return []


def save_results(results):
    df = pd.DataFrame(results)

    df.to_csv(
        RESULTS_FILE,
        index=False,
        encoding="utf-8-sig"
    )

    summary = {}

    for mode in ("baseline", "rag"):
        subset = df[df["mode"] == mode]

        if subset.empty:
            summary[mode] = {
                "total_questions": 0,
                "successful_calls": 0,
                "failed_calls": 0,
                "must_include_pass_rate": None,
                "must_not_include_pass_rate": None,
                "refusal_flag_count": 0,
                "average_latency_seconds": None
            }
            continue

        successful = subset[subset["error"].astype(str) == ""]
        failed_count = len(subset) - len(successful)

        required_checks = successful[
            "must_include_pass"
        ].dropna()

        required_checks = required_checks[
            required_checks.astype(str).str.lower().isin(
                ["true", "false"]
            )
        ]

        forbidden_checks = successful[
            "must_not_include_pass"
        ].dropna()

        forbidden_checks = forbidden_checks[
            forbidden_checks.astype(str).str.lower().isin(
                ["true", "false"]
            )
        ]

        summary[mode] = {
            "total_questions": int(len(subset)),
            "successful_calls": int(len(successful)),
            "failed_calls": int(failed_count),
            "must_include_pass_rate": (
                round(
                    required_checks.astype(str).str.lower()
                    .eq("true").mean(),
                    4
                )
                if len(required_checks) else None
            ),
            "must_not_include_pass_rate": (
                round(
                    forbidden_checks.astype(str).str.lower()
                    .eq("true").mean(),
                    4
                )
                if len(forbidden_checks) else None
            ),
            "refusal_flag_count": int(
                successful["answerable_refusal_flag"]
                .astype(str)
                .ne("not_flagged")
                .sum()
            ),
            "average_latency_seconds": (
                round(
                    pd.to_numeric(
                        successful["latency_seconds"],
                        errors="coerce"
                    ).mean(),
                    3
                )
                if len(successful) else None
            )
        }

    SUMMARY_FILE.write_text(
        json.dumps(summary, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    return summary


def main():
    parser = argparse.ArgumentParser(
        description="Evaluate ZentroMart baseline and RAG answers."
    )

    parser.add_argument(
        "--limit",
        type=int,
        default=0,
        help="Evaluate first N questions; 0 means all."
    )

    parser.add_argument(
        "--fresh",
        action="store_true",
        help="Start a new evaluation instead of resuming saved results."
    )

    args = parser.parse_args()

    if not QUESTIONS_FILE.exists():
        raise FileNotFoundError(
            f"Questions dataset not found: {QUESTIONS_FILE}"
        )

    questions = pd.read_csv(
        QUESTIONS_FILE,
        dtype=str
    ).fillna("")

    if args.limit > 0:
        questions = questions.head(args.limit)

    if args.fresh:
        results = []
        print("Starting a fresh evaluation.")
    else:
        results = load_existing_results()
        print("Resume mode enabled.")

    # Resume only successful calls for the selected question set.
    question_ids = set(questions["id"].astype(str))

    results = [
        result for result in results
        if str(result.get("id", "")) in question_ids
        and str(result.get("mode", "")) in ("baseline", "rag")
    ]

    completed = {
        (str(result.get("id", "")), str(result.get("mode", "")))
        for result in results
        if str(result.get("error", "")).strip() == ""
    }

    print(f"Questions in this run: {len(questions)}")
    print(f"Saved successful calls: {len(completed)}")
    print("Results are saved after every API call.")

    quota_hit = False

    for index, (_, row) in enumerate(
        questions.iterrows(),
        start=1
    ):
        question_id = str(row.get("id", ""))

        print(
            f"\n[{index}/{len(questions)}] "
            f"{question_id}: {row.get('question', '')}"
        )

        for mode in ("baseline", "rag"):
            key = (question_id, mode)

            if key in completed:
                print(f"  {mode.upper()}: already completed; skipping.")
                continue

            print(f"  Running {mode.upper()}...")

            result = evaluate_one(row, mode)

            # Replace a previous failed attempt for the same ID/mode.
            results = [
                old for old in results
                if not (
                    str(old.get("id", "")) == question_id
                    and str(old.get("mode", "")) == mode
                )
            ]

            results.append(result)

            # Save immediately, including failed attempts.
            summary = save_results(results)

            if result["error"]:
                print(f"  {mode.upper()} ERROR: {result['error']}")

                if is_quota_error(result["error"]):
                    print(
                        "\nGemini quota/rate limit detected. "
                        "Stopping now to avoid wasting more requests."
                    )
                    quota_hit = True
                    break
            else:
                completed.add(key)
                print(f"  {mode.upper()} answer saved.")

        if quota_hit:
            break

    print("\nEvaluation checkpoint saved.")
    print(f"Results CSV: {RESULTS_FILE}")
    print(f"Summary JSON: {SUMMARY_FILE}")
    print(json.dumps(save_results(results), indent=2))

    if quota_hit:
        print(
            "\nQuota abhi exhausted hai. API quota reset hone ke baad "
            "same command dobara run karna; successful calls skip "
            "ho jayengi aur failed question se resume hoga."
        )


if __name__ == "__main__":
    main()
