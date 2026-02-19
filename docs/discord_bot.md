<h1 style="width: 70%; padding: 0 15%; background: darkblue; text-align: center">Documentation</h1>

## Overview
The DTF Discord bot listens for mentions, moves the conversation into a thread, shows a loader GIF, sends the user’s question to an external agent (via an n8n webhook), and posts the response back—optionally with a CSV attachment. Core goals: keep channels tidy, provide clear formatting for answers, and handle files safely.

## Architecture
- **Entry point:** `main.py`
  - Sets up Discord intents, bot instance, loader path, and the `on_message` handler.
  - Flow per message:
    1) Ignore messages from the bot itself.
    2) Proceed only if the bot is mentioned.
    3) Extract question text (mention stripped). If empty, prompt user.
    4) Ensure a thread exists (create one if needed); send loader GIF.
    5) Call `send_to_agent(question, thread_id)` to reach the external agent.
    6) Delete loader, dispatch response via `send_answer`.
    7) On errors, reply with a concise error message.

- **Agent + messaging helpers:** `utils/send.py`
  - `send_to_agent(question, thread_id)`: POSTs payload to `N8N_WEBHOOK_URL`; expects JSON.
  - `send_to_target(target, content=None, file=None)`: convenience to send either to the thread (`thread.send`) or as a reply (`ctx.reply`).
  - `send_answer(ctx, thread, answer)`: routes based on `answer['type']`:
    - `no-sql-query`: reply with text (mentions the author).
    - `sql-query`: format answer, if `file` exists, decode base64 CSV and attach.

- **Formatting + debug:** `utils/tools.py`
  - `debug(ctx)`: prints message context for troubleshooting.
  - `format_answer(answer, author=None)`: Markdown response with query, explanation preview (truncated), and head preview rendered as markdown.

## Key Data Concepts
Expected agent response shape (examples):
- No-SQL: `{ "type": "no-sql-query", "response": "..." }`
- SQL with file: `{ "type": "sql-query", "query": "...", "explanation": "...", "file": { "data": { "data": "<base64>", "fileName": "results.csv" } } }`
- SQL without file: `{ "type": "sql-query", "query": "...", "explanation": "...", "head": "```text...```" }`

## Configuration
Set in `.env`:
- `DISCORD_TOKEN` (required)
- `N8N_WEBHOOK_URL` (required)
- `MAX_HISTORY_MESSAGES` (optional, default 10)

## Message Size & Limits
- Discord limit: 2000 characters per message. 
- Attachments: base64 CSV decoded and sent as `discord.File`.

## Running
```bash
conda env create -f environment.yml 
python main.py                   # or: make run-bot
```