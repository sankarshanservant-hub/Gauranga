// Мягкая тень-пятно под персонажем
shader_type spatial;
render_mode unshaded, blend_mix, depth_draw_never, cull_disabled;
uniform float strength = 0.45;
void fragment() {
	float d = length(UV - vec2(0.5)) * 2.0;
	ALBEDO = vec3(0.0);
	ALPHA = strength * smoothstep(1.0, 0.2, d);
}
