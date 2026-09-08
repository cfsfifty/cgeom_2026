# basiert auf Jupyter Notebook von Chantal Faustmann und Marlena Henn, 04.2026
# Literatur:
# U. Meyer, V. Weichert: Algorithm Engineering für moderne Hardware, Informatik Spektrum 36(2), 2013

import numpy as np
import time
import copy
from numba import njit
import matplotlib.pyplot as plt 

def benchmark(func, matrix, repeats=5, copy_matrix=False):
	times = []
	for _ in range(repeats):
		data  = copy.deepcopy(matrix) if copy_matrix else matrix
		start = time.perf_counter()
		func(data)
		end = time.perf_counter()
		times.append(end - start)
	return sum(times) / len(times)

# version using numpy.array; also off-diagonal block is handled recursively
@njit
def transpose_numpy_recursive(matrix : np.ndarray, row=0, col=0, size=None) -> np.ndarray:
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

# version using numpy.array
@njit
def transpose_numpy_naive(matrix : np.ndarray) -> np.ndarray:
	transpose = np.zeros(matrix.shape, dtype=np.float64)
	for i in range(transpose.shape[0]):
		for j in range(transpose.shape[1]):
			transpose[j][i] = matrix[i][j]
	return transpose

# version using numpy.array; inplace!
@njit
def transpose_numpy_inplace(matrix : np.ndarray) -> np.ndarray:
	#N = matrix.shape[0]
	for i in range(matrix.shape[0]):
		for j in range(i+1, matrix.shape[1]):
			matrix_ij   = matrix[i,j]
			matrix[i,j] = matrix[j,i]
			matrix[j,i] = matrix_ij
	return matrix

N_values = [250, 500, 1000, 2000, 4000]
methods = [ list() for _ in range(4) ]  # 4 empty lists for each method
for N in N_values:
	matrix_list = [[np.float64(j) for j in range(N)] for i in range(N)]
	matrix_np = np.array(matrix_list, dtype=np.float64)

	# Benchmarks
	time_naive   = benchmark(transpose_numpy_naive, matrix_np)
	methods[0].append(time_naive)
	time_rowwise = benchmark(transpose_numpy_inplace, matrix_np)
	methods[1].append(time_rowwise)
	time_recursive = benchmark(transpose_numpy_recursive, matrix_np)
	methods[2].append(time_recursive)
	time_numpytranspose = benchmark(np.transpose, matrix_np)
	methods[3].append(time_numpytranspose)

	# Output results
	print("\n=== Performance Vergleich ===")
	print(f"Matrixgroesse: {N} x {N}")
	print(f"Row-wise (new NumPy arr):      {time_naive:.6f} s")
	print(f"Row-wise (inplace NumPy arr):  {time_rowwise:.6f} s")
	print(f"Recursive (inplace NumPy arr): {time_recursive:.6f} s")
	print(f"Python numpy.transpose:        {time_numpytranspose:.6f} s")

# plot results
sizes = np.array(N_values) 
plt.plot(sizes, methods[0], 'go-', label='Row-wise (new NumPy arr)')
plt.plot(sizes, methods[1], 'bo-', label='Row-wise (inplace NumPy arr)')
plt.plot(sizes, methods[2], 'ro-', label='Recursive (inplace NumPy arr)')
plt.plot(sizes, methods[3], 'co-', label='Python numpy.transpose')
plt.xlabel('Matrix Size')
plt.ylabel('Time (s)')
plt.title('Performance Comparison of Transpose Operations (Numba)')
plt.legend()
plt.grid(True)
plt.show() 
