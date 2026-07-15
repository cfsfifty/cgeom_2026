# MonotoneDecomposition
# basiert auf Abgabe von Robin Fabian Pechta, 07.2026
#
# Rückwärtslink HalfEdge.face nur benutzt um Randkanten und Diagonalen zu unterscheiden!
# Ansonsten ist es aufwendig, Sie aktuell zu halten während des Aufbaus! 
#

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from   dataclasses import dataclass
from   typing import Optional

import glfw
# full imports not nice, here for OpenGL ..
from   OpenGL.GL import * # type: ignore

# OBJ einlesen
def parseObj(filepath):
    points = []
    faces  = []
    with open(filepath, 'r') as f:
        for line in f:
            parts = line.split()
            if not parts:
                continue
            if parts[0] == 'v':
                points.append((float(parts[1]), float(parts[2])))
            elif parts[0] == 'f':
                faces.append([int(x) - 1 for x in parts[1:]])
    if len(faces) == 0:
        faces.append(list(range(len(points))))
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    bbox = [min(xs), max(xs), min(ys), max(ys)]
    return points, faces, bbox

def signedArea(points, faceIdx):
    a = 0.0
    n = len(faceIdx)
    for j in range(n):
        x1, y1 = points[faceIdx[j]]
        x2, y2 = points[faceIdx[(j + 1) % n]]
        a += x1 * y2 - x2 * y1
    return 0.5 * a

# erzwingt CCW (Aufgabe garantiert CCW, aber sicher ist sicher)
def ensureCCW(points, faces):
    for i, fi in enumerate(faces):
        if signedArea(points, fi) < 0:
            faces[i] = fi[::-1]
    return faces

# HE-Datenstruktur
class Vertex:
    def __init__(self, x : float, y : float):
        self.x  : float = x
        self.y  : float = y
        self.he = None   # ein ausgehender HalfEdge
    def __str__(self):
        return "(" + str(self.x) + "," + str(self.y) + ")"
        
class HalfEdge:
    def __init__(self):
        self.origin = None
        self.twin   = None
        self.next   = None
        self.prev   = None
        # expensive to keep self.face up-to-date! 
        # just self.twin.face!=None on diagonals, self.twin.face!=None on border 
        self.face   = None 
        # associated SweepEdge
        self.sweep  = None 
    def __str__(self):
        return str(self.origin) + "*" + repr(self) + "#" + repr(self.prev) +"#" + repr(self.next)

class Face:
    def __init__(self, he : HalfEdge = None):
        self.he = he
    def getHE (self) -> list[HalfEdge]:
        ''' Get all half-edges starting in self.he. '''
        face_hes = list()
        # vertices
        he = self.he
        while not he is None:
            face_hes.append(he)
            he = he.next 
            if he == self.he: # back at start he
                break
        return face_hes

# HE aufbauen
def buildHE(points, faces) -> tuple[list[Vertex], list[HalfEdge], list[Face]]:
    coord_to_vertex   = {}
    obj_idx_to_vertex = {}

    vertices          = []
    for i, pt in enumerate(points):
        key = (pt[0], pt[1])
        if key not in coord_to_vertex:
            v = Vertex(pt[0], pt[1])
            coord_to_vertex[key] = v
            vertices.append(v)
        obj_idx_to_vertex[i] = coord_to_vertex[key]

    all_halfedges = []
    face_objects  = []
    edge_map      = {}
    # half-edge rings
    for face_indices in faces:
        f = Face()
        face_objects.append(f)
        n   = len(face_indices)

        hes = []
        # origin
        for j in range(n):
            he        = HalfEdge()
            he.face   = f
            he.origin = obj_idx_to_vertex[face_indices[j]]
            #he.origin.outgoing.append(he)
            assert(not he.origin is None)
            he.origin.he = he # type: ignore
            hes.append(he)
            all_halfedges.append(he)
        # next and prev
        for j in range(n):
            hes[j].next = hes[(j + 1) % n]
            hes[j].prev = hes[(j - 1) % n]
        f.he = hes[0]
        # build edge_map
        for j in range(n):
            v_from = hes[j].origin
            v_to   = hes[j].next.origin
            edge_map[(id(v_from), id(v_to))] = hes[j]

    # twins
    for he in all_halfedges:
        v_from   = he.origin
        v_to     = he.next.origin
        twin_key = (id(v_to), id(v_from))
        if twin_key in edge_map:
            he.twin = edge_map[twin_key]
        
    return vertices, all_halfedges, face_objects

# ---------- Geometrie-Helfer ----------
def below(a, b):
    return (a.y < b.y) or (a.y == b.y and a.x < b.x)

def cross(ax, ay, bx, by):
    return ax * by - ay * bx

def isConvexCCW (v1 : Vertex, v2 : Vertex, v : Vertex) -> bool:
    dx1 = v.x -v1.x
    dy1 = v.y -v1.y            
    dx2 = v2.x  -v1.x
    dy2 = v2.y  -v1.y            
    det = (dx1*dy2 -dy1*dx2)
    return det <= 0.0 # v is left

# ---------- 1. Klassifikation (Definition 3) ----------
START, END, REGULAR, SPLIT, MERGE, UNKNOWN = 'start', 'end', 'regular', 'split', 'merge', 'unknown'

def classify (vertices : list[HalfEdge]):
    counts = {START: 0, END: 0, REGULAR: 0, SPLIT: 0, MERGE: 0}
    for e in vertices:
        assert(not e.prev is None)
        assert(not e.next is None)
        assert(not e.sweep is None)
        p = e.prev.origin # type: ignore
        n = e.next.origin # type: ignore
        #v.pv, v.nv = v.he.prev, v.he.next
        assert(not p is None)
        assert(not n is None)
        assert(not e.origin is None)
        pBelow = below(p, e.origin)
        nBelow = below(n, e.origin)
        c = cross(e.origin.x - p.x, e.origin.y - p.y, n.x - e.origin.x, n.y - e.origin.y)
        convex = c > 0                      # Innenwinkel < pi (bei CCW)
        if pBelow and nBelow:               # beide Nachbarn unter v
            e.sweep.kind = START if convex else SPLIT
        elif (not pBelow) and (not nBelow): # beide Nachbarn über v
            e.sweep.kind = END   if convex else MERGE
        else:
            e.sweep.kind = REGULAR
        counts[e.sweep.kind] += 1
    return counts

# ---------- 2. Sweep: y-monotone Zerlegung (Algorithmus 1) ----------
class SweepEdge:
    ''' Wrapper for half-edge, containing self.kind, self.helper, self.helperIsMerge. '''
    def __init__(self, he : HalfEdge):
        self.he   : HalfEdge = he      # Quelle he.origin, Ziel he.next.origin
        self.kind : str = UNKNOWN
        self.helper : HalfEdge = he # helper vertex
        self.helperIsMerge  : bool = False # is helper vertex a merge vertex?

    def __str__ (self):
        return str(self.he) + "(" + str(self.kind) + "):" + str(self.helperIsMerge) 

def isInteriorRight(he : HalfEdge) -> bool:
    ''' Innenraum rechts von v? Also v auf der absteigenden (linken) Kette. '''
    assert(not he.prev is None and not he.next is None)
    return below(he.origin, he.prev.origin) and below(he.next.origin, he.origin)  

def makeMonotone(vertices : list[HalfEdge], face_objects : list[Face]):
    T       : list[SweepEdge] = list()                                          # aktive Kanten (linke Innenkanten)

    def leftEdge(ei : SweepEdge) -> SweepEdge:
        vi = ei.he.origin
        assert(not vi is None)

        last = T[0]
        for e in T:
            #x = e.xAtY(vi.y)
            v1 = e.he.origin
            assert(not v1 is None)
            assert(not e.he.next is None)
            v2 = e.he.next.origin
            assert(not v2 is None)

            rightSide = not isConvexCCW(v1, v2, vi)
            if rightSide:
                return last
            last = e
        assert(last == T[-1])
        return last

    def insertSweepState (T : list[SweepEdge], se : SweepEdge):
        v = se.he.origin
        assert(not v is None) 
        #x1 = min(he.origin.x, he.next.origin.x)
        #x2 = max(he.origin.x, he.next.origin.x)
        for i, e in enumerate(T):
            #ex1 = min(e.he.origin.x, e.he.next.origin.x)
            #ex2 = max(e.he.origin.x, e.he.next.origin.x)            
            v1 = e.he.origin
            assert(not v1 is None)
            assert(not e.he.next is None)
            v2 = e.he.next.origin
            assert(not v2 is None)
            # classifying one point se.he.origin of se.he is enough, as no intersections!
            rightSide = not isConvexCCW(v1, v2, v)
            if rightSide: # insert before e
                T.insert(i, se)
                return
        T.append(se)
    
    keyFunction = lambda he: (he.origin.y, he.origin.x)
    Q = sorted(vertices, key=keyFunction, reverse=True)   # oben -> unten
    #assert(not he.sweep is None for he in vertices)

    for he in Q:
        # get SweepEdge for he
        ei    = he.sweep
        eprev = he.prev.sweep # type: ignore 
        print(ei, eprev)
        assert(not ei is None)
        assert(not eprev is None)
        k     = ei.kind
        print("kind " + k + ": " + str(ei) + " " + str(eprev))
        #print(T)
        #input("next round")
        
        if k == START:
            ei.helper, ei.helperIsMerge = ei.he, False
            insertSweepState(T, ei)

        elif k == END:
            if eprev.helperIsMerge:
                insertDiagonal (ei.he, eprev.helper, face_objects)
            if eprev in T: # CF do binary search, but len(T) is small
                T.remove(eprev)

        elif k == SPLIT:
            ej = leftEdge(ei)
            h1 = insertDiagonal (ei.he, ej.helper, face_objects)
            # CF ei.he, False 
            ej.helper, ej.helperIsMerge = h1, False # new helper is new h1

            ei.helper, ei.helperIsMerge = ei.he, False # beginning helper for ei
            insertSweepState(T, ei)

        elif k == MERGE:
            if eprev.helperIsMerge:
                h1 = insertDiagonal (ei.he, eprev.helper, face_objects)
            if eprev in T: # CF do binary search, but len(T) is small
                T.remove(eprev)
            ej = leftEdge(ei)
            if ej.helperIsMerge:
                h1 = insertDiagonal (ei.he, ej.helper, face_objects)
                # CF ei.he, False 
                ej.helper, ej.helperIsMerge = h1, True
            else:
                ej.helper, ej.helperIsMerge = ei.he, True

        else:  # REGULAR
            if isInteriorRight(ei.he): # left side
                if eprev.helperIsMerge:
                    h1 = insertDiagonal (ei.he, eprev.helper, face_objects)
                if eprev in T: # CF do binary search, but len(T) is small
                    T.remove(eprev)
                ei.helper, ei.helperIsMerge = ei.he, False
                insertSweepState(T, ei)
            else: # right side
                ej = leftEdge(ei)
                if ej.helperIsMerge:
                    h1 = insertDiagonal (ei.he, ej.helper, face_objects)
                    # CF ei.he
                    ej.helper, ej.helperIsMerge = h1, False
                else:
                    ej.helper, ej.helperIsMerge = ei.he, False

    # find all faces, start with original face
    assert(len(face_objects) == 1)
    i = 0
    while i < len(face_objects):
        face = face_objects[i]
        # iterate face
        he = face.he
        while True:
            he = he.next
            if not he.twin is None and he.face is None: # is diagonal
                he.face = face
                # create new face on twin
                te = he.twin
                # insert neighbor face into face_objects 
                te.face = Face()
                te.face.he = te
                face_objects.append(te.face)
            if he == face.he:
                i += 1
                break
    # set all HalfEdge.face links correctly
    for face in face_objects:
        he = face.he
        while True:
            he = he.next
            he.face = face
            if he == face.he:
                break
    return face_objects


# ---------- 3. Diagonale als HE-Paar in die DCEL einspleißen ----------
def insertDiagonal (hv1 : Optional[HalfEdge], hv2 : Optional[HalfEdge], face_objects : list[Face]) -> HalfEdge:
    assert(not hv1 is None)
    assert(not hv2 is None)
    h1, h2 = HalfEdge(), HalfEdge()
    h1.origin, h2.origin = hv1.origin, hv2.origin
    h1.twin, h2.twin     = h2, h1
    assert(not hv1.sweep is None)
    assert(not hv2.sweep is None)
    h1.sweep = SweepEdge(h1)
    h2.sweep = SweepEdge(h2)
    #h1.sweep.kind = hv1.sweep.kind
    #h2.sweep.kind = hv2.sweep.kind
    # new linking
    hv2.prev.next, h2.prev = h2, hv2.prev # type: ignore
    h1.next, hv2.prev      = hv2, h1
    h1.prev, hv1.prev.next = hv1.prev, h1 # type: ignore
    h2.next, hv1.prev      = hv1, h2 

    # faces later
    #assert (hv1.face == hv2.face)
    return h1

# ---------- OBJ schreiben ----------
def writeObj(path, vertices, faces):
    idx = {id(v): i + 1 for i, v in enumerate(vertices)}
    with open(path, 'w') as f:
        f.write("# y-monotone Zerlegung: %d Vertices, %d Faces\n" % (len(vertices), len(faces)))
        for v in vertices:
            f.write("v %f %f\n" % (v.x, v.y))
        for fc in faces:
            seq = []
            he = fc.he
            start = he
            while True:
                seq.append(idx[id(he.origin)])
                he = he.next
                if he is start:
                    break
            f.write("f " + " ".join(str(i) for i in seq) + "\n")


# ---------- Zeichnen (Faces eingefärbt -> monotone Stücke sichtbar) ----------
PALETTE = [(0.25, 0.8, 1.0), (1.0, 0.55, 0.25), (0.55, 1.0, 0.45),
           (0.95, 0.45, 0.9), (1.0, 0.9, 0.35), (0.45, 0.7, 1.0), (1.0, 0.6, 0.6)]

def drawFaces(faces):
    for k, fc in enumerate(faces):
        r, g, b = PALETTE[k % len(PALETTE)]
        glColor3f(r, g, b)
        glBegin(GL_LINE_LOOP)
        he = fc.he
        start = he
        while True:
            glVertex2f(he.origin.x, he.origin.y)
            he = he.next
            if he is start:
                break
        glEnd()


def run(filename):
    #filepath = os.path.join(os.path.dirname(__file__), filename)
    filepath = filename
    points, faces, bbox = parseObj(filepath)
    faces = ensureCCW(points, faces)

    # half-edge structure
    vertices, halfedges, face_objects = buildHE(points, faces)
    # first face only, iterate for all faces ..
    face_vertices = face_objects[0].getHE()

    # sweep-line algorithm
    for he in face_vertices: # create SweepEdge object
        he.sweep = SweepEdge(he)
    counts    = classify(face_vertices)
    print("Vertices:", len(face_vertices))
    print("Klassifikation:", counts)

    monoFaces = makeMonotone(face_vertices, face_objects)
    print("monotone Faces:", len(monoFaces))

    outpath = os.path.join(os.path.dirname(__file__),
                           os.path.splitext(filename)[0] + "_monotone.obj")
    writeObj(outpath, vertices, monoFaces)
    print("geschrieben:", outpath)

    if not glfw.init():
        sys.exit(1)
    window = glfw.create_window(800, 800, f"y-monotone - {filename}", None, None)
    if not window:
        glfw.terminate()
        sys.exit(1)
    glfw.make_context_current(window)

    def on_key(win, key, scancode, action, mods):
        if key == glfw.KEY_ESCAPE and action == glfw.PRESS:
            glfw.set_window_should_close(win, True)
    glfw.set_key_callback(window, on_key)

    xmin, xmax, ymin, ymax = bbox
    pad = 0.05
    pw  = (xmax - xmin) * pad
    ph  = (ymax - ymin) * pad
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(xmin - pw, xmax + pw, ymin - ph, ymax + ph, -1, 1)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    glClearColor(0.1, 0.1, 0.15, 1.0)
    glLineWidth(1.2)

    while not glfw.window_should_close(window):
        glClear(GL_COLOR_BUFFER_BIT)
        drawFaces(monoFaces)
        glfw.swap_buffers(window)
        glfw.poll_events()
    glfw.terminate()


if __name__ == '__main__':
    #run("../models/nrw.obj")
    run("../models/PNonConvexSimple1_ccw.obj")
    #run("../models/PNonConvexSimple2_ccw.obj")
