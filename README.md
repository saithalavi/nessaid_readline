# nessaid_readline
Basic readline interface for CLI apps, common for Windows, Linux and Mac systems

## Installation

This package can be installed by cloning this repo and running python3 setup.py install from top directory. It's also available in pypi. pip3 install nessaid_readline will install the package.

## Basic line editing
Supports following basic line editing options

Arrow keys
History and search CTRL+R for backward lookup, CTRL+S for forward lookup
PAGE_UP for first history entry page down for last

HOME or CTRL+A for beginning of line END or CTRL+E for end of line

INSERT for toggling INSERT/REPLACE

CTRL+B toggles the terminal bell/beep sound. But it is seen to be misbehaving.

## Key bindings
Basic key binding support is available

Refer key.py: KEY_NAME_MAP for key names

Refer readline.py:NessaidReadline._op_bindings for available actions/hooks

## Usage:

```python
from nessaid_readline.readline import NessaidReadline, NessaidReadlineEOF, NessaidReadlineKeyboadInterrupt

enable_bell = False # Disable the BEEP alerts from readline
prompt = "# "
mask_input = False # Show the echo in plain text
readline = NessaidReadline()
readline.enable_bell(enable_bell)

# Custom key bindings
readline.parse_and_bind("esc: line-eof") # This will cause 'ESC' to be mapped to EOF

readline.parse_and_bind("ctrl-k: goto-line-start") # ctrl+k will move the cursor to start of line
readline.parse_and_bind("ctrl-l: goto-line-end") # ctrl+k will move the cursor to end of line

while True:
    try:
        if not mask_input:
            # readline.readline(prompt) is equivalent to readline.input(prompt, False) or readline.input(prompt)
            # Using both methods just for usage reference.
            line = readline.readline(prompt)
        else:
            line = readline.input(prompt, mask_input)
    except NessaidReadlineKeyboadInterrupt:
        print("CTRL+C")
        break
    except NessaidReadlineEOF:
        print("EOF")
        break

    mask_input = not mask_input
    print("Last input:", line)
```
