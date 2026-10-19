import tempfile
import io
import json
import urllib.error
from unittest.mock import patch
import unittest
from pathlib import Path
from first_ai import ALFI

class TestALFI(unittest.TestCase):
    def test_greeting(self):
        with tempfile.TemporaryDirectory() as folder:
            ai = ALFI(Path(folder) / "memory.json")
            self.assertEqual(ai.classify("hello")[0], "greeting")
            self.assertEqual(ai.respond("hello"), "Hello! I'm A.L.F.I.")

    def test_unknown_words(self):
        with tempfile.TemporaryDirectory() as folder:
            ai = ALFI(Path(folder) / "memory.json")
            self.assertIsNone(ai.classify("quasar nebula")[0])

    def test_teaching_validation(self):
        with tempfile.TemporaryDirectory() as folder:
            ai = ALFI(Path(folder) / "memory.json")
            with self.assertRaises(ValueError):
                ai.teach("new_topic", "", "Answer")
            self.assertNotIn("new_topic", ai.data)

    def test_exact_learned_example(self):
        with tempfile.TemporaryDirectory() as folder:
            ai = ALFI(Path(folder) / "memory.json")
            ai.teach("project_identity", "what is project inception?", "Phase One.")
            self.assertEqual(ai.respond("What is project inception?"), "Phase One.")

    def test_paraphrase_matches(self):
        with tempfile.TemporaryDirectory() as folder:
            ai = ALFI(Path(folder) / "memory.json")
            ai.teach("project_identity", "what is project inception?", "First phase.")
            self.assertEqual(ai.respond("Tell me about project inception"), "First phase.")

    def test_followup_uses_topic(self):
        with tempfile.TemporaryDirectory() as folder:
            ai = ALFI(Path(folder) / "memory.json")
            ai.teach("project_identity", "what is project inception?", "First phase.")
            ai.respond("what is project inception?")
            self.assertIn("First phase.", ai.respond("tell me more"))

    def test_reteach_replaces_answer(self):
        with tempfile.TemporaryDirectory() as folder:
            ai = ALFI(Path(folder) / "memory.json")
            ai.teach("creator", "who created you", "Original")
            ai.teach("creator", "who created you", "Updated")
            self.assertEqual(ai.respond("who created you"), "Updated")

    def test_local_model_generates_unknown_answer(self):
        with tempfile.TemporaryDirectory() as folder:
            ai = ALFI(Path(folder) / "memory.json")
            fake = io.BytesIO(json.dumps({"message": {"content": "A generated answer."}}).encode())
            with patch("first_ai.urllib.request.urlopen", return_value=fake) as mocked:
                self.assertEqual(ai.respond("explain quantum gravity"), "A generated answer.")
                request = mocked.call_args.args[0]
                self.assertEqual(json.loads(request.data)["model"], "gemma3:4b")

    def test_taught_knowledge_skips_model(self):
        with tempfile.TemporaryDirectory() as folder:
            ai = ALFI(Path(folder) / "memory.json")
            ai.teach("project", "what is project inception?", "Phase One.")
            with patch("first_ai.urllib.request.urlopen") as mocked:
                self.assertEqual(ai.respond("what is project inception?"), "Phase One.")
                mocked.assert_not_called()

    def test_model_unavailable_graceful(self):
        with tempfile.TemporaryDirectory() as folder:
            ai = ALFI(Path(folder) / "memory.json")
            with patch("first_ai.urllib.request.urlopen", side_effect=urllib.error.URLError("offline")):
                self.assertIn("couldn't reach", ai.respond("explain quantum gravity"))

    def test_disable_model(self):
        with tempfile.TemporaryDirectory() as folder:
            ai = ALFI(Path(folder) / "memory.json", use_ollama=False)
            self.assertIn("don't know", ai.respond("explain quantum gravity"))

    def test_generated_followup_uses_model(self):
        with tempfile.TemporaryDirectory() as folder:
            ai = ALFI(Path(folder) / "memory.json")
            ai.record = lambda user, answer: ai.history.append({"user": user, "assistant": answer})
            ai.record("explain artificial intelligence", "AI recognizes patterns.")
            ai.last_source = "generated"
            fake = io.BytesIO(json.dumps({"message": {"content": "For example, spam filtering."}}).encode())
            with patch("first_ai.urllib.request.urlopen", return_value=fake) as mocked:
                self.assertEqual(ai.respond("tell me more"), "For example, spam filtering.")
                messages = json.loads(mocked.call_args.args[0].data)["messages"]
                self.assertTrue(any(m["role"] == "assistant" and m["content"] == "AI recognizes patterns." for m in messages))
                self.assertEqual(messages[-1]["role"], "user")
                self.assertIn("explain artificial intelligence", messages[-1]["content"].lower())

    def test_forget_topic(self):
        with tempfile.TemporaryDirectory() as folder:
            ai = ALFI(Path(folder) / "memory.json", use_ollama=False)
            ai.teach("project_identity", "what is project inception?", "Phase One.")
            self.assertTrue(ai.forget_topic("project identity"))
            self.assertFalse(ai.forget_topic("project identity"))
            self.assertNotIn("project_identity", ALFI(Path(folder) / "memory.json").data)

    def test_clear_history(self):
        with tempfile.TemporaryDirectory() as folder:
            ai = ALFI(Path(folder) / "memory.json", use_ollama=False)
            ai.history = [{"user": "hello", "assistant": "hi"}]
            ai.last_topic = "greeting"
            ai.last_source = "taught"
            with patch("first_ai.HISTORY_FILE", Path(folder) / "history.json"):
                ai.clear_history()
            self.assertEqual(ai.history, [])
            self.assertIsNone(ai.last_topic)
            self.assertIsNone(ai.last_source)

    def test_memory_answer_is_grounded(self):
        with tempfile.TemporaryDirectory() as folder:
            ai = ALFI(Path(folder) / "memory.json")
            with patch("first_ai.urllib.request.urlopen") as model:
                answer = ai.respond("Did you permanently learn anything new from our conversation?")
                self.assertIn("does not retrain", answer)
                self.assertIn("conversation_history.json", answer)
                self.assertIn("/teach", answer)
                model.assert_not_called()

    def test_example_prompt_includes_subject(self):
        with tempfile.TemporaryDirectory() as folder:
            ai = ALFI(Path(folder) / "memory.json")
            ai.history = [{"user": "Explain how spam filters work",
                           "assistant": "They classify messages."}]
            fake = io.BytesIO(json.dumps({"message": {"content": "A sample email."}}).encode())
            with patch("first_ai.urllib.request.urlopen", return_value=fake) as model:
                ai.respond("Give me a simple example of that.")
                messages = json.loads(model.call_args.args[0].data)["messages"]
                self.assertTrue(any("Explain how spam filters work" in m["content"]
                                    and m["role"] == "system" for m in messages))

    def test_learning_persists(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "memory.json"
            ai = ALFI(path)
            ai.teach("movies", "favorite movie", "Let's talk movies.")
            self.assertEqual(ALFI(path).data["movies"]["responses"], ["Let's talk movies."])

if __name__ == "__main__":
    unittest.main()

class Increment8RetryIntegrationTests(unittest.TestCase):
    def _response(self, content):
        return io.BytesIO(json.dumps({"message": {"content": content}}).encode())

    def test_default_retry(self):
        with tempfile.TemporaryDirectory() as folder:
            ai = ALFI(Path(folder) / "memory.json")
            with patch("first_ai.urllib.request.urlopen", side_effect=[
                self._response("word " * 190), self._response("A focused answer.")
            ]) as model:
                self.assertEqual(ai.generate("Explain photosynthesis."), "A focused answer.")
                self.assertEqual(model.call_count, 2)

    def test_failed_retry_preserves_original(self):
        with tempfile.TemporaryDirectory() as folder:
            ai = ALFI(Path(folder) / "memory.json")
            with patch("first_ai.urllib.request.urlopen", side_effect=[
                self._response("One. Two. Three."), urllib.error.URLError("offline")
            ]) as model:
                self.assertEqual(ai.generate("Briefly explain quantum computing."), "One. Two. Three.")
                self.assertEqual(model.call_count, 2)

    def test_compliant_answer_one_call(self):
        with tempfile.TemporaryDirectory() as folder:
            ai = ALFI(Path(folder) / "memory.json")
            with patch("first_ai.urllib.request.urlopen", return_value=self._response("Photosynthesis converts light to chemical energy.")) as model:
                self.assertIn("Photosynthesis", ai.generate("Explain photosynthesis."))
                self.assertEqual(model.call_count, 1)

class ModelSelectionTests(unittest.TestCase):
    def _model_used(self, ai):
        fake = io.BytesIO(json.dumps({"message": {"content": "Model response."}}).encode())
        with patch("first_ai.urllib.request.urlopen", return_value=fake) as call:
            ai.generate("What causes rain?")
        return json.loads(call.call_args.args[0].data)["model"]

    def test_gemma_default(self):
        with tempfile.TemporaryDirectory() as folder:
            with patch.dict("first_ai.os.environ", {"ALFI_OLLAMA_MODEL": ""}):
                ai = ALFI(Path(folder) / "memory.json")
                self.assertEqual(self._model_used(ai), "gemma3:4b")

    def test_llama_fallback_via_environment(self):
        with tempfile.TemporaryDirectory() as folder:
            with patch.dict("first_ai.os.environ", {"ALFI_OLLAMA_MODEL": "llama3.2:3b"}):
                ai = ALFI(Path(folder) / "memory.json")
                self.assertEqual(self._model_used(ai), "llama3.2:3b")

    def test_explicit_model_override(self):
        with tempfile.TemporaryDirectory() as folder:
            with patch.dict("first_ai.os.environ", {"ALFI_OLLAMA_MODEL": "llama3.2:3b"}):
                ai = ALFI(Path(folder) / "memory.json", ollama_model="gemma3:4b")
                self.assertEqual(self._model_used(ai), "gemma3:4b")

    def test_retry_uses_same_selected_model(self):
        with tempfile.TemporaryDirectory() as folder:
            ai = ALFI(Path(folder) / "memory.json", ollama_model="llama3.2:3b")
            answers = [
                io.BytesIO(json.dumps({"message": {"content": "word " * 190}}).encode()),
                io.BytesIO(json.dumps({"message": {"content": "A focused answer."}}).encode()),
            ]
            with patch("first_ai.urllib.request.urlopen", side_effect=answers) as call:
                ai.generate("Explain photosynthesis.")
            self.assertEqual(call.call_count, 2)
            self.assertTrue(all(json.loads(x.args[0].data)["model"] == "llama3.2:3b" for x in call.call_args_list))
