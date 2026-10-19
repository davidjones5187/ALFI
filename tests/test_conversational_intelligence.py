"""Regression tests for A.L.F.I. 1.6 follow-up resolution."""
import unittest
from conversational_intelligence import resolve_followup, response_guidance, natural_acknowledgment, conversational_intent, clarification_needed, conversation_guidance, feedback_intent, feedback_response, quality_guidance

class ConversationalIntelligenceTests(unittest.TestCase):
    def test_example_retains_subject(self):
        history = [{"user": "Explain supervised learning.", "assistant": "It uses labels."}]
        self.assertIn("Explain supervised learning.", resolve_followup("Give me an example.", history))

    def test_no_context_does_not_guess(self):
        self.assertIsNone(resolve_followup("Explain that.", []))

    def test_new_question_not_rewritten(self):
        history = [{"user": "Explain Python.", "assistant": "A language."}]
        self.assertIsNone(resolve_followup("Explain quantum computing.", history))

    def test_commands_untouched(self):
        self.assertIsNone(resolve_followup("/forgetmemory", [{"user": "Explain Python."}]))

    def test_bounded_history(self):
        history = [{"user": "Explain Python."}] + [{"user": "/help"}] * 5
        self.assertIsNone(resolve_followup("Give me an example.", history))

    def test_prior_followup_skipped(self):
        history = [{"user": "Explain supervised learning."}, {"user": "Give me an example."}]
        self.assertIn("supervised learning", resolve_followup("Tell me more.", history))

    def test_unrelated_pronoun_not_assumed(self):
        self.assertIsNone(resolve_followup("Is it raining tomorrow?", [{"user": "Explain Python."}]))

class ResponseIntelligenceTests(unittest.TestCase):
    def setUp(self):
        self.history = [{"user": "Explain supervised learning.", "assistant": "It learns from labeled data."}]

    def test_followup_avoids_repetition(self):
        guidance = response_guidance("Tell me more.", self.history)
        self.assertIn("without repeating", guidance)
        self.assertIn("NEW relevant insight", guidance)

    def test_example_is_concise(self):
        self.assertIn("2-4 sentences", response_guidance("Give me an example.", self.history))

    def test_explicit_detail_wins(self):
        self.assertIn("explain thoroughly", response_guidance("Explain that in detail.", self.history))

    def test_explicit_brevity_wins(self):
        self.assertIn("one or two sentences", response_guidance("Briefly explain that.", self.history))

    def test_topic_change_not_dragged_back(self):
        guidance = response_guidance("Explain quantum computing.", self.history)
        self.assertIn("different subject", guidance)
        self.assertNotIn("2-4 sentences", guidance)

    def test_history_not_modified(self):
        before = [dict(turn) for turn in self.history]
        response_guidance("Tell me more.", self.history)
        self.assertEqual(self.history, before)

    def test_no_context_guidance(self):
        self.assertIn("Be concise by default", response_guidance("Hello", []))

class NaturalAcknowledgmentTests(unittest.TestCase):
    def test_praise_is_brief(self):
        self.assertEqual(natural_acknowledgment("Great job!"), "Thanks! Glad that helped.")

    def test_thanks_is_brief(self):
        self.assertEqual(natural_acknowledgment("Thank you."), "You're welcome!")

    def test_substantive_question_is_not_intercepted(self):
        self.assertIsNone(natural_acknowledgment("Great job. Can you explain more?"))

    def test_topic_change_is_not_intercepted(self):
        self.assertIsNone(natural_acknowledgment("Explain quantum computing."))

    def test_no_false_learning_claim(self):
        self.assertNotIn("learn", natural_acknowledgment("Well done!").lower())


if __name__ == "__main__":
    unittest.main()

class Phase2Tests(unittest.TestCase):
    def test_correction(self):
        self.assertEqual(conversational_intent("Actually, I meant Python."), "correction")

    def test_alternative_praise(self):
        self.assertEqual(conversational_intent("Nice work!"), "acknowledgment")

    def test_missing_context(self):
        self.assertIsNotNone(clarification_needed("Tell me more.", []))

    def test_followup_with_context(self):
        history = [{"user": "Explain neural networks.", "assistant": "Networks."}]
        self.assertIsNone(clarification_needed("Tell me more.", history))

    def test_new_topic_not_intercepted(self):
        history = [{"user": "Explain Python."}]
        self.assertIsNone(clarification_needed("Explain chemistry.", history))

    def test_correction_does_not_claim_memory_update(self):
        self.assertIn("without claiming permanent memory", conversation_guidance("Actually, I meant Java.", []))

    def test_commands_not_intercepted(self):
        self.assertEqual(conversational_intent("/forget"), "other")

    def test_history_unchanged(self):
        history = [{"user": "Explain Python."}]
        before = [dict(t) for t in history]
        conversation_guidance("Tell me more.", history)
        self.assertEqual(history, before)

class Increment4FeedbackTests(unittest.TestCase):
    def test_praise(self):
        self.assertEqual(feedback_intent("Great job!"), "praise")

    def test_dissatisfaction(self):
        self.assertEqual(feedback_intent("That's not right."), "dissatisfaction")
        self.assertIn("Which part", feedback_response("That's not right."))

    def test_correction(self):
        self.assertEqual(feedback_intent("Actually, I meant Python."), "correction")

    def test_no_substantive_interception(self):
        self.assertEqual(feedback_intent("Why is this wrong?"), "other")
        self.assertIsNone(feedback_response("Explain quantum computing."))

    def test_commands_unaffected(self):
        self.assertEqual(feedback_intent("/correct"), "other")

    def test_no_memory_claim(self):
        self.assertIn("Do not claim", quality_guidance("Actually, I meant Java."))

    def test_technical_qualification(self):
        self.assertIn("unsupported certainty", quality_guidance("Explain quantum encryption."))

    def test_feedback_does_not_mutate_history(self):
        history = [{"user": "Explain Python.", "assistant": "A language."}]
        before = [dict(t) for t in history]
        feedback_intent("That's wrong.")
        quality_guidance("Actually, I meant Java.")
        self.assertEqual(history, before)


from conversational_intelligence import adaptive_guidance, adaptive_clarification

class Increment5AdaptiveTests(unittest.TestCase):
    def test_beginner_style(self):
        self.assertIn("everyday language", adaptive_guidance("Explain quantum computing in simple terms.", []))

    def test_technical_style(self):
        self.assertIn("technical mechanisms", adaptive_guidance("Give a technical explanation.", []))

    def test_default_accessibility(self):
        self.assertIn("accessible language", adaptive_guidance("Explain neural networks.", []))

    def test_uncertainty_safeguard(self):
        self.assertIn("universal speedup", adaptive_guidance("Explain quantum computing.", []))

    def test_missing_referent(self):
        self.assertEqual(adaptive_clarification("Why is it important?", []), "Which topic are you referring to?")

    def test_context_available(self):
        history = [{"user": "Explain neural networks.", "assistant": "Networks of nodes."}]
        self.assertIsNone(adaptive_clarification("Why is it important?", history))

    def test_new_topic_not_intercepted(self):
        self.assertIsNone(adaptive_clarification("Explain quantum computing.", []))

    def test_no_mutation(self):
        history = [{"user": "Explain Python.", "assistant": "A language."}]
        before = [dict(t) for t in history]
        adaptive_guidance("Explain simply.", history)
        adaptive_clarification("Why is it important?", history)
        self.assertEqual(history, before)
