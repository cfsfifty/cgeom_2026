import math 
from   typing import Self

class AABB:
    def __init__(self):
        self.k   = 3
        self.extent = [ [math.inf for i in range(self.k)], [-math.inf for i in range(self.k)] ]

    def center (self) -> tuple[float]:
        center = [ 0.0 for i in range(self.k)]
        for i in range(self.k):
            center[i] = 0.5*(self.extent[0][i]+self.extent[1][i])
        return center
    
    def is_intersect (self, b : 'AABB') -> bool:
        for i in self.k:
            if (self.extent[1][i] < b.extent[0][i] or self.extent[0][i] > b.extent[1][i]):
                return False
        return True

    def is_inside (self, coord : list) -> bool:
        if self.k >= 1 and not(self.extent[0][0] <= coord[0] and coord[0] <= self.extent[1][0]):
            return False
        if self.k >= 2 and not(self.extent[0][1] <= coord[1] and coord[1] <= self.extent[1][1]):
            return False
        if self.k >= 3 and not(self.extent[0][2] <= coord[2] and coord[2] <= self.extent[1][2]):
            return False
        return True

    def add_coords (self, coords : list[tuple]) -> None:
        for c in coords:
            assert(len(c) <= self.k)
            for i in range(len(c)):
                self.extent[0][i] = min(self.extent[0][i], c[i])                    
                self.extent[1][i] = max(self.extent[1][i], c[i])   
    def add_box (self, b : 'AABB') -> None:
        assert(self.k == b.k)
        for i in range(len(self.k)):
            self.extent[0][i] = min(self.extent[0][i], b.extent[0][i])                    
            self.extent[1][i] = max(self.extent[1][i], b.extent[1][i])   
            
    def __str__ (self):
        return str(self.extent)

                            
