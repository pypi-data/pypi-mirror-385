"""Tint - add color and style to your terminal output."""

from .core import (
    reset,
    bold, dim, italic, underline,
    black, red, green, yellow,
    blue, magenta, cyan, white
)

__version__ = "0.0.2a"
__all__ = [
    "reset",
    "bold", "dim", "italic", "underline",
    "black", "red", "green", "yellow",
    "blue", "magenta", "cyan", "white"
]
