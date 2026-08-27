# basiert auf Jupyter Notebook von Chantal Faustmann und Marlena Henn, 04.2026
# Literatur:
# U. Meyer, V. Weichert: Algorithm Engineering für moderne Hardware, Informatik Spektrum 36(2), 2013

import numpy as np
import time
import copy

def benchmark(func, matrix, repeats=5, copy_matrix=False):
	times = []
	for _ in range(repeats):
		data = copy.deepcopy(matrix) if copy_matrix else matrix
		start = time.perf_counter()
		func(data)
		end = time.perf_counter()
		times.append(end - start)
	return sum(times) / len(times)

# version using Python list
def transpose_list_naive(matrix):
	N = len(matrix)
	transpose = [[np.float64(0.0) for _ in range(N)] for _ in range(N)]
	for i in range(N):
		for j in range(N):
			transpose[j][i] = matrix[i][j]
	return transpose
# version using numpy.array
def transpose_numpy_naive(matrix):
	transpose = np.empty_like(matrix)
	for i in range(transpose.shape[0]):
		for j in range(transpose.shape[1]):
			transpose[j][i] = matrix[i][j]
	return transpose

# version using numpy.array; also off-diagonal block is handled recursively
def transpose_numpy_recursive(matrix, row=0, col=0, size=None):
	if size is None:
		size = matrix.shape[0]

	if size <= 16:
		if row == col:
			for i in range(size):
				for j in range(i + 1, size):
					matrix_ij = matrix[row + i, col + j]
					matrix[row + i, col + j] = matrix[row + j, col + i] 
					matrix[row + j, col + i] = matrix_ij
		else:
			for i in range(size):
				for j in range(size):
					matrix_ij = matrix[row + i, col + j] 
					matrix[row + i, col + j] = matrix[row + j, col + i] 
					matrix[row + j, col + i] = matrix_ij
		return matrix

	half = size // 2

	transpose_numpy_recursive(matrix, row, col, half)
	transpose_numpy_recursive(matrix, row + half, col + half, half)

	transpose_numpy_recursive(matrix, row, col + half, half)
	# cf this is not necessary, like 'for j in range(i + 1, size)':
	#transpose_numpy_recursive(matrix, row + half, col, half)
	return matrix

# version using numpy.array; inplace!
def transpose_numpy_inplace(matrix):
	#N = matrix.shape[0]
	for i in range(matrix.shape[0]):
		for j in range(i+1, matrix.shape[1]):
			matrix_ij   = matrix[i,j]
			matrix[i,j] = matrix[j,i]
			matrix[j,i] = matrix_ij
	return matrix


N_values = [100, 400, 1000, 2000, 4000]
for N in N_values:
	matrix_list = [[np.float64(j) for j in range(N)] for i in range(N)]
	matrix_np   = np.array(matrix_list, dtype=np.float64)

	# Benchmarks
	time_naive   = benchmark(transpose_list_naive, matrix_list)
	time_naive2  = benchmark(transpose_numpy_naive, matrix_np)
	time_rowwise = benchmark(transpose_numpy_inplace, matrix_np)
	time_recursive = benchmark(transpose_numpy_recursive, matrix_np)
	time_numpytranspose = benchmark(np.transpose, matrix_np)

	# Output results
	print("\n=== Performance Vergleich ===")
	print(f"Matrixgroesse: {N} x {N}")
	print(f"Row-wise (new Python list):    {time_naive:.6f} s")
	print(f"Row-wise (new NumPy arr):      {time_naive2:.6f} s")
	print(f"Row-wise (inplace NumPy arr):  {time_rowwise:.6f} s")
	print(f"Recursive (inplace NumPy arr): {time_recursive:.6f} s")
	print(f"Python numpy.transpose:        {time_numpytranspose:.6f} s")
