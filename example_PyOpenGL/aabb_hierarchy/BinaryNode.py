import math 

class BinaryNode:
    def __init__(self, k :int, left : int, right : int, indices : list[int], points : list[tuple], faces : list[list]):
        self.left    = left
        self.right   = right
        self.k       = k 
        self.points  = points
        self.faces   = faces
        self.indices = indices
        self.color   = [ -1, -1, -1 ]
        self.left_node  = None
        self.right_node = None

    def __str__ (self):
        return "dim " + str(self.k) + ", (" + str(self.left) + "," + str(self.right) + "):" + ("0" if not self.left_node else "<") + ("0" if not self.right_node else ">")

