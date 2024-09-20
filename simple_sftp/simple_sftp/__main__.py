from . import client
import argparse
import sys


def main():
    parser = argparse.ArgumentParser(description="simple_sftp")
    parser.add_argument("--local", help="local folder", required=True)
    parser.add_argument("--remote", help="remote folder", required=True)
    parser.add_argument("--ip", help="flag to sftp ip", required=True)
    parser.add_argument("--port", help="flag to sftp port")
    parser.add_argument("--user", help="flag to user name", required=True)
    parser.add_argument("--pwd", help="flag to user password", required=True)
    parser.add_argument("--upload", action="store_true", help="flag to upload the file")
    parser.add_argument(
        "--download", action="store_true", help="flag to download the file"
    )

    try:
        args = parser.parse_args()
    except argparse.ArgumentError as e:
        print(f"Argument parsing error: {e}")
        parser.print_help()
        sys.exit(2)

    if not args.upload and not args.download:
        args.upload = True

    port = 22
    if args.port is not None:
        port = int(args.port)

    c = client.Client(args.ip, args.user, args.pwd, port)

    if args.upload:
        c.upload(args.remote, args.local)
    elif args.download:
        c.download(args.remote, args.local)


if __name__ == "__main__":
    main()
