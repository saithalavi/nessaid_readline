# Copyright 2021 by Saithalavi M, saithalavi@gmail.com
# All rights reserved.
# This file is part of the Nessaid readline Framework, nessaid_readline python package
# and is released under the "MIT License Agreement". Please see the LICENSE
# file included as part of this package.
#

import sys
import time

import nessaid_readline.key as key


class PlatformNotSupported(Exception):
    pass


class ReadKeyError(Exception):
    pass


if sys.platform.startswith("linux") or sys.platform == "darwin":

    import os
    import tty # noqa
    import select # noqa
    import termios # pylint: disable=import-error
    import fcntl # pylint: disable=import-error


    def _setup_tty(stdin):
        old_settings = None
        try:
            fd = stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            tty.setraw(stdin.fileno())
        finally:
            return old_settings

    def _restore_tty(stdin, old_settings):
        try:
            fd = stdin.fileno()
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        except Exception:
            pass

    def _sequence_from_input_data(chars, single_char=False):
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

        def _read_sequence(stdin, single_char=False):

            try:
                old_settings = _setup_tty(stdin)
                fd = stdin.fileno()
                fl = fcntl.fcntl(fd, fcntl.F_GETFL)
                fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK) # pylint: disable=maybe-no-member

                inputready, _, exceptready = select.select([fd], [], [])

                if fd in exceptready:
                    raise ReadKeyError("Exception in stdin FD")

                if fd in inputready:
                    chars = stdin.read()
                    if chars:
                        return _sequence_from_input_data(chars, single_char=single_char)

                raise ReadKeyError("Select call returned without data")

            except Exception as e:
                raise e
            finally:
                fcntl.fcntl(fd, fcntl.F_SETFL, fl)
                _restore_tty(stdin, old_settings)

    else:

        def _read_sequence(stdin, single_char=False):

            try:
                old_settings = _setup_tty(stdin)
                fd = stdin.fileno()
                fl = fcntl.fcntl(fd, fcntl.F_GETFL)
                fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK) # pylint: disable=maybe-no-member
                epoll = select.epoll() # pylint: disable=maybe-no-member
                epoll.register(fd, select.EPOLLIN) # pylint: disable=maybe-no-member

                while True:
                    events = epoll.poll(10)
                    if (fd, select.EPOLLIN) in events: # pylint: disable=maybe-no-member
                        chars = stdin.read()
                        if not chars:
                            raise ReadKeyError("Epoll returned empty")

                        return _sequence_from_input_data(chars, single_char=single_char)

            except Exception as e:
                raise e
            finally:
                epoll.unregister(fd)
                epoll.close()
                fcntl.fcntl(fd, fcntl.F_SETFL, fl)
                _restore_tty(stdin, old_settings)


    def readkey(stdin=None):
        if not stdin:
            stdin = sys.stdin
        try:
            return _read_sequence(stdin, single_char=True)[0]
        except Exception as e:
            raise e


    def readkeys(stdin=None):
        if not stdin:
            stdin = sys.stdin
        try:
            return _read_sequence(stdin)
        except Exception as e:
            raise e

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


    def readkey(stdin=None): # noqa
        try:
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


    def readkeys(stdin=None):
        sequence = []
        while not msvcrt.kbhit():
            time.sleep(.001)
        while msvcrt.kbhit():
            sequence.append(readkey(stdin=stdin))
        return sequence

else:
    raise PlatformNotSupported(sys.platform)
