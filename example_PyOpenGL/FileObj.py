import math
import numpy as np
import locale
from   locale import atof

''' '''
class FileObj:
    # 
    def __init__(self):
        self.dtype = np.float64

    # update from self.indices, self.points
    def updateBBox (self):
        self.x = [ self.dtype(math.inf), -self.dtype(math.inf)]
        self.y = [ self.dtype(math.inf), -self.dtype(math.inf)]
        self.z = [ self.dtype(math.inf), -self.dtype(math.inf)]
        for idx in self.indices:
            coord = self.points[idx]
            self.x[0] = min(self.x[0], coord[0])
            self.x[1] = max(self.x[1], coord[0])
            if len(coord) >= 2:
                self.y[0] = min(self.y[0], coord[1])
                self.y[1] = max(self.y[1], coord[1])
            if len(coord) >= 3:
                self.z[0] = min(self.z[0], coord[2])
                self.z[1] = max(self.z[1], coord[2])

    #
    def read (self, filename : str) -> None:
        self.readWithType(filename, dtype=float)
    #
    def readWithType (self, filename : str, dtype : type) -> None:
        locale.setlocale(locale.LC_ALL, "en_US.utf8")
        self.dtype    = dtype
        self.points   = list()
        self.indices  = list()
        self.filename = filename
        with open(self.filename, 'r') as file:
            num_line = 0
            while file:
                line      = file.readline()
                num_line += 1
                #print(line)
                if not line: # line==None, so end-of-file
                    break
                #print(line)
                elements = line.split(sep=None)
                #print(elements)
                if len(elements) < 1 or elements[0] == "#": # skip empty line or comment line
                    continue 

                assert(len(elements) >= 1)
                if elements[0] == "v":
                    assert(2 <= len(elements) and len(elements) <= 4)
                    print(len(elements))
                    if len(elements) == 2: # 1d
                        x = atof(elements[1])
                        coord = (self.dtype(x))    
                    if len(elements) == 3: # 2d
                        #x = atof(elements[1])
                        #y = atof(elements[2])
                        x = self.dtype(elements[1])
                        y = self.dtype(elements[2])
                        coord = (self.dtype(x), self.dtype(y))   
                    if len(elements) == 4: # 3d
                        #x = atof(elements[1])
                        #y = atof(elements[2])
                        #z = atof(elements[3])
                        x = self.dtype(elements[1])
                        y = self.dtype(elements[2])
                        z = self.dtype(elements[3])
                        coord = (self.dtype(x), self.dtype(y), self.dtype(z))    
                    self.points.append(coord)
                    continue
                if elements[0] == "f":
                    if len(self.indices) > 0:
                        print("WARNING: skipped additional face in line", num_line)
                        self.indices.clear() # clear list with each tag 'f', so only last face persists
                    for i in range(1, len(elements)): 
                        # indices in OBJ are 1 based
                        self.indices.append(int(elements[i])-1)
                    continue
        print("read points", len(self.points), "polygon", len(self.indices))
        self.updateBBox()

    def writeObj(self, filename : str, points : list[tuple], indices : list[int]) -> None:
        # index remapping
        remap = dict()
        for id in indices:
            remap[id] = len(remap)

        with open(filename, 'w') as file:
            comment = "#" + str(len(points)) + " points," + str(len(indices)) + " indices\n"
            file.write(comment)   
            # point coordinates
            for id, p in enumerate(points):
                if id in remap.keys():
                    v_line = "v"
                    if len(p) == 1:
                        v_line += f" {p[0]}"
                    if len(p) == 2:
                        v_line += f" {p[0]} {p[1]}" 
                    if len(p) == 3:
                        v_line += f" {p[0]} {p[1]} {p[2]}"  
                    v_line += "\n"  
                    file.write(v_line)        
            # indices are 1 based
            ids = [ remap[idx] for idx in indices ]
            f_line = 'f' + ' '.join(str(id+1) for id in ids) + '\n'
            file.write(f_line)      

    # List of coords tuples of all points read 
    def getPointCoords (self) -> list[tuple]:
        return self.points
    
    # List of indices into PointCoords list
    def getPolygonIndices (self) -> list[int]:
        if len(self.indices) == 0: # if no indices, create list from point coords list
            for i in range(len(self.points)):
                self.indices.append(i) 
        assert(0 <= min(self.indices) and max(self.indices) < len(self.points))
        return self.indices
    
    # List of polygon coords tuples
    def getPolygon (self) -> list[tuple]:
        indices   = self.getPolygonIndices()
        polygon   = [ self.points[idx] for idx in indices ]
        return polygon