// Даршан: лучистое сияние из точки (облик Господа не изображается — только свет)
shader_type canvas_item;
uniform float amount : hint_range(0.0, 1.0) = 0.0;
uniform vec2 center = vec2(0.5, 0.5);
void fragment() {
	vec2 d = (UV - center) * vec2(16.0 / 9.0, 1.0);
	float r = length(d);
	float a = atan(d.y, d.x);
	float rays = 0.5 + 0.5 * sin(a * 18.0 + TIME * 0.8) * sin(a * 7.0 - TIME * 0.5);
	float core = smoothstep(0.55, 0.0, r);
	float glow = core * (0.65 + 0.35 * rays) + smoothstep(0.12, 0.0, r);
	vec3 c = mix(vec3(0.35, 0.55, 1.0), vec3(1.0, 0.92, 0.65), smoothstep(0.4, 0.0, r));
	COLOR = vec4(c * glow * 1.4, clamp(glow, 0.0, 1.0) * amount);
}
