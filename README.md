# A.L.F.I.
**Artificial Lifeform — First Iteration**

MyFirstAI — Phase One: Inception

A beginner-friendly, offline Python chatbot that classifies messages and learns new responses. A.L.F.I. is an educational machine-learning program, not a conscious lifeform or a large language model.

## Requirements
Python 3.10 or newer. No third-party packages or API keys.

## Run
```bash
python3 first_ai.py
```

Try `hello`, `who are you`, or `what can you do`.

Commands: `/teach` (add an example and response), `/knowledge` (list known topics), `/help`, and `/quit`.

## Test
```bash
python3 -m unittest discover -s tests -v
```

A.L.F.I. stores learned examples in `ai_memory.json`, which is excluded from Git to protect local data.
