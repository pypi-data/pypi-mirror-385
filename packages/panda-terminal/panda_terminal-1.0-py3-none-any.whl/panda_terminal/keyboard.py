import platform
from typing import TYPE_CHECKING

if platform.system() == "Windows" or (TYPE_CHECKING and sys.platform == "win32"):
    import msvcrt  # windows import
else:
    import termios, tty, sys  # unix imports


class _BaseKey:
    LF = "\x0a"
    CR = "\x0d"
    SPACE = "\x20"
    ESC = "\x1b"
    TAB = "\x09"

    # CTRL
    CTRL_A = "\x01"
    CTRL_B = "\x02"
    CTRL_C = "\x03"
    CTRL_D = "\x04"
    CTRL_E = "\x05"
    CTRL_F = "\x06"
    CTRL_G = "\x07"
    CTRL_H = "\x08"
    CTRL_I = TAB
    CTRL_J = LF
    CTRL_K = "\x0b"
    CTRL_L = "\x0c"
    CTRL_M = CR
    CTRL_N = "\x0e"
    CTRL_O = "\x0f"
    CTRL_P = "\x10"
    CTRL_Q = "\x11"
    CTRL_R = "\x12"
    CTRL_S = "\x13"
    CTRL_T = "\x14"
    CTRL_U = "\x15"
    CTRL_V = "\x16"
    CTRL_W = "\x17"
    CTRL_X = "\x18"
    CTRL_Y = "\x19"
    CTRL_Z = "\x1a"


class _UnixKey:
    BACKSPACE = "\x7f"

    # cursors
    UP = "\x1b\x5b\x41"
    DOWN = "\x1b\x5b\x42"
    LEFT = "\x1b\x5b\x44"
    RIGHT = "\x1b\x5b\x43"

    # navigation keys
    INSERT = "\x1b\x5b\x32\x7e"
    SUPR = "\x1b\x5b\x33\x7e"
    HOME = "\x1b\x5b\x48"
    END = "\x1b\x5b\x46"
    PAGE_UP = "\x1b\x5b\x35\x7e"
    PAGE_DOWN = "\x1b\x5b\x36\x7e"

    # function keys
    F1 = "\x1b\x4f\x50"
    F2 = "\x1b\x4f\x51"
    F3 = "\x1b\x4f\x52"
    F4 = "\x1b\x4f\x53"
    F5 = "\x1b\x5b\x31\x35\x7e"
    F6 = "\x1b\x5b\x31\x37\x7e"
    F7 = "\x1b\x5b\x31\x38\x7e"
    F8 = "\x1b\x5b\x31\x39\x7e"
    F9 = "\x1b\x5b\x32\x30\x7e"
    F10 = "\x1b\x5b\x32\x31\x7e"
    F11 = "\x1b\x5b\x32\x33\x7e"
    F12 = "\x1b\x5b\x32\x34\x7e"
    SHIFT_TAB = "\x1b\x5b\x5a"
    CTRL_ALT_SUPR = "\x1b\x5b\x33\x5e"
    ALT_A = "\x1b\x61"
    CTRL_ALT_A = "\x1b\x01"
    ENTER = "\x0a"
    DELETE = SUPR


class _WinKey:
    BACKSPACE = "\x08"

    # cursors
    UP = "\x00\x48"
    DOWN = "\x00\x50"
    LEFT = "\x00\x4b"
    RIGHT = "\x00\x4d"

    # navigation keys
    INSERT = "\x00\x52"
    SUPR = "\x00\x53"
    HOME = "\x00\x47"
    END = "\x00\x4f"
    PAGE_UP = "\x00\x49"
    PAGE_DOWN = "\x00\x51"

    # function keys
    F1 = "\x00\x3b"
    F2 = "\x00\x3c"
    F3 = "\x00\x3d"
    F4 = "\x00\x3e"
    F5 = "\x00\x3f"
    F6 = "\x00\x40"
    F7 = "\x00\x41"
    F8 = "\x00\x42"
    F9 = "\x00\x43"
    F10 = "\x00\x44"
    F11 = "\x00\x85"  # only in second source
    F12 = "\x00\x86"  # only in second source

    # other
    ESC_2 = "\x00\x01"
    ENTER_2 = "\x00\x1c"

    # aliases
    ENTER = "\x0d"
    DELETE = SUPR


if platform.system() == "Windows":
    bases = (_BaseKey, _WinKey)
else:
    bases = (_BaseKey, _UnixKey)


class Key(*bases):
    pass


if platform.system() == "Windows" or (TYPE_CHECKING and sys.platform == "win32"):

    def _read_char_win() -> str:
        return msvcrt.getwch()

    def _read_key_win():
        ch = _read_char_win()

        if ch == Key.CTRL_C:
            raise KeyboardInterrupt

        if ch in "\x00\xe0":
            ch = "\x00" + _read_char_win()

        if "\ud800" <= ch <= "\udfff":
            ch += _read_char_win()
            ch = ch.encode("utf-16", errors="surrogatepass").decode("utf-16")

        return ch

else:

    def _read_char_unix() -> str:
        fd = sys.stdin.fileno()
        old = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old)
        return ch

    def _read_key_unix() -> str:
        c1 = _read_char_unix()

        if c1 in Key.CTRL_Z:
            raise KeyboardInterrupt

        if c1 != "\x1b":
            return c1

        c2 = _read_char_unix()
        if c2 not in "\x4f\x5b":
            return c1 + c2

        c3 = _read_char_unix()
        if c3 not in "\x31\x32\x33\x35\x36":
            return c1 + c2 + c3

        c4 = _read_char_unix()
        if c4 not in "\x30\x31\x33\x34\x35\x37\x38\x39":
            return c1 + c2 + c3 + c4

        c5 = _read_char_unix()
        return c1 + c2 + c3 + c4 + c5


def read_char() -> str:
    if platform.system() == "Windows" or (TYPE_CHECKING and sys.platform == "win32"):
        return _read_char_win()
    else:
        return _read_char_unix()


def read_key() -> str:
    if platform.system() == "Windows" or (TYPE_CHECKING and sys.platform == "win32"):
        return _read_key_win()
    else:
        return _read_key_unix()
