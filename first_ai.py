"""A.L.F.I. — Artificial Lifeform, First Iteration."""
import json
import math
import os
import random
import re
import urllib.error
import urllib.request
from collections import Counter
from pathlib import Path
from memory_intelligence import MemoryStore
from conversational_intelligence import resolve_followup, response_guidance, natural_acknowledgment, clarification_needed, conversation_guidance, feedback_response, quality_guidance, adaptive_guidance, adaptive_clarification, precision_guidance, length_guidance, increment7_guidance, contextual_subject, response_policy, response_needs_revision, format_violation, factual_revision_guidance

MEMORY_FILE = Path(__file__).with_name("ai_memory.json")
HISTORY_FILE = Path(__file__).with_name("conversation_history.json")
OLLAMA_URL = "http://127.0.0.1:11434/api/chat"
OLLAMA_MODEL = "gemma3:4b"  # Preferred development model; override with ALFI_OLLAMA_MODEL
STOPWORDS = {"a", "an", "the", "is", "are", "what", "who", "how", "why", "does", "do", "you", "your", "me", "my", "of", "to", "about", "tell", "please", "it", "and", "was", "were"}
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
    def __init__(self, memory_file=MEMORY_FILE, use_ollama=True, ollama_url=OLLAMA_URL, ollama_model=None):
        self.memory_file = Path(memory_file)
        self.use_ollama = use_ollama
        self.ollama_url = ollama_url
        self.ollama_model = ollama_model or os.environ.get("ALFI_OLLAMA_MODEL") or OLLAMA_MODEL
        self.structured_memory = MemoryStore(self.memory_file.with_name('structured_memory.json'))
        self.data = self.load()
        self.train()
        self.history = self.load_history()
        self.last_topic = None
        self.last_source = None

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

    def find_knowledge(self, message):
        """Find the most relevant taught example, avoiding low-information matches."""
        query = set(tokenize(message)) - STOPWORDS
        if not query:
            return None
        best = None
        best_score = 0.0
        for topic, entry in self.data.items():
            for index, example in enumerate(entry["examples"]):
                terms = set(tokenize(example)) - STOPWORDS
                overlap = len(query & terms)
                if not overlap:
                    continue
                score = overlap / len(query | terms)
                # Require substantial shared content; don't guess from one generic word.
                if score > best_score:
                    best_score = score
                    best = (topic, index)
        return best if best_score >= 0.60 else None

    def topic_details(self, topic):
        entry = self.data.get(topic, {})
        responses = list(dict.fromkeys(entry.get("responses", [])))
        if not responses:
            return "I don't have additional details about that topic yet."
        return "Here's what I know about " + topic.replace("_", " ") + ": " + " ".join(responses)

    def history_question_answer(self, message):
        """Answer explicit requests to recall user questions from recorded history.

        Never substitute a matching saved fact or invent an earlier conversation.
        """
        prompt = message.strip().lower()
        immediate = re.match(r"^what did i just ask you(?: to do)?(?: (?:about|with|regarding) .+)?[?.!]*$", prompt)
        older = re.match(r"^what did i ask you about (.+?) in (?:our |the )?earlier conversation[?.!]*$", prompt)
        if not (immediate or older):
            return None
        if immediate:
            for turn in reversed(self.history):
                if isinstance(turn, dict) and isinstance(turn.get("user"), str):
                    prior = turn["user"].strip()
                    if prior and not prior.startswith("/"):
                        return f"You asked me: {prior}"
            return "I can't find a preceding question in my saved conversation history."
        subject = older.group(1).strip().strip("?.! ")
        terms = set(tokenize(subject)) - STOPWORDS
        if not terms:
            return "I can't identify which earlier question you mean."
        for turn in reversed(self.history):
            if not isinstance(turn, dict) or not isinstance(turn.get("user"), str):
                continue
            prior = turn["user"].strip()
            if (prior and not prior.startswith("/")
                    and not re.match(r"^what did i (?:just )?ask you\b", prior, re.I)
                    and terms <= set(tokenize(prior))):
                return f"Your recorded earlier question was: {prior}"
        return "I can't find a matching earlier question in my saved conversation history."

    def direct_memory_answer(self, message):
        """Answer explicit saved-fact questions without model speculation."""
        query = set(tokenize(message)) - STOPWORDS
        if not query or not ("?" in message or message.lower().startswith(("what ", "which ", "who ", "where "))):
            return None
        candidates = []
        for item in self.structured_memory.items:
            if item["kind"] != "fact":
                continue
            key_terms = set(tokenize(item["key"])) - STOPWORDS
            if key_terms and key_terms <= query:
                candidates.append(item)
        if len(candidates) != 1:
            return None
        item = candidates[0]
        return f"Your saved {item['key']} is: {item['value']}. (User-provided memory; not independently verified.)"

    def memory_explanation(self):
        return ("No. Chatting does not retrain my model or permanently teach me new facts. "
                "Conversations may be saved locally in conversation_history.json and reused "
                "as context. /teach saves lessons in ai_memory.json; /remember and /correct save structured facts in structured_memory.json. "
                "Use /clearhistory to erase local chat history.")

    def is_memory_question(self, message):
        words = set(tokenize(message))
        return bool(words & {"you", "your"}) and bool(words & {"learn", "learned", "remember"}) and bool(words & {"permanently", "permanent", "conversation", "new"})

    def generate(self, message):
        """Ask the local Ollama model without automatically teaching the answer."""
        if not self.use_ollama:
            return "I don't know that yet. Use /teach to help me learn."
        messages = [{"role": "system", "content": (
            "You are A.L.F.I. (Artificial Lifeform — First Iteration), "
            "a helpful local AI assistant. Be concise, accurate, and acknowledge uncertainty. "
            "You are a language model, not a conscious lifeform. "
            "Your model weights do not change during chat. Conversation history is temporary context, "
            "and only /teach or /remember saves explicitly provided facts or lessons. Never invent past interactions or "
            "claim to have learned or updated knowledge from ordinary conversation. "
            "For examples, use a concrete external scenario, not a story about your own learning. "
            "Never say that chatting retrains your model. Chat logs can persist locally. A memory source such as explicit /correct records how a user entered a value, NOT independent verification. Never claim a saved memory was externally verified merely because of its source label."
        )}]
        relevant = self.structured_memory.search(message, limit=3)
        if relevant:
            facts = "\n".join(f"{item['kind']} ({item['key']}; source: {item['source']}): {item['value']}" for item in relevant)
            messages.append({"role": "system", "content": "User-provided saved memories, not independently verified:\n" + facts})
        for turn in self.recent_history(5):
            if isinstance(turn, dict):
                user, answer = turn.get("user"), turn.get("assistant")
                if isinstance(user, str) and isinstance(answer, str):
                    messages.extend([{"role": "user", "content": user},
                                     {"role": "assistant", "content": answer}])
        if "example" in tokenize(message):
            for turn in reversed(self.recent_history(5)):
                if isinstance(turn, dict) and isinstance(turn.get("user"), str):
                    prior = turn["user"]
                    if "example" not in tokenize(prior):
                        messages.append({"role": "system", "content":
                                         "The current subject is: " + prior +
                                         ". Give a concrete external example, not an account of your own learning."})
                        break
        messages.append({"role": "system", "content": response_policy(message, self.recent_history(5))})
        resolved = resolve_followup(message, self.recent_history(5))
        if not resolved:
            subject = contextual_subject(message, self.recent_history(5))
            if subject:
                resolved = "Why is the subject of this earlier question important? " + subject
        messages.append({"role": "user", "content": resolved or message})
        payload = json.dumps({"model": self.ollama_model, "messages": messages,
                              "stream": False}).encode("utf-8")
        request = urllib.request.Request(
            self.ollama_url, data=payload,
            headers={"Content-Type": "application/json"}, method="POST")
        try:
            with urllib.request.urlopen(request, timeout=90) as response:
                result = json.load(response)
            answer = result.get("message", {}).get("content", "")
            if isinstance(answer, str) and answer.strip():
                answer = answer.strip()
                issue = factual_revision_guidance(message, answer)
                format_issue = format_violation(message, answer)
                if response_needs_revision(message, answer) or issue:
                    revision_messages = messages + [
                        {"role": "assistant", "content": answer},
                        {"role": "user", "content": ("Revise the previous answer without repeated steps. Preserve factual meaning and caveats. " + issue + " " + format_issue + (" Use at most two short sentences, no list." if "brief" in message.lower() and not format_issue else " Keep the answer focused and concise."))},
                    ]
                    retry_payload = json.dumps({"model": self.ollama_model, "messages": revision_messages, "stream": False}).encode("utf-8")
                    retry_request = urllib.request.Request(self.ollama_url, data=retry_payload,
                        headers={"Content-Type": "application/json"}, method="POST")
                    try:
                        with urllib.request.urlopen(retry_request, timeout=90) as retry_response:
                            retry_result = json.load(retry_response)
                        candidate = retry_result.get("message", {}).get("content", "")
                        if (isinstance(candidate, str) and candidate.strip() and not response_needs_revision(message, candidate)
                                and not factual_revision_guidance(message, candidate)):
                            return candidate.strip()
                    except (urllib.error.URLError, TimeoutError, OSError, ValueError, KeyError):
                        pass
                return answer
            return "The local model returned an empty response. Please try again."
        except (urllib.error.URLError, TimeoutError, OSError, ValueError, KeyError) as exc:
            return ("I couldn't reach my local AI engine. Check that Ollama is running "
                    "and " + self.ollama_model + " is installed. Details: " + str(exc))

    def respond(self, message):
        feedback = feedback_response(message)
        if feedback is not None:
            return feedback
        clarification = adaptive_clarification(message, self.recent_history(5))
        if clarification:
            return clarification
        clarification = clarification_needed(message, self.recent_history(5))
        if clarification:
            return clarification
        social = natural_acknowledgment(message)
        if social is not None:
            return social
        if self.is_memory_question(message):
            return self.memory_explanation()
        historical = self.history_question_answer(message)
        if historical is not None:
            return historical
        direct = self.direct_memory_answer(message)
        if direct is not None:
            return direct
        words = tokenize(message)
        if words in (["tell", "me", "more"], ["more", "about", "that"], ["what", "else", "do", "you", "know"]):
            if self.last_source == "taught" and self.last_topic:
                return self.topic_details(self.last_topic)
            if self.history:
                return self.generate(message)
            return "Please ask about a topic first."
        # Preserve exact examples and their corresponding responses, not a random
        # response from the same topic.
        for topic, entry in self.data.items():
            for index, example in enumerate(entry["examples"]):
                if tokenize(example) == words:
                    self.last_topic = topic
                    self.last_source = "taught"
                    responses = entry["responses"]
                    if not responses:
                        return "I recognize that topic but have no answer yet."
                    return responses[min(index, len(responses) - 1)]
        match = self.find_knowledge(message)
        if match:
            topic, index = match
            self.last_topic = topic
            self.last_source = "taught"
            responses = self.data[topic]["responses"]
            return responses[min(index, len(responses) - 1)] if responses else "I don't have an answer yet."
        self.last_topic = None
        self.last_source = "generated"
        return self.generate(message)

    def forget_topic(self, topic):
        """Delete a taught topic, leaving conversation history untouched."""
        key = re.sub(r"[^a-z0-9_-]+", "_", topic.strip().lower()).strip("_")
        if key not in self.data:
            return False
        del self.data[key]
        self.train()
        self.save()
        if self.last_topic == key:
            self.last_topic = None
            self.last_source = None
        return True

    def clear_history(self):
        """Erase on-disk conversation history and current conversational context."""
        self.history = []
        self.last_topic = None
        self.last_source = None
        try:
            HISTORY_FILE.unlink(missing_ok=True)
        except OSError as exc:
            print(f"Warning: history could not be deleted: {exc}")

    def teach(self, intent, example, response):
        intent = re.sub(r"[^a-z0-9_-]+", "_", intent.strip().lower()).strip("_")
        if not intent or not example.strip() or not response.strip():
            raise ValueError("Topic, example, and response are required.")
        entry = self.data.setdefault(intent, {"examples": [], "responses": []})
        if example in entry["examples"]:
            entry["responses"][entry["examples"].index(example)] = response
        else:
            entry["examples"].append(example)
            entry["responses"].append(response)
        self.train()
        self.save()

def teaching_mode(ai):
    print("\nTEACHING MODE — type /cancel at any prompt to leave.")
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
    print("\nReview your lesson:")
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
    print("A.L.F.I. 1.6-dev | Conversational Intelligence")
    print("Commands: /teach, /knowledge, /forget, /history, /clearhistory, /remember, /memories, /recall, /correct, /forgetmemory, /help, /quit")
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
        if command == "/cancel":
            print("No teaching session is active. Use /teach to start one.")
        elif command == "/remember":
            kind = input("Type (fact/preference/instruction): ").strip().lower()
            key = input("Memory key: ").strip()
            value = input("Memory value: ").strip()
            if input("Save this memory? [y/N]: ").strip().lower() in ("y", "yes"):
                try:
                    ai.structured_memory.put(kind, key, value)
                    print("Memory saved.")
                except (ValueError, OSError) as exc:
                    print("Memory not saved:", exc)
        elif command == "/memories":
            for item in ai.structured_memory.list_items():
                print(f"{item['key']} [{item['kind']}]: {item['value']} | {item['source']} | {item['updated']}")
        elif command == "/recall":
            for item in ai.structured_memory.search(input("Search memory: ")):
                print(f"{item['key']} [{item['kind']}]: {item['value']} | {item['source']}")
        elif command == "/correct":
            key = input("Memory key: ").strip().lower()
            old = next((item for item in ai.structured_memory.items if item["key"] == key), None)
            if old is None:
                print("Memory not found.")
            else:
                print("Current:", old["value"])
                print("Enter the COMPLETE replacement value. Existing details are not automatically retained.")
                value = input("Full corrected value: ").strip()
                if value:
                    print("Before:", old["value"])
                    print("After: ", value)
                if value and input("Replace the entire old value with this new value? [y/N]: ").strip().lower() in ("y", "yes"):
                    try:
                        ai.structured_memory.put(old["kind"], key, value, "explicit /correct")
                        print("Memory corrected.")
                    except (ValueError, OSError) as exc:
                        print("Correction failed:", exc)
        elif command == "/forgetmemory":
            key = input("Memory key to delete: ").strip()
            if key and input("Delete this memory? [y/N]: ").strip().lower() in ("y", "yes"):
                try:
                    print("Memory removed." if ai.structured_memory.forget(key) else "Memory not found.")
                except OSError as exc:
                    print("Deletion failed:", exc)
        elif command == "/help":
            print("/teach lesson | /knowledge topics | /forget topic | /history chats | /clearhistory erase chats | /remember save | /memories list | /recall search | /correct revise | /forgetmemory delete | /quit exit")
        elif command == "/forget":
            topic = input("Topic to forget: ").strip()
            if topic and input(f"Delete taught topic {topic!r}? [y/N]: ").strip().lower() in ("y", "yes"):
                print("Topic removed." if ai.forget_topic(topic) else "Topic not found.")
            else:
                print("Canceled.")
        elif command == "/clearhistory":
            if input("Permanently erase local conversation history? [y/N]: ").strip().lower() in ("y", "yes"):
                ai.clear_history()
                print("Conversation history cleared.")
            else:
                print("Canceled.")
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
