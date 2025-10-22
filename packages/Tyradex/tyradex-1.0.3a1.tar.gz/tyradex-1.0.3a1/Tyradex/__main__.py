import json
import os
import sys

try:
    import API as API
except ModuleNotFoundError:
    import Tyradex.API as API

def help_message():
    print("Usage:")
    print('py' if os.name == 'nt' else 'python3', end='')
    print(" -m Tyradex [options] <endpoint>\n")
    print("Description:")
    print("\tTyradex for Python is an easy-to-use API based on the web version of Tyradex by Yarkis and Ashzuu.\n")
    print("Options:")
    print("\t-h, --help     Display this help message and exit.")
    print("\t-v, --version  Display the version and exit.")

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1].lower() in ['-h', '--help']:
        help_message()
    elif len(sys.argv) > 1 and sys.argv[1].lower() in ['-v', '--version']:
        with open('../metadata.json', 'r') as f:
            print(API.VERSION)
    else:
        print(json.dumps(API.Tyradex.call('/'.join(sys.argv[1:])), indent=4))