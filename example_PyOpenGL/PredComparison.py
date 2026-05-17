'''
 Predicate 'rightTurn' visualization
'''
from dataclasses import dataclass
import numpy as np
import math
import time

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
 
# Global variables
title        = "LineDist-Det:" # Windowed mode's title
windowWidth  = 600 # Windowed mode's width
windowHeight = 600 # Windowed mode's height
windowPosX   = 50  # Windowed mode's top-left corner x
windowPosY   = 50  # Windowed mode's top-left corner y

# Application state
@dataclass
class AppState:
	state_gl     : list[int]
	texture      : np.ndarray
	line_slope   : float # line-segment slope
	line_slope_step : float # step size for slope changes
	line_length  : float # length of line-segment
	win_width    : float
	win_height   : float
state   = AppState([ -1 ], np.empty((128,128,3)), 0.0, 0.01, 1.2, windowWidth, windowHeight)

# Initialize OpenGL Graphics 
def initGL() -> None:
	glClearColor(0.0, 0.0, 0.0, 1.0) # Set background (clear) color to black

	# points or lines
	glEnable(GL_LINE_SMOOTH)
	glHint  (GL_LINE_SMOOTH_HINT,  GL_NICEST)
	glEnable(GL_POINT_SMOOTH)
	glHint  (GL_POINT_SMOOTH_HINT, GL_NICEST)
	glPointSize(1.0)
	glLineWidth(2.0)

	# for polygonal types, not line types
	glFrontFace  (GL_CCW) # GL_CCW is the default 
	glPolygonMode(GL_FRONT_AND_BACK, GL_FILL) # front and back face

	state.state_gl[0] = glGenTextures(1)
	glPixelStorei  (GL_UNPACK_ALIGNMENT, 1)
	glBindTexture  (GL_TEXTURE_2D, state.state_gl[0])
	glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
	glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
	glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
	glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
	# mimap not used here: write to baselevel!
	glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_BASE_LEVEL, 0)
	glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAX_LEVEL,  0)

def drawGeometry() -> None:
	# draw textured quad
	glColor3f(1.0, 1.0, 1.0)
	glEnable(GL_TEXTURE_2D)
	glBegin (GL_TRIANGLE_FAN)
	glTexCoord2f(0.0, 0.0)
	glVertex2f  (0, 0)
	glTexCoord2f(0.0, 1.0)
	glVertex2f  (state.win_width, 0)
	glTexCoord2f(1.0, 1.0)
	glVertex2f  (state.win_width, state.win_height)
	glTexCoord2f(1.0, 0.0)
	glVertex2f  (0, state.win_height)
	glEnd()
	glDisable(GL_TEXTURE_2D)

	# draw line
	glColor3f(0.0, 0.0, 0.0)
	glBegin(GL_LINES)
	glVertex2f(0.0,        0.5*state.win_height)
	glVertex2f(state.line_length, 0.5*state.win_height+state.line_length*state.line_slope)
	glEnd()

# Callback handler for window re-paint event
def display() -> None:
	glClear     (GL_COLOR_BUFFER_BIT) # Clear the color buffer
	glMatrixMode(GL_MODELVIEW)  # To operate on the ModelView matrix
	glLoadIdentity()

	drawGeometry()
	glutSwapBuffers()  # Swap front and back buffers (of double buffered mode)
 
# Callback handler when the windows is re-sized
def reshape(width : int, height : int) -> None:
	# Compute aspect ratio of the new window
	if height == 0: 
		height = 1 # To prevent divide by 0
	aspect = width / float(height)
	# Set the viewport to the full, new window
	glViewport(0, 0, width, height)
 
	# Set the aspect ratio of the clipping area to match the viewport
	glMatrixMode(GL_PROJECTION)  # To operate on the Projection matrix
	glLoadIdentity()             # Reset the projection matrix
	if width >= height:
		clipAreaXLeft   = 0.0 * aspect
		clipAreaXRight  = width * aspect
		clipAreaYBottom = 0.0
		clipAreaYTop    = height
	else:
		clipAreaXLeft   = 0.0
		clipAreaXRight  = width
		clipAreaYBottom = 0.0 / aspect
		clipAreaYTop    = height / aspect
	gluOrtho2D(clipAreaXLeft, clipAreaXRight, clipAreaYBottom, clipAreaYTop)

	state.win_width  = width
	state.win_height = height
	calcDifferences(state.texture)

# Callback handler for keypress
def keyPress (key : int, x : int, y : int) -> None:
	if key == b'z':
		state.line_length /= 1.1
	if key == b'Z':
		state.line_length *= 1.1
	if key == b'!':
		state.line_slope = -state.line_slope
	if key == b'+':
		state.line_slope_step  *= 1.1
	if key == b'-':
		state.line_slope_step  /= 1.1
	if key == b'y':
		state.line_slope -= state.line_slope_step
	if key == b'Y':
		state.line_slope += state.line_slope_step

	info = 	title + " slope('y')=%f, rate('+'-')=%f, len('z')=%f" % (state.line_slope, state.line_slope_step, state.line_length)
	# info string as ascii binary
	glutSetWindowTitle(info.encode(encoding="ascii"))
	calcDifferences(state.texture)
	glutPostRedisplay()

def rightTurn (p : tuple, q : tuple, r : tuple) -> float:
	''' Predicate: rightTurn r wrt. pq. Classification wrt. line segment pq. '''
	d1 = (q[0]-p[0], q[1]-p[1])
	d2 = (r[0]-p[0], r[1]-p[1])
	n  = ( -d1[1], d1[0])
	len= math.sqrt(np.dot(n, n))
	n  = (n[0]/len, n[1]/len) # normalized
	# scalar product n^t*d2
	return np.dot(n, d2)

def rightTurnDet (p : tuple, q : tuple, r : tuple) -> float:
	''' Predicate: rightTurn r wrt. pq. Classification wrt. signed volume
		of parallelogram (p, q, q, r-p) . '''
	d1    = (q[0]-p[0], q[1]-p[1])
	d2    = (r[0]-p[0], r[1]-p[1])
	diag1 =  d1[0]*d2[1] 
	diag2 = -d1[1]*d2[0]
	return diag1+diag2

# simple colormap: blue (negative) via white (0.0) to red (positive)
def colorMap (value : float, bias : float, radius : float) -> tuple:
	# clamping to [0.0, 1.0]
	value = 100*(value+bias)/radius+0.5
	#print(f" {value}", end="")
	if value < 0.0: 
		value = 0.0
	if value > 1.0: 
		value = 1.0
	if value < 0.5:
		# Kalt bis Weiß (Blau -> Weiß)
		# Blau nimmt ab, Rot und Grün nehmen zu
		v = value * 2.0
		r = int(v * 255)
		g = int(v * 255)
		b = 255
	else:
		# Weiß bis Heiß (Weiß -> Rot)
		# Rot bleibt voll, Grün und Blau nehmen ab
		v = (value - 0.5) * 2.0
		r = 255
		g = int((1.0 - v) * 255)
		b = int((1.0 - v) * 255)
	return (r, g, b)

def calcDifferences (pix : np.ndarray) -> None:
	width, height, comp = pix.shape
	#pix = np.array(image)
	#print(np.info(pix))

	tex_width  = float(max(width, height))
	grid_width = 1.0/float(tex_width) #max(state.win_width, state.win_height)
	radius = tex_width*tex_width

	p = (0.0, 0.0)
	qscale = state.line_length/math.sqrt(1.0 + state.line_slope*state.line_slope)
	q = (1.0*qscale, state.line_slope*qscale)
	predRange = (math.inf, -math.inf)
	for y in range(height):
		for x in range(width):
			r  = (float(x), float(y)-0.5*height)

			p1 = rightTurn   (p, q, r)+0.5
			p2 = rightTurnDet(p, q, r)
			#pred   = (p1-p2) # difference of p1 and p2
			pred   = p1      # value of p1
			#pred   = (p1*p2) # product of p1 and p2
			predRange = (min(predRange[0], pred), max(predRange[1], pred))
			pix[x, y, :] = colorMap(pred, 0.0, radius)
	print("predicate-range=", predRange)

	pixData = pix.reshape((3*width*height,1))
	glBindTexture(GL_TEXTURE_2D, state.state_gl[0])
	glTexImage2D (GL_TEXTURE_2D, 0, GL_RGB8, width, height, 0, GL_RGB, GL_UNSIGNED_BYTE, pixData)

# Callback handler when the timer expired 
#def Timer(value : int) -> None:
#glutTimerFunc(10, Timer, 0) # subsequent timer call at milliseconds
 
# GLUT runs as a console application starting at main() 
def main(argv : list[str]) -> None:
	# Open image
	state.texture = np.empty(shape=(128, 128, 3), dtype=np.uint8)

	glutInit(argv)             # Initialize GLUT
	glutInitDisplayMode(GLUT_DOUBLE) # Enable double buffered mode
	glutInitWindowSize (windowWidth, windowHeight)  # Initial window width and height
	glutInitWindowPosition(windowPosX, windowPosY)  # Initial window top-left corner (x, y)
	info = 	title + " slope('y')=%f, rate('+'-')=%f, len('z')=%f" % (state.line_slope, state.line_slope_step, state.line_length)
	glutCreateWindow(info.encode(encoding="ascii"))
	glutReshapeFunc(reshape)      # Register callback handler for window re-shape
	glutDisplayFunc(display)      # Register callback handler for window re-paint
	#glutIdleFunc(display)         # Register callback handler for window idling: redisplay
	glutKeyboardFunc(keyPress)    # Register callback handler for kae presses
	
	initGL()                      # Our own OpenGL initialization
	glutMainLoop()                # Enter event-processing loop

if __name__ == '__main__':
	main(sys.argv)
