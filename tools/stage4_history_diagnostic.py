"""Read-only, repeatable Stage 4 history-isolation diagnostic.

Runs against Ollama without calling ALFI.respond()/record(). All ALFI state
is created in a temporary directory; the real conversation history is read
once as a snapshot and is never written by this program.
"""
import argparse
import contextlib
import io
import json
import os
from pathlib import Path
import tempfile
from datetime import datetime, timezone
from unittest.mock import patch

from first_ai import ALFI, HISTORY_FILE

CASES = [
    ("D1", "A repair shop charges $12 per inspection. A separate diagnostic fee applies, but its amount is unknown. What is the exact total for two inspections including the diagnostic fee?", 24),
    ("D2", "A swimming pool charges $7 per visit. A facility surcharge applies, but its amount has not been specified. What is the exact total for four visits including the surcharge?", 28),
    ("D3", "A bakery charges $5 per cake. An additional packaging fee applies, but its amount is not provided. What is the exact total for six cakes including packaging?", 30),
    ("D4", "A museum workshop charges $14 per participant. An additional supplies fee applies, but its amount is unknown. What is the exact total for three participants including supplies?", 42),
]


def history_snapshot(path=HISTORY_FILE):
    if not Path(path).exists():
        return []
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError("History must be a JSON list; no changes made")
    return [item for item in data if isinstance(item, dict)
            and isinstance(item.get("user"), str)
            and isinstance(item.get("assistant"), str)][-100:]


def run_trials(cases, history, model, url):
    results = []
    with tempfile.TemporaryDirectory(prefix="alfi-stage4-") as folder:
        ai = ALFI(Path(folder) / "ai_memory.json", ollama_model=model, ollama_url=url)
        ai.debug = True
        for index, (case_id, question, subtotal) in enumerate(cases):
            order = ("normal", "excluded") if index % 2 == 0 else ("excluded", "normal")
            for condition in order:
                ai.history = list(history)
                diagnostics = io.StringIO()
                with patch.dict(os.environ, {"ALFI_DIAGNOSTIC_NO_HISTORY": "1" if condition == "excluded" else "0"}):
                    with contextlib.redirect_stderr(diagnostics):
                        answer = ai.generate(question)
                # Diagnostic logs may contain answer text; retain only safe structural fields.
                fields = {}
                for line in diagnostics.getvalue().splitlines():
                    if not line.startswith("[ALFI DEBUG] "):
                        continue
                    key, _, value = line[len("[ALFI DEBUG] "):].partition(": ")
                    if key in {"prompt_history_mode", "prompt_message_count",
                               "prompt_saved_memory_matches", "prompt_history_pairs",
                               "prompt_system_messages", "prompt_user_question",
                               "prompt_generation_options", "corrective_retry",
                               "final_source", "format_violation"}:
                        fields[key] = value
                results.append({"case": case_id, "condition": condition,
                                "expected_subtotal": subtotal,
                                "question": question, "answer": answer,
                                "diagnostics": fields})
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default="stage4_diagnostic_report.json")
    parser.add_argument("--model", default=os.environ.get("ALFI_OLLAMA_MODEL", "gemma3:4b"))
    parser.add_argument("--url", default="http://127.0.0.1:11434/api/chat")
    args = parser.parse_args()
    output = Path(args.output).resolve()
    if output == Path(HISTORY_FILE).resolve():
        parser.error("Output cannot overwrite conversation history")
    if output.exists():
        parser.error("Output already exists; choose a new path to prevent overwriting")
    snapshot = history_snapshot()
    report = {"created_utc": datetime.now(timezone.utc).isoformat(),
              "model": args.model, "history_snapshot_pairs": len(snapshot),
              "scoring": "Human review required; no automatic correctness claims",
              "generation_options": "Ollama defaults (not seeded)",
              "runs": run_trials(CASES, snapshot, args.model, args.url)}
    output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"Completed {len(report['runs'])} runs. Report: {output}")
    print("History not written. Review report before sharing; it contains model answers.")


if __name__ == "__main__":
    main()
