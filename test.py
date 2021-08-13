# Copyright 2021 by Saithalavi M, saithalavi@gmail.com
# All rights reserved.
# This file is part of the Nessaid readline Framework, nessaid_readline python package
# and is released under the "MIT License Agreement". Please see the LICENSE
# file included as part of this package.
#

import nessaid_readline.key as key
from nessaid_readline.readkey import readkey


def main():
    print("Readkey test. Press 'q' to exit")

    key_map = {getattr(key, item): item for item in dir(key) if not item.startswith("_") and item not in ['KEY_NAME_MAP']}


    while True:
        ch = readkey()
        if not ch:
            print("Failed to read that")
            continue
        if ch in key_map:
            print("\r", end="")
            print(ch.encode(), key_map[ch], end="\r\n")
        else:
            print("\r", end="")
            print(ch.encode(), ch, end="\r\n")
        if ch == 'q':
            break

if __name__ == '__main__':
    main()
