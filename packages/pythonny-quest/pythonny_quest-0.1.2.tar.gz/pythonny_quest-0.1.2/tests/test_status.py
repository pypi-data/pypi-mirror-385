import doctest
from pyquest import status


def test_status(m=status):
    results = doctest.testmod(m)
    assert results.failed == 0, f'doctest.testmod({m}) -> {results}'
