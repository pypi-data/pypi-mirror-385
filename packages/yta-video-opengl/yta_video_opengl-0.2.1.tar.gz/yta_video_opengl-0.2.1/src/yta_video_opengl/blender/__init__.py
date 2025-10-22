"""
The blenders, capable of mixing different inputs into
a single one by using different parameters and 
techniques.

All the classes here will have an instance of the
specific CPU and/or GPU class that is able to run the
code by using either CPU or GPU. The user can choose
between GPU and CPU and that option will be considered
(only if available).
"""
from yta_video_opengl.blender.gpu import _BlenderGPU, AlphaBlenderGPU, AddBlenderGPU, MixBlenderGPU
from yta_video_opengl.blender.cpu import _BlenderCPU, AlphaBlenderCPU, AddBlenderCPU, MixBlenderCPU
from yta_video_opengl.abstract import _ProcessorGPUAndCPU
from typing import Union

import numpy as np
import moderngl


class _Blender(_ProcessorGPUAndCPU):
    """
    *Singleton class*

    *For internal use only*

    *This class must be inherited by the specific
    implementation of some blenders that will use
    CPU or GPU (at least one of the options)*

    Class that is capable of mixing 2 different
    inputs by using the GPU or the CPU.
    """

    def __init__(
        self,
        blender_cpu: Union[_BlenderCPU, None] = None,
        blender_gpu: Union[_BlenderGPU, None] = None,
        do_use_gpu: bool = True,
    ):
        super().__init__(
            processor_cpu = blender_cpu,
            processor_gpu = blender_gpu,
            do_use_gpu = do_use_gpu
        )

    def __reinit__(
        self,
        blender_cpu: Union[_BlenderCPU, None] = None,
        blender_gpu: Union[_BlenderGPU, None] = None,
        do_use_gpu: bool = True,
    ):
        super().__reinit__(
            processor_cpu = self._processor_cpu,
            # TODO: Do we need to reinit this here (?)
            processor_gpu = self._processor_gpu,
            do_use_gpu = do_use_gpu
        )

    def process(
        self,
        base_input: Union[np.ndarray, moderngl.Texture],
        overlay_input: Union[np.ndarray, moderngl.Texture],
        mix_weight: float = 1.0,
        **kwargs
    # TODO: What about the output type (?)
    ) -> Union[np.ndarray, moderngl.Texture]:
        """
        Process the provided 'base_input' and 'overlay_input'
        with GPU or CPU according to the internal flag.

        The `mix_weight` will determine how much of the result
        we keep against the base, where a `mix_weight == 1.0`
        means that we want the result at 100%, but a
        `mix_weight == 0.4` means a 40% of the result and a 60%
        of the base.
        """
        return self._processor.process(
            base_input = base_input,
            overlay_input = overlay_input,
            mix_weight = mix_weight,
            **kwargs
        )
    
    def blend_multiple_inputs(
        self,
        inputs: list[Union[np.ndarray, moderngl.Texture]],
        mix_weights: Union[list[float], float] = 1.0,
        **kwargs
    # TODO: What about the output type (?)
    ) -> Union[np.ndarray, moderngl.Texture]:
        """
        Process the provided 'inputs' with GPU or CPU
        according to the internal flag.
        """
        return self._processor.process_multiple_inputs(
            inputs = inputs,
            mix_weights = mix_weights,
            **kwargs
        )
    
class MixBlender(_Blender):
    """
    A blender that uses a float value to mix the
    result with the original input as much as that
    value determines.
    """

    def __init__(
        self,
        do_use_gpu: bool = True
    ):
        super().__init__(
            blender_cpu = MixBlenderCPU(),
            blender_gpu = MixBlenderGPU(
                opengl_context = None,
                # TODO: Do not hardcode please...
                output_size = (1920, 1080),
            ),
            do_use_gpu = do_use_gpu
        )

    def blend(
        self,
        base_input: Union[np.ndarray, moderngl.Texture],
        overlay_input: Union[np.ndarray, moderngl.Texture],
        mix_weight: float = 1.0,
        **kwargs
    # TODO: What about the output type (?)
    ) -> Union[np.ndarray, moderngl.Texture]:
        """
        Process the provided 'base_input' and 'overlay_input'
        with GPU or CPU according to the internal flag.

        The `mix_weight` will determine how much of the result
        we keep against the base, where a `mix_weight == 1.0`
        means that we want the result at 100%, but a
        `mix_weight == 0.4` means a 40% of the result and a 60%
        of the base.
        """
        return self._processor.process(
            base_input = base_input,
            overlay_input = overlay_input,
            mix_weight = mix_weight,
            **kwargs
        )

class AlphaBlender(_Blender):
    """
    The most common blender used in video edition.

    This blender will use the alpha channel of the 
    overlay input, multiplied by the `blend_strength`
    parameter provided, to use it as the mixer factor
    between the base and the overlay inputs.
    """

    def __init__(
        self,
        do_use_gpu: bool = True
    ):
        super().__init__(
            blender_cpu = AlphaBlenderCPU(),
            blender_gpu = AlphaBlenderGPU(
                opengl_context = None,
                # TODO: Do not hardcode please...
                output_size = (1920, 1080),
            ),
            do_use_gpu = do_use_gpu
        )

    def blend(
        self,
        base_input: Union[np.ndarray, moderngl.Texture],
        overlay_input: Union[np.ndarray, moderngl.Texture],
        mix_weight: float = 1.0,
        blend_strength: float = 1.0,
        **kwargs
    # TODO: What about the output type (?)
    ) -> Union[np.ndarray, moderngl.Texture]:
        """
        Process the provided 'base_input' and 'overlay_input'
        with GPU or CPU according to the internal flag.

        The `mix_weight` will determine how much of the result
        we keep against the base, where a `mix_weight == 1.0`
        means that we want the result at 100%, but a
        `mix_weight == 0.4` means a 40% of the result and a 60%
        of the base.
        """
        return self._processor.process(
            base_input = base_input,
            overlay_input = overlay_input,
            mix_weight = mix_weight,
            blend_strength = blend_strength,
            **kwargs
        )
    
    # TODO: This method has to be reviewed in the general
    # class to be able to receive array parameters and
    # send them to the individual process as single parameter
    def blend_multiple_inputs(
        self,
        inputs: list[Union[np.ndarray, moderngl.Texture]],
        mix_weights: Union[list[float], float] = 1.0,
        blend_strengths: Union[list[float], float] = 1.0,
        **kwargs
    # TODO: What about the output type (?)
    ) -> Union[np.ndarray, moderngl.Texture]:
        """
        Process the provided 'inputs' with GPU or CPU
        according to the internal flag.
        """
        return self._processor.process_multiple_inputs(
            inputs = inputs,
            mix_weights = mix_weights,
            blend_strength = blend_strengths,
            **kwargs
        )
    
class AddBlender(_Blender):
    """
    The most common blender used in video edition.

    This blender will increase the brightness by
    combining the colors of the base and the overlay
    inputs, using the overlay as much as the 
    `stregth` parameter is indicating.
    """

    def __init__(
        self,
        do_use_gpu: bool = True
    ):
        super().__init__(
            blender_cpu = AddBlenderCPU(),
            blender_gpu = AddBlenderGPU(
                opengl_context = None,
                # TODO: Do not hardcode please...
                output_size = (1920, 1080),
            ),
            do_use_gpu = do_use_gpu
        )

    def blend(
        self,
        base_input: Union[np.ndarray, moderngl.Texture],
        overlay_input: Union[np.ndarray, moderngl.Texture],
        mix_weight: float = 1.0,
        strength: float = 1.0,
        **kwargs
    # TODO: What about the output type (?)
    ) -> Union[np.ndarray, moderngl.Texture]:
        """
        Process the provided 'base_input' and 'overlay_input'
        with GPU or CPU according to the internal flag.

        The `mix_weight` will determine how much of the result
        we keep against the base, where a `mix_weight == 1.0`
        means that we want the result at 100%, but a
        `mix_weight == 0.4` means a 40% of the result and a 60%
        of the base.
        """
        return self._processor.process(
            base_input = base_input,
            overlay_input = overlay_input,
            mix_weight = mix_weight,
            strength = strength,
            **kwargs
        )
    
    # TODO: This method has to be reviewed in the general
    # class to be able to receive array parameters and
    # send them to the individual process as single parameter
    def blend_multiple_inputs(
        self,
        inputs: list[Union[np.ndarray, moderngl.Texture]],
        mix_weights: Union[list[float], float] = 1.0,
        strengths: Union[list[float], float] = 1.0,
        **kwargs
    # TODO: What about the output type (?)
    ) -> Union[np.ndarray, moderngl.Texture]:
        """
        Process the provided 'inputs' with GPU or CPU
        according to the internal flag.
        """
        return self._processor.process_multiple_inputs(
            inputs = inputs,
            mix_weights = mix_weights,
            strengths = strengths,
            **kwargs
        )


__all__ = [
    'AlphaBlender',
    'AddBlender'
]