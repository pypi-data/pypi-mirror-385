"""
The transitions module, with all the classes that
are able to process transitions by using CPU, GPU
or both.

All the classes here will have an instance of the
specific CPU and/or GPU class that is able to run
the code by using either CPU or GPU. The user can
choose between GPU and CPU and that option will be
considered (only if available).

Note for the developer:
A class must have, at least, one specific 
processor (GPU is prefered).
"""
from yta_video_opengl.nodes.video.transitions.cpu import _TransitionProcessorCPU, SlideTransitionProcessorCPU
from yta_video_opengl.nodes.video.transitions.gpu import _TransitionProcessorGPU, SlideTransitionProcessorGPU, CrossfadeTransitionProcessorGPU, DistortedCrossfadeTransitionProcessorGPU, AlphaPediaMaskTransitionProcessorGPU, CircleClosingTransitionProcessorGPU, CircleOpeningTransitionProcessorGPU, BarsFallingTransitionProcessorGPU
from yta_video_opengl.abstract import _ProcessorGPUAndCPU
from typing import Union

import numpy as np
import moderngl


class _TransitionProcessor(_ProcessorGPUAndCPU):
    """
    *Abstract class*
    
    *Singleton class*

    *For internal use only*

    *This class must be inherited by the specific
    implementation of some transition that will be
    done by CPU or GPU (at least one of the options)*

    Class that is capable of doing some processing on
    an input by using the GPU or the CPU.
    """

    def __init__(
        self,
        transition_processor_cpu: Union[_TransitionProcessorCPU, None] = None,
        transition_processor_gpu: Union[_TransitionProcessorGPU, None] = None,
        do_use_gpu: bool = True,
    ):
        """
        The `transition_processor_cpu` and
        `transition_processor_gpu` have to be set by the
        developer when building the specific classes, but
        the `do_use_gpu` boolean flag will be set by the
        user when instantiating the class to choose between
        GPU and CPU.
        """
        super().__init__(
            processor_cpu = transition_processor_cpu,
            processor_gpu = transition_processor_gpu,
            do_use_gpu = do_use_gpu
        )

    def process(
        self,
        first_input: Union[moderngl.Texture, np.ndarray],
        second_input: Union[moderngl.Texture, np.ndarray],
        progress: float
    ) -> Union[moderngl.Texture, np.ndarray]:
        """
        Process the transition between the given `first_input`
        and `second_input`, with GPU or CPU according to the
        internal flag.
        """
        return self._processor.process(
            first_input = first_input,
            second_input = second_input,
            progress = progress,
        )
    
class SlideTransitionProcessor(_TransitionProcessor):
    """
    A transition in which the frames goes from one
    side to the other, disappearing the first one
    and appearing the second one.

    Class that is capable of doing some processing on
    an input by using the GPU or the CPU.
    """

    def __init__(
        self,
        do_use_gpu: bool = True,
        # TODO: Review this
        output_size: tuple[int, int] = (1920, 1080)
    ):
        """
        The `transition_processor_cpu` and
        `transition_processor_gpu` have to be set by the
        developer when building the specific classes, but
        the `do_use_gpu` boolean flag will be set by the
        user when instantiating the class to choose between
        GPU and CPU.
        """
        super().__init__(
            transition_processor_cpu = SlideTransitionProcessorCPU(),
            transition_processor_gpu = SlideTransitionProcessorGPU(
                opengl_context = None,
                output_size = output_size
            ),
            do_use_gpu = do_use_gpu
        )

class CrossfadeTransitionProcessor(_TransitionProcessor):
    """
    A transition between the frames of 2 videos,
    transforming the first one into the second one.

    Class that is capable of doing some processing on
    an input by using the GPU or the CPU.
    """

    def __init__(
        self,
        do_use_gpu: bool = True,
        # TODO: Review this
        output_size: tuple[int, int] = (1920, 1080)
    ):
        """
        The `transition_processor_cpu` and
        `transition_processor_gpu` have to be set by the
        developer when building the specific classes, but
        the `do_use_gpu` boolean flag will be set by the
        user when instantiating the class to choose between
        GPU and CPU.
        """
        super().__init__(
            transition_processor_cpu = None,
            transition_processor_gpu = CrossfadeTransitionProcessorGPU(
                opengl_context = None,
                output_size = output_size
            ),
            do_use_gpu = do_use_gpu
        )

class DistortedCrossfadeTransitionProcessor(_TransitionProcessor):
    """
    A transition between the frames of 2 videos,
    transforming the first one into the second one
    with a distortion in between.

    Class that is capable of doing some processing on
    an input by using the GPU or the CPU.
    """

    def __init__(
        self,
        do_use_gpu: bool = True,
        # TODO: Review this
        output_size: tuple[int, int] = (1920, 1080)
    ):
        """
        The `transition_processor_cpu` and
        `transition_processor_gpu` have to be set by the
        developer when building the specific classes, but
        the `do_use_gpu` boolean flag will be set by the
        user when instantiating the class to choose between
        GPU and CPU.
        """
        super().__init__(
            transition_processor_cpu = None,
            transition_processor_gpu = DistortedCrossfadeTransitionProcessorGPU(
                opengl_context = None,
                output_size = output_size
            ),
            do_use_gpu = do_use_gpu
        )

class AlphaPediaMaskTransitionProcessor(_TransitionProcessor):
    """
    A transition made by using a custom mask to
    join the 2 videos. This mask is specifically
    obtained from the AlphaPediaYT channel in which
    we upload specific masking videos.

    Both videos will be placed occupying the whole
    scene, just overlapping by using the transition
    video mask, but not moving the frame through 
    the screen like other classes do (like the
    FallingBars).

    Class that is capable of doing some processing on
    an input by using the GPU or the CPU.
    """

    def __init__(
        self,
        do_use_gpu: bool = True,
        # TODO: Review this
        output_size: tuple[int, int] = (1920, 1080),
    ):
        """
        The `transition_processor_cpu` and
        `transition_processor_gpu` have to be set by the
        developer when building the specific classes, but
        the `do_use_gpu` boolean flag will be set by the
        user when instantiating the class to choose between
        GPU and CPU.
        """
        super().__init__(
            transition_processor_cpu = None,
            transition_processor_gpu = AlphaPediaMaskTransitionProcessorGPU(
                opengl_context = None,
                output_size = output_size
            ),
            do_use_gpu = do_use_gpu
        )

    def process(
        self,
        first_input: Union[moderngl.Texture, np.ndarray],
        second_input: Union[moderngl.Texture, np.ndarray],
        mask_input: Union[moderngl.Texture, np.ndarray],
        progress: float
    ) -> Union[moderngl.Texture, np.ndarray]:
        """
        Process the transition between the given `first_input`
        and `second_input`, with GPU or CPU according to the
        internal flag.
        """
        return self._processor.process(
            first_input = first_input,
            second_input = second_input,
            mask_input = mask_input,
            progress = progress,
        )
    
class CircleOpeningTransitionProcessor(_TransitionProcessor):
    """
    A transition between the frames of 2 videos in
    which the frames are mixed by generating a circle
    that grows from the middle to end fitting the 
    whole screen.

    Class that is capable of doing some processing on
    an input by using the GPU or the CPU.
    """

    def __init__(
        self,
        do_use_gpu: bool = True,
        # TODO: Review this
        output_size: tuple[int, int] = (1920, 1080),
        border_smoothness: float = 0.02
    ):
        """
        The `transition_processor_cpu` and
        `transition_processor_gpu` have to be set by the
        developer when building the specific classes, but
        the `do_use_gpu` boolean flag will be set by the
        user when instantiating the class to choose between
        GPU and CPU.
        """
        super().__init__(
            transition_processor_cpu = None,
            transition_processor_gpu = CircleOpeningTransitionProcessorGPU(
                opengl_context = None,
                output_size = output_size,
                border_smoothness = border_smoothness
            ),
            do_use_gpu = do_use_gpu
        )

class CircleClosingTransitionProcessor(_TransitionProcessor):
    """
    A transition between the frames of 2 videos in
    which the frames are mixed by generating a circle
    that grows from the middle to end fitting the 
    whole screen.

    Class that is capable of doing some processing on
    an input by using the GPU or the CPU.
    """

    def __init__(
        self,
        do_use_gpu: bool = True,
        # TODO: Review this
        output_size: tuple[int, int] = (1920, 1080),
        border_smoothness: float = 0.02
    ):
        """
        The `transition_processor_cpu` and
        `transition_processor_gpu` have to be set by the
        developer when building the specific classes, but
        the `do_use_gpu` boolean flag will be set by the
        user when instantiating the class to choose between
        GPU and CPU.
        """
        super().__init__(
            transition_processor_cpu = None,
            transition_processor_gpu = CircleClosingTransitionProcessorGPU(
                opengl_context = None,
                output_size = output_size,
                border_smoothness = border_smoothness
            ),
            do_use_gpu = do_use_gpu
        )

class BarsFallingTransitionProcessor(_TransitionProcessor):
    """
    A transition between the frames of 2 videos in which
    a set of bars fall with the first video to let the
    second one be seen.

    Class that is capable of doing some processing on
    an input by using the GPU or the CPU.
    """

    def __init__(
        self,
        do_use_gpu: bool = True,
        # TODO: Review this
        output_size: tuple[int, int] = (1920, 1080),
        number_of_bars: int = 30,
        amplitude: float = 2,
        noise: float = 0.1,
        frequency: float = 0.5,
        drip_scale: float = 0.5,
    ):
        """
        The `transition_processor_cpu` and
        `transition_processor_gpu` have to be set by the
        developer when building the specific classes, but
        the `do_use_gpu` boolean flag will be set by the
        user when instantiating the class to choose between
        GPU and CPU.
        """
        super().__init__(
            transition_processor_cpu = None,
            transition_processor_gpu = BarsFallingTransitionProcessorGPU(
                opengl_context = None,
                output_size = output_size,
                number_of_bars = number_of_bars,
                amplitude = amplitude,
                noise = noise,
                frequency = frequency,
                drip_scale = drip_scale
            ),
            do_use_gpu = do_use_gpu
        )