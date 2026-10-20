"""Automated Stage 4 multi-turn continuity diagnostic (no persistent writes).

Runs paired normal/selective sequences using generated responses as subsequent
context. No user-history file is read or written; no ALFI.record() is called.
Human review is required for semantic correctness.
"""
import argparse
import contextlib
from datetime import datetime, timezone
import io
import json
import os
from pathlib import Path
import sys
import tempfile
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from first_ai import ALFI, HISTORY_FILE

SCENARIOS = [
    {"id": "F1", "kind": "followup", "turns": [
        "Explain photosynthesis in simple terms.",
        "Why is it important?",
        "Give me another example."]},
    {"id": "F2", "kind": "followup", "turns": [
        "Explain what a computer firewall does.",
        "How does it work?",
        "Tell me more about that."]},
    {"id": "T1", "kind": "topic_shift", "turns": [
        "What does a bicycle helmet protect?",
        "A theater sells three tickets for $9 each, with an additional unspecified booking fee. What is the exact total including the fee?",
        "Explain that."]},
    {"id": "T2", "kind": "topic_shift", "turns": [
        "Explain the water cycle.",
        "A museum charges $6 per ticket for four tickets and an unknown service charge. What is the exact total including the charge?",
        "Why is it important?"]},
]


def run_scenarios(scenarios, model, url):
    results = []
    with tempfile.TemporaryDirectory(prefix="alfi-stage4-continuity-") as folder:
        ai = ALFI(Path(folder) / "ai_memory.json", ollama_model=model, ollama_url=url)
        ai.debug = True
        for index, scenario in enumerate(scenarios):
            order = ("normal", "selective") if index % 2 == 0 else ("selective", "normal")
            for condition in order:
                ai.history = []
                turns = []
                for question in scenario["turns"]:
                    diagnostic_output = io.StringIO()
                    with patch.dict(os.environ, {
                        "ALFI_DIAGNOSTIC_NO_HISTORY": "0",
                        "ALFI_STAGE4_SELECTIVE_HISTORY": "1" if condition == "selective" else "0",
                    }):
                        with contextlib.redirect_stderr(diagnostic_output):
                            answer = ai.generate(question)
                    fields = {}
                    for line in diagnostic_output.getvalue().splitlines():
                        if line.startswith("[ALFI DEBUG] "):
                            key, _, value = line[len("[ALFI DEBUG] "):].partition(": ")
                            if key in {"prompt_history_mode", "prompt_message_count",
                                       "prompt_saved_memory_matches", "prompt_history_pairs",
                                       "prompt_system_messages", "prompt_user_question",
                                       "prompt_generation_options", "corrective_retry",
                                       "final_source", "format_violation"}:
                                fields[key] = value
                    if not isinstance(answer, str) or not answer.strip() or answer.startswith("I couldn't reach my local AI engine."):
                        raise RuntimeError(f"Model unavailable or empty answer: {scenario['id']} {condition} turn {len(turns)+1}: {answer}")
                    turns.append({"question": question, "answer": answer, "diagnostics": fields})
                    ai.history.append({"user": question, "assistant": answer})
                results.append({"scenario": scenario["id"], "kind": scenario["kind"],
                                "condition": condition, "turns": turns})
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default="stage4_continuity_report.json")
    parser.add_argument("--model", default=os.environ.get("ALFI_OLLAMA_MODEL", "gemma3:4b"))
    parser.add_argument("--url", default="http://127.0.0.1:11434/api/chat")
    args = parser.parse_args()
    output = Path(args.output).resolve()
    if output == Path(HISTORY_FILE).resolve():
        parser.error("Cannot overwrite conversation history")
    if output.exists():
        parser.error("Output already exists; choose a new path")
    report = {
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "model": args.model,
        "comparison": "normal_vs_selective_multiturn",
        "history_source": "isolated synthetic scenario turns only",
        "generation_options": "Ollama defaults (not seeded)",
        "scoring": "Human review required; no automatic semantic correctness claims",
        "runs": run_scenarios(SCENARIOS, args.model, args.url),
    }
    output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"Completed {len(report['runs'])} sequences, {sum(len(x['turns']) for x in report['runs'])} turns. Report: {output}")
    print("No persistent history written. Review model answers before sharing.")


if __name__ == "__main__":
    main()
