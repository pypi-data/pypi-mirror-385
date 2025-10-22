"""
Nodes that modify inputs to obtain outputs but
depending on a 't' time moment to adjust it to the
time of the video in which the input (a frame of a
video) is being edited. A movement effect is not 
edited the same when we are at the begining of the
video effect than when we are at the end.
"""
from yta_video_opengl.nodes import _NodeProcessor
from yta_video_opengl.nodes.video.cpu import _VideoNodeProcessorCPU, WavingFramesVideoNodeProcessorCPU
from yta_video_opengl.nodes.video.gpu import _VideoNodeProcessorGPU, BreathingFrameVideoNodeProcessorGPU, WavingFramesVideoNodeProcessorGPU
from typing import Union

import numpy as np
import moderngl


class _VideoNodeProcessor(_NodeProcessor):
    """
    *Abstract class*
    
    *Singleton class*

    *For internal use only*

    *This class must be inherited by the specific
    implementation of some effect that will be done by
    CPU or GPU (at least one of the options)*

    Class that is capable of doing some processing on
    an input by using the GPU or the CPU, but for 
    video frames, including a `t` time moment parameter
    when processing.
    """

    def __init__(
        self,
        video_node_processor_cpu: Union[_VideoNodeProcessorCPU, None] = None,
        video_node_processor_gpu: Union[_VideoNodeProcessorGPU, None] = None,
        do_use_gpu: bool = True,
    ):
        """
        The `video_node_processor_cpu` and `video_node_processor_gpu`
        have to be set by the developer when building the specific
        classes, but the `do_use_gpu` boolean flag will be set
        by the user when instantiating the class to choose 
        between GPU and CPU.
        """
        # TODO: Validate that are '_VideoNodeProcessorCPU'
        # and '_VideoNodeProcessorGPU' subclasses
        super().__init__(
            node_processor_cpu = video_node_processor_cpu,
            node_processor_gpu = video_node_processor_gpu,
            do_use_gpu = do_use_gpu
        )

    def __reinit__(
        self,
        video_node_processor_cpu: Union[_VideoNodeProcessorCPU, None] = None,
        video_node_processor_gpu: Union[_VideoNodeProcessorGPU, None] = None,
        do_use_gpu: bool = True,
    ):
        super().__reinit__(
            node_processor_cpu = video_node_processor_cpu,
            node_processor_gpu = video_node_processor_gpu,
            do_use_gpu = do_use_gpu
        )

    def process(
        self,
        input: Union[np.ndarray, moderngl.Texture],
        t: float,
        **kwargs
    ) -> Union[np.ndarray, moderngl.Texture]:
        """
        Process the provided 'input' with GPU or CPU 
        according to the internal flag.
        """
        return self._processor.process(
            input = input,
            t = t,
            **kwargs
        )
    
class BreathingFrameVideoNodeProcessor(_VideoNodeProcessor):
    """
    The frame but as if it was breathing.
    """

    def __init__(
        self,
        do_use_gpu: bool = True,
        zoom: float = 0.05
    ):
        super().__init__(
            video_node_processor_cpu = None,
            video_node_processor_gpu = BreathingFrameVideoNodeProcessorGPU(
                opengl_context = None,
                # TODO: Do not hardcode please...
                output_size = (1920, 1080),
                zoom = zoom
            ),
            do_use_gpu = do_use_gpu
        )

    def __reinit__(
        self,
        do_use_gpu: bool = True,
        zoom: Union[float, None] = None
    ):
        super().__init__(
            video_node_processor_cpu = self._processor_cpu,
            # TODO: Reset it to reload the uniforms
            
            video_node_processor_gpu =  BreathingFrameVideoNodeProcessorGPU(
                opengl_context = None,
                output_size = None,
                zoom = zoom
            ),
            do_use_gpu = do_use_gpu
        )

class WavingFramesVideoNodeProcessor(_VideoNodeProcessor):
    """
    A video frame that is moving like a wave.
    """

    def __init__(
        self,
        do_use_gpu: bool = True,
        amplitude: float = 0.05,
        frequency: float = 10.0,
        speed: float = 2.0,
    ):
        super().__init__(
            video_node_processor_cpu = WavingFramesVideoNodeProcessorCPU(
                amplitude = amplitude,
                frequency = frequency,
                speed = speed
            ),
            video_node_processor_gpu = WavingFramesVideoNodeProcessorGPU(
                opengl_context = None,
                # TODO: Do not hardcode please...
                output_size = (1920, 1080),
                amplitude = amplitude,
                frequency = frequency,
                speed = speed
            ),
            do_use_gpu = do_use_gpu
        )

    def __reinit__(
        self,
        do_use_gpu: bool = True,
        amplitude: Union[float, None] = None,
        frequency: Union[float, None] = None,
        speed: Union[float, None] = None,
    ):
        super().__reinit__(
            video_node_processor_cpu = self._processor_cpu,
            # TODO: Reset it to reload the uniforms
            video_node_processor_gpu = WavingFramesVideoNodeProcessorGPU(
                opengl_context = None,
                output_size = None,
                amplitude = amplitude,
                frequency = frequency,
                speed = speed
            ),
            do_use_gpu = do_use_gpu
        )