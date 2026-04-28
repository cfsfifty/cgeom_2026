'''
 Drawing a OBJ 2d-polygon
'''
from dataclasses import dataclass

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from math import *
import FileObj
import random
 
# Global variables
title        = b"Polygon" # Windowed mode's title
windowWidth  = 600 # Windowed mode's width
windowHeight = 600 # Windowed mode's height
windowPosX   = 50  # Windowed mode's top-left corner x
windowPosY   = 50  # Windowed mode's top-left corner y
 
# Projection clipping area
# clipAreaXLeft, clipAreaXRight, clipAreaYBottom, clipAreaYTop;
@dataclass
class AppState:
	polygon  = FileObj.FileObj()
	state_gl = [ -1 ]

state = AppState()

# Initialize OpenGL Graphics 
def initGL():
	glClearColor(1.0, 1.0, 1.0, 1.0) # Set background (clear) color to black

	# for polygonal types, not line types
	glFrontFace  (GL_CCW) # this is the default 
	glPolygonMode(GL_FRONT, GL_FILL) # front face (Vorderseite)
	glPolygonMode(GL_BACK,  GL_LINE) # back  face (Rückseite)

def drawGeometry():
	# Outline polygon
	glLineWidth(2.0)
	glBegin(GL_POLYGON)
	#glBegin(GL_TRIANGLE_FAN)
	#glBegin(GL_LINE_LOOP)
	point = state.polygon.getPointCoords()
	glColor3f  (1.0, 0.0, 0.0)  # Red
	for face in state.polygon.getPolygonIndices():
		for i, idx in enumerate(face): # Last vertex same as first vertex
			#glColor3f  (random.random(), random.random(), random.random())  # Red
			glVertex2fv(point[idx])
	glEnd()

# Callback handler for window re-paint event
def display():
	glClear     (GL_COLOR_BUFFER_BIT) # Clear the color buffer
	center_x = 0.5*(state.polygon.x[0] + state.polygon.x[1]) # refactor: move to "state"
	center_y = 0.5*(state.polygon.y[0] + state.polygon.y[1])
	print("model-center", center_x, center_y)
	glMatrixMode(GL_MODELVIEW)  # To operate on the ModelView matrix
	glLoadIdentity()
	glTranslated  (-center_x, -center_y, 0.0)

	drawGeometry()
	glutSwapBuffers()  # Swap front and back buffers (of double buffered mode)

# Callback handler for window re-paint event, using display lists
def displayDisplayList():
	glClear     (GL_COLOR_BUFFER_BIT) # Clear the color buffer
	center_x = 0.5*(state.polygon.x[1] + state.polygon.x[0]) # refactor: move to "state"
	center_y = 0.5*(state.polygon.y[1] + state.polygon.y[0])
	print("model-center", center_x, center_y)
	glMatrixMode(GL_MODELVIEW)  # To operate on the ModelView matrix
	glLoadIdentity()
	glTranslated  (-center_x, -center_y, 0.0)

	if state.state_gl[0] < 0: # not compiled, then compile and execute
		glNewList(state.state_gl[0], GL_COMPILE_AND_EXECUTE)
		drawGeometry()
		glEndList()
	else: # execute display-list
		glCallList(state.state_gl[0])
	glutSwapBuffers()  # Swap front and back buffers (of double buffered mode)
 
# Call back when the windows is re-sized */
def reshape(width, height):
	# Compute aspect ratio of the new window
	if height == 0: 
		height = 1 # To prevent divide by 0
	aspect = width / float(height)
	# Set the viewport to cover the new window
	glViewport(0, 0, width, height)
 
	# Set the aspect ratio of the clipping area to match the viewport
	glMatrixMode(GL_PROJECTION)  # To operate on the Projection matrix
	glLoadIdentity()             # Reset the projection matrix
	size_x = 0.5*(state.polygon.x[1] - state.polygon.x[0]) # refactor: move to "state"
	size_y = 0.5*(state.polygon.y[1] - state.polygon.y[0])
	size   = max(size_x, size_y)
	if width >= height:
		clipAreaXLeft   = -size * aspect
		clipAreaXRight  =  size * aspect
		clipAreaYBottom = -size
		clipAreaYTop    =  size
	else:
		clipAreaXLeft   = -size
		clipAreaXRight  =  size
		clipAreaYBottom = -size / aspect
		clipAreaYTop    =  size / aspect
	gluOrtho2D(clipAreaXLeft, clipAreaXRight, clipAreaYBottom, clipAreaYTop)
 
# Called back when the timer expired 
#def Timer(value : int) -> None:
#glutTimerFunc(10, Timer, 0) # subsequent timer call at milliseconds
 
# Main function: GLUT runs as a console application starting at main() */
def main():
	state.polygon.read("../models/5gon.obj")
	#state.polygon.read("../models/nrw.obj")

	glutInit(sys.argv)             # Initialize GLUT
	glutInitDisplayMode(GLUT_DOUBLE) # Enable double buffered mode
	glutInitWindowSize (windowWidth, windowHeight)  # Initial window width and height
	glutInitWindowPosition(windowPosX, windowPosY)  # Initial window top-left corner (x, y)
	glutCreateWindow(title)       # Create window with given title
	glutReshapeFunc(reshape)      # Register callback handler for window re-shape
	glutDisplayFunc(display)      # Register callback handler for window re-paint
	#glutIdleFunc(display)         # Register callback handler for window idling: redisplay
	#glutTimerFunc(0, Timer, 0)    # First timer call immediately
	
	initGL()                      # Our own OpenGL initialization
	glutMainLoop()                # Enter event-processing loop

if __name__ == '__main__':
	main()
