

import argparse
import os
import sys
from . import client

def upload_data(m, def_dir: str, loc_path: str, dir_path: str):
    if os.path.isfile(loc_path):
        m.upload_file(loc_path, f'{def_dir}/{dir_path}')
    else:
        m.upload_dir(loc_path,f'{def_dir}/{dir_path}')

def main():
    parser = argparse.ArgumentParser(description='simple-sharepoint')
    parser.add_argument("filename", help="the file to be uploaded")
    parser.add_argument("--remote-dir", help="destination folder", required=True)
    parser.add_argument("--client-id", help="client id", required=True)
    parser.add_argument("--client-secret", help="client secret", required=True)
    parser.add_argument("--default-path", help="default path", required=True)
    parser.add_argument("--base-url", help="base url", required=True)

    try:
        args = parser.parse_args()
    except argparse.ArgumentError as e:
        print(f"Argument parsing error: {e}")
        parser.print_help()
        sys.exit(2)

    c = client.Client(args.client_id, args.client_secret, args.base_url)
    upload_data(c, args.default_path, args.filename, args.remote_dir)


if __name__ == "__main__":
    main()
