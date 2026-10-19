# A.L.F.I.
**Artificial Lifeform — First Iteration**

MyFirstAI — A.L.F.I. 1.1: Conversational Intelligence

A beginner-friendly, offline Python chatbot that classifies messages and learns new responses. A.L.F.I. is an educational machine-learning program, not a conscious lifeform or a large language model.

## Requirements
Python 3.10 or newer. No third-party packages or API keys.

## Run
```bash
python3 first_ai.py
```

Try `hello`, `who are you`, or `what can you do`.

Commands: `/teach` (review and confirm a lesson before saving; `/cancel` to abort), `/knowledge`, `/history` (last five conversations), `/help`, `/quit`.

A.L.F.I. 1.1 saves up to 100 chat turns in `conversation_history.json` and can handle simple follow-ups like `tell me more`. It remains a rule-based/classifier assistant, **not** a generative LLM.

## Test
```bash
python3 -m unittest discover -s tests -v
```

A.L.F.I. stores learned examples in `ai_memory.json`, and conversation history locally; both are excluded from Git to protect local data.
