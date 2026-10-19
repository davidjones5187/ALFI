# A.L.F.I.
**Artificial Lifeform — First Iteration**

MyFirstAI — A.L.F.I. 1.4: Context and Memory Management

A beginner-friendly Python assistant combining explicitly taught local knowledge with an Ollama-hosted language model. A.L.F.I. is not a conscious lifeform.

## Requirements
Python 3.10 or newer, Ollama running locally, and the `llama3.2:3b` model. No Python third-party packages or cloud API keys are required.

## Setup
Install Ollama from https://ollama.com/download/mac and run `ollama pull llama3.2:3b`. Ensure the Ollama application/server is running.

## Run
```bash
python3 first_ai.py
```

Try `hello`, `who are you`, or `what can you do`.

Commands: `/teach` (review and confirm a lesson before saving; `/cancel` to abort), `/knowledge`, `/history` (last five conversations), `/help`, `/quit`.

A.L.F.I. 1.4 saves up to 100 chat turns in `conversation_history.json` and can handle simple follow-ups like `tell me more`. Version 1.4 adds conservative matching for rephrased questions, topic-aware follow-ups, and correction of existing lessons. Each example has a corresponding response. Known lessons take precedence. Unknown questions are sent to Ollama at `http://127.0.0.1:11434/api/chat` with up to five previous exchanges for context. Model output is not saved as taught knowledge. If Ollama is unavailable, A.L.F.I. shows a helpful error. Responses can be incorrect; verify important facts. The local conversation history is shared with the local model, not a cloud API by this code.

## Test
```bash
python3 -m unittest discover -s tests -v
```

A.L.F.I. stores learned examples in `ai_memory.json`, and conversation history locally; both are excluded from Git to protect local data.

## Version 1.4
The assistant now tracks whether the last answer came from taught knowledge or from the language model. Follow-ups to generated answers use recent chat context. New `/forget` and `/clearhistory` commands ask for confirmation before removing a taught topic or local chat history. This does not change the model weights. Generated answers are not automatically saved as lessons.
