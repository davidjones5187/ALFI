"""Gate D synthetic robustness fixture. Offline; no Ollama calls or production memory."""
import argparse
import hashlib
import json
import os
import secrets
from pathlib import Path
from unittest.mock import patch

from experiments.car_v2_context import build_car_context
from experiments.car_v2_review import ReviewedCARPilot

CASES = [
    {"id":"paraphrase-a","topic_key":"orion_color","question":"Which color did the fictional Orion team finally select?"},
    {"id":"paraphrase-b","topic_key":"orion_color","question":"Remind me of Orion's approved launch hue."},
    {"id":"conflict","topic_key":"orion_color","question":"An unverified note says amber is approved. What color does the reviewed Orion decision specify?"},
    {"id":"second-topic","topic_key":"orion_window","question":"What is Orion's approved launch window?"},
    {"id":"restart-supersession","topic_key":"orion_color","question":"After the revision, what color was approved for Orion?"},
    {"id":"unapproved","topic_key":"orion_slogan","question":"What is Orion's approved slogan? If unknown, say so."},
    {"id":"missing","topic_key":"orion_budget","question":"What is Orion's exact approved budget? If unknown, say so."},
    {"id":"unrelated","topic_key":"rain_formation","question":"How do clouds produce rain?"},
]
EXPECTED = {"orion_color":"violet","orion_window":"morning"}

def create_fixture(directory):
    directory = Path(directory)
    if directory.exists():
        raise FileExistsError("Refusing existing directory")
    directory.mkdir(parents=True)
    db = directory / "synthetic_car.sqlite3"
    token = secrets.token_urlsafe(32)
    digest = hashlib.sha256(token.encode()).hexdigest()
    fields = dict(context="Fictional synthetic test", goal="Measure correction robustness",
                  action="Record decision", result="Test-only fixture",
                  evidence=["synthetic-fixture:not-independent-evidence"])
    with patch.dict(os.environ, {"ALFI_CAR_REVIEWER_SHA256": digest}):
        store = ReviewedCARPilot(db)
        try:
            old = store.propose(topic_key="orion_color", lesson="Orion's approved launch color is amber.", **fields)
            store.confirm(old, reviewer_token=token)
            new = store.propose(topic_key="orion_color", lesson="Orion's approved launch color is violet.", correction="Violet replaces amber.", **fields)
            store.confirm(new, reviewer_token=token, supersedes_id=old)
            window = store.propose(topic_key="orion_window", lesson="Orion's approved launch window is morning.", **fields)
            store.confirm(window, reviewer_token=token)
            pending = store.propose(topic_key="orion_slogan", lesson="Orion's approved slogan is Silver Fox.", **fields)
            assert store.get(old)["status"] == "superseded"
            assert store.get(new)["status"] == "approved"
            assert store.get(window)["status"] == "approved"
            assert store.get(pending)["status"] == "unverified"
        finally:
            store.close()
    # Verify persistence and isolation after an actual close/reopen.
    reopened = ReviewedCARPilot(db)
    try:
        color = build_car_context(reopened, "orion_color", enabled=True)
        time = build_car_context(reopened, "orion_window", enabled=True)
        assert "violet" in color and "amber" not in color and "morning" not in color
        assert "morning" in time and "violet" not in time
        for key in ("orion_slogan", "orion_budget", "rain_formation"):
            assert build_car_context(reopened, key, enabled=True) == ""
        assert build_car_context(reopened, "orion_color") == ""
    finally:
        reopened.close()
    (directory / "cases.json").write_text(json.dumps(CASES, indent=2), encoding="utf-8")
    summary = {"status":"validated_gate_d_fixture","model_calls":0,"cases":len(CASES),
               "expected":EXPECTED,"approved_ids":[new,window],
               "superseded_id":old,"unapproved_id":pending,
               "verified_after_restart":True}
    (directory / "fixture_validation.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory", required=True, type=Path)
    args = parser.parse_args()
    print(json.dumps(create_fixture(args.directory), indent=2))

if __name__ == "__main__":
    main()
