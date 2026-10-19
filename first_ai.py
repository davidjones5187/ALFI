"""A.L.F.I. — Artificial Lifeform, First Iteration."""
import json
import math
import random
import re
from collections import Counter
from pathlib import Path

MEMORY_FILE = Path(__file__).with_name("ai_memory.json")
HISTORY_FILE = Path(__file__).with_name("conversation_history.json")
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
        self.history = self.load_history()

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

    def load_history(self):
        try:
            data = json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
            return data[-100:] if isinstance(data, list) else []
        except (OSError, ValueError):
            return []

    def record(self, message, answer):
        self.history.append({"user": message, "assistant": answer})
        self.history = self.history[-100:]
        try:
            HISTORY_FILE.write_text(json.dumps(self.history, indent=2), encoding="utf-8")
        except OSError as exc:
            print(f"Warning: conversation history not saved: {exc}")

    def recent_history(self, limit=5):
        return self.history[-limit:]

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
        # Follow-up references to the last discussed topic.
        if tokenize(message) in (["tell", "me", "more"], ["more", "about", "that"]):
            if self.history:
                return "We were discussing: " + self.history[-1]["user"] + ". What would you like to know?"
            return "What topic would you like to explore?"
        # Exact training examples are known, even when a small model assigns
        # them a low normalized probability.
        normalized = tokenize(message)
        for intent, item in self.data.items():
            if any(tokenize(example) == normalized for example in item["examples"]):
                responses = item["responses"]
                return random.choice(responses) if responses else "I recognize the topic but have no reply."
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

def teaching_mode(ai):
    print("\\nTEACHING MODE — type /cancel at any prompt to leave.")
    fields = []
    for prompt in ("Topic", "Example message", "Response"):
        value = input(prompt + ": ").strip()
        if value.lower() == "/cancel":
            print("Lesson canceled; nothing saved.")
            return
        if not value:
            print("Lesson canceled: all fields are required.")
            return
        fields.append(value)
    print("\\nReview your lesson:")
    for label, value in zip(("Topic", "Example", "Response"), fields):
        print(f"  {label}: {value}")
    confirmation = input("Save lesson? [y/N]: ").strip().lower()
    if confirmation not in ("y", "yes"):
        print("Lesson canceled; nothing saved.")
        return
    try:
        ai.teach(*fields)
        print("A.L.F.I.: Learned and saved.")
    except (ValueError, OSError) as exc:
        print(f"A.L.F.I.: Could not save lesson: {exc}")

def main():
    ai = ALFI()
    print("A.L.F.I. 1.1 | Conversational Intelligence")
    print("Commands: /teach, /knowledge, /history, /help, /quit")
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
            print("/teach: reviewed lesson | /knowledge: topics | /history: recent chats | /quit: exit")
        elif command == "/knowledge":
            print("Known topics:", ", ".join(sorted(ai.data)))
        elif command == "/history":
            for turn in ai.recent_history():
                print("You:", turn["user"])
                print("A.L.F.I.:", turn["assistant"])
        elif command == "/teach":
            teaching_mode(ai)
        else:
            answer = ai.respond(message)
            print("A.L.F.I.:", answer)
            ai.record(message, answer)

if __name__ == "__main__":
    main()
