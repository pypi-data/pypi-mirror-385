from tint import red, bold, reset

def test_red():
    assert tint.red("hello") == "\033[31mhello\033[0m"

def test_bold():
    assert tint.bold("world") == "\033[1mword\033[0m"

def test_reset():
    assert tint.reset() == "\033[0m"
    assert tint.reset("x") == "\033[0mx"
