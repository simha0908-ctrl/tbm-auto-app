# tbm-auto-app
tbm 자동화

## Claude CLI

A small command-line wrapper for calling a Claude-compatible API endpoint.

Usage:

```bash
export CLAUDE_API_KEY="your_api_key"
python3 claude_cli.py --prompt "Write a short summary of this repo."
```

Optional environment variables:

- `CLAUDE_API_URL` — custom API endpoint (default: `https://api.anthropic.com/v1/complete`)
- `CLAUDE_MODEL` — Claude model name (default: `claude-3.5`)
- `CLAUDE_MAX_TOKENS` — maximum tokens to sample (default: `1024`)
- `CLAUDE_TEMPERATURE` — sampling temperature (default: `0.0`)
- `CLAUDE_API_KEY_HEADER` — API key header name (default: `x-api-key`)

Examples:

```bash
python3 claude_cli.py --prompt "List the main files in this repository."
python3 claude_cli.py --file prompt.txt
cat prompt.txt | python3 claude_cli.py
```
