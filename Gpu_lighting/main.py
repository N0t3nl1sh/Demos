import moderngl
import struct

# Create a context without an existing window
ctx = moderngl.create_context(standalone=True)

with open("test.vert", "r") as f:
    vertex_shader_source = f.read()

program = ctx.program(vertex_shader=vertex_shader_source,
                   # what we want to export to the buffer
                   varyings=["v_color"])

VERT_COUNT = 10


# We always need a vertex array in order to execute a shader program.
# Our shader doesn't have any buffer inputs, so we give it an empty array.
vao = ctx.vertex_array(program, [])

# Create a buffer allocating room for 20 32 bit floats
# num of vertices (10) * num of varyings per vertex (2) * size of float in bytes (4)
buffer = ctx.buffer(reserve=VERT_COUNT * 2 * 4)

# Start a transform with buffer as the destination.
# We force the vertex shader to run 10 times
vao.transform(buffer, vertices=VERT_COUNT)

# Unpack the 20 float values from the buffer (copy from graphics memory to system memory).
# Reading from the buffer will cause a sync (the python program stalls until the shader is done)
data = struct.unpack("20f", buffer.read())
for i in range(0, 20, 2):
    print("value = {}, product = {}".format(*data[i:i+2]))
