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
