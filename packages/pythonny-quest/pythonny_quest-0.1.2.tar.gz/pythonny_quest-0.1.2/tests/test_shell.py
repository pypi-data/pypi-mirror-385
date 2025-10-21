import doctest
from pyquest import shell


def test_shell(m=shell):
    results = doctest.testmod(m)
    assert results.failed == 0, f'doctest.testmod({m}) -> {results}'
