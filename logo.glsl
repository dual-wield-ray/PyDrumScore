
vec3 rgb(float r, float g, float b) {
	return vec3(r / 255.0, g / 255.0, b / 255.0);
}


vec4 circle(vec2 uv, vec2 pos, float rad, vec3 color) {

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
    float head_middle = radians(20.0);
    float head_end = radians(25.0);
    float head_var = smoothstep(head_start, head_middle, theta);
    head_var -= smoothstep(head_middle, head_end, theta);
    head_var *= 1. - step(head_end, theta);

    // Main wave
    float amp = 3.0;
    float period = 12.0;
    
    // Offset to get the right look
    float wave_offset = radians(270.);
    
    // Offset radian val by sine wave
    rad += sin(period * theta + wave_offset) * amp;
    
    // Get the value with the head and tail vars
    float tail_mult = 5.;
    float head_mult = 10.0;
    float rad_t = rad - tail_var * tail_mult
                      + head_var * head_mult;
          
    // Apply smoothing and get value for the outer rad
	float t = 1. -smoothstep(rad_t-(rad_t*0.01),
                         rad_t+(rad_t*0.01),
                         d);

    // Inner section
    float thickness = 17.5;
    rad -= thickness;
    rad_t = rad + tail_var * tail_mult - head_var * head_mult;
	float t2 = 1. -smoothstep(rad_t-(rad_t*0.01),
                         rad_t+(rad_t*0.01),
                         d);

    // Subtract to get only within the snake
    t = t - t2;
          
    return vec4(color, t);
}

void mainImage( out vec4 fragColor, in vec2 fragCoord ) {

	vec2 uv = fragCoord.xy;
	vec2 center = iResolution.xy * 0.5;
    
	float radius = 0.25 * iResolution.y;

    // Background layer
	vec4 layer1 = vec4(rgb(245., 245., 220.), 1.0);
	
	// Circle
	vec3 red = rgb(183., 183., 52.);
	vec4 layer2 = circle(uv, center, radius, red);
	
	// Blend the two
	fragColor = mix(layer1, layer2, layer2.a);

}
