"""
Interesting information:
| Abrev.  | Nombre completo            | Uso principal                          |
| ------- | -------------------------- | -------------------------------------- |
| VAO     | Vertex Array Object        | Esquema de datos de vértices           |
| VBO     | Vertex Buffer Object       | Datos crudos de vértices en GPU        |
| FBO     | Frame Buffer Object        | Renderizar fuera de pantalla           |
| UBO     | Uniform Buffer Object      | Variables `uniform` compartidas        |
| EBO/IBO | Element / Index Buffer Obj | Índices para reutilizar vértices       |
| PBO     | Pixel Buffer Object        | Transferencia rápida de imágenes       |
| RBO     | Render Buffer Object       | Almacén intermedio (profundidad, etc.) |
"""
from yta_video_opengl.context import OpenGLContext
from yta_video_opengl.texture import _Textures
from yta_video_opengl.uniforms import _Uniforms
from yta_video_opengl.utils import get_fullscreen_quad_vao, _get_texture_size
from yta_validation.parameter import ParameterValidator
from yta_programming.singleton import SingletonABCMeta
from abc import abstractmethod
from typing import Union

import numpy as np
import moderngl


class _OpenGLBase(metaclass = SingletonABCMeta):
    """
    Class to be inherited by any class that is using
    OpenGL to operate, able to manage the context, the
    textures, etc.

    Make sure the that the shaders code include these
    variables:
    - `tex` (only when one shader)
    - `in_vert`
    - `in_texcoord`

    These values above are the default ones, but you
    can create custom classes and expect other values
    by setting them in the code.
    """

    @property
    def vertex_shader(
        self
    ) -> str:
        """
        The code of the vertex shader. This is, by default,
        a rectangle made by 2 triangles that will fit the
        whole screen.

        Feel free to override this method if you need 
        something more complex, but this is very useful for
        our projects.
        """
        return (
            '''
            #version 330
            in vec2 in_vert;
            in vec2 in_texcoord;
            out vec2 v_uv;

            void main() {
                v_uv = in_texcoord;
                gl_Position = vec4(in_vert, 0.0, 1.0);
            }
            '''
        )

    @property
    @abstractmethod
    def fragment_shader(
        self
    ) -> str:
        """
        The code of the fragment shader.
        """
        pass

    def __init__(
        self,
        opengl_context: Union[moderngl.Context, None],
        output_size: tuple[int, int],
        **kwargs
    ):
        """
        Provide all the variables you want to be initialized
        as uniforms at the begining for the global OpenGL
        animation in the `**kwargs`.

        The `output_size` is the size (width, height) of the
        texture that will be obtained as result. This size
        can be modified when processing a specific input, but
        be consider the cost of resources of modifying the 
        size, that will regenerate the output texture.
        """
        ParameterValidator.validate_instance_of('opengl_context', opengl_context, moderngl.Context)
        # TODO: Validate size

        self.context: moderngl.Context = (
            OpenGLContext().context
            if opengl_context is None else
            opengl_context
        )
        """
        The context of the OpenGL program.
        """
        self.output_size: tuple[int, int] = output_size
        """
        The size we want to use for the frame buffer
        in a (width, height) format.
        """

        self.reset_program_and_quad()

        self.uniforms: _Uniforms = _Uniforms(self.program)
        """
        Shortcut to the uniforms functionality.
        """
        self.textures: _Textures = _Textures(self)
        """
        Shortcut to the internal textures handler instance.
        """

        # Prepare textures
        #self._prepare_output_texture(self.output_size)
        self._prepare_input_textures()
        self._set_uniforms(**kwargs)

    def __reinit__(
        self,
        output_size: Union[tuple[int, int], None] = None,
        **kwargs
    ):
        """
        Reinitialize the output size and the uniforms
        provided, if needed, and restart the program
        and the quad to render properly.

        Giving an `output_size` that is None will not
        change it. All the keys and values provided as
        `kwargs` will be set as uniforms.
        """
        if output_size is not None:
            self.output_size = output_size

        self._set_uniforms(**kwargs)

    def reset_program_and_quad(
        self
    ) -> '_OpenGLBase':
        """
        Initialize and set the program and the quad needed
        to use the shades and render properly.

        Call this method within a test before any operation
        to make sure the quad and the program have been
        loaded correctly. This can fail due to the fact that
        the tests are isolated and we are using singleton
        instances.
        """
        # Compile shaders within the program
        self.program: moderngl.Program = self.context.program(
            vertex_shader = self.vertex_shader,
            fragment_shader = self.fragment_shader
        )

        # Create the fullscreen quad
        self.quad = get_fullscreen_quad_vao(
            context = self.context,
            program = self.program
        )

        return self

    def _set_uniforms(
        self,
        **kwargs
    ):
        """
        Set the uniforms from the **kwargs received.

        Here we set the uniforms dynamically, that are the
        initial uniforms and would be static during the
        whole rendering process. You can set or update the
        uniforms also when processing each frame if needed.

        We can define an effect with a specific parameter
        that is set here, but we can pass a dynamic `t` or
        a random value to process each frame.
        """
        for key, value in kwargs.items():
            if value is not None:
                # By now we are not setting the None variables because
                # we could be resetting values
                self.uniforms.set(key, value)

    def _prepare_output_texture(
        self,
        size: tuple[int, int]
    ) -> '_OpenGLBase':
        """
        *For internal use only*

        Set the output texture and the FBO if needed
        (the size changed or it was not set). This
        method has to be called before rendering any
        frame/texture to adapt it if needed.

        The output texture settings and the FBO will
        determine how the output result is obtained.
        """
        if (
            not hasattr(self, '_output_tex') or
            self._output_tex is None or
            self._output_tex.size != size
        ):
            self.output_size = size
            self._output_tex = self.context.texture(self.output_size, 4)
            self._output_tex.filter = (moderngl.LINEAR, moderngl.LINEAR)
            # Avoid repeating the texture and use black pixels instead
            # self._output_tex.repeat_x = False
            # self._output_tex.repeat_y = False
            self.fbo = self.context.framebuffer(color_attachments = [self._output_tex])

        return self

    def _process_common(
        self,
        textures_map: dict,
        output_size: Union[tuple[int, int], None] = None,
        **kwargs
    ) -> moderngl.Texture:
        """
        *For internal use only*

        Common and internal method to process the inputs
        and obtain the result.

        The `textures_map` is a dict to map the input
        frames to the textures, and it has to include the
        uniform texture name as the key and the method
        parameter as the value:
        - `{'texA': tex_a, 'texB': tex_b}`

        The `output_size` is the size (width, height) of the
        texture that will be obtained as result. This size
        can be modified when processing a specific input, but
        be consider the cost of resources of modifying the 
        size, that will regenerate the output texture.
        """
        if not textures_map:
            raise ValueError('At least one texture must be provided.')

        output_size = (
            # Use the 'size' of the first texture as the
            _get_texture_size(next(iter(textures_map.values())))
            if output_size is None else
            output_size
        )

        # OpenGL manages different sizes by itself
        # according to the filter (LINEAR, NEAREST, etc.)
        self._prepare_output_texture(output_size)

        self.fbo.use()
        self.context.clear(0.0, 0.0, 0.0, 1.0) # 0.0 before

        for name, tex in textures_map.items():
            self.textures.update(name, tex)

        # Set uniforms for this specific moment
        self._set_uniforms(**kwargs)

        self.quad.render()

        return self._output_tex
    
    # TODO: Overwrite this method
    def _prepare_input_textures(
        self
    ) -> '_OpenGLBase':
        """
        *For internal use only*

        *This method should be overwritten*

        Set the input texture variables and handlers
        we need to manage this. This method has to be
        called only once, just to set the slot for 
        the different textures we will use (and are
        registered as textures in the shader).
        """
        self.textures.add('base_texture', 0)

        return self

    # TODO: Overwrite this method
    def process(
        self,
        input: Union[moderngl.Texture, np.ndarray],
        output_size: Union[tuple[int, int], None] = None,
        **kwargs
    ) -> moderngl.Texture:
        """
        *This method should be overwritten*

        Apply the shader to the 'input', that
        must be a frame or a texture, and return
        the new resulting texture.

        You can provide any additional parameter
        in the **kwargs, but be careful because
        this could overwrite other uniforms that
        were previously set.

        We use and return textures to maintain
        the process in GPU and optimize it.
        """
        ParameterValidator.validate_mandatory_instance_of('input', input, [moderngl.Texture, np.ndarray])

        textures_map = {
            'base_texture': input
        }

        return self._process_common(
            textures_map = textures_map,
            output_size = output_size,
            **kwargs
        )
    
class _ProcessorGPUAndCPU(metaclass = SingletonABCMeta):
    """
    *Abstract class*

    *For internal use only*

    Abstract class to share the common behaviour of
    being able to handle a process with a GPU and/or
    a CPU processor, chosen by the user.
    """

    @property
    def is_gpu_available(
        self
    ) -> bool:
        """
        Boolean flag to indicate if the GPU is available
        or not, that means that the processor that uses
        GPU is set.
        """
        return self._processor_gpu is not None
    
    @property
    def is_cpu_available(
        self
    ) -> bool:
        """
        Boolean flag to indicate if the CPU is available
        or not, that means that the processor that uses
        CPU is set.
        """
        return self._processor_cpu is not None
    
    @property
    def _processor(
        self
    ) -> Union['_ProcessorCPU', '_ProcessorGPU']:
        """
        *For internal use only*
        
        Get the processor that must be applied to process
        the inputs according to the internal flag that
        indicates if we want to use GPU or CPU and also
        depending on the availability of these classes.
        """
        return (
            (
                # Prefer GPU if available
                self._processor_gpu or
                self._processor_cpu
            ) if self._do_use_gpu else (
                # Prefer CPU if available
                self._processor_cpu or
                self._processor_gpu
            )
        )
    
    def __init__(
        self,
        processor_cpu: Union['_ProcessorGPU', None] = None,
        processor_gpu: Union['_ProcessorCPU', None] = None,
        do_use_gpu: bool = True,
    ):
        """
        The `processor_cpu` and
        `processor_gpu` have to be set by the
        developer when building the specific classes, but
        the `do_use_gpu` boolean flag will be set by the
        user when instantiating the class to choose between
        GPU and CPU.
        """
        ParameterValidator.validate_mandatory_bool('do_use_gpu', do_use_gpu)

        if (
            processor_cpu is None and
            processor_gpu is None
        ):
            raise Exception('No node processor provided. At least one node processor is needed.')

        self._processor_cpu: Union['_ProcessorCPU', None] = processor_cpu
        """
        The transition processor that is able to do the
        processing by using the CPU. If it is None we cannot
        process it with CPU.
        """
        self._processor_gpu: Union['_ProcessorGPU', None] = processor_gpu
        """
        The transition processor that is able to do the
        processing by using the GPU. If it is None we cannot
        process it with GPU.
        """
        self._do_use_gpu: bool = do_use_gpu
        """
        Internal flag to indicate if we should use GPU,
        if True, or CPU if False.
        """

    def __reinit__(
        self,
        processor_cpu: Union['_ProcessorGPU', None] = None,
        processor_gpu: Union['_ProcessorCPU', None] = None,
        do_use_gpu: bool = True,
    ):
        if (
            processor_cpu is None and
            processor_gpu is None
        ):
            raise Exception('No node processor provided. At least one node processor is needed.')

        self._processor_cpu: Union['_ProcessorCPU', None] = processor_cpu
        self._processor_gpu: Union['_ProcessorGPU', None] = processor_gpu
        self._do_use_gpu: bool = do_use_gpu

    def use_gpu(
        self
    ) -> '_ProcessorGPUAndCPU':
        """
        Set the internal flag to use GPU if available.
        """
        self._do_use_gpu = True

    def use_cpu(
        self
    ) -> '_ProcessorGPUAndCPU':
        """
        Set the internal flag to use CPU if available.
        """
        self._do_use_gpu = False

    @abstractmethod
    def process(
        self,
        input: Union[moderngl.Texture, np.ndarray]
    ) -> Union[moderngl.Texture, np.ndarray]:
        """
        Process the provided 'input' with GPU or CPU 
        according to the internal flag.
        """
        pass

"""
Notes for the developer:

If the size of the input textures is different
than the size of the output texture, the OpenGL
system will internally modify it to make it fit
the whole texture, resizing it if necessary.

This will be done according to the sampler that
you have chosen (maybe GL_LINEAR), and the 
result quality could vary according to it. This
GL_LINEAR will apply interpolation, but NEAREST
will be faster but with less quality.

Here you have a valid example of the 2 shader parts
of a simple effect made with OpenGL. You can see the
`in_vert`, `in_texcoord` and `tex` variables:

@property
def vertex_shader(
    self
) -> str:
    return (
        '''
        #version 330
        in vec2 in_vert;
        in vec2 in_texcoord;
        out vec2 v_uv;
        void main() {
            v_uv = in_texcoord;
            gl_Position = vec4(in_vert, 0.0, 1.0);
        }
        '''
    )

@property
def fragment_shader(
    self
) -> str:
    return (
        '''
        #version 330
        uniform sampler2D tex;
        uniform float time;
        uniform float amplitude;
        uniform float frequency;
        uniform float speed;
        in vec2 v_uv;
        out vec4 f_color;
        void main() {
            float wave = sin(v_uv.x * frequency + time * speed) * amplitude;
            vec2 uv = vec2(v_uv.x, v_uv.y + wave);
            f_color = texture(tex, uv);
        }
        '''
    )
"""