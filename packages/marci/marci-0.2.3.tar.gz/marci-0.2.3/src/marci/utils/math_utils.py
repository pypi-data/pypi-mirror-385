import numpy as np


def antidiag_sums(x: np.ndarray) -> np.ndarray:
	"""
	Compute sums of antidiagonals (i+j constant) of a 2D numpy array.

	Parameters
	----------
	x : np.ndarray
		2D array (matrix).

	Returns
	-------
	np.ndarray
		1D array of sums, length = n_rows + n_cols - 1
	"""
	if x.ndim != 2:
		raise ValueError("Input must be a 2D matrix")

	n, m = x.shape
	i, j = np.indices((n, m))
	keys = (i + j).ravel()
	return np.bincount(keys, weights=x.ravel())
