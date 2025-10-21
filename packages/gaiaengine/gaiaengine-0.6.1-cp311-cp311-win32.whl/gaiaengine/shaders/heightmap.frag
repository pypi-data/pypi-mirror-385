// Version is defined by shader compiler, 330 for desktop and 300 es for mobile

const vec3 lightDir = normalize(vec3 (1,0,1));

in vec2 texCoords;
in vec3 normal;
in vec4 color;

layout (location = 0) out vec4 fragColor;

uniform sampler2D tex;

uniform bool useColor;
uniform bool noNormal;

void main() {
	if (useColor)
		fragColor = color;
	else
		fragColor = texture( tex, texCoords );
		
	if (!noNormal)
		fragColor.rgb *= min(0.5 + (useColor ? 0.5 : 1.0) * dot(lightDir,normal), 1.0);
}
