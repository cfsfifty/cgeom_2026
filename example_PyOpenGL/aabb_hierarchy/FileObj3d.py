import math
import numpy as np
import AABB
import locale
from   locale import atof
import re

class FileObj3d:
    ''' '''
    def __init__(self):
        self.dtype = float
        self.bbox  = AABB.AABB()

    def updateBBox (self):
        ''' Update from self.indices, self.points. '''
        coords = list()
        for face in self.indices:
            for idx in face:
                coords.append(self.points[idx])
        self.bbox.add_coords(coords)


    def read (self, filename : str) -> None:
        ''' '''
        self.readWithDType(filename, dtype=self.dtype)
    def readWithDType (self, filename : str, dtype : type) -> None:
        ''' '''
        locale.setlocale(locale.LC_ALL, "en_US.utf8")
        self.dtype    = dtype
        self.points   = list()
        self.indices  = list()
        self.filename = filename
        self.box      = AABB.AABB()
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
                if len(elements) < 1: # skip empty line
                    continue 

                assert(len(elements) >= 1)
                if elements[0] == "v":
                    #assert(2 <= len(elements) and len(elements) <= 4)
                    #print(len(elements))
                    coord = ( 0.0, 0.0, 0.0 )
                    if len(elements) == 2: # 1d
                        x = atof(elements[1])
                        coord = self.dtype(x)    
                    if len(elements) == 3: # 2d
                        x = atof(elements[1])
                        y = atof(elements[2])
                        #x = float(elements[1])
                        #y = float(elements[2])
                        coord = (self.dtype(x), self.dtype(y))   
                    if len(elements) >= 4: # 3d
                        x = atof(elements[1])
                        y = atof(elements[2])
                        z = atof(elements[3])
                        coord = (self.dtype(x), self.dtype(y), self.dtype(z))    
                    #print(coord) 
                    self.points.append(coord)
                    continue
                if elements[0] == "f":
                    self.indices.append(list())
                    for i in range(1, len(elements)): 
                        # indices in OBJ are 1 based
                        match = re.search(r'(\d+)', elements[i])
                        if match:
                            idx = int(match.group(0))-1
                            self.indices[-1].append(idx)
                    continue
        print("read points", len(self.points), "faces", len(self.indices))
        self.updateBBox()

    def writeObj(self, filename : str, points : list[tuple], indices : list[list[int]]) -> None:
        ''' '''
        # index remapping
        #remap = dict()
        #for id in indices:
        #    remap[id] = len(remap)

        with open(filename, 'w') as file:
            comment = "#" + str(len(points)) + " points," + str(len(indices)) + " faces\n"
            file.write(comment)   
            # point coordinates
            for id, p in enumerate(points):
                #if id in remap.keys():
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
            #ids = [ remap[idx] for idx in indices ]
            for face in indices:
                f_line = 'f ' + ' '.join(str(id+1) for id in face) + '\n'
                file.write(f_line)      

    def getPointCoords (self) -> list[tuple]:
        ''' List of coords tuples of all points read. ''' 
        return self.points
    def getIndices (self) -> list[list]:
        ''' List of index lists. ''' 
        return self.indices
    
    def getFaces (self) -> list[int]:
        ''' List of indices into PointCoords list. '''
        if len(self.indices) == 0:
            self.indices.append(list())
            firstFace = self.indices[0]
            if len(firstFace) == 0: # if no indices, create list from point coords list
                for i in range(len(self.points)):
                    firstFace.append(i) 
        return self.indices  
