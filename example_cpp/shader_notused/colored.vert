#version 100
precision mediump float;

uniform mat4   PM;
attribute vec3 position;
attribute vec3 color;

varying vec3   vColor;

void main() {
    gl_Position  = PM * vec4(position, 1.0);
    gl_PointSize = 10.0;
    vColor = color;
}
