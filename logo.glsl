#define PI 3.1415926538
#ifdef GL_ES
precision mediump float;
#endif

uniform vec2 u_resolution;
uniform float u_time;

float stroke(float x, float s, float w){
    float d = step(s, x+w*.5)
            - step(s, x-w*.5);

    return clamp(d, 0., 1.);
}

float circle(vec2 uv, vec2 pos, float rad) {

    vec2 pos_diff = pos - uv;
    float theta = atan(pos_diff.y, pos_diff.x);
    float d = length(pos_diff);

	return 1. -smoothstep(rad-(rad*0.01),
                         rad+(rad*0.01),
                         d);
}

vec4 snake(vec2 uv, vec2 pos, float rad, vec3 color) {

    // Get pixel info
    vec2 pos_diff = pos - uv;
    float theta = atan(pos_diff.y, pos_diff.x);
    float d = length(pos_diff);

    // Tail smoothing
    float tail_start = radians(0. - u_time * 5.);
    float tail_end = tail_start + radians(45.);
    float tail_var = smoothstep(tail_start, tail_end, theta);
    tail_var *= 1. - step(tail_end, theta);  // no tail var past the range
    
    // Head
    float head_start = tail_end;
    float head_middle = head_start + radians(10.0);
    float head_end = head_middle + radians(5.0);
    float head_var = smoothstep(head_start, head_middle, theta)
                   - smoothstep(head_middle, head_end, theta);
    head_var *= 1. - step(head_end, theta);

    // Main wave
    float amp = 4.0;
    float period = 12.0;
    
    // Offset to get the right look
    float wave_offset = radians(270. + u_time * 150.);
    
    // Offset radian val by sine wave
    rad += sin(period * theta + wave_offset) * amp;
    
    // Get the value with the head and tail vars
    float tail_mult = 8.;
    float head_mult = 15.;
    float rad_t = rad - tail_var * tail_mult
                      + head_var * head_mult;
          
    // Apply smoothing and get value for the outer rad
	float t = 1. -smoothstep(rad_t-(rad_t*0.01),
                         rad_t+(rad_t*0.01),
                         d);

    // Inner section
    float thickness = 35.5;

    // thickness *= tail_var;

    rad -= thickness;
    rad_t = rad + (tail_var * tail_mult) - (head_var * head_mult);
	float t2 = 1. -smoothstep(rad_t-(rad_t*0.01),
                         rad_t+(rad_t*0.01),
                         d);

    // Subtract to get only within the snake
    t = t - t2;

    return vec4(color, t);
}

void main() {

	vec2 uv = gl_FragCoord.xy;
    vec2 st = gl_FragCoord.xy/u_resolution;
	vec2 center = u_resolution.xy * 0.5;

    // Background layer
	vec4 layer1 = vec4(vec3(1.), 1.0);
	
    // Snake diagram
	vec3 snake_color = vec3(0.4078, 0.5373, 0.3333);
	float radius = 0.35 * u_resolution.y;
	vec4 layer2 = snake(uv, center, radius, snake_color);

    // Drumsticks
    float drumstick_thickness = 0.035;
    float sdf = 0.5 + (st.x - 1.75*st.y)*.5;
    float is_drumstick = stroke(sdf, 0.5, drumstick_thickness);
    float sdf_inv = (st.x + 1.75*st.y)*.5;
    is_drumstick += stroke(sdf_inv, .5, drumstick_thickness);
    is_drumstick = clamp(is_drumstick, 0., 1.);

    is_drumstick *= step(0.1, st.x);
    is_drumstick *= 1. - step(0.9, st.x);
    is_drumstick *= step(0.15, st.y);

    vec4 layer3 = vec4(vec3(0.8431, 0.7412, 0.4745), is_drumstick);


	// Blend background and snake
	gl_FragColor = mix(layer1, layer2, layer2.a);

    gl_FragColor = mix(gl_FragColor, layer3, layer3.a);

}
