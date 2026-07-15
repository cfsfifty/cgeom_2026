# basiert auf Jupyter Notebook von Chantal Faustmann und Marlena Henn, 04.2026
# Literatur:
# U. Meyer, V. Weichert: Algorithm Engineering für moderne Hardware, Informatik Spektrum 36(2), 2013

import numpy as np
import time
import copy

def benchmark(func, matrix, repeats=5, in_place=False):
	times = []
	for _ in range(repeats):
		data = copy.deepcopy(matrix) if in_place else matrix
		start = time.perf_counter()
		func(data)
		end = time.perf_counter()
		times.append(end - start)
	return sum(times) / len(times)

# Cache-unfriendly code
def transpose_naiv(matrix):
	N = len(matrix)
	transpose = [[None] * N for _ in range(N)]
	for i in range(N):
		for j in range(N):
			transpose[j][i] = matrix[i][j]
	return transpose

# version using Python arrays
def transpose_recursive(matrix, row=0, col=0, size=None):
	if size is None:
		size = len(matrix)

	if size <= 16:
		for i in range(size):
			for j in range(i + 1, size):
				matrix[row + i][col + j], matrix[row + j][col + i] = (
					matrix[row + j][col + i],
					matrix[row + i][col + j],
				)
		return

	half = size // 2

	transpose_recursive(matrix, row, col, half)
	transpose_recursive(matrix, row + half, col + half, half)

	for i in range(half):
		for j in range(half):
			matrix[row + i][col + half + j], matrix[row + half + j][col + i] = (
				matrix[row + half + j][col + i],
				matrix[row + i][col + half + j],
			)


# cf version using numpy.array; also off-diagonal block is handled recursively
def transpose_recursive2(matrix, row=0, col=0, size=None):
	if size is None:
		size = matrix.shape[0]

	if size <= 16:
		if row == col:
			for i in range(size):
				for j in range(i + 1, size):
					matrix[row + i, col + j], matrix[row + j, col + i] = (
						matrix[row + j, col + i],
						matrix[row + i, col + j],
					)
		else:
			for i in range(size):
				for j in range(size):
					matrix[row + i, col + j], matrix[row + j, col + i] = (
						matrix[row + j, col + i],
						matrix[row + i, col + j],
					)
		return

	half = size // 2

	transpose_recursive2(matrix, row, col, half)
	transpose_recursive2(matrix, row + half, col + half, half)

	transpose_recursive2(matrix, row, col + half, half)
	# cf this is not necessary, like 'for j in range(i + 1, size)':
	#transpose_recursive2(matrix, row + half, col, half)



def transpose_rowwise(matrix):
	N = len(matrix)
	result = [[None] * N for _ in range(N)]
	for i in range(N):
		for j in range(N):
			result[j][i] = matrix[i][j]
	return result


def transpose_colwise(matrix):
	N = len(matrix)
	result = [[None] * N for _ in range(N)]
	for j in range(N):
		for i in range(N):
			result[j][i] = matrix[i][j]
	return result

# cf version using numpy.array; inplace!
def transpose_rowwise2(matrix):
	N = matrix.shape[0]
	for i in range(N):
		for j in range(i+1, N):
			matrix[i,j], matrix[j,i] = (matrix[j,i], matrix[i,j])
	return matrix


def transpose_colwise2(matrix):
	N = matrix.shape[0]
	for j in range(N):
		for i in range(j+1, N):
			matrix[i,j], matrix[j,i] = (matrix[j,i], matrix[i,j])
	return matrix

N_values = [100, 500, 1000, 2000, 5000]
for N in N_values:
	matrix_list = [[j for j in range(N)] for i in range(N)]
	matrix_np = np.array(matrix_list)

	# Benchmarks
	time_naiv = benchmark(transpose_naiv, matrix_list)
	time_rowwise = benchmark(transpose_rowwise2, matrix_np)
	time_colwise = benchmark(transpose_colwise2, matrix_np)
	time_recursive = benchmark(transpose_recursive2, matrix_np, in_place=True)
	time_numpy = benchmark(np.transpose, matrix_np)

	# Output results
	print("\n=== Performance Vergleich ===")
	print(f"Matrixgroesse: {N} x {N}")
	print(f"Python (Standard):  {time_naiv:.6f} s")
	print(f"Row-wise (inplace): {time_rowwise:.6f} s")
	print(f"Col-wise (inplace): {time_colwise:.6f} s")
	print(f"Rekursiv (inplace): {time_recursive:.6f} s")
	print(f"NumPy:              {time_numpy:.6f} s")
