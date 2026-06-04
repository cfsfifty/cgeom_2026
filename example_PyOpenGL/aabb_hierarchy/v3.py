import math 

def length (v) -> float:
	''' '''
	return math.sqrt(v[0]*v[0]+v[1]*v[1]+v[2]*v[2])

def min_inplace (a, b) -> None:
	''' Min of a and b components, stored to a. '''
	a[0] = min(a[0], b[0])
	a[1] = min(a[1], b[1])
	a[2] = min(a[2], b[2])
def max_inplace (a, b) -> None:
	''' Max of a and b components, stored to a. '''
	a[0] = max(a[0], b[0])
	a[1] = max(a[1], b[1])
	a[2] = max(a[2], b[2])
def add_inplace (a, b, s=1.0) -> None:
	''' Multiply-add to a. '''
	a[0] += s*b[0]
	a[1] += s*b[1]
	a[2] += s*b[2]
def scale_inplace (a, s=1.0) -> None:
	''' Scale components of a, stored to a. '''
	a[0] *= s
	a[1] *= s
	a[2] *= s

def rotate_y(dir : list[float], start, radian : float):
	''' Rotate start by radian around y, stored to dir. '''
	c = math.cos(radian)
	s = math.sin(radian)
	x = start[0]
	z = start[2]
	dir[0] =  c*x-s*z
	dir[2] =  s*x+c*z
def rotate_x(dir : list[float], start, radian : float):
	''' Rotate start by radian around x, stored to dir. '''
	c = math.cos(radian)
	s = math.sin(radian)
	y = start[1]
	z = start[2]
	dir[1] =  c*y-s*z
	dir[2] =  s*y+c*z
