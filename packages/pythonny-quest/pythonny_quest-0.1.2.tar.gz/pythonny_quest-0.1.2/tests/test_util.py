import doctest
from pyquest import util


def test_util(m=util):
    results = doctest.testmod(m)
    assert results.failed == 0, f'doctest.testmod({m}) -> {results}'
