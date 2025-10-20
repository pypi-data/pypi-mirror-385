# ANSI escape codes
_RESET = "\033[0m"

# Styles
_BOLD = "\033[1m"
_DIM = "\033[2m"
_ITALIC = "\033[3m"
_UNDERLINE = "\033[4m"

# Colors
_BLACK = "\033[30m"
_RED = "\033[31m"
_GREEN = "\033[32m"
_YELLOW = "\033[33m"
_BLUE = "\033[34m"
_MAGENTA = "\033[35m"
_CYAN = "\033[36m"
_WHITE = "\033[37m"

# Style functions
def reset(text: str = "") -> str:
    return _RESET + text

def bold(text: str) -> str:
    return _BOLD + text + _RESET

def dim(text: str) -> str:
    return _DIM + text + _RESET

def italic(text: str) -> str:
    return _ITALIC + text + _RESET

def underline(text: str) -> str:
    return _UNDERLINE + text + _RESET

# Color functions
def black(text: str) -> str:
    return _BLACK + text + _RESET

def red(text: str) -> str:
    return _RED + text + _RESET

def green(text: str) -> str:
    return _GREEN + text + _RESET

def yellow(text: str) -> str:
    return _YELLOW + text + _RESET

def blue(text: str) -> str:
    return _BLUE + text + _RESET

def magenta(text: str) -> str:
    return _MAGENTA + text + _RESET

def cyan(text: str) -> str:
    return _CYAN + text + _RESET

def white(text: str) -> str:
    return _WHITE + text + _RESET
