# Self-Evaluating Lesson Generator

A bounded generate → evaluate → revise pipeline for beginner AI lessons. Assessment topic: **Introduction to RAG**.

## Modes and integrity
- **Mock:** no API key; the first fixture deliberately contains the false claim that RAG guarantees correct answers. The evaluator rejects it and the next fixture fixes it. This validates orchestration and logs, **not real AI generation or semantic evaluation**.
- **Live:** calls an LLM separately for generation and rubric-based evaluation. The judge returns eight binary checks; Python validates the response and adds three deterministic structural gates. An LLM judge is fallible and must not be treated as ground truth.
- **Gemini:** supported through Google's documented OpenAI-compatible API endpoint.
- **OpenAI:** also supported.
- No lesson is published if the retry limit is reached without a pass.

## Setup (Windows PowerShell)
```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m pytest -q
python main.py --mode mock
```

## Live mode with Gemini (recommended)
1. Open [Google AI Studio API keys](https://aistudio.google.com/apikey) and create a Gemini API key. Check the account's available model access and usage limits.
2. Copy `.env.example` to `.env`.
3. Set `GEMINI_API_KEY` in `.env`; keep `LLM_PROVIDER=gemini`. Do not put quotes around the key unless they are part of it.
4. Run:
```powershell
python main.py --mode live --topic "Introduction to RAG"
```
The default model is configured as `gemini-3.8-flash`; if that model is unavailable to your account, set `GEMINI_MODEL` to a currently available compatible model in `.env`.

Google documents the compatibility endpoint as `https://generativelanguage.googleapis.com/v1beta/openai/`. See [official OpenAI compatibility docs](https://ai.google.dev/gemini-api/docs/openai). Free-tier availability, rate limits, model access, and billing depend on the account and model; verify them in AI Studio.

## Live mode with OpenAI (alternative)
Set `LLM_PROVIDER=openai`, `OPENAI_API_KEY`, and optionally `OPENAI_MODEL` in `.env`, then run `python main.py --mode live`.

## Outputs
- `outputs/final_lesson.md`: last passing lesson (removed on failure)
- `outputs/last_run.json`: all attempts, check verdicts, failure reasons, and prior insights
- `lesson_memory.db`: persistent SQLite records across runs

## Architecture
`main.py` wires a generator, evaluator, memory store, and bounded orchestrator. Each attempt generates a lesson, evaluates it, stores results, and either publishes it or sends failure reasons to the next attempt. At most two retries are allowed; API/JSON errors fail closed. Previous failures are retrieved from SQLite and included as generation hints on later runs.

## Rubric
Eight binary semantic checks: accuracy, accessibility, worked example, jargon, coverage, flow, standalone clarity, and knowledge check. Three deterministic checks: title, worked-example markers, and comprehension questions. Every check must pass. The judge receives a curated reference baseline; it is not an exhaustive external fact-check. Deterministic gates require explicit Question / Retrieved evidence / Answer labels and at least three numbered, answered questions.

## Self-evolution and memory
Failure reasons are persisted and deduplicated by check ID, then inserted as improvement hints into future generation prompts. This is memory-driven prompt adaptation, **not model training**. The acceptance rubric is fixed and must not weaken itself to improve pass rates.

## Demo sequence
1. Run `python -m pytest -q`.
2. Run `python main.py --mode mock`; show attempt 1 rejected for the false guarantee, attempt 2 accepted.
3. Open `outputs/last_run.json` and `outputs/final_lesson.md`.
4. Run again to show prior insights loaded from SQLite.
5. If API access is available, run live mode and show real generation/evaluation. Label mock evidence clearly.
6. Explain bounded retries, judge limitations, and the distinction between mock workflow testing and live semantic evaluation.

## Security
Never commit `.env`, API keys, or a personal `lesson_memory.db`. Review `.gitignore` before pushing. Do not share screenshots that expose the key.
