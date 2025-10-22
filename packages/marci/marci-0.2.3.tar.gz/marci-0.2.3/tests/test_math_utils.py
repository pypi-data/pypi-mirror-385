import numpy as np
from marci import antidiag_sums


def test_antidiag_sums_square():
    x = np.array(
        [
            [1, 2, 3],
            [4, 5, 6],
            [7, 8, 9],
        ]
    )
    # Antidiagonals: [1], [2,4], [3,5,7], [6,8], [9]
    res = antidiag_sums(x)
    assert res.tolist() == [1, 6, 15, 14, 9]


def test_antidiag_sums_rectangular():
    x = np.array(
        [
            [1, 2, 3, 4],
            [5, 6, 7, 8],
        ]
    )
    # Antidiagonals: [1], [2,5], [3,6], [4,7], [8]
    res = antidiag_sums(x)
    assert res.tolist() == [1, 7, 9, 11, 8]
