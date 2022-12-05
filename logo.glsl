#define PI 3.1415926538
#ifdef GL_ES
precision mediump float;
#endif

uniform vec2 u_resolution;

float stroke(float x, float s, float w){
    float d = step(s, x+w*.5)
            - step(s, x-w*.5);

    return clamp(d, 0., 1.);
}

vec3 rgb(float r, float g, float b) {
	return vec3(r / 255.0, g / 255.0, b / 255.0);
}

float circle(vec2 uv, vec2 pos, float rad) {

    vec2 pos_diff = pos - uv;
    float theta = atan(pos_diff.y, pos_diff.x);
    float d = length(pos_diff);

	return 1. -smoothstep(rad-(rad*0.01),
                         rad+(rad*0.01),
                         d);
}

vec4 snake(vec2 uv, vec2 pos, float rad, vec3 color, vec3 inside_col) {

    vec2 pos_diff = pos - uv;
    float theta = atan(pos_diff.y, pos_diff.x);
    float d = length(pos_diff);

    // Tail smoothing
    float tail_start = radians(0.);
    float tail_end = radians(15.);
    float tail_var = smoothstep(tail_start, tail_end, theta);
    tail_var *= 1. - step(tail_end, theta);  // no tail var past the range
    
    // Head
    float head_start = tail_end;
    float head_middle = radians(25.0);
    float head_end = radians(35.0);
    float head_var = smoothstep(head_start, head_middle, theta);
    head_var -= smoothstep(head_middle, head_end, theta);
    head_var *= 1. - step(head_end, theta);

    // Main wave
    float amp = 2.0;
    float period = 12.0;
    
    // Offset to get the right look
    float wave_offset = radians(270.);
    
    // Offset radian val by sine wave
    rad += sin(period * theta + wave_offset) * amp;
    
    // Get the value with the head and tail vars
    float tail_mult = 5.;
    float head_mult = 7.0;
    float rad_t = rad - tail_var * tail_mult
                      + head_var * head_mult;
          
    // Apply smoothing and get value for the outer rad
	float t = 1. -smoothstep(rad_t-(rad_t*0.01),
                         rad_t+(rad_t*0.01),
                         d);

    // Inner section
    float thickness = 25.5;
    rad -= thickness;
    rad_t = rad + tail_var * tail_mult - head_var * head_mult;
	float t2 = 1. -smoothstep(rad_t-(rad_t*0.01),
                         rad_t+(rad_t*0.01),
                         d);

    // Subtract to get only within the snake
    //t = t - t2;
          
    vec3 res_color = mix(color, inside_col, t * t2);

    return vec4(res_color, t);
}

void main() {

	vec2 uv = gl_FragCoord.xy;
	vec2 center = u_resolution.xy * 0.5;
    
	float radius = 0.35 * u_resolution.y;

    // Background layer
	vec4 layer1 = vec4(rgb(255., 255., 255.), 1.0);
	
	vec3 snake_color = vec3(0.643,0.643,0.643);
    vec3 inside_color = vec3(1.,1.,1.);
	vec4 layer2 = snake(uv, center, radius, snake_color, inside_color);
	
    // Middle circle
    float middle_rad = u_resolution.y * 0.285;
    float in_middle = circle(uv, center, middle_rad);
    vec3 middle_color = vec3(0.89,0.855,0.788);
    vec4 layer3 = vec4(middle_color, 1.);

	// Blend the two
	gl_FragColor = mix(layer1, layer2, layer2.a);

}
