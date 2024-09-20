from . import client

import argparse
import json
import sys


def main():
    parser = argparse.ArgumentParser(description="simple_msteams")
    parser.add_argument("--url", help="webhook_url", required=True)
    parser.add_argument("--msg", help="message", required=True)
    parser.add_argument("--timeout", type=int, help="request timeout")

    try:
        args = parser.parse_args()
    except argparse.ArgumentError as e:
        print(f"Argument parsing error: {e}")
        parser.print_help()
        sys.exit(2)

    if args.timeout:
        c = client.Client(args.url, args.timeout)
    else:
        c = client.Client(args.url)
    
    try:
        message = json.loads(args.msg)
        
        if isinstance(message, dict):
            c.safe_send(message)
        else:
            c.safe_send(args.msg)
    except json.JSONDecodeError:
        c.safe_send(args.msg)


if __name__ == "__main__":
    main()
