#!/usr/bin/env python3
"""Token management CLI for book-mcp.

Usage:
  uv run python manage_tokens.py list
  uv run python manage_tokens.py add <user_id>
  uv run python manage_tokens.py revoke <user_id>
"""
import secrets
import sys
from pathlib import Path

from dotenv import dotenv_values, set_key, unset_key

ENV_FILE = Path(__file__).parent / ".env.library"
PREFIX = "TOKEN_"


def list_users():
    env = dotenv_values(ENV_FILE)
    users = [k[len(PREFIX):] for k in env if k.startswith(PREFIX)]
    if not users:
        print("No users registered.")
    else:
        print(f"{'USER ID':<30} TOKEN")
        print("-" * 70)
        for user_id in sorted(users):
            token = env[f"{PREFIX}{user_id}"]
            print(f"{user_id:<30} {token}")


def add_user(user_id: str):
    env = dotenv_values(ENV_FILE)
    key = f"{PREFIX}{user_id}"
    if key in env:
        print(f"User '{user_id}' already exists. Revoke first if you want to rotate the token.")
        sys.exit(1)
    token = secrets.token_hex(32)
    set_key(ENV_FILE, key, token)
    print(f"User '{user_id}' added.")
    print(f"Token: {token}")
    print()
    print("Give the user this token and have them set it in their .mcp.json:")
    print(f'  "env": {{ "USER_TOKEN": "{token}" }}')


def revoke_user(user_id: str):
    env = dotenv_values(ENV_FILE)
    key = f"{PREFIX}{user_id}"
    if key not in env:
        print(f"User '{user_id}' not found.")
        sys.exit(1)
    unset_key(ENV_FILE, key)
    print(f"User '{user_id}' revoked. Restart the server for changes to take effect.")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    command = sys.argv[1]

    if command == "list":
        list_users()
    elif command == "add":
        if len(sys.argv) < 3:
            print("Usage: manage_tokens.py add <user_id>")
            sys.exit(1)
        add_user(sys.argv[2])
    elif command == "revoke":
        if len(sys.argv) < 3:
            print("Usage: manage_tokens.py revoke <user_id>")
            sys.exit(1)
        revoke_user(sys.argv[2])
    else:
        print(f"Unknown command: {command}")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
