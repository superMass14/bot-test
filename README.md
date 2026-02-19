<h1 style="width: 100%; padding: 0 25%; background: darkblue"> DTF Discord Bot (EpsilonAI) </h1>

A lightweight Discord bot that answers questions when mentioned. It creates a thread per request, shows a loader GIF while processing, forwards the question to an external agent (via n8n webhook), and returns formatted answers (optionally with CSV attachments).

## Features

- Mention-triggered Q&A: mention the bot with a question, it responds in a thread.
- Thread workflow: auto-creates a thread if not already in one, keeping channels tidy.
- Loader animation: sends a small loader GIF while the agent works.
- Agent integration: forwards question + thread_id to an n8n webhook; expects JSON response.
- Result + files: formats answers nicely, can attach CSV results from base64 payloads.

## Quick Start

1) Create and activate your Python env (e.g., conda) and install deps:

   ```bash
   conda env create -f environment.yml 
   ```

2) Set env vars in `.env`:
   - `DISCORD_TOKEN` (required)
   - `N8N_WEBHOOK_URL` (required)
3) Run the bot:

   ```bash
   make run-bot    # or: python main.py
   ```

4) In Discord, mention the bot with your question. It will reply in the thread it creates.

## File Map

- `main.py` — bot entrypoint; threading, loader, routing to agent, response dispatch.
- `utils/send.py` — network call to agent, helpers to send replies, answer handling.
- `utils/tools.py` — formatting helpers and debug logging.
- `scripts/make_loader.py` — build a compact circular loader GIF from a source GIF.
- `assets/loading.gif` / `assets/loading_loader.gif` — source and processed loader GIFs.

## File Structure

```bash
dtf-discord/
├── assets/
│   └── loader.gif
├── docs/
│   └── discord_bot.md
├── utils/
│   ├── send.py
│   └── tools.py
├── .env.example
├── .gitignore
├── environment.yml
├── main.py
├── makefile
└── README.md
```

## Configuration

- `.env` holds secrets.

## Troubleshooting

- No agent response: verify `N8N_WEBHOOK_URL` and network reachability.
