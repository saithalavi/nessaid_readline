# Copyright 2021 by Saithalavi M, saithalavi@gmail.com
# All rights reserved.
# This file is part of the Nessaid readline Framework, nessaid_readline python package
# and is released under the "MIT License Agreement". Please see the LICENSE
# file included as part of this package.
#

import sys

import nessaid_readline.key as key


class PlatformNotSupported(Exception):
    pass


class ReadKeyError(Exception):
    pass


if sys.platform.startswith("linux") or sys.platform == "darwin":

    import os
    import tty # noqa
    import select # noqa
    import termios # noqa
    import fcntl # noqa


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

    try:
        select.epoll # noqa
    except AttributeError:

        def _read_sequence(stdin):
            try:
                old_settings = _setup_tty(stdin)
                fd = stdin.fileno()
                fl = fcntl.fcntl(fd, fcntl.F_GETFL)
                fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK) # noqa

                inputready, _, exceptready = select.select([fd], [], [])
                if fd in exceptready:
                    raise ReadKeyError("Exception in stdin FD")
                if fd in inputready:
                    c1 = stdin.read(1)
                    if ord(c1) != 0x1B:
                        return c1
                else:
                    raise ReadKeyError("Select call returned without data")

                c2 = stdin.read(1)
                if c2:
                    if ord(c2) not in [0x5B, 0x4f]:
                        return c1 + c2
                else:
                    return c1

                c3 = stdin.read(1)
                if c3:
                    if ord(c3) not in [0x31, 0x32, 0x33, 0x34, 0x35, 0x36]:
                        return c1 + c2 + c3
                else:
                    return c1 + c2

                c4 = stdin.read(1)
                if c4:
                    return c1 + c2 + c3 + c4
                else:
                    return c1 + c2 + c3
            except Exception as e:
                raise e
            finally:
                fcntl.fcntl(fd, fcntl.F_SETFL, fl)
                _restore_tty(stdin, old_settings)
    else:

        def _read_sequence(stdin):
            try:
                old_settings = _setup_tty(stdin)
                fd = stdin.fileno()
                fl = fcntl.fcntl(fd, fcntl.F_GETFL)
                fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK) # noqa
                epoll = select.epoll() # noqa
                epoll.register(fd, select.EPOLLIN) # noqa

                while True:
                    events = epoll.poll(10)
                    if (fd, select.EPOLLIN) in events: # noqa
                        c1 = stdin.read(1)
                        if c1:
                            if ord(c1) != 0x1B:
                                return c1
                            break
                        else:
                            raise ReadKeyError("Epoll returned empty")

                c2 = stdin.read(1)
                if c2:
                    if ord(c2) not in [0x5B, 0x4f]:
                        return c1 + c2
                else:
                    return c1

                c3 = stdin.read(1)
                if c3:
                    if ord(c3) not in [0x31, 0x32, 0x33, 0x34, 0x35, 0x36]:
                        return c1 + c2 + c3
                else:
                    return c1 + c2

                c4 = stdin.read(1)
                if c4:
                    return c1 + c2 + c3 + c4
                else:
                    return c1 + c2 + c3

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
                try:
                    return xlate_dict[a]
                except KeyError:
                    return ch.decode()
        except Exception as e:
            raise e
else:
    raise PlatformNotSupported(sys.platform)
