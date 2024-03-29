# Copyright 2021 by Saithalavi M, saithalavi@gmail.com
# All rights reserved.
# This file is part of the Nessaid readline Framework, nessaid_readline python package
# and is released under the "MIT License Agreement". Please see the LICENSE
# file included as part of this package.
#

import re
import sys
import time
import string
import asyncio

from concurrent.futures import ThreadPoolExecutor

import nessaid_readline.key as key
import nessaid_readline.readkey as readkey

if sys.platform.startswith("linux") or sys.platform == "darwin":

    import os
    import tty # noqa
    import select # noqa
    import termios # pylint: disable=import-error
    import fcntl # pylint: disable=import-error

elif sys.platform in ("win32", "cygwin"):
    import msvcrt # noqa

    xlate_dict = {
        8: key.BACKSPACE,
        27: key.ESC,
        7680: key.ALT_A,
        21216: key.INSERT,
        21472: key.DELETE,
        18912: key.PAGE_UP,
        20960: key.PAGE_DOWN,
        18400: key.HOME,
        20448: key.END,
        18656: key.UP,
        20704: key.DOWN,
        19424: key.LEFT,
        19936: key.RIGHT,
    }
else:
    raise readkey.PlatformNotSupported(sys.platform)


class NessaidReadlineEOF(Exception):
    pass


class NessaidReadlineKeyboadInterrupt(Exception):
    pass


SPECIAL_KEY_MAP = key.KEY_NAME_MAP


class NessaidAsyncReadline():

    EXECUTOR = ThreadPoolExecutor(max_workers=3)

    def __init__(self, loop=None, stdin=None, stdout=None, stderr=None, history_size=100):
        self._loop = loop or asyncio.get_event_loop()
        self._readbuf = []
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

        self._normal_key_bindings = {}
        self._lookup_key_bindings = {}

        self._op_bindings = {
            "carriage-return": self._handle_cr,
            "newline": self._handle_newline,
            "delete": self._handle_delete,
            "complete": self._handle_complete,
            "backspace": self._handle_backspace,
            "lookup-backspace": self._handle_lookup_backspace,
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
            "open-reverse-lookup": self._handle_reverse_lookup,
            "forward-lookup-result": self._handle_lookup_result,
            "cancel-lookup-result": self._handle_cancel_lookup_result,
            "none": self._handle_nop,
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
        self._init_lookup_state()
        self._keyboard_interrupted = False
        self._executor = NessaidAsyncReadline.EXECUTOR

    def write(self, s):
        try:
            op = "*" * len(s) if self._mask_input else s
            self._stdout.write(op)
            self._stdout.flush()
        except:
            pass

    def handle_external_keyboard_interrupt(self):
        self._keyboard_interrupted = True

    def load_default_bindings(self):
        self._normal_key_bindings.clear()

        self._normal_key_bindings.update({
            key.TAB: "complete",
            key.UP: "history-previous",
            key.DOWN: "history-next",
            key.PAGE_UP: "history-first",
            key.PAGE_DOWN: "history-last",
            key.INSERT: "toggle-insert-replace",
            key.DELETE: "delete",
            key.BACKSPACE: "backspace",
            key.HOME: "goto-line-start",
            key.END: "goto-line-end",
            key.LEFT: "goto-line-left",
            key.RIGHT: "goto-line-right",
            key.CTRL_A: "goto-line-start",
            key.CTRL_E: "goto-line-end",
            key.CTRL_L: "line-clear",
            key.CTRL_C: "line-cancel",
            key.CTRL_D: "line-eof",
            key.LF: "newline",
            key.CR: "carriage-return",
            key.CTRL_B: "toggle-bell",
            key.CTRL_R: "open-reverse-lookup",
        })

        self._lookup_key_bindings.clear()
        self._lookup_key_bindings.update({
            key.TAB: "none",
            key.ESC: "cancel-lookup-result",
            key.LF: "forward-lookup-result",
            key.CR: "forward-lookup-result",
            key.TAB: "forward-lookup-result",
            key.RIGHT: "forward-lookup-result",
            key.LEFT: "forward-lookup-result",
            key.UP: "forward-lookup-result",
            key.DOWN: "forward-lookup-result",
            key.PAGE_UP: "forward-lookup-result",
            key.PAGE_DOWN: "forward-lookup-result",
            key.INSERT: "forward-lookup-result",
            key.DELETE: "forward-lookup-result",
            key.CTRL_R: "lookup-back",
            key.CTRL_S: "lookup-forward",
            key.BACKSPACE: "lookup-backspace",
        })

    def get_completer(self):
        return self._completer

    async def _handle_nop(self, ch, **kwargs): # noqa
        return False, False, None

    async def _handle_cr(self, ch, **kwargs): # noqa
        return await self._handle_newline(ch)

    async def _handle_newline(self, ch, **kwargs): # noqa
        self._stdout.write("\r\n")
        self._stdout.flush()
        return True, self._line_buffer

    async def _handle_delete(self, ch, **kwargs): # noqa
        if self._caret_pos < len(self._line_buffer):
            self.clear_trailing_string()
            if self._caret_pos < len(self._line_buffer) - 1:
                trailing_part = self._line_buffer[self._caret_pos + 1:]
            else:
                trailing_part = ""
            self.write(trailing_part)
            self._stdout.write(" ")
            self._stdout.write("\b" * (len(trailing_part) + 1))
            self._stdout.flush()
            self._line_buffer = self._line_buffer[:self._caret_pos - len(self._line_buffer)] + trailing_part
        else:
            self.play_bell()
        return False, None

    async def _handle_backspace(self, ch, **kwargs): # noqa
        if self._caret_pos:
            trailing_buf = self._line_buffer[self._caret_pos:]
            if trailing_buf:
                self.clear_trailing_string()
            self._stdout.write("\b \b")
            self.write(trailing_buf)
            self._stdout.write("\b" * len(trailing_buf))
            self._stdout.flush()
            self._caret_pos -= 1
            self._line_buffer = self._line_buffer[:-len(trailing_buf) - 1] + trailing_buf
        else:
            self.play_bell()

        return False, None

    async def _handle_history_previous(self, ch, **kwargs): # noqa
        if not self._bare_input:

            if self._history_index is None or self._history_index < 0:
                self._history_index = len(self._history)

            if self._input_backup is None:
                self._input_backup = self._line_buffer

            if self._history_index:
                self._history_index -= 1
                if len(self._history) > self._history_index:
                    history_line = self._history[self._history_index]
                    self._suppress_bell = True
                    await self._handle_line_clear("")
                    await self.insert_text(history_line)
                    self._suppress_bell = False
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

    async def _handle_history_next(self, ch, **kwargs): # noqa
        if not self._bare_input:
            if self._history_index is None:
                self._history_index = len(self._history)
            if self._input_backup is None:
                self._input_backup = self._line_buffer
            if self._history_index < len(self._history):
                self._history_index += 1
            if self._history_index < len(self._history):
                history_line = self._history[self._history_index]
                self._suppress_bell = True
                await self._handle_line_clear("")
                await self.insert_text(history_line)
                self._suppress_bell = False
            elif self._input_backup == self._line_buffer:
                self.play_bell()
            elif self._input_backup is not None:
                self._suppress_bell = True
                await self._handle_line_clear("")
                await self.insert_text(self._input_backup)
                self._input_backup = None
                self._suppress_bell = False

        return False, None

    async def _handle_line_left(self, ch, **kwargs): # noqa
        if self._line_buffer and self._caret_pos:
            self._stdout.write("\b")
            self._stdout.flush()
            self._caret_pos -= 1
        else:
            self.play_bell()
        return False, None

    async def _handle_line_right(self, ch, **kwargs): # noqa
        if self._line_buffer and self._caret_pos < len(self._line_buffer):
            self.write(self._line_buffer[self._caret_pos])
            self._caret_pos += 1
        else:
            self.play_bell()
        return False, None

    async def _handle_line_start(self, ch, **kwargs): # noqa
        if not self._line_buffer or not self._caret_pos:
            self.play_bell()
            return False, None
        self._stdout.write("\b" * self._caret_pos)
        self._stdout.flush()
        self._caret_pos = 0
        return False, None

    async def _handle_line_end(self, ch, **kwargs): # noqa
        if not self._line_buffer or self._caret_pos == len(self._line_buffer):
            self.play_bell()
            return False, None
        if self._caret_pos < len(self._line_buffer):
            trailing_buf = self._line_buffer[self._caret_pos:]
            self.write(trailing_buf)
            self._caret_pos = len(self._line_buffer)
        return False, None

    async def _handle_line_clear(self, ch, **kwargs): # noqa
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

    async def _handle_keyboard_interrupt(self, ch, **kwargs): # noqa
        self._stdout.write("\r\n")
        self._stdout.flush()
        raise NessaidReadlineKeyboadInterrupt()

    async def _handle_line_eof(self, ch, **kwargs): # noqa
        self._stdout.write("\r\n")
        self._stdout.flush()
        raise NessaidReadlineEOF()

    async def _handle_complete(self, ch, **kwargs): # noqa
        if self._completing:
            return None

        self._completing = True
        if self._completer:
            index = 0
            completer_options = []
            pre_complete_linebuf = self._line_buffer

            while True:
                if asyncio.iscoroutinefunction(self._completer):
                    c = await self._completer(self._line_buffer, index)
                else:
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

    async def _handle_escape(self, ch, **kwargs): # noqa
        self.play_bell()
        return False, None

    async def _handle_history_start(self, ch, **kwargs): # noqa
        if not self._bare_input:
            if self._history:
                if self._input_backup is None:
                    self._input_backup = self._line_buffer
                if self._history_index == 0:
                    self.play_bell()
                else:
                    self._suppress_bell = True
                    self._history_index = 0
                    history_line = self._history[0]
                    await self._handle_line_clear("")
                    await self.insert_text(history_line)
                    self._suppress_bell = False
            else:
                self.play_bell()
        return False, None

    async def _handle_history_end(self, ch, **kwargs): # noqa
        if not self._bare_input:
            if self._history:
                if self._input_backup is None:
                    self._input_backup = self._line_buffer
                if self._history_index == len(self._history):
                    self.play_bell()
                else:
                    self._suppress_bell = True
                    self._history_index = len(self._history)
                    await self._handle_line_clear("")
                    await self.insert_text(self._input_backup)
                    self._input_backup = None
                    self._suppress_bell = False
            else:
                self.play_bell()
        return False, None

    async def _handle_insert_replace(self, ch, **kwargs): # noqa
        self._replace_mode = not self._replace_mode
        return False, None

    async def _handle_toggle_bell(self, ch, **kwargs): # noqa
        self._enable_bell = not self._enable_bell
        self._stdout.write("\a")
        if self._enable_bell:
            self._stdout.write("\a")
        self._stdout.flush()
        return False, None

    def _init_lookup_state(self):
        self._lookup_string = ""
        self._lookup_direction = "back"
        self._lookup_index = len(self._history)

        self._current_lookup_match = None
        self._previous_lookup_match = ""
        self._current_lookup_indices = []
        self._current_match_index = 0
        self._lookup_failed = True

    async def _handle_reverse_lookup(self, ch, **kwargs): # noqa

        if self._bare_input:
            return False, None

        self._init_lookup_state()

        if self._line_buffer:
            self._lookup_string = self._line_buffer

        self._input_backup = self._line_buffer

        line_len = len(self._input_prompt) + len(self._line_buffer)

        while True:

            if not self._line_buffer:
                self._lookup_failed = False

            if self._lookup_string:

                if self._current_lookup_match:
                    if self._lookup_direction == "forward":
                        if self._current_match_index < len(self._current_lookup_indices) - 1:
                            self._current_match_index += 1
                        else:
                            self._current_lookup_match = None
                            self._lookup_index += 1
                    else:
                        if self._current_match_index > 0:
                            self._current_match_index -= 1
                        else:
                            self._current_lookup_match = None
                            self._lookup_index -= 1
                else:
                    if self._lookup_direction == "forward":
                        if self._lookup_index < len(self._history):
                            self._lookup_index += 1
                        else:
                            self._lookup_failed = True
                    else:
                        if self._lookup_index >= 0:
                            self._lookup_index -= 1
                        else:
                            self._lookup_failed = True

                if not self._current_lookup_match:
                    if self._lookup_index >= 0 and self._lookup_index < len(self._history):
                        cur_line = self._history[self._lookup_index]
                        lookup_string = self._lookup_string.replace("\\", "\\\\")
                        self._current_lookup_indices = [m.start() for m in re.finditer(lookup_string, cur_line)]
                        if len(self._current_lookup_indices) :
                            self._current_lookup_match = self._previous_lookup_match = cur_line
                            self._lookup_failed = False
                            if self._lookup_direction == "forward":
                                self._current_match_index = 0
                            else:
                                self._current_match_index = len(self._current_lookup_indices) - 1
                        else:
                            self._current_lookup_match = None
                            continue
                    else:
                        self._lookup_failed = True

            lookup_prompt = "({failed}reverse-i-search`{lookup_str}'): {previous_match}".format(
                failed = "failed " if self._lookup_failed else "",
                lookup_str=self._lookup_string,
                previous_match=self._previous_lookup_match
            )

            self._suppress_bell = True
            await self._handle_line_end("")
            self._stdout.write("\b" * line_len)
            self._stdout.write(" " * line_len)
            self._stdout.write("\b" * line_len)
            self._stdout.write(lookup_prompt)
            line_len = len(lookup_prompt)
            try:
                if self._current_lookup_indices:
                    caret_position = len(self._previous_lookup_match) - self._current_lookup_indices[self._current_match_index]
                else:
                    caret_position = len(self._previous_lookup_match)
                self._stdout.write("\b" * caret_position)
            except:
                pass
            self._stdout.flush()

            while True:
                ch = await self.readchar()
                if ch in self._lookup_key_bindings:
                    key_binding = self._lookup_key_bindings[ch]
                    key_handler = self._op_bindings[key_binding]
                    status, ret_status, ret = await key_handler(ch)
                    if status:
                        return ret_status, ret
                    else:
                        break
                elif self.is_printable(ch):
                    self._lookup_putchar(ch)
                    break
                else:
                    continue

        return False, None

    async def _handle_lookup_result(self, ch, **kwargs): # noqa

        lookup_prompt = "({failed}reverse-i-search`{lookup_str}'): {previous_match}".format(
            failed = "failed " if self._lookup_failed else "",
            lookup_str=self._lookup_string,
            previous_match=self._previous_lookup_match
        )

        try:
            caret_position = len(self._previous_lookup_match) - self._current_lookup_indices[self._current_match_index]
        except:
            caret_position = 0
        prompt_len = len(lookup_prompt)

        self._stdout.write("\b" * (prompt_len - caret_position))
        self._stdout.write(" " * prompt_len)
        self._stdout.write("\b" * prompt_len)

        self.print_prompt(self._input_prompt)
        self._caret_pos = 0
        self._line_buffer = ""
        if not self._previous_lookup_match:
            await self.insert_text(self._lookup_string)
        else:
            await self.insert_text(self._previous_lookup_match)

        if ch in self._normal_key_bindings:
            key_handler = self._op_bindings[self._normal_key_bindings[ch]]
            if key_handler != self._handle_complete:
                self._last_completion = None
            self._history_index = self._lookup_index
            return (True,) + await key_handler(ch)

        return True, False, None

    async def _handle_cancel_lookup_result(self, ch, **kwargs): # noqa

        lookup_prompt = "({failed}reverse-i-search`{lookup_str}'): {previous_match}".format(
            failed = "failed " if self._lookup_failed else "",
            lookup_str=self._lookup_string,
            previous_match=self._previous_lookup_match
        )

        try:
            caret_position = len(self._previous_lookup_match) - self._current_lookup_indices[self._current_match_index]
        except:
            caret_position = 0
        prompt_len = len(lookup_prompt)

        self._stdout.write("\b" * (prompt_len - caret_position))
        self._stdout.write(" " * prompt_len)
        self._stdout.write("\b" * prompt_len)

        self.print_prompt(self._input_prompt)
        self._caret_pos = 0
        self._line_buffer = ""
        await self.insert_text(self._input_backup)
        self._input_backup = None
        self._lookup_index = len(self._history)
        return True, False, None

    async def _handle_lookup_backspace(self, ch, **kwargs): # noqa
        lookup_str = self._lookup_string
        self._init_lookup_state()
        self._lookup_string = lookup_str[:-1]
        return False, False, None

    def _lookup_putchar(self, ch, **kwargs): # noqa
        lookup_str = self._lookup_string
        self._init_lookup_state()
        self._lookup_string = lookup_str + ch

    async def _handle_history_lookup_back(self, ch, **kwargs): # noqa
        self._lookup_direction = "back"
        return False, False, None

    async def _handle_history_lookup_forward(self, ch, **kwargs): # noqa
        self._lookup_direction = "forward"
        return False, False, None

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
            self._normal_key_bindings[SPECIAL_KEY_MAP[key]] = op

    async def insert_text(self, text):
        self._suppress_bell = True
        await self._handle_line_end("")
        await self.send(text)
        self._suppress_bell = False

    async def send(self, text):
        for ch in text:
            if ch in self._normal_key_bindings:
                key_handler = self._op_bindings[self._normal_key_bindings[ch]]
                try:
                    await key_handler(ch)
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

    def _putchar(self, ch, **kwargs): # noqa
        trailing_buf = self._line_buffer[self._caret_pos:] if self._caret_pos < len(self._line_buffer) else ""
        if self._replace_mode:
            if trailing_buf:
                self._line_buffer = self._line_buffer[:-len(trailing_buf)] + ch + trailing_buf[1:]
            else:
                self._line_buffer += ch
            self.write(ch)
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
            self.write(ch + trailing_buf)
            self._stdout.write("\b" * len(trailing_buf))
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

    async def readchar(self):
        if self._readbuf:
            return self._readbuf.pop(0)
        else:
            try:
                self._readbuf = await self._loop.run_in_executor(self._executor, self.readkeys)
            except KeyboardInterrupt:
                self._readbuf.append(key.CTRL_C)
            return self._readbuf.pop(0)

    def flush(self):
        """"
        Flushes the cached input data
        """
        self._readbuf = []

    async def _input(self, prompt, mask_input=False, bare_input=False):

        self.print_prompt(prompt)
        self._caret_pos = 0
        self._line_buffer = ""
        if bare_input or mask_input:
            self._input_history = False
        else:
            self._input_history = self._enable_history

        try:
            self._mask_input = mask_input
            self._input_prompt = prompt
            self._bare_input = bare_input

            while True:
                try:
                    ch = await self.readchar()
                except KeyboardInterrupt:
                    pass
                except Exception as e: # noqa
                    self._add_to_history(self._line_buffer)
                    return self._line_buffer

                if ch in self._normal_key_bindings:
                    key_handler = self._op_bindings[self._normal_key_bindings[ch]]
                    if key_handler != self._handle_complete:
                        self._last_completion = None
                    res, ret = await key_handler(ch)
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

    async def input(self, prompt=None, mask_input=False):
        return await self._input(prompt or "", mask_input=mask_input, bare_input=True)

    async def readline(self, prompt=None):
        inp = await self._input(prompt or "", mask_input=False, bare_input=False)
        return inp

    if sys.platform.startswith("linux") or sys.platform == "darwin":

        def _setup_tty(self):
            old_settings = None
            try:
                fd = self._stdin.fileno()
                old_settings = termios.tcgetattr(fd) # pylint: disable=undefined-variable
                tty.setraw(self._stdin.fileno()) # pylint: disable=undefined-variable
            finally:
                return old_settings

        def _restore_tty(self, old_settings):
            try:
                fd = self._stdin.fileno()
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            except Exception:
                pass

        def _sequence_from_input_data(self, chars, single_char=False):
            sequence = []
            while chars:
                if single_char is True and sequence:
                    return sequence

                c1 = chars[0]
                chars = chars[1:]
                if ord(c1) != 0x1B:
                    sequence.append(c1)
                    continue

                if not chars:
                    sequence.append(c1)
                    break

                c2 = chars[0]
                chars = chars[1:]
                if c2:
                    if ord(c2) not in [0x5B, 0x4f]:
                        sequence.append(c1 + c2)
                        continue
                else:
                    sequence.append(c1)
                    break

                if not chars:
                    break

                c3 = chars[0]
                chars = chars[1:]
                if c3:
                    if ord(c3) not in [0x31, 0x32, 0x33, 0x34, 0x35, 0x36]:
                        sequence.append(c1 + c2 + c3)
                        continue
                else:
                    sequence.append(c1 + c2)
                    break

                if not chars:
                    break

                c4 = chars[0]
                chars = chars[1:]
                if c4:
                    sequence.append(c1 + c2 + c3 + c4)
                    continue
                else:
                    sequence.append(c1 + c2 + c3)
                    break
            return sequence


        try:
            select.epoll # noqa
        except AttributeError:

            def _read_sequence(self, single_char=False):

                try:
                    old_settings = self._setup_tty()
                    fd = self._stdin.fileno()
                    fl = fcntl.fcntl(fd, fcntl.F_GETFL)
                    fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK) # pylint: disable=maybe-no-member

                    while True:

                        inputready, _, exceptready = select.select([fd], [], [], 1)

                        if fd in exceptready:
                            raise readkey.ReadKeyError("Exception in stdin FD")

                        if fd in inputready:
                            chars = self._stdin.read()
                            if chars:
                                return self._sequence_from_input_data(chars, single_char=single_char)
                        else:
                            continue

                        raise readkey.ReadKeyError("Select call returned without data")

                except Exception as e:
                    raise e
                finally:
                    fcntl.fcntl(fd, fcntl.F_SETFL, fl)
                    self._restore_tty(old_settings)

        else:

            def _read_sequence(self, single_char=False):

                try:
                    old_settings = self._setup_tty()
                    fd = self._stdin.fileno()
                    fl = fcntl.fcntl(fd, fcntl.F_GETFL)
                    fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK) # pylint: disable=maybe-no-member
                    epoll = select.epoll() # pylint: disable=maybe-no-member
                    epoll.register(fd, select.EPOLLIN) # pylint: disable=maybe-no-member

                    while True:
                        events = epoll.poll(1)
                        if (fd, select.EPOLLIN) in events: # pylint: disable=maybe-no-member
                            chars = self._stdin.read()
                            if not chars:
                                raise readkey.ReadKeyError("Epoll returned empty")

                            return self._sequence_from_input_data(chars, single_char=single_char)

                except Exception as e:
                    raise e
                finally:
                    epoll.unregister(fd)
                    epoll.close()
                    fcntl.fcntl(fd, fcntl.F_SETFL, fl)
                    self._restore_tty(old_settings)


        def readkey(self):
            try:
                return self._read_sequence(single_char=True)[0]
            except Exception as e:
                raise e


        def readkeys(self):
            try:
                return self._read_sequence()
            except Exception as e:
                raise e

    elif sys.platform in ("win32", "cygwin"):

        def readkey(self): # noqa
            try:
                if self._keyboard_interrupted:
                    self._keyboard_interrupted = False
                    raise KeyboardInterrupt

                ch = msvcrt.getch()
                a = ord(ch)
                if a == 0 or a == 224:
                    b = ord(msvcrt.getch())
                    x = a + (b * 256)
                    try:
                        return xlate_dict[x]
                    except KeyError:
                        pass
                    return x
                else:
                    if a in xlate_dict:
                        return xlate_dict[a]
                    return ch.decode()
            except Exception as e:
                raise e

        def readkeys(self):
            sequence = []
            try:
                while not msvcrt.kbhit():
                    time.sleep(.01)
                    if self._keyboard_interrupted:
                        self._keyboard_interrupted = False
                        raise KeyboardInterrupt
                while msvcrt.kbhit():
                    if self._keyboard_interrupted:
                        self._keyboard_interrupted = False
                        raise KeyboardInterrupt
                    sequence.append(self.readkey())
            except KeyboardInterrupt:
                sequence.append(key.CTRL_C)
            return sequence
