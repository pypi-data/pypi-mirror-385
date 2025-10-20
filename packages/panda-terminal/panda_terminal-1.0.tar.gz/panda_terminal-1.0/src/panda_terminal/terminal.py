from __future__ import annotations
import sys
import os
import ctypes
from panda_math import ivec2


class Cursor:
    def __init__(self, term: Terminal):
        self._handle = ctypes.windll.kernel32.GetStdHandle(-11)  # STD_OUTPUT_HANDLE
        self._pos = self._get_pos()
        self._term = term

    def _get_pos(self):
        class COORD(ctypes.Structure):
            _fields_ = [("X", ctypes.c_short), ("Y", ctypes.c_short)]

        class SMALL_RECT(ctypes.Structure):
            _fields_ = [
                ("Left", ctypes.c_short),
                ("Top", ctypes.c_short),
                ("Right", ctypes.c_short),
                ("Bottom", ctypes.c_short),
            ]

        class CSBI(ctypes.Structure):
            _fields_ = [
                ("dwSize", COORD),
                ("dwCursorPosition", COORD),
                ("wAttributes", ctypes.c_ushort),
                ("srWindow", SMALL_RECT),
                ("dwMaximumWindowSize", COORD),
            ]

        csbi = CSBI()
        ctypes.windll.kernel32.GetConsoleScreenBufferInfo(
            self._handle, ctypes.byref(csbi)
        )
        return ivec2(csbi.dwCursorPosition.X, csbi.dwCursorPosition.Y)

    @property
    def pos(self):
        return self._get_pos()

    def move(self, value):
        self._pos = ivec2(value)
        self._pos.x = max(self._pos.x, 0)
        self._pos.y = max(self._pos.y, 0)
        terminal_size = ivec2(self._term.size)
        self._pos.x = min(self._pos.x, terminal_size.x)
        self._pos.y = min(self._pos.y, terminal_size.y)

        class COORD(ctypes.Structure):
            _fields_ = [("X", ctypes.c_short), ("Y", ctypes.c_short)]

        ctypes.windll.kernel32.SetConsoleCursorPosition(
            self._handle, COORD(int(self._pos.x), int(self._pos.y))
        )

    def update_pos(self):
        self._term.ansi(f"[{self.pos.y};{self.pos.x}]")


class DoubleBuffer:
    """Double buffer implementation to reduce flicker"""

    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        # Use lists of strings for each row
        self.back_buffer = [[" " for _ in range(width)] for _ in range(height)]
        self.front_buffer = [[" " for _ in range(width)] for _ in range(height)]

    def clear(self):
        """Clear the back buffer"""
        self.back_buffer = [
            [" " for _ in range(self.width)] for _ in range(self.height)
        ]
        # Clear front buffer too so all spaces are considered changes and get drawn
        self.front_buffer = [
            ["X" for _ in range(self.width)] for _ in range(self.height)
        ]  # Use different char to force redraw

    def write(self, x: int, y: int, text: str):
        """Write text to the back buffer at position (x, y)"""
        if not (0 <= y < self.height):
            return

        x = max(0, x)
        if x >= self.width:
            return

        # For colored text, we need to handle ANSI codes specially
        # This is a simplified version - just write character by character
        for i, char in enumerate(text):
            if x + i < self.width:
                self.back_buffer[y][x + i] = char

    def set_char(self, x: int, y: int, char: str):
        """Set a single character (or colored string) at position (x, y)"""
        if 0 <= x < self.width and 0 <= y < self.height:
            self.back_buffer[y][x] = char  # Store the whole string, not just one char

    def swap(self) -> str:
        commands = []
        for y in range(self.height):
            x = 0
            while x < self.width:
                # Skip unchanged
                while (
                    x < self.width and self.back_buffer[y][x] == self.front_buffer[y][x]
                ):
                    x += 1
                if x >= self.width:
                    break

                start_x = x
                changed_chars = []
                while (
                    x < self.width and self.back_buffer[y][x] != self.front_buffer[y][x]
                ):
                    changed_chars.append(self.back_buffer[y][x])
                    self.front_buffer[y][x] = self.back_buffer[y][x]
                    x += 1

                text = "".join(changed_chars)
                commands.append(f"\033[{y + 1};{start_x + 1}H{text}")

        return "".join(commands)


class Terminal:
    def __init__(self, seperate: bool, double_buffer: bool = True) -> None:
        self._show_cursor: bool = True
        self.seperate = seperate
        self._cursor = Cursor(self)
        self._double_buffer = double_buffer
        self._buffer = None
        self._cached_size = None

        if double_buffer:
            size = self.size
            self._cached_size = size
            self._buffer = DoubleBuffer(*size)

    def __enter__(self):
        if self.seperate:
            self.ansi("[?1049h")  # new win
        self.clear()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.ansi("[?25h")  # show cursor
        self.ansi("[?1049l")  # original window

    def ansi(self, ansi: str):
        sys.stdout.write(f"\033{ansi}")
        sys.stdout.flush()

    def clear(self):
        if self._double_buffer and self._buffer:
            self._buffer.clear()
        else:
            os.system("cls" if os.name == "nt" else "clear")

    @property
    def size(self) -> ivec2:
        return ivec2(os.get_terminal_size())

    @property
    def show_cursor(self) -> bool:
        return self._show_cursor

    @show_cursor.setter
    def show_cursor(self, value: bool):
        self._show_cursor = value
        if value == True:
            self.ansi("[?25h")
        else:
            self.ansi("[?25l")

    @property
    def cursor_pos(self) -> ivec2:
        return self._cursor.pos

    def move_cursor(self, position: ivec2):
        self._cursor.move(position)

    def _check_and_resize(self):
        """Check if terminal was resized and recreate buffer if needed"""
        if self._double_buffer and self._cached_size:
            current_size = self.size
            if (
                self._cached_size.x != current_size.x
                or self._cached_size.y != current_size.y
            ):
                self._cached_size = current_size
                self._buffer = DoubleBuffer(current_size.x, current_size.y)

    def write(self, x: int, y: int, text: str):
        """Write text at position (x, y). Uses double buffer if enabled."""
        if self._double_buffer and self._buffer:
            self._buffer.write(x, y, text)
        else:
            # Fallback to direct writing
            self.move_cursor(ivec2(x, y))
            sys.stdout.write(text)
            sys.stdout.flush()

    def set_char(self, x: int, y: int, char: str):
        """Set a single character at position (x, y). Uses double buffer if enabled."""
        if self._double_buffer and self._buffer:
            self._buffer.set_char(x, y, char)
        else:
            self.write(x, y, char)

    def render(self):
        """Render the back buffer to screen (only works with double buffering)"""
        if self._double_buffer and self._buffer:
            self._check_and_resize()
            commands = self._buffer.swap()
            if commands:
                sys.stdout.write(commands)
                sys.stdout.flush()

    def resize_buffer(self):
        """Resize the buffer if terminal size changed"""
        if self._double_buffer:
            size = self.size
            self._buffer = DoubleBuffer(size.x, size.y)
