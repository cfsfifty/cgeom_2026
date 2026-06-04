'''
 AABBHierarchy, subdivision at the median of dimension
'''
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import math
import FileObj3d
import copy
import random
import BinaryNode
import ProgramState
import v3
import scalar
from collections.abc import Iterable

# Program state
state   = ProgramState.ProgramState(cam_dir=[0.0, 0.0, -10.0])

# Global variables
title        = b"AABBHierarchy" # Windowed mode's title
windowWidth  = 600 # Windowed mode's width
windowHeight = 600 # Windowed mode's height
windowPosX   = 50  # Windowed mode's top-left corner x
windowPosY   = 50  # Windowed mode's top-left corner y

def face_center (indices : list[int], points : list[tuple]):
	center = [ 0.0 for i in range(3) ]
	for idx in indices:
		v3.add_inplace(center, points[idx])
	center[0] /= float(len(indices))
	center[1] /= float(len(indices))
	center[2] /= float(len(indices))
	return center
def face_min (indices : list[int], points : list[tuple]):
	center = [ math.inf for i in range(3) ]
	for idx in indices:
		v3.min_inplace(center, points[idx])
	return center
def face_max (indices : list[int], points : list[tuple]):
	center = [ -math.inf for i in range(3) ]
	for idx in indices:
		v3.max_inplace(center, points[idx])
	return center
def create_hierarchy (l : int, section : tuple, index_list : list[list], points : list[Iterable], faces : list[list]) -> BinaryNode.BinaryNode:
	global state
	node = BinaryNode.BinaryNode(0, section[0], section[1], index_list[0], points, faces)
	assert(set(index_list[0][section[0]:section[1]]) == set(index_list[1][section[0]:section[1]]))
	assert(set(index_list[0][section[0]:section[1]]) == set(index_list[2][section[0]:section[1]]))
	# if number of faces=1, then leaf node
	print("node", section)
	if section[1]-section[0] <= 2:
		state.max_level = max(state.max_level, l)
		return node

	# determine subdivision axis k
	max_side    = [0, 0, 0]
	key_x       = lambda f: face_center(faces[f], points)[0]
	key_y       = lambda f: face_center(faces[f], points)[1]
	key_z       = lambda f: face_center(faces[f], points)[2]
	max_side[0] = key_x(index_list[0][section[1]-1])-key_x(index_list[0][section[0]])
	max_side[1] = key_y(index_list[1][section[1]-1])-key_y(index_list[1][section[0]])
	max_side[2] = key_z(index_list[2][section[1]-1])-key_z(index_list[2][section[0]])

	# heuristic: which axis?
	_, k= max((max_side[i], i) for i in range(3))
	# which subdivision position?
	median = int(math.ceil((section[0]+section[1])/2))
	print("dim", k, "at position", median, (section[0], median), (median, section[1]))

	#index_list[k][section[0]:median-1]
	#index_list[k][median:section[1]]
	# filter other dimensions k+1, k+2
	filtered  = [ 0 for i in range(section[0], section[1])]
	left_part = index_list[k][section[0]:median]
	#print(left_part, 
	#   index_list[(k+1)%3][section[0]:section[1]],
	#   index_list[(k+2)%3][section[0]:section[1]])
	for kk in range(3):
		if kk == k: # k is sorted
			continue

		left  = 0
		right = median-section[0]
		for i in range(section[0], section[1]):
			if index_list[kk][i] in left_part:
				#print(left, index_list[kk][i], "in", left_part)
				assert(left < median)
				filtered[left]  = index_list[kk][i]
				left += 1
			else:
				#print(right, index_list[kk][i], "!in", left_part)
				assert(right < section[1])
				filtered[right] = index_list[kk][i]
				right += 1
		# replace filtered section
		#print("vor", index_list[kk][section[0]:median], index_list[kk][median:section[1]])
		index_list[kk][section[0]:section[1]] = filtered
		#print("nach", index_list[kk][section[0]:median], index_list[kk][median:section[1]])

	node.k       = k
	node.indices = index_list[k]
	left_node  = create_hierarchy (l+1, (section[0], median),     index_list, points, faces)
	right_node = create_hierarchy (l+1, (median,     section[1]), index_list, points, faces)
	node.left_node  = left_node
	node.right_node = right_node
	return node

def draw_node(l : int,  level : int, node : BinaryNode.BinaryNode):
	global state
	model_center = state.model.bbox.center()
	#print(l, level)

	if node.left_node == None and node.right_node == None: 
		# in leaf node: draw triangles
		glEnable     (GL_LIGHTING)
		glPolygonMode(GL_FRONT, GL_FILL)
		glColor3f  (0.5, 0.5, 0.5)
		for i in range(node.left, node.right):
			f = node.indices[i]
			glBegin(GL_TRIANGLE_FAN)
			for p in node.faces[f]:
				# normal is only approximate!
				normal = [ node.points[p][i] for i in range(3) ]
				v3.add_inplace  (normal, model_center, -1.0)
				#v3.scale_inplace(normal, 1.0/v3.length(normal))
				glNormal3fv(normal)
				glVertex3fv(node.points[p])
			glEnd()
		return

	if l == level:
		glDisable(GL_LIGHTING)
		glPolygonMode(GL_FRONT, GL_LINE)
		if node.color[0] < 0.0: # assign random color to this node
			node.color = [ random.random(), random.random(), random.random() ]
		glColor3fv (node.color)

		# bbox is min/max of face points
		bbox = [[math.inf for i in range(3)], [-math.inf for i in range(3)] ]
		# Python error: [ obj ]*n creates n-times a reference to obj; beware, they are not independent!
		#bbox = [[math.inf, -math.inf]]*3
		for f in node.indices[node.left:node.right]:
			#center = face_center(node.faces[f], node.points)
			for p in node.faces[f]:
				v3.min_inplace(bbox[0], node.points[p])
				v3.max_inplace(bbox[1], node.points[p])
		glBegin(GL_QUADS)
		# side min[0] 
		glVertex3f(bbox[0][0], bbox[0][1], bbox[0][2])
		glVertex3f(bbox[0][0], bbox[0][1], bbox[1][2])
		glVertex3f(bbox[0][0], bbox[1][1], bbox[1][2])
		glVertex3f(bbox[0][0], bbox[1][1], bbox[0][2])

		glVertex3f(bbox[1][0], bbox[0][1], bbox[0][2])
		glVertex3f(bbox[1][0], bbox[0][1], bbox[1][2])
		glVertex3f(bbox[1][0], bbox[1][1], bbox[1][2])
		glVertex3f(bbox[1][0], bbox[1][1], bbox[0][2])
		# side min[1] 
		glVertex3f(bbox[0][0], bbox[0][1], bbox[0][2])
		glVertex3f(bbox[0][0], bbox[0][1], bbox[1][2])
		glVertex3f(bbox[1][0], bbox[0][1], bbox[1][2])
		glVertex3f(bbox[1][0], bbox[0][1], bbox[0][2])

		glVertex3f(bbox[0][0], bbox[1][1], bbox[0][2])
		glVertex3f(bbox[0][0], bbox[1][1], bbox[1][2])
		glVertex3f(bbox[1][0], bbox[1][1], bbox[1][2])
		glVertex3f(bbox[1][0], bbox[1][1], bbox[0][2])
		# side min[2] 
		glVertex3f(bbox[0][0], bbox[0][1], bbox[0][2])
		glVertex3f(bbox[0][0], bbox[1][1], bbox[0][2])
		glVertex3f(bbox[1][0], bbox[1][1], bbox[0][2])
		glVertex3f(bbox[1][0], bbox[0][1], bbox[0][2])

		glVertex3f(bbox[0][0], bbox[0][1], bbox[1][2])
		glVertex3f(bbox[0][0], bbox[1][1], bbox[1][2])
		glVertex3f(bbox[1][0], bbox[1][1], bbox[1][2])
		glVertex3f(bbox[1][0], bbox[0][1], bbox[1][2])
		glEnd()

	if node.left_node != None: # visit left node
		draw_node(l+1, level, node.left_node)
	if node.right_node != None: # visit right node
		draw_node(l+1, level, node.right_node)


# initialize OpenGL 
def initGL():
	glClearColor(0.0, 0.0, 0.0, 1.0) # Set background (clear) color to black
	glClearDepth(1.0)
	glEnable(GL_DEPTH_TEST)
	glLineWidth(2.0)

	glEnable(GL_NORMALIZE) # normalize given normal vectors
	glShadeModel(GL_SMOOTH)
	# glEnable(GL_LIGHTING) # changed in draw_node
	glEnable(GL_LIGHT0) # enable default light0
    # "The initial position is (0, 0, 1, 0); thus, the initial light source is directional, parallel to, and in the direction of the -z axis."

	glFrontFace  (GL_CCW)  
	# changed in draw_node
	glPolygonMode(GL_FRONT, GL_LINE)
	glPolygonMode(GL_BACK,  GL_LINE) 

# window display event
def draw_geometry():
	global state
	# always look at center, distance state.cam_scale, direction state.cam_dir,
	# up is y-axis
	model_center = state.model.bbox.center()
	gluLookAt(model_center[0]+state.cam_scale*state.cam_dir[0], 
		   model_center[1]+state.cam_scale*state.cam_dir[1], 
		   model_center[2]+state.cam_scale*state.cam_dir[2],
		   model_center[0], model_center[1], model_center[2],
		   0.0, 1.0, 0.0)

	draw_node(0, state.level, state.node)

# window re-paint event
def display():
	glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT) # Clear the color buffer
	glMatrixMode  (GL_MODELVIEW)  # To operate on the ModelView matrix
	glLoadIdentity()
	# model center in (0, 0, 0)
	center = state.model.bbox.center()
	#print("model-center", center)
	glTranslatef  (-center[0], -center[1], -center[2])
	cam_len   = v3.length(state.cam_dir)
	light_dir = ( state.cam_dir[0]/cam_len, state.cam_dir[1]/cam_len, state.cam_dir[2]/cam_len, 0.0 )
	glLightfv(GL_LIGHT0, GL_POSITION, light_dir) 

	draw_geometry()
	glutSwapBuffers()  # Swap front and back buffers (of double buffered mode)
 
# window re-size event
def reshape(width, height):
	global state
	# Compute aspect ratio of the new window
	if height == 0: 
		height = 1 # To prevent divide by 0
	aspect = width / float(height)
	# Set the viewport to cover the new window
	glViewport(0, 0, width, height)
 
	# Set the aspect ratio of the clipping area to match the viewport
	size_x = 0.5*(state.model.bbox.extent[0][1] - state.model.bbox.extent[0][0])
	size_y = 0.5*(state.model.bbox.extent[1][1] - state.model.bbox.extent[1][0])
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
	glMatrixMode(GL_PROJECTION)  # To operate on the Projection matrix
	glLoadIdentity()             # Reset the projection matrix
	# fovy=50, aspect-ratio, zNear=0.1, zFar=10000.0
	gluPerspective(50.0, aspect, 0.1, 10000.0)
	#glFrustum (clipAreaXLeft, clipAreaXRight, clipAreaYBottom, clipAreaYTop, 0.1, 1000.0)
	#gluOrtho2D(clipAreaXLeft, clipAreaXRight, clipAreaYBottom, clipAreaYTop)

# key-press event 
def key_press(kcode, x, y):
	global state
	
	modstate = glutGetModifiers()
	#if kcode == b'\x1b':
	#	exit(1)
	if kcode == b'+':
		state.level = scalar.clamp(state.level+1, 0, state.max_level)
	if kcode == b'-':
		state.level = scalar.clamp(state.level-1, 0, state.max_level)

	glutSetWindowTitle(str(state))
	glutPostRedisplay()
# key-release event 
def key_release(kcode, x, y):
	global state
	glutPostRedisplay()

# mouse button down/up event
enum_rotate = 0
enum_zoom = 1
def mouse_button (button, button_state, x, y):
	global state

	if button_state==GLUT_UP:
		state.inter_type = -1
		return
	
	#if state==GLUT_DOWN:
	if button==GLUT_LEFT_BUTTON:
		state.inter_x = x
		state.inter_y = y
		state.inter_type = enum_rotate 
	elif button==GLUT_MIDDLE_BUTTON:
		# not used
		pass
	elif button==GLUT_RIGHT_BUTTON:
		state.inter_x = x
		state.inter_y = y
		state.inter_type = enum_zoom

wc_scalefactor = 1e-4 # part of pixel
# mouse motion event:
# CAUTION: mode enum_rotate shows dof-locking, trackball interator would use quaternions!
def mouse_motion (x, y):
	global state
	if state.inter_type < 0: # key pressed
		return

	# left-mouse button pressed: rotate  (always looking at model-center)
	if state.inter_type == enum_rotate: 
		# rotate yz by win-y
		radian = 2.0*math.pi*float(y-state.inter_y)*wc_scalefactor
		v3.rotate_x(state.cam_dir, state.cam_dir, radian)
		# rotate xz by win-x
		radian = 2.0*math.pi*float(x-state.inter_x)*wc_scalefactor
		v3.rotate_y(state.cam_dir, state.cam_dir, radian)
	# right-mouse button pressed: zooming (always looking at model-center)	
	if state.inter_type == enum_zoom: 
		factor = math.pow(1.1, float(y-state.inter_y))
		state.cam_scale = factor 
	glutPostRedisplay() 

# Callback when the timer expired 
#def Timer(value : int) -> None:
#glutTimerFunc(10, Timer, 0) # subsequent timer call at milliseconds

# GLUT starts running event processing
def main():
	global state

	# create hierarchy for model
	print("local directory", os.getcwd())
	state.model.read("../models_3d/teapot.obj")
	points = state.model.getPointCoords()
	faces  = state.model.getFaces()
	# center model in origin
	#model_center = state.model.bbox.center()
	#for i, p in enumerate(points):
	#	points[i] = ( p[0]-model_center[0], p[1]-model_center[1], p[2]-model_center[2] )

	index_list = [list(), list(), list()]
	index_list[0] = [f for f in range(len(faces))]
	index_list[1] = copy.deepcopy(index_list[0]) 
	index_list[2] = copy.deepcopy(index_list[0]) 
	#print(index_list)

	# compute face centerpoint
	key_x   = lambda f: face_center(faces[f], points)[0]
	key_y   = lambda f: face_center(faces[f], points)[1]
	key_z   = lambda f: face_center(faces[f], points)[2]
	# take the first (random) point of face
	#key_x   = lambda f: points[faces[f][0]][0]
	#key_y   = lambda f: points[faces[f][0]][1]
	#key_z   = lambda f: points[faces[f][0]][2]
	index_list[0].sort(key=key_x)
	index_list[1].sort(key=key_y)
	index_list[2].sort(key=key_z)
	section = (0, len(faces))
	#print(index_list)
	state.node = create_hierarchy (0, section, index_list, points, faces)

	# GLUT setup
	glutInit(sys.argv)             # Initialize GLUT
	glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGBA) # Enable double buffered mode
	glutInitWindowSize (windowWidth, windowHeight)  # Initial window width and height
	glutInitWindowPosition(windowPosX, windowPosY)  # Initial window top-left corner (x, y)
	glutCreateWindow(title)       # Create window with given title
	glutSetWindowTitle(str(state))
	glutReshapeFunc(reshape)      # Register callback handler for window re-shape
	glutDisplayFunc(display)      # Register callback handler for window re-paint
	glutKeyboardFunc(key_press)
	glutKeyboardUpFunc(key_release)
	glutMouseFunc (mouse_button)
	glutMotionFunc(mouse_motion)
	#glutIdleFunc(display)         # Register callback handler for window idling: redisplay
	#glutTimerFunc(0, Timer, 0)    # First timer call immediately
	
	initGL()                      # OpenGL initialization
	glutMainLoop()                # Enter event-processing loop

# Python application entry point
if __name__ == '__main__':
	main()
