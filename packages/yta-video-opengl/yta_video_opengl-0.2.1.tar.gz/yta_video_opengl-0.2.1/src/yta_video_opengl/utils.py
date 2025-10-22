from yta_validation import PythonValidator
from yta_programming.decorators.requires_dependency import requires_dependency
from typing import Union

import numpy as np
import moderngl


def frame_to_texture(
    frame: Union['VideoFrame', 'np.ndarray'],
    context: moderngl.Context,
    numpy_format: str = 'rgb24'
):
    """
    Transform the given 'frame' to an opengl
    texture. The frame can be a VideoFrame
    instance (from pyav library) or a numpy
    array.

    (!) This method is useful to transform a
    frame into a texture quick and for a single
    use, but we have the GPUTextureHandler class
    to handle it in an specific contexto to 
    optimize the performance and avoid creating
    textures but rewriting on them.
    """
    # To numpy RGB inverted for opengl
    frame: np.ndarray = (
        np.flipud(frame.to_ndarray(format = numpy_format))
        if PythonValidator.is_instance_of(frame, 'VideoFrame') else
        np.flipud(frame)
    )

    # Sometimes we have 'float32' values but we need to
    # force 'uint8' to be able to work with
    if frame.dtype != np.uint8:
        frame = np.clip(frame, 0, 255).astype(np.uint8)

    return context.texture(
        size = (frame.shape[1], frame.shape[0]),
        components = frame.shape[2],
        data = frame.tobytes()
    )

# TODO: I should make different methods to
# obtain a VideoFrame or a numpy array frame
def texture_to_frame(
    texture: moderngl.Texture,
    do_include_alpha: bool = True
) -> np.ndarray:
    """
    Transform an opengl texture into numpy array.

    The `do_include_alpha` will include the
    alpha channel if True.
    """
    data = texture.read(alignment = 1)
    # Read 4 channels always (RGBA8)
    frame = np.frombuffer(data, dtype = np.uint8).reshape((texture.size[1], texture.size[0], 4))
    # TODO: Do this with a utils
    frame = (
        frame
        if do_include_alpha else
        # Discard alpha channel if not needed
        frame[:, :, :3]
    )
    # Opengl gives it with the 'y' inverted
    frame = np.flipud(frame)
    # TODO: This can be returned as a numpy frame

    # This is if we need an 'av' VideoFrame (to
    # export through the demuxer, for example)
    # TODO: I avoid this by now because we don't
    # want to import the pyav library, so this
    # below has to be done with the numpy array
    # received...
    # frame = av.VideoFrame.from_ndarray(frame, format = 'rgba')
    # # TODO: Make this customizable
    # frame = frame.reformat(format = 'yuv420p')

    return frame

# TODO: The code of this one is similar to the
# 'texture_to_frame', so we should keep only one
# (maybe this one)
def texture_to_numpy(
    texture: moderngl.Texture,
    do_include_alpha: bool = True
) -> np.ndarray:
    """
    Transform the provided OpenGL `texture` into a numpy
    array to be able to validate the values that are
    contained in the texture.

    The alpha layer will be removed if the parameter
    `do_include_alpha` is set as False.
    """
    data = texture.read()

    # OpenGL uses only f4 and u1 for the textures so
    # we don't need a mapping
    dtype = (
        np.float32
        if texture.dtype == 'f4' else
        np.uint8
    )

    frame = np.frombuffer(
        buffer = data,
        dtype = dtype
    ).reshape(
        texture.height,
        texture.width,
        texture.components
    )

    # Discard alpha channel if not needed
    frame = (
        frame
        if do_include_alpha else
        frame[:, :, :3]
    )

    # Opengl gives it with the 'y' inverted
    frame = np.flipud(frame)

    return frame

def _get_texture_size(
    texture: Union[moderngl.Texture, np.ndarray]
):
    """
    *For internal use only*

    Get the (width, height) of a texture, regardless of
    whether it's a moderngl.Texture or a numpy.ndarray.
    """
    if PythonValidator.is_instance_of(texture, moderngl.Texture):
        return texture.size
    elif PythonValidator.is_numpy_array(texture):
        h, w = texture.shape[:2]
        return (w, h)
    else:
        raise Exception('The "texture" provided is not a moderngl.Texture nor a np.ndarray.')

def get_fullscreen_quad_vao(
    context: moderngl.Context,
    program: moderngl.Program
) -> moderngl.VertexArray:
    """
    Get the vertex array object of a quad, by
    using the vertices, the indexes, the vbo,
    the ibo and the vao content.
    """
    # Quad vertices in NDC (-1..1) with texture
    # coords (0..1)
    """
    The UV coordinates to build the quad we
    will use to represent the frame by 
    applying it as a texture.
    """
    vertices = np.array(
        object = [
            # pos.x, pos.y, tex.u, tex.v
            -1.0, -1.0, 0.0, 0.0,  # vertex 0 - bottom left
            1.0, -1.0, 1.0, 0.0,  # vertex 1 - bottom right
            -1.0,  1.0, 0.0, 1.0,  # vertex 2 - top left
            1.0,  1.0, 1.0, 1.0,  # vertex 3 - top right
        ],
        dtype = 'f4'
    )

    """
    The indexes of the vertices (see 'vertices'
    property) to build the 2 opengl triangles
    that will represent the quad we need for
    the frame.
    """
    indices = np.array(
        object = [
            0, 1, 2,
            2, 1, 3
        ],
        dtype = 'i4'
    )

    vbo = context.buffer(vertices.tobytes())
    ibo = context.buffer(indices.tobytes())

    vao_content = [
        # TODO: This is the reason of needing 'in_vert'
        # and 'in_texcoord' variables set in our shaders
        # 2 floats position, 2 floats texcoords
        (vbo, '2f 2f', 'in_vert', 'in_texcoord'),
    ]

    return context.vertex_array(program, vao_content, ibo)

# TODO: I think I have this methods in other library
# maybe yta-image-utils (?)
@requires_dependency('cv2', 'yta_video_opengl', 'opencv-python')
def scale_numpy(
    input: np.ndarray,
    size: tuple[int, int]
) -> np.ndarray:
    """
    *Optional dependency `opencv-python` required*

    Resize the 'input' numpy array to the provided 'size'
    if needed, using a rescaling method with 'opencv-python'
    (cv2).

    The 'size' provided must be (width, height).
    """
    import cv2

    return cv2.resize(input, size, interpolation = cv2.INTER_LINEAR)

@requires_dependency('PIL', 'yta_video_opengl', 'pillow')
def scale_numpy_pillow(
    input: np.ndarray,
    size: tuple[int, int]
) -> np.ndarray:
    """
    *Optional dependency `pillow` (imported as `PIL`) required*

    Resize the 'input' numpy array to the provided 'size'
    if needed, using a rescaling method with 'pillow'
    (PIL).

    The 'size' provided must be (width, height).
    """
    from PIL import Image

    return np.array(Image.fromarray(input).resize(size, Image.BILINEAR))

@requires_dependency('PIL', 'yta_video_opengl', 'pillow')
def read_image_as_numpy(
    path: str,
    do_read_as_rgba: bool = True,
    size: Union[tuple[int, int], None] = None
) -> np.ndarray:
    """
    *Optional dependency `pillow` (imported as `PIL`) required*

    Read an image from a file and transform it into a
    numpy array. It will force the 'size' if provided,
    or leave the original one if it is None.
    """
    from PIL import Image

    mode = (
        'RGBA'
        if do_read_as_rgba else
        'RGB'
    )

    with Image.open(path) as img:
        img = img.convert(mode)
        np_img = np.array(img, dtype = np.uint8)

    return (
        scale_numpy_pillow(
            input = np_img,
            size = size
        ) if size is not None else
        np_img
    )

@requires_dependency('PIL', 'yta_video_opengl', 'pillow')
def numpy_to_file(
    input: np.ndarray,
    output_filename: str
) -> str:
    """
    *Optional dependency `pillow` (imported as `PIL`) required*

    Export the provided 'array' numpy array as a file
    with the given 'output_filename' name.
    """
    from PIL import Image

    Image.fromarray(input).save(output_filename)

    return output_filename

@requires_dependency('PIL', 'yta_video_opengl', 'pillow')
def texture_to_file(
    texture: 'moderngl.Texture',
    output_filename: str
) -> str:
    """
    *Optional dependency `pillow` (imported as `PIL`) required*

    Export the provided OpenGL texture 'texture' as a
    file with the given 'output_filename' name.
    """
    return numpy_to_file(
        input = texture_to_frame(texture),
        output_filename = output_filename
    )