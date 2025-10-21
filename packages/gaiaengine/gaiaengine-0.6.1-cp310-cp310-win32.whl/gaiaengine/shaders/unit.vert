// Version is defined by shader compiler, 330 for desktop and 300 es for mobile

layout (location = 0) in vec3 in_Vertex;
layout (location = 1) in vec3 in_Pos;
layout (location = 2) in vec2 in_TexCoords;
layout (location = 3) in float in_Layer;
layout (location = 4) in vec3 in_HeightmapNormal;

out vec2 texCoords;
out float layer;

// If the element is too close
out float discardFrag;

uniform mat4 VP;
uniform mat4 MODEL;

uniform float elementNearPlane;
uniform vec3 camPos;

void main(){
	vec3 posToCam = camPos - in_Pos;
	discardFrag = step(length(posToCam), elementNearPlane);

	vec4 pos = VP * (vec4(in_Pos,0) + MODEL * vec4(in_Vertex,1));
	// Move units towards the camera to avoid clipping
	pos.z -= 0.1 * step(0.0, dot(vec2(posToCam), vec2(in_HeightmapNormal)));
	gl_Position = pos;

	texCoords = in_TexCoords;
	layer = in_Layer;
}
