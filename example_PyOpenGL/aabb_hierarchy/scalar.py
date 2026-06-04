import math 

def clamp (value : float, min_value : float, max_value : float) -> float:
	''' Clamp to interval [min_value, max_value]. '''
	if value > max_value:
		value = max_value
	if value < min_value:
		value = min_value
	return value
