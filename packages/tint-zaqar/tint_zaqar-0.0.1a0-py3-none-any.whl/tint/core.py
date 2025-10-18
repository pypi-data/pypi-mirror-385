# ANSI escape codes
_RESET = "\033[0m"
_BOLD = "\033[1m"
_RED = "\033[31m"
_GREEN = "\033[32m"
_BLUE = "\033[34m"

def reset(text: str = "") -> str:
    """Reset all styles."""
    return _RESET + text

def bold(text: str) -> str:
    """Make text bold."""
    return _BOLD + text + _RESET

def red(text: str) -> str:
    """Color text red."""
    return _RED + text + _RESET

def green(text: str) -> str:
    """Color text green."""
    return _GREEN + text + _RESET

def blue(text: str) -> str:
    """Color text blue."""
    return _BLUE + text + _RESET
