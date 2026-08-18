#!/usr/bin/env python3
import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

DEFAULT_API_URL = "https://api.anthropic.com/v1/complete"
DEFAULT_API_KEY_HEADER = "x-api-key"
DEFAULT_MODEL = "claude-3.5"


def build_prompt(text, no_wrap):
    if no_wrap:
        return text

    lower = text.strip().lower()
    if "human:" in lower or "assistant:" in lower:
        return text

    return f"Human: {text.strip()}\n\nAssistant:"


def call_claude(api_url, api_key, api_key_header, model, prompt, max_tokens, temperature):
    payload = {
        "model": model,
        "prompt": prompt,
        "max_tokens_to_sample": max_tokens,
        "temperature": temperature,
    }
    data = json.dumps(payload).encode("utf-8")
    headers = {
        "Content-Type": "application/json",
        api_key_header: api_key,
    }

    req = urllib.request.Request(api_url, data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req) as res:
            body = res.read().decode("utf-8")
            return json.loads(body)
    except urllib.error.HTTPError as err:
        message = err.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {err.code}: {message}") from err
    except urllib.error.URLError as err:
        raise RuntimeError(f"Request failed: {err.reason}") from err


def parse_args():
    parser = argparse.ArgumentParser(
        description="Claude CLI: call a Claude-compatible LLM endpoint from the terminal."
    )
    parser.add_argument(
        "--prompt",
        "-p",
        help="The prompt text to send to Claude. If omitted, the script reads stdin.",
    )
    parser.add_argument("--file", "-f", help="Read the prompt text from a file.")
    parser.add_argument(
        "--model",
        default=os.environ.get("CLAUDE_MODEL", DEFAULT_MODEL),
        help=f"Claude model name (default: {DEFAULT_MODEL} or $CLAUDE_MODEL).",
    )
    parser.add_argument(
        "--max-tokens",
        type=int,
        default=int(os.environ.get("CLAUDE_MAX_TOKENS", "1024")),
        help="Maximum tokens to sample in the response.",
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=float(os.environ.get("CLAUDE_TEMPERATURE", "0.0")),
        help="Sampling temperature for the Claude response.",
    )
    parser.add_argument(
        "--api-url",
        default=os.environ.get("CLAUDE_API_URL", DEFAULT_API_URL),
        help=f"Claude API URL (default: {DEFAULT_API_URL} or $CLAUDE_API_URL).",
    )
    parser.add_argument(
        "--api-key-header",
        default=os.environ.get("CLAUDE_API_KEY_HEADER", DEFAULT_API_KEY_HEADER),
        help="HTTP header name used for the API key (default: x-api-key).",
    )
    parser.add_argument(
        "--no-wrap",
        action="store_true",
        help="Do not wrap the prompt in a Human/Assistant Claude-style prefix.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print the full JSON response from the Claude endpoint.",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    api_key = os.environ.get("CLAUDE_API_KEY")
    if not api_key:
        print("Error: CLAUDE_API_KEY environment variable is required.", file=sys.stderr)
        sys.exit(1)

    if args.file and args.prompt:
        print("Error: specify only one of --prompt or --file.", file=sys.stderr)
        sys.exit(1)

    if args.file:
        try:
            with open(args.file, "r", encoding="utf-8") as fh:
                prompt_text = fh.read()
        except OSError as err:
            print(f"Error reading file: {err}", file=sys.stderr)
            sys.exit(1)
    elif args.prompt:
        prompt_text = args.prompt
    else:
        prompt_text = sys.stdin.read()

    if not prompt_text.strip():
        print("Error: prompt is empty. Provide --prompt, --file, or stdin.", file=sys.stderr)
        sys.exit(1)

    prompt = build_prompt(prompt_text, args.no_wrap)

    try:
        response = call_claude(
            api_url=args.api_url,
            api_key=api_key,
            api_key_header=args.api_key_header,
            model=args.model,
            prompt=prompt,
            max_tokens=args.max_tokens,
            temperature=args.temperature,
        )
    except RuntimeError as err:
        print(f"Error: {err}", file=sys.stderr)
        sys.exit(1)

    if args.json:
        print(json.dumps(response, indent=2, ensure_ascii=False))
        return

    completion = response.get("completion")
    if completion is None:
        # Some Claude endpoints may return 'text' or a nested 'response' field.
        completion = response.get("text") or response.get("response")

    if isinstance(completion, dict):
        print(json.dumps(completion, indent=2, ensure_ascii=False))
    elif completion is not None:
        print(completion)
    else:
        print(json.dumps(response, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
