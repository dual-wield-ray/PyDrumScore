
vec3 rgb(float r, float g, float b) {
	return vec3(r / 255.0, g / 255.0, b / 255.0);
}


vec4 circle(vec2 uv, vec2 pos, float rad, vec3 color) {

    vec2 pos_diff = pos - uv;
    float theta = atan(pos_diff.y, pos_diff.x);
    float d = length(pos_diff);
    
    theta += radians(22.5);

    // Tail smoothing
    float tail_var = smoothstep(0., radians(15.), theta);
    tail_var *= 1. - step(radians(15.), theta);
    
    // Head
    float head_var = smoothstep(radians(15.), radians(20.), theta);
    head_var -= smoothstep(radians(20.), radians(25.), theta);
    head_var *= 1. - step(radians(25.), theta);


    float amp = 3.0;
    float period = 12.0;
    rad += sin(period * theta) * amp;
    
    float rad_t = rad - tail_var * 5. + head_var * 10.;
          
	float t = 1. -smoothstep(rad_t-(rad_t*0.01),
                         rad_t+(rad_t*0.01),
                         d);

    rad -= 17.5;
    rad_t = rad + tail_var * 5. - head_var * 10.;
	float t2 = 1. -smoothstep(rad_t-(rad_t*0.01),
                         rad_t+(rad_t*0.01),
                         d);

    t = 1.0 - (t - t2);
          
    return vec4(color, 1.0 - t);
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
