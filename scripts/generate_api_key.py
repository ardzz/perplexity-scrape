#!/usr/bin/env python3
"""Generate a cryptographically secure API key."""

import argparse
import secrets


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--length", type=int, default=32, help="Key length in bytes")
    args = parser.parse_args()
    print(secrets.token_urlsafe(args.length))


if __name__ == "__main__":
    main()
