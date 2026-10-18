"""A.L.F.I. — Artificial Lifeform, First Iteration."""
import json
import math
import random
import re
from collections import Counter
from pathlib import Path

MEMORY_FILE = Path(__file__).with_name("ai_memory.json")
DEFAULT_DATA = {
    "greeting": {"examples": ["hello", "hi", "hey", "good morning"], "responses": ["Hello! I'm A.L.F.I."]},
    "identity": {"examples": ["who are you", "what is your name", "tell me your name"], "responses": ["I'm A.L.F.I., Artificial Lifeform — First Iteration."]},
    "capabilities": {"examples": ["what can you do", "how can you help", "what do you know"], "responses": ["I recognize topics and learn new responses."]},
    "thanks": {"examples": ["thank you", "thanks", "I appreciate it"], "responses": ["You're welcome!"]},
    "goodbye": {"examples": ["goodbye", "bye", "see you later"], "responses": ["Goodbye!"]},
}

def tokenize(text):
    return re.findall(r"[a-z0-9']+", text.lower())

class ALFI:
    def __init__(self, memory_file=MEMORY_FILE):
        self.memory_file = Path(memory_file)
        self.data = self.load()
        self.train()

    def load(self):
        if not self.memory_file.exists():
            return json.loads(json.dumps(DEFAULT_DATA))
        try:
            data = json.loads(self.memory_file.read_text(encoding="utf-8"))
            if not isinstance(data, dict):
                raise ValueError("Memory must be an object")
            for entry in data.values():
                if not isinstance(entry, dict) or not all(
                    isinstance(entry.get(key), list) and all(isinstance(x, str) for x in entry[key])
                    for key in ("examples", "responses")
                ):
                    raise ValueError("Invalid memory structure")
            return data
        except (OSError, ValueError) as exc:
            print(f"Memory unavailable ({exc}); starting with defaults.")
            return json.loads(json.dumps(DEFAULT_DATA))

    def save(self):
        self.memory_file.write_text(json.dumps(self.data, indent=2), encoding="utf-8")

    def train(self):
        self.counts = {}
        self.examples = {}
        self.vocabulary = set()
        for intent, item in self.data.items():
            counts = Counter()
            for example in item["examples"]:
                counts.update(tokenize(example))
            self.counts[intent] = counts
            self.examples[intent] = len(item["examples"])
            self.vocabulary.update(counts)

    def classify(self, message):
        words = tokenize(message)
        known = [w for w in words if w in self.vocabulary]
        if not known or not self.data:
            return None, 0.0
        total_examples = sum(self.examples.values())
        size = max(1, len(self.vocabulary))
        scores = {}
        for intent, counts in self.counts.items():
            score = math.log((self.examples[intent] + 1) / (total_examples + len(self.data)))
            denominator = sum(counts.values()) + size
            for word in known:
                score += math.log((counts[word] + 1) / denominator)
            scores[intent] = score
        top = max(scores, key=scores.get)
        peak = max(scores.values())
        weights = {k: math.exp(v - peak) for k, v in scores.items()}
        return top, weights[top] / sum(weights.values())

    def respond(self, message):
        intent, confidence = self.classify(message)
        if intent is None or confidence < 0.42:
            return "I don't know that yet. Use /teach to help me learn."
        responses = self.data[intent]["responses"]
        return random.choice(responses) if responses else "I recognize the topic but have no reply."

    def teach(self, intent, example, response):
        intent = re.sub(r"[^a-z0-9_-]+", "_", intent.strip().lower()).strip("_")
        if not intent or not example.strip() or not response.strip():
            raise ValueError("Topic, example, and response are required.")
        entry = self.data.setdefault(intent, {"examples": [], "responses": []})
        if example not in entry["examples"]:
            entry["examples"].append(example)
        if response not in entry["responses"]:
            entry["responses"].append(response)
        self.train()
        self.save()

def main():
    ai = ALFI()
    print("A.L.F.I. | MyFirstAI — Inception")
    print("Commands: /teach, /knowledge, /help, /quit")
    while True:
        try:
            message = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nA.L.F.I.: Goodbye!")
            break
        if not message:
            continue
        command = message.lower()
        if command in {"/quit", "quit", "exit"}:
            print("A.L.F.I.: Goodbye!")
            break
        if command == "/help":
            print("/teach: add a topic | /knowledge: list topics | /quit: exit")
        elif command == "/knowledge":
            print("Known topics:", ", ".join(sorted(ai.data)))
        elif command == "/teach":
            try:
                ai.teach(input("Topic: "), input("Example message: "), input("Response: "))
                print("A.L.F.I.: Learned and saved.")
            except (ValueError, OSError) as exc:
                print(f"A.L.F.I.: Could not save lesson: {exc}")
        else:
            print("A.L.F.I.:", ai.respond(message))

if __name__ == "__main__":
    main()
