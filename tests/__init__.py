from unittest import TestLoader

def test_all():
    return TestLoader().discover("tests", pattern="test_*.py")
