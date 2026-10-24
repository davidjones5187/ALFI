"""Create and verify a disposable synthetic CAR fixture. No model calls.

Run from repository root:
python3 -m experiments.car_v2_fixture --directory /tmp/alfi-car-fixture-001
"""
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
    {"id": "approved-correction", "topic_key": "larkspur_launch",
     "question": "What launch color was approved for the fictional Larkspur project?"},
    {"id": "unapproved-control", "topic_key": "larkspur_policy",
     "question": "What is the approved slogan for the fictional Larkspur project?"},
    {"id": "unrelated-control", "topic_key": "rain_formation",
     "question": "How does rain form in clouds?"},
]


def create_fixture(directory):
    directory = Path(directory)
    if directory.exists():
        raise FileExistsError("Refusing to reuse an existing experiment directory")
    directory.mkdir(parents=True)
    db_path = directory / "synthetic_car.sqlite3"
    token = secrets.token_urlsafe(32)
    digest = hashlib.sha256(token.encode()).hexdigest()
    with patch.dict(os.environ, {"ALFI_CAR_REVIEWER_SHA256": digest}):
        store = ReviewedCARPilot(db_path)
        try:
            fields = {"context": "Synthetic experiment only", "goal": "Compare responses",
                      "action": "Record fictional decision", "result": "Test fixture",
                      "evidence": ["synthetic-test-fixture:not-external-evidence"]}
            old = store.propose(topic_key="larkspur_launch",
                                lesson="The fictional Larkspur launch color is amber.",
                                **fields)
            store.confirm(old, reviewer_token=token)
            new = store.propose(topic_key="larkspur_launch",
                                lesson="The fictional Larkspur launch color is violet.",
                                correction="Violet supersedes amber.", **fields)
            store.confirm(new, reviewer_token=token, supersedes_id=old)
            pending = store.propose(topic_key="larkspur_policy",
                                    lesson="The fictional Larkspur slogan is Silver Fox.",
                                    **fields)
            assert store.get(old)["status"] == "superseded"
            assert store.get(new)["status"] == "approved"
            assert store.get(pending)["status"] == "unverified"
            approved = build_car_context(store, "larkspur_launch", enabled=True)
            assert "violet" in approved and "amber" not in approved
            assert build_car_context(store, "larkspur_policy", enabled=True) == ""
            assert build_car_context(store, "rain_formation", enabled=True) == ""
            assert build_car_context(store, "larkspur_launch") == ""
            summary = {"status": "validated_synthetic_fixture",
                       "approved_id": new, "superseded_id": old,
                       "unapproved_id": pending,
                       "expected_approved_answer": "violet",
                       "model_calls": 0}
        finally:
            store.close()
    (directory / "cases.json").write_text(json.dumps(CASES, indent=2), encoding="utf-8")
    (directory / "fixture_validation.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8")
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory", required=True, type=Path)
    args = parser.parse_args()
    print(json.dumps(create_fixture(args.directory), indent=2))


if __name__ == "__main__":
    main()
