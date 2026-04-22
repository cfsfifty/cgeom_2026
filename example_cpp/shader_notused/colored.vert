#version 130
precision mediump float;

uniform mat4   PM;
in  vec3 position;
in  vec3 color;

out vec3   vColor;

void main() {
    gl_Position  = PM * vec4(position, 1.0);
    gl_PointSize = 10.0;
    vColor = color;
}
