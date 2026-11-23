// Небесное зрение: золотистое сияние, виньетка и плывущие светлые искры
shader_type canvas_item;
uniform float amount : hint_range(0.0, 1.0) = 0.0;
uniform sampler2D screen_tex : hint_screen_texture, filter_linear;
float hash(vec2 p) { return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453); }
void fragment() {
	vec3 col = texture(screen_tex, SCREEN_UV).rgb;
	float lum = dot(col, vec3(0.299, 0.587, 0.114));
	vec3 gold = mix(vec3(0.25, 0.18, 0.35), vec3(1.0, 0.86, 0.55), lum);
	vec3 c = mix(col, gold * 1.15 + col * 0.35, 0.55);
	// искры
	vec2 uv = UV * vec2(32.0, 18.0);
	uv.y += TIME * 0.35;
	vec2 id = floor(uv);
	vec2 f = fract(uv) - 0.5;
	float h = hash(id);
	float spark = step(0.93, h) * smoothstep(0.12, 0.0, length(f + 0.25 * vec2(sin(TIME + h * 6.0), cos(TIME * 0.7 + h * 9.0))));
	c += vec3(1.0, 0.9, 0.6) * spark * (0.6 + 0.4 * sin(TIME * 3.0 + h * 20.0));
	float vig = smoothstep(0.95, 0.35, length(UV - 0.5));
	c = mix(c * vec3(0.55, 0.45, 0.7), c, vig);
	COLOR = vec4(mix(col, c, amount), 1.0);
}
