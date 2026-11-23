// Прокси-геометрия фона: рисует пиксели пререндеренного фона по экранным координатам.
// Персонаж за стеной/под навесом загораживается точно по силуэту из рендера.
shader_type spatial;
render_mode unshaded, cull_disabled;
uniform sampler2D bg_a : source_color, filter_linear, repeat_disable;
uniform sampler2D bg_b : source_color, filter_linear, repeat_disable;
uniform float mix_ab = 0.0;
uniform float debug_tint = 0.0;
void fragment() {
	vec3 a = texture(bg_a, SCREEN_UV).rgb;
	vec3 b = texture(bg_b, SCREEN_UV).rgb;
	vec3 c = mix(a, b, mix_ab);
	ALBEDO = mix(c, vec3(1.0, 0.0, 1.0) * (0.3 + 0.7 * fract(VERTEX.y)), debug_tint);
}
