from aifund import say_hello


def test_say_hello():
    assert say_hello("Alice") == "Hello, Alice! Welcome to aifund."
