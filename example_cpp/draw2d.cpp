// Drawing a OBJ 2d-polygon
#include <cmath>
#include <ctime>
#include <GLFW/glfw3.h>
#include <GL/gl.h>
//#include <GL/glu.h>
#include <GLM/glm.hpp>
#include <glm/gtc/type_ptr.hpp>
#include "FileObj.h"
 
// Global variables
const char* title= "Polygon"; // Windowed mode's title
int windowWidth  = 600; // Windowed mode's width
int windowHeight = 600; // Windowed mode's height
int windowPosX   = 50;  // Windowed mode's top-left corner x
int windowPosY   = 50;  // Windowed mode's top-left corner y
 
// Projection clipping area
// clipAreaXLeft, clipAreaXRight, clipAreaYBottom, clipAreaYTop;
FileObj state;
GLuint  stateGL[] = { GLuint(-1), GLuint(-1), GLuint(-1) };


bool checkErrorGL () {
    GLenum err = glGetError(); 
    assert(err == GL_NO_ERROR);
    return (err != GL_NO_ERROR);
}

// Initialize OpenGL Graphics 
void initGL() {
   glClearColor(0.0, 0.0, 0.0, 1.0); // Set background (clear) color to black
   glClearDepth(1.0f);
   //glEnable(GL_DEPTH_TEST);
}
void releaseGL() {
    if (stateGL[0] != GLuint(-1)) {
        glDeleteLists(stateGL[0], 1);
        stateGL[0] = GLuint(-1);
    }
}
// Callback handler for window re-paint event
void display(GLFWwindow* window) 
{
  float center_x = 0.5*(state.bbox_min[0] + state.bbox_max[0]);
  float center_y = 0.5*(state.bbox_min[1] + state.bbox_max[1]);
  std::cout << "model-center" << center_x << ", " << center_y << std::endl;
  glClear  (GL_COLOR_BUFFER_BIT); // Clear the color buffer
  //glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT); // Clear the color and depth buffer
  glMatrixMode(GL_MODELVIEW); // To operate on the model-view matrix
  glLoadIdentity();           // Reset model-view matrix
  glTranslated  (-center_x, -center_y, 0.0);
	
  // Use triangular segments to form a circle
  glLineWidth(2.0f);
  glBegin(GL_LINE_LOOP);
  glColor3f  (1.0f, 0.0f, 0.0f);  // Red
  auto poly = state.getPolygon();
  for (auto iter = poly.begin(); iter != poly.end(); ++iter) { // Last vertex same as first vertex
      glVertex2f(iter->x, iter->y);
  }
  glEnd();
  checkErrorGL();
  glfwSwapBuffers(window);
}
// Callback handler for window re-paint event, using display lists
void displayDisplayList(GLFWwindow* window)
{
  float center_x = 0.5*(state.bbox_min[0] + state.bbox_max[0]);
  float center_y = 0.5*(state.bbox_min[1] + state.bbox_max[1]);
  std::cout << "model-center" << center_x << ", " << center_y << std::endl;
  glClear     (GL_COLOR_BUFFER_BIT); // Clear the color buffer
  glMatrixMode(GL_MODELVIEW); // To operate on the model-view matrix
  glLoadIdentity();           // Reset model-view matrix
  glTranslated  (-center_x, -center_y, 0.0);

  if (stateGL[0] == GLuint(-1)) {
      stateGL[0] = glGenLists(1);
  }
  glNewList(stateGL[0], GL_COMPILE_AND_EXECUTE); // Use triangular segments to form a circle
    checkErrorGL();
    glLineWidth(2.0);
    glBegin(GL_LINE_LOOP);
    glColor3f  (1.0, 0.0, 0.0); // Red
    auto poly = state.getPolygon();
    for (auto iter = poly.begin(); iter != poly.end(); ++iter) { // Last vertex same as first vertex
	glVertex2fv(*iter);
    }
    glEnd();
  glEndList();
  checkErrorGL();
  glfwSwapBuffers(window);
}
// Call back when the windows is re-sized */
void resize(GLFWwindow* window, int width, int height) 
{
    // Compute aspect ratio of the new window
    if (height == 0) {
        height = 1; // To prevent divide by 0
    }
        float aspect = float(width) / float(height);
        // Set the viewport to cover the new window
        glViewport(0, 0, width, height);

        // Set the aspect ratio of the clipping area to match the viewport
	    float size_x = 0.5f*(state.bbox_max[0] - state.bbox_min[0]); // refactor: move to "state"
	    float size_y = 0.5f*(state.bbox_max[1] - state.bbox_min[1]);
	    float size   = std::max(size_x, size_y);
        glMatrixMode(GL_PROJECTION); // To operate on the Projection matrix
        glLoadIdentity();            // Reset the projection matrix
        float clipAreaXLeft, clipAreaXRight, clipAreaYBottom, clipAreaYTop;
        if (width >= height) {
            clipAreaXLeft   = -size * aspect; 
            clipAreaXRight  =  size * aspect;
            clipAreaYBottom = -size;
            clipAreaYTop    =  size;
        }
        else {
            clipAreaXLeft   = -size;
            clipAreaXRight  =  size;
            clipAreaYBottom = -size / aspect; 
            clipAreaYTop    =  size / aspect;
        }
        glm::mat4 projection = glm::ortho(clipAreaXLeft, clipAreaXRight, clipAreaYBottom, clipAreaYTop);
        glLoadMatrixf(glm::value_ptr(projection));
        //gluOrtho2D(clipAreaXLeft, clipAreaXRight, clipAreaYBottom, clipAreaYTop);
}
 
// Called back when the timer expired 
//def Timer(value : int) -> None:
//glutTimerFunc(10, Timer, 0) // subsequent timer call at milliseconds
 
int main(int argc, char* argv[]) 
{
  //state.read("../star.obj");
  state.read("../nrw.obj");

  // Initialize glfw library (window toolkit).
  if (!glfwInit()) {
		return -1;
  } 

	// GLFW: Create a window and opengl context (version 4.3 compatibility profile).
	glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR, 4);
	glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR, 3);
	glfwWindowHint(GLFW_OPENGL_PROFILE, GLFW_OPENGL_COMPAT_PROFILE);
    // OpenGL 4.3 core profile uses GLSL shaders
    //glfwWindowHint(GLFW_OPENGL_PROFILE, GLFW_OPENGL_CORE_PROFILE);
    glfwWindowHint(GLFW_RESIZABLE, GL_TRUE);
    glfwWindowHint(GLFW_DOUBLEBUFFER, GL_TRUE);
    glfwWindowHint(GLFW_DEPTH_BITS, 24);
    glfwWindowHint(GLFW_RESIZABLE, GL_TRUE);
    glfwWindowHint(GLFW_DOUBLEBUFFER, GL_TRUE);
	// Turn this on for smoother lines.
	// glfwWindowHint(GLFW_SAMPLES, 8);
	
    GLFWwindow* window = glfwCreateWindow(windowWidth, windowHeight, title, nullptr, nullptr);
	if (!window) {
		glfwTerminate();
		return -2;
	}

	// Make the window's opengl context current.
	glfwMakeContextCurrent(window);

    // Set callbacks for resize and keyboard events.
	glfwSetWindowSizeCallback   (window, resize);
    glfwSetWindowRefreshCallback(window, displayDisplayList);
	//fwSetKeyCallback(window, keyboard);

    // own OpenGL initialization
    initGL();                      

    // We have to call resize once for a proper setup.
	resize(window, windowWidth, windowHeight);

	// Loop until the user closes the window.
	while (!glfwWindowShouldClose(window)) {
        //glfwPollEvents();           // poll for and process events and change state (busy idle processing)
		glfwWaitEvents();           // wait for process events and change state (no idle processing)
        //glfwWaitEventsTimeout(0.033);  // sleep for up to 33ms to reduce CPU usage (idle processing)
        displayDisplayList(window); // then display
	}

	// Clean up everything on termination.
	releaseGL();
	glfwTerminate();

	return 0;

}
