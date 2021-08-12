# Copyright 2021 by Saithalavi M, saithalavi@gmail.com
# All rights reserved.
# This file is part of the Nessaid readline Framework, nessaid_readline python package
# and is released under the "MIT License Agreement". Please see the LICENSE
# file included as part of this package.
#

import sys
import time
import string

import nessaid_readline.key as key
import nessaid_readline.readkey as readkey


class NessaidReadlineEOF(Exception):
    pass


class NessaidReadlineKeyboadInterrupt(Exception):
    pass


SPECIAL_KEY_MAP = {
    "cr": key.CR,
    "lf": key.LF,
    "tab": key.TAB,
    "up": key.UP,
    "down": key.DOWN,
    "page-up": key.PAGE_UP,
    "page-down": key.PAGE_DOWN,
    "insert": key.INSERT,
    "delete": key.DELETE,
    "backspace": key.BACKSPACE,
    "home": key.HOME,
    "end": key.END,
    "left": key.LEFT,
    "right": key.RIGHT,
    "up": key.UP,
    "down": key.DOWN,
    "esc": key.ESC,
    "ctrl-a": key.CTRL_A,
    "ctrl-c": key.CTRL_C,
    "ctrl-d": key.CTRL_D,
    "ctrl-d": key.CTRL_E,
    "ctrl-l": key.CTRL_L,
}


class NessaidReadline():

    def __init__(self, stdin=None, stdout=None, stderr=None, history_size=100):
        self._stdin = stdin or sys.stdin
        self._stdout = stdout or sys.stdout
        self._stderr = stderr or sys.stderr
        self._completer = None
        self._line_buffer = ""
        self._complete_char = key.TAB
        self._caret_pos = 0
        self._replace_mode = False

        self._mask_input = False
        self._input_prompt = None
        self._bare_input = False
        self._completing = False
        self._enable_history = True
        self._input_history = False
        self._history = []
        self._history_index = None
        self._input_backup = None

        self._key_bindings = {}

        self._op_bindings = {
            "delete": self._handle_delete,
            "complete": self._handle_complete,
            "backspace": self._handle_backspace,
            "history-previous": self._handle_history_previous,
            "history-next": self._handle_history_next,
            "history-first": self._handle_history_start,
            "history-last": self._handle_history_end,
            "toggle-insert-replace": self._handle_insert_replace,
            "goto-line-left": self._handle_line_left,
            "goto-line-right": self._handle_line_right,
            "goto-line-start": self._handle_line_start,
            "goto-line-end": self._handle_line_end,
            "line-clear": self._handle_line_clear,
            "lookup-back": self._handle_history_lookup_back,
            "lookup-forward": self._handle_history_lookup_forward,
            "line-cancel": self._handle_keyboard_interrupt,
            "line-eof": self._handle_line_eof,
            "toggle-bell": self._handle_toggle_bell,
        }
        self.load_default_bindings()
        self._history_size = history_size
        self._prepare_history_entry = self.prepare_history_entry

        self._enable_bell = True
        self._bell_silence_time = 2
        self._last_bell_time = 0
        self._suppress_bell = False
        self._last_completion = None
        self._last_completion_linebuf = None

    def load_default_bindings(self):
        self._key_bindings.clear()

        self._key_bindings.update({
            key.TAB: self._handle_complete,
            key.UP: self._handle_history_previous,
            key.DOWN: self._handle_history_next,
            key.PAGE_UP: self._handle_history_start,
            key.PAGE_DOWN: self._handle_history_end,
            key.INSERT: self._handle_insert_replace,
            key.DELETE: self._handle_delete,
            key.BACKSPACE: self._handle_backspace,
            key.HOME: self._handle_line_start,
            key.END: self._handle_line_end,
            key.LEFT: self._handle_line_left,
            key.RIGHT: self._handle_line_right,
            key.CTRL_A: self._handle_line_start,
            key.CTRL_E: self._handle_line_end,
            key.CTRL_L: self._handle_line_clear,
            key.CTRL_C: self._handle_keyboard_interrupt,
            key.CTRL_D: self._handle_line_eof,
            key.LF: self._handle_newline,
            key.CR: self._handle_cr,
            key.CTRL_B: self._handle_toggle_bell,
        })

    def get_completer(self):
        return self._completer

    def _handle_cr(self, ch):
        return self._handle_newline(ch)

    def _handle_newline(self, ch):
        self._stdout.write("\r\n")
        self._stdout.flush()
        return True, self._line_buffer

    def _handle_delete(self, ch):
        if self._caret_pos < len(self._line_buffer):
            self.clear_trailing_string()
            if self._caret_pos < len(self._line_buffer) - 1:
                trailing_part = self._line_buffer[self._caret_pos + 1:]
            else:
                trailing_part = ""
            self._stdout.write(trailing_part + " ")
            self._stdout.write("\b" * (len(trailing_part) + 1))
            self._stdout.flush()
            self._line_buffer = self._line_buffer[:self._caret_pos - len(self._line_buffer)] + trailing_part
        else:
            self.play_bell()
        return False, None

    def _handle_backspace(self, ch):
        if self._caret_pos:
            trailing_buf = self._line_buffer[self._caret_pos:]
            if trailing_buf:
                self.clear_trailing_string()
            self._stdout.write("\b \b" + trailing_buf + "\b" * len(trailing_buf))
            self._stdout.flush()
            self._caret_pos -= 1;
            self._line_buffer = self._line_buffer[:-len(trailing_buf) - 1] + trailing_buf
        else:
            self.play_bell()

        return False, None

    def _handle_history_previous(self, ch):
        if not self._bare_input:

            if self._history_index is None:
                self._history_index = len(self._history)

            if self._input_backup is None:
                self._input_backup = self._line_buffer

            if self._history_index:
                self._history_index -= 1
                if len(self._history) > self._history_index:
                    history_line = self._history[self._history_index]
                    self._handle_line_clear("")
                    self.insert_text(history_line)
                else:
                    self.play_bell()
            else:
                self.play_bell()

        return False, None

    def play_bell(self):
        if not self._suppress_bell:

            if self._enable_bell and (self._last_bell_time + self._bell_silence_time) < time.time():
                self._last_bell_time = time.time()
                self._stdout.write("\a")
                self._stdout.flush()

    def enable_bell(self, enable=True):
        self._enable_bell = False if enable is False else True

    def set_bell_silence_time(self, t):
        try:
            t = float(t)
            if t < 0:
                t = 2
        except:
            t = 2
        self._bell_silence_time = t

    def _handle_history_next(self, ch):
        if not self._bare_input:
            if self._history_index is None:
                self._history_index = len(self._history)
            if self._input_backup is None:
                self._input_backup = self._line_buffer
            if self._history_index < len(self._history):
                self._history_index += 1
            if self._history_index < len(self._history):
                history_line = self._history[self._history_index]
                self._handle_line_clear("")
                self.insert_text(history_line)
            elif self._input_backup == self._line_buffer:
                self.play_bell()
            elif self._input_backup is not None:
                self._handle_line_clear("")
                self.insert_text(self._input_backup)
                self._input_backup = None

        return False, None

    def _handle_line_left(self, ch):
        if self._line_buffer and self._caret_pos:
            self._stdout.write("\b")
            self._stdout.flush()
            self._caret_pos -= 1
        else:
            self.play_bell()
        return False, None

    def _handle_line_right(self, ch):
        if self._line_buffer and self._caret_pos < len(self._line_buffer):
            self._stdout.write(self._line_buffer[self._caret_pos])
            self._stdout.flush()
            self._caret_pos += 1
        else:
            self.play_bell()
        return False, None

    def _handle_line_start(self, ch):
        if not self._line_buffer or not self._caret_pos:
            self.play_bell()
            return False, None
        self._stdout.write("\b" * self._caret_pos)
        self._stdout.flush()
        self._caret_pos = 0
        return False, None

    def _handle_line_end(self, ch):
        if not self._line_buffer or self._caret_pos == len(self._line_buffer):
            self.play_bell()
            return False, None
        if self._caret_pos < len(self._line_buffer):
            trailing_buf = self._line_buffer[self._caret_pos:]
            self._stdout.write(trailing_buf)
            self._stdout.flush()
            self._caret_pos = len(self._line_buffer)
        return False, None

    def _handle_line_clear(self, ch):
        if self._line_buffer:
            if self._caret_pos < len(self._line_buffer):
                trailing_buf = self._line_buffer[self._caret_pos:]
                self._stdout.write(" " * len(trailing_buf) + "\b" * len(trailing_buf))
                self._line_buffer = self._line_buffer[:-len(trailing_buf)]
            self._stdout.write("\b" * len(self._line_buffer) + " " * len(self._line_buffer) + "\b" * len(self._line_buffer))
            self._stdout.flush()
            self._line_buffer = ""
            self._caret_pos = 0
        else:
            self.play_bell()
        return False, None

    def _handle_keyboard_interrupt(self, ch):
        self._stdout.write("\r\n")
        self._stdout.flush()
        raise NessaidReadlineKeyboadInterrupt()

    def _handle_line_eof(self, ch):
        self._stdout.write("\r\n")
        self._stdout.flush()
        raise NessaidReadlineEOF()

    def _handle_history_lookup_back(self, ch):
        return False, None

    def _handle_history_lookup_forward(self, ch):
        return False, None

    def _handle_complete(self, ch):
        if self._completing:
            return None

        self._completing = True
        if self._completer:
            index = 0
            completer_options = []
            pre_complete_linebuf = self._line_buffer

            while True:
                c = self._completer(self._line_buffer, index)
                index += 1
                if c is None:
                    break
                completer_options.append(c)

            if completer_options:
                self._stdout.write("\r\n\r\n")
                for c in completer_options:
                    self._stdout.write(c + "\r\n")
                self._stdout.write("\r\n")
                self.print_prompt(self._input_prompt)
                self._stdout.write(self._line_buffer)
                self._stdout.flush()
                self._caret_pos = len(self._line_buffer)

                if set(completer_options) == self._last_completion and self._last_completion_linebuf == self._line_buffer:
                    if pre_complete_linebuf == self._line_buffer:
                        self.play_bell()

                self._last_completion = set(completer_options)
                self._last_completion_linebuf = self._line_buffer
            else:
                if not self._last_completion:
                    self.play_bell()

        self._completing = False
        return False, None

    def _handle_escape(self, ch):
        self.play_bell()
        return False, None

    def _handle_history_start(self, ch):
        if not self._bare_input:
            if self._history:
                if self._input_backup is None:
                    self._input_backup = self._line_buffer
                if self._history_index == 0:
                    self.play_bell()
                else:
                    self._history_index = 0
                    history_line = self._history[0]
                    self._handle_line_clear("")
                    self.insert_text(history_line)
            else:
                self.play_bell()
        return False, None

    def _handle_history_end(self, ch):
        if not self._bare_input:
            if self._history:
                if self._input_backup is None:
                    self._input_backup = self._line_buffer
                if self._history_index == len(self._history):
                    self.play_bell()
                else:
                    self._history_index = len(self._history)
                    self._handle_line_clear("")
                    self.insert_text(self._input_backup)
                    self._input_backup = None
            else:
                self.play_bell()
        return False, None

    def _handle_insert_replace(self, ch):
        self._replace_mode = not self._replace_mode
        return False, None

    def _handle_toggle_bell(self, ch):
        self._enable_bell = not self._enable_bell
        self._stdout.write("\a")
        if self._enable_bell:
            self._stdout.write("\a")
        self._stdout.flush()
        return False, None

    def set_completer(self, completer):
        self._completer = completer

    def parse_and_bind(self, config):
        try:
            key = config.split(":", 1)[0].strip().lower()
        except:
            key = None
        try:
            op = config.split(":", 1)[1].strip().lower()
        except:
            op = None

        if key and op and key in SPECIAL_KEY_MAP and op in self._op_bindings:
            self._key_bindings[SPECIAL_KEY_MAP[key]] = self._op_bindings[op]

    def insert_text(self, text):
        self._suppress_bell = True
        self._handle_line_end("")
        self.send(text)
        self._suppress_bell = False

    def send(self, text):
        for ch in text:
            if ch in self._key_bindings:
                key_handler = self._key_bindings[ch]
                try:
                    key_handler(ch)
                except Exception as e:
                    if type(e) in [NessaidReadlineEOF, NessaidReadlineKeyboadInterrupt]:
                        continue
                    self.play_bell()
                    raise e
            elif self.is_printable(ch):
                self._putchar(ch)

    def get_line_buffer(self):
        return self._line_buffer

    def is_printable(self, ch):
        return ch in string.printable

    def clear_trailing_string(self):
        trailing_buf = self._line_buffer[self._caret_pos:] if self._caret_pos else ""
        if trailing_buf:
            self._stdout.write(" " * len(trailing_buf))
            self._stdout.write("\b" * len(trailing_buf))
            self._stdout.flush()

    def _putchar(self, ch): # noqa
        print_ch = "*" if self._mask_input else ch
        trailing_buf = self._line_buffer[self._caret_pos:] if self._caret_pos < len(self._line_buffer) else ""
        if self._replace_mode:
            if trailing_buf:
                self._line_buffer = self._line_buffer[:-len(trailing_buf)] + ch + trailing_buf[1:]
            else:
                self._line_buffer += ch
            self._stdout.write(print_ch)
        else:
            if trailing_buf:
                self.clear_trailing_string()
            if self._line_buffer:
                if trailing_buf:
                    self._line_buffer = self._line_buffer[:-len(trailing_buf)] + ch + trailing_buf
                else:
                    self._line_buffer += ch
            else:
                self._line_buffer = ch
            self._stdout.write(print_ch + trailing_buf + "\b" * len(trailing_buf))
        self._stdout.flush()
        self._caret_pos += 1

    def print_prompt(self, prompt):
        if prompt:
            prompt.replace("\r", "\n")
            if "\n" in prompt:
                trail_str = prompt.rsplit("\n", 1)[-1]
                prompt.replace("\n", "\r\n")
            else:
                trail_str = prompt
        else:
            return 0
        self._stdout.write(prompt)
        self._stdout.flush()
        return len(trail_str)

    def prepare_history_entry(self, entry):
        return entry

    def set_prepare_history_entry(self, func):
        self._prepare_history_entry = func if callable(func) else self.prepare_history_entry

    def set_history_size(self, hsize):
        self._history_size = hsize

    def _add_to_history(self, line):
        if line and self._input_history:
            entry = self._prepare_history_entry(line)
            if not self._history or self._history[-1] != entry:
                self._history.append(entry)
                while len(self._history) > self._history_size:
                    self._history.pop(0)

    def _input(self, prompt, mask_input=False, bare_input=False):

        self.print_prompt(prompt)
        self._caret_pos = 0
        self._line_buffer = ""
        if bare_input:
            self._input_history = False
        else:
            self._input_history = self._enable_history

        try:
            self._mask_input = mask_input
            self._input_prompt = prompt
            self._bare_input = bare_input

            while True:
                try:
                    ch = readkey.readkey(self._stdin)
                except Exception as e: # noqa
                    self._add_to_history(self._line_buffer)
                    return self._line_buffer

                if ch in self._key_bindings:
                    key_handler = self._key_bindings[ch]
                    if key_handler != self._handle_complete:
                        self._last_completion = None
                    res, ret = key_handler(ch)
                    self._add_to_history(ret)
                    if res is True:
                        return ret
                elif self.is_printable(ch):
                    self._putchar(ch)
        except Exception as e:
            if type(e) in [NessaidReadlineKeyboadInterrupt, NessaidReadlineEOF]:
                raise e
            self.play_bell()
            self._stderr.write("Exception in input: " + str(type(e)) + " " + str(e))
            return ""
        finally:
            self._history_index = None
            self._completing = False
            self._mask_input = False
            self._input_prompt = None
            self._input_history = False
            self._input_backup = None
            self._bare_input = False
            self._last_completion = None
            self._last_completion_linebuf = None

    def input(self, prompt=None, mask_input=False):
        return self._input(prompt or "", mask_input=mask_input, bare_input=True)

    def readline(self, prompt=None):
        return self._input(prompt or "", mask_input=False, bare_input=False)