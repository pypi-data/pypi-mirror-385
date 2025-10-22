import aethermark


def test_greet():
    assert aethermark.greet("World") == "Hello, World from Aethermark!"


def test_greet_empty():
    assert aethermark.greet("") == "Hello,  from Aethermark!"


def test_greet_doc():
    doc = aethermark.greet.__doc__
    assert doc is not None
    assert "Greet someone by name." in doc
    assert "Args:" in doc
    assert "name (str): Name of the person." in doc
    assert "Returns:" in doc
    assert "str: Greeting string." in doc
