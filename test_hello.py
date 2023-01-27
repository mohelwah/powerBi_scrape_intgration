from hello import add


def test_add():
    """This is a test for the add function"""
    assert add(1, 2) == 3
    assert add(2, 2) == 4
    assert add(2, 3) == 5
