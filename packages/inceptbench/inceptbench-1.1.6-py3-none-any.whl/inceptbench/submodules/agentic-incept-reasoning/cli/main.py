#!/usr/bin/env python
"""
Usage:
    python -m cli.main "Create an MCQ on the causes of the civil war"
"""
from __future__ import annotations

import argparse
import sys
import time
import json
import os
import requests
from dotenv import load_dotenv, find_dotenv

START_TIME = time.time()

load_dotenv(find_dotenv())

# Colors for output
REASONING = "\033[38;5;73m"
INTERMEDIATE = "\033[38;5;39m"
FINAL = "\033[38;5;48m"
EVAL = "\033[38;5;208m"  # Orange for evaluation results
ERROR = "\033[38;5;196m"  # Bright red for errors
RETRY = "\033[38;5;226m"  # Bright yellow for retries
RESET = "\033[0m"

# API configuration
DEFAULT_API_URL = "http://localhost:8000/respond"
API_URL = os.getenv("INCEPT_API_URL", DEFAULT_API_URL)

def _print_reasoning(data: str) -> None:
    print(f"{REASONING}{data}{RESET}", end="", flush=True, file=sys.stderr)

def _print_intermediate_output(data: str) -> None:
    print(f"{INTERMEDIATE}{data}{RESET}", end="", flush=True)

def _print_final(data: str, is_eval: bool = False) -> None:
    color = EVAL if is_eval else FINAL
    header = "=== Evaluation Results ===" if is_eval else "=== Final Response ==="
    print(f"\n\n{color}{header}\n\n{data}\n{RESET}")

def handle_event(event: dict) -> None:
    """Handle an event from the API stream."""
    event_type = event["type"]
    data = event["data"]
    text = data["text"]
    
    if event_type == "text_delta":
        _print_intermediate_output(text)
    elif event_type == "reasoning_delta":
        _print_reasoning(text)
    elif event_type == "echo_result":
        _print_intermediate_output(text + "\n\n")
    elif event_type == "tool_final":
        _print_intermediate_output("\n\n")
    elif event_type == "response_final":
        _print_final(text)
    elif event_type == "error":
        error_type = data.get("error_type", "Unknown")
        print(f"\n{ERROR}❌ Error ({error_type}): {text}{RESET}", file=sys.stderr)
        sys.exit(1)
    elif event_type == "retry_attempt":
        attempt = data.get("attempt", 1)
        max_attempts = data.get("max_attempts", 3)
        print(f"\n{RETRY}🔄 {text} ({attempt}/{max_attempts}){RESET}", file=sys.stderr)

def main(prompt: str) -> None:
    """Run the generator using the REST API."""
    print(f"\n{FINAL}Generating content...{RESET}\n")
    
    try:
        # Make request to API
        response = requests.post(
            API_URL,
            json={'prompt': prompt},
            stream=True
        )
        response.raise_for_status()
        
        # Process the SSE stream
        for line in response.iter_lines():
            if line:
                try:
                    event = json.loads(line)
                    handle_event(event)
                except json.JSONDecodeError:
                    print(f"Error decoding event: {line}", file=sys.stderr)
        
        print(f"\n\nTime taken: {time.time() - START_TIME:.2f} seconds\n\n")
    
    except requests.exceptions.ConnectionError:
        print(f"{ERROR}Error: Could not connect to API at {API_URL}{RESET}")
        print("Make sure the API server is running and accessible.")
        sys.exit(1)
    except requests.exceptions.HTTPError as e:
        print(f"{ERROR}Error: API request failed: {e}{RESET}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nCancelled by user")
        sys.exit(0)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate educational content")
    parser.add_argument("prompt", help="The prompt to generate content for")
    parser.add_argument("--api-url", help=f"API URL (default: {DEFAULT_API_URL})")
    args = parser.parse_args()
    
    # Override API URL if provided
    if args.api_url:
        API_URL = args.api_url
    
    main(args.prompt) 