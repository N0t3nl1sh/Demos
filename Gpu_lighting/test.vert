#version 430

// Output values for the shader. They end up in the buffer.
out float value;
out float product;

void main() {
        // Implicit type conversion from int to float will happen here
        value = gl_VertexID;
        product = gl_VertexID * gl_VertexID;
    }