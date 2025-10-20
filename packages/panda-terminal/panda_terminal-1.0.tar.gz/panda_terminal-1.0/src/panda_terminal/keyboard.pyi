# key.pyi

__all__ = ["Key", "read_key", "read_char"]

from typing import Optional

class Key:
    """
    Cross-platform key constants.

    Platform-specific keys are marked in comments.
    """

    # Base keys (all platforms)
    LF: str
    CR: str
    SPACE: str
    ESC: str
    TAB: str

    CTRL_A: str
    CTRL_B: str
    CTRL_C: str
    CTRL_D: str
    CTRL_E: str
    CTRL_F: str
    CTRL_G: str
    CTRL_H: str
    CTRL_I: str
    CTRL_J: str
    CTRL_K: str
    CTRL_L: str
    CTRL_M: str
    CTRL_N: str
    CTRL_O: str
    CTRL_P: str
    CTRL_Q: str
    CTRL_R: str
    CTRL_S: str
    CTRL_T: str
    CTRL_U: str
    CTRL_V: str
    CTRL_W: str
    CTRL_X: str
    CTRL_Y: str
    CTRL_Z: str

    # Cursor / navigation keys
    BACKSPACE: str  # Windows: "\x08", Unix: "\x7f"
    UP: str
    DOWN: str
    LEFT: str
    RIGHT: str
    INSERT: Optional[str]  # Windows/Unix only
    SUPR: Optional[str]
    HOME: Optional[str]
    END: Optional[str]
    PAGE_UP: Optional[str]
    PAGE_DOWN: Optional[str]

    # Function keys (F1–F12)
    F1: Optional[str]
    F2: Optional[str]
    F3: Optional[str]
    F4: Optional[str]
    F5: Optional[str]
    F6: Optional[str]
    F7: Optional[str]
    F8: Optional[str]
    F9: Optional[str]
    F10: Optional[str]
    F11: Optional[str]
    F12: Optional[str]

    # Other keys
    SHIFT_TAB: Optional[str]  # Unix only
    CTRL_ALT_SUPR: Optional[str]  # Unix only
    ALT_A: Optional[str]  # Unix only
    CTRL_ALT_A: Optional[str]  # Unix only
    ENTER: str
    DELETE: str
    ESC_2: Optional[str]  # Windows only
    ENTER_2: Optional[str]  # Windows only

def _read_char_win() -> str: ...
def _read_key_win() -> str: ...
def _read_char_unix() -> str: ...
def _read_key_unix() -> str: ...
def read_char() -> str: ...
def read_key() -> str: ...
