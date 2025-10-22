"""
The nodes that modify inputs by using static parameters
and not 't' time moments, with GPU.
"""
from yta_video_opengl.abstract import _OpenGLBase
from yta_validation.parameter import ParameterValidator
from typing import Union

import numpy as np
import moderngl


class _NodeProcessorGPU(_OpenGLBase):
    """
    *Singleton class*

    *For internal use only*
    
    Class to represent a node processor that uses GPU
    to transform the input.

    The basic class of a node to manipulate frames as
    opengl textures. This node will process the frame
    as an input texture and will generate also a
    texture as the output.

    Nodes can be chained and the result from one node
    can be applied on another node.
    """

    # TODO: Do we really need this class just to add
    # one step on the hierarchy? It is to differentiate
    # between any class that uses OpenGL on the base
    # from the ones that are nodes to process and to
    # be added to a general NodeProcessor class
    
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
        super().__init__(
            opengl_context = opengl_context,
            output_size = output_size,
            **kwargs
        )

    def __reinit__(
        self,
        opengl_context: Union[moderngl.Context, None] = None,
        output_size: Union[tuple[int, int], None] = None,
        **kwargs
    ):
        # TODO: We ignore the 'opengl_context' as we don't need
        # to reset it
        super().__reinit__(
            output_size = output_size,
            **kwargs
        )

class SelectionMaskProcessorGPU(_NodeProcessorGPU):
    """
    Class to use a mask selection (from which we will
    read the red color to determine if the pixel must
    be applied or not) to apply the `processed_texture`
    on the `original_texture`.

    If the selection mask is completely full, the
    result will be the `processed_texture`.
    """
    
    @property
    def fragment_shader(
        self
    ):
        return (
            '''
            #version 330

            uniform sampler2D original_texture;
            uniform sampler2D processed_texture;
            // White = apply, black = ignore
            uniform sampler2D selection_mask_texture;
            in vec2 v_uv;
            out vec4 output_color;

            void main() {
                vec4 original_color = texture(original_texture, v_uv);
                vec4 processed_color = texture(processed_texture, v_uv);
                // We use the red as the value
                float mask = texture(selection_mask_texture, v_uv).r; 

                output_color = mix(original_color, processed_color, mask);
            }
            '''
        )
    
    def _prepare_input_textures(
        self
    ) -> '_OpenGLBase':
        """
        *For internal use only*

        Set the input texture variables and handlers
        we need to manage this. This method has to be
        called only once, just to set the slot for 
        the different textures we will use (and are
        registered as textures in the shader).
        """
        self.textures.add('original_texture', 0)
        self.textures.add('processed_texture', 1)
        self.textures.add('selection_mask_texture', 2)

        return self

    def process(
        self,
        original_input: Union[moderngl.Texture, np.ndarray],
        processed_input: Union[moderngl.Texture, np.ndarray],
        selection_mask_input: Union[moderngl.Texture, np.ndarray],
        output_size: Union[tuple[int, int], None] = None,
        **kwargs
    ) -> moderngl.Texture:
        """
        Mix the `processed_input` with the 
        `original_input` as the `selecction_mask_input`
        says.

        You can provide any additional parameter
        in the **kwargs, but be careful because
        this could overwrite other uniforms that
        were previously set.

        We use and return textures to maintain
        the process in GPU and optimize it.
        """
        ParameterValidator.validate_mandatory_instance_of('original_input', original_input, [moderngl.Texture, np.ndarray])
        ParameterValidator.validate_mandatory_instance_of('processed_input', processed_input, [moderngl.Texture, np.ndarray])
        ParameterValidator.validate_mandatory_instance_of('selection_mask_input', selection_mask_input, [moderngl.Texture, np.ndarray])

        textures_map = {
            'original_texture': original_input,
            'processed_texture': processed_input,
            'selection_mask_texture': selection_mask_input
        }

        return self._process_common(
            textures_map = textures_map,
            output_size = output_size,
            **kwargs
        )