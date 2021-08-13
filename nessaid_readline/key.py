# Copyright 2021 by Saithalavi M, saithalavi@gmail.com
# All rights reserved.
# This file is part of the Nessaid readline Framework, nessaid_readline python package
# and is released under the "MIT License Agreement". Please see the LICENSE
# file included as part of this package.
#

# common
CR = "\x0d"
LF = "\x0a"
BACKSPACE = "\x7f"
SPACE = "\x20"
TAB = "\x09"
ESC = "\x1b"
INSERT = "\x1b\x5b\x32\x7e"
DELETE = "\x1b\x5b\x33\x7e"
PAGE_UP = "\x1b\x5b\x35\x7e"
PAGE_DOWN = "\x1b\x5b\x36\x7e"
HOME = "\x1b\x5b\x48"
END = "\x1b\x5b\x46"

# cursors
UP = "\x1b\x5b\x41"
DOWN = "\x1b\x5b\x42"
LEFT = "\x1b\x5b\x44"
RIGHT = "\x1b\x5b\x43"

# CTRL
CTRL_A = '\x01'
CTRL_B = '\x02'
CTRL_C = '\x03'
CTRL_D = '\x04'
CTRL_E = '\x05'
CTRL_F = '\x06'
CTRL_G = '\x07'
# CTRL_H is '\x08', '\b', BACKSPACE
# CTRL_I is '\x09', '\t', TAB
# CTRL_J is '\x0a', '\n', LF
CTRL_K = '\x0b'
CTRL_L = '\x0c'
# CTRL_M is '\x0d', '\r', CR
CTRL_N = '\x0e'
CTRL_O = '\x0f'
CTRL_P = '\x10'
CTRL_Q = '\x11'
CTRL_R = '\x12'
CTRL_S = '\x13'
CTRL_T = '\x14'
CTRL_U = '\x15'
CTRL_V = '\x16'
CTRL_W = '\x17'
CTRL_X = '\x18'
CTRL_Y = '\x19'
CTRL_Z = '\x1a'

# ALT
ALT_A = "\x1b" + 'a'
ALT_B = "\x1b" + 'b'
ALT_C = "\x1b" + 'c'
ALT_D = "\x1b" + 'd'
ALT_E = "\x1b" + 'e'
ALT_F = "\x1b" + 'f'
ALT_G = "\x1b" + 'g'
ALT_H = "\x1b" + 'h'
ALT_I = "\x1b" + 'i'
ALT_J = "\x1b" + 'j'
ALT_K = "\x1b" + 'k'
ALT_L = "\x1b" + 'l'
ALT_M = "\x1b" + 'm'
ALT_N = "\x1b" + 'n'
ALT_O = "\x1b" + 'o'
ALT_P = "\x1b" + 'p'
ALT_Q = "\x1b" + 'q'
ALT_R = "\x1b" + 'r'
ALT_S = "\x1b" + 's'
ALT_T = "\x1b" + 't'
ALT_U = "\x1b" + 'u'
ALT_V = "\x1b" + 'v'
ALT_W = "\x1b" + 'w'
ALT_X = "\x1b" + 'x'
ALT_Y = "\x1b" + 'y'
ALT_Z = "\x1b" + 'z'

# CTRL + ALT
CTRL_ALT_A = "\x1b" + CTRL_A
CTRL_ALT_B = "\x1b" + CTRL_B
CTRL_ALT_C = "\x1b" + CTRL_C
CTRL_ALT_D = "\x1b" + CTRL_D
CTRL_ALT_E = "\x1b" + CTRL_E
CTRL_ALT_F = "\x1b" + CTRL_F
CTRL_ALT_G = "\x1b" + CTRL_G
CTRL_ALT_H = "\x1b" + '\x08'
CTRL_ALT_I = "\x1b" + '\x09'
CTRL_ALT_J = "\x1b" + '\x0a'
CTRL_ALT_K = "\x1b" + CTRL_K
CTRL_ALT_L = "\x1b" + CTRL_L
CTRL_ALT_M = "\x1b" + '\x0d'
CTRL_ALT_N = "\x1b" + CTRL_N
CTRL_ALT_O = "\x1b" + CTRL_O
CTRL_ALT_P = "\x1b" + CTRL_P
CTRL_ALT_Q = "\x1b" + CTRL_Q
CTRL_ALT_R = "\x1b" + CTRL_R
CTRL_ALT_S = "\x1b" + CTRL_S
CTRL_ALT_T = "\x1b" + CTRL_T
CTRL_ALT_U = "\x1b" + CTRL_U
CTRL_ALT_V = "\x1b" + CTRL_V
CTRL_ALT_W = "\x1b" + CTRL_W
CTRL_ALT_X = "\x1b" + CTRL_X
CTRL_ALT_Y = "\x1b" + CTRL_Y
CTRL_ALT_Z = "\x1b" + CTRL_Z

CTRL_ALT_DELETE = "\x1b\x5b\x33\x5e"


KEY_NAME_MAP = {
    "cr": CR,
    "lf": LF,
    "tab": TAB,
    "up": UP,
    "down": DOWN,
    "page-up": PAGE_UP,
    "page-down": PAGE_DOWN,
    "insert": INSERT,
    "delete": DELETE,
    "backspace": BACKSPACE,
    "home": HOME,
    "end": END,
    "left": LEFT,
    "right": RIGHT,
    "up": UP,
    "down": DOWN,
    "esc": ESC,
    "escape": ESC,
    "ctrl-a": CTRL_A,
    "ctrl-b": CTRL_B,
    "ctrl-c": CTRL_C,
    "ctrl-d": CTRL_D,
    "ctrl-e": CTRL_E,
    "ctrl-f": CTRL_F,
    "ctrl-g": CTRL_G,
    "ctrl-k": CTRL_K,
    "ctrl-l": CTRL_L,
    "ctrl-n": CTRL_N,
    "ctrl-o": CTRL_O,
    "ctrl-p": CTRL_P,
    "ctrl-q": CTRL_Q,
    "ctrl-r": CTRL_R,
    "ctrl-s": CTRL_S,
    "ctrl-t": CTRL_T,
    "ctrl-u": CTRL_U,
    "ctrl-v": CTRL_V,
    "ctrl-w": CTRL_W,
    "ctrl-x": CTRL_X,
    "ctrl-y": CTRL_Y,
    "ctrl-z": CTRL_Z,
    "alt-a": ALT_A,
    "alt-b": ALT_B,
    "alt-c": ALT_C,
    "alt-d": ALT_D,
    "alt-e": ALT_E,
    "alt-f": ALT_F,
    "alt-g": ALT_G,
    "alt-h": ALT_H,
    "alt-i": ALT_I,
    "alt-j": ALT_J,
    "alt-k": ALT_K,
    "alt-l": ALT_L,
    "alt-m": ALT_M,
    "alt-n": ALT_N,
    "alt-o": ALT_O,
    "alt-p": ALT_P,
    "alt-q": ALT_Q,
    "alt-r": ALT_R,
    "alt-s": ALT_S,
    "alt-t": ALT_T,
    "alt-u": ALT_U,
    "alt-v": ALT_V,
    "alt-w": ALT_W,
    "alt-x": ALT_X,
    "alt-y": ALT_Y,
    "alt-z": ALT_Z,
    "ctrl-alt-a": CTRL_ALT_A,
    "ctrl-alt-b": CTRL_ALT_B,
    "ctrl-alt-c": CTRL_ALT_C,
    "ctrl-alt-d": CTRL_ALT_D,
    "ctrl-alt-e": CTRL_ALT_E,
    "ctrl-alt-f": CTRL_ALT_F,
    "ctrl-alt-g": CTRL_ALT_G,
    "ctrl-alt-h": CTRL_ALT_H,
    "ctrl-alt-i": CTRL_ALT_I,
    "ctrl-alt-j": CTRL_ALT_J,
    "ctrl-alt-k": CTRL_ALT_K,
    "ctrl-alt-l": CTRL_ALT_L,
    "ctrl-alt-m": CTRL_ALT_M,
    "ctrl-alt-n": CTRL_ALT_N,
    "ctrl-alt-o": CTRL_ALT_O,
    "ctrl-alt-p": CTRL_ALT_P,
    "ctrl-alt-q": CTRL_ALT_Q,
    "ctrl-alt-r": CTRL_ALT_R,
    "ctrl-alt-s": CTRL_ALT_S,
    "ctrl-alt-t": CTRL_ALT_T,
    "ctrl-alt-u": CTRL_ALT_U,
    "ctrl-alt-v": CTRL_ALT_V,
    "ctrl-alt-w": CTRL_ALT_W,
    "ctrl-alt-x": CTRL_ALT_X,
    "ctrl-alt-y": CTRL_ALT_Y,
    "ctrl-alt-z": CTRL_ALT_Z,
    "ctrl-alt-delete": CTRL_ALT_DELETE,
}
