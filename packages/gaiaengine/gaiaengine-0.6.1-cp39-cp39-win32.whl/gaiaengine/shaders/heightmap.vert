// Version is defined by shader compiler, 330 for desktop and 300 es for mobile

layout (location = 0) in vec3 in_Vertex;
layout (location = 1) in vec3 in_Normal;
layout (location = 2) in vec4 in_Color;

out vec2 texCoords;
out vec3 normal;
out vec4 color;

uniform mat4 MVP;
uniform vec3 originOffset;

void main(){
	gl_Position =  MVP * vec4(in_Vertex + originOffset,1);

	texCoords = in_Vertex.rg / 5.0;
	normal = in_Normal;
	color = in_Color;
}
