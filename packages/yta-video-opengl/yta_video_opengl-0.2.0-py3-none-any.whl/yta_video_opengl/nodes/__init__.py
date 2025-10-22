"""
Nodes that modify inputs to obtain outputs but
depending not on a 't' time moment but just with
static parameters.

Check the video module to see the video nodes
that are specialized in editing video frames.
"""
from yta_video_opengl.nodes.cpu import _NodeProcessorCPU, SelectionMaskProcessorCPU
from yta_video_opengl.nodes.gpu import _NodeProcessorGPU, SelectionMaskProcessorGPU
from yta_video_opengl.abstract import _ProcessorGPUAndCPU
from typing import Union

import numpy as np
import moderngl


"""
The implementations below are nodes that don't
need any 't' time moment to operate but only
static parameters that will modify the input
and generate a new output.

For nodes that work with 't' time moments check
the _VideoNodeProcessor class.
"""
class _NodeProcessor(_ProcessorGPUAndCPU):
    """
    *Abstract class*
    
    *Singleton class*

    *For internal use only*

    *This class must be inherited by the specific
    implementation of some effect that will be done by
    CPU or GPU (at least one of the options)*

    Class that is capable of doing some processing on
    an input by using the GPU or the CPU.
    """

    def __init__(
        self,
        node_processor_cpu: Union[_NodeProcessorCPU, None] = None,
        node_processor_gpu: Union[_NodeProcessorGPU, None] = None,
        do_use_gpu: bool = True,
    ):
        """
        The `node_processor_cpu` and `node_processor_gpu` have
        to be set by the developer when building the specific
        classes, but the `do_use_gpu` boolean flag will be set
        by the user when instantiating the class to choose 
        between GPU and CPU.
        """
        super().__init__(
            processor_cpu = node_processor_cpu,
            processor_gpu = node_processor_gpu,
            do_use_gpu = do_use_gpu
        )

    def __reinit__(
        self,
        node_processor_cpu: Union[_NodeProcessorCPU, None] = None,
        node_processor_gpu: Union[_NodeProcessorGPU, None] = None,
        do_use_gpu: bool = True,
    ):
        super().__reinit__(
            processor_cpu = node_processor_cpu,
            processor_gpu = node_processor_gpu,
            do_use_gpu = do_use_gpu
        )

    def process(
        self,
        # TODO: What about the type (?)
        input: Union[np.ndarray, moderngl.Texture],
        **kwargs
    # TODO: What about the output type (?)
    ) -> Union[np.ndarray, moderngl.Texture]:
        """
        Process the provided 'input' with GPU or CPU 
        according to the internal flag.
        """
        return self._processor.process(
            input = input,
            **kwargs
        )

class SelectionMaskNodeProcessor(_NodeProcessor):
    """
    Class to use a mask selection (from which we will
    determine if the pixel must be applied or not) to
    apply the processed input over the original one.

    If the selection mask is completely full, the
    result will be the processed input.
    """

    def __init__(
        self,
        do_use_gpu: bool = True,
    ):
        """
        The `node_processor_cpu` and `node_processor_gpu` have
        to be set by the developer when building the specific
        classes, but the `do_use_gpu` boolean flag will be set
        by the user when instantiating the class to choose 
        between GPU and CPU.
        """
        super().__init__(
            node_processor_cpu = SelectionMaskProcessorCPU(),
            node_processor_gpu = SelectionMaskProcessorGPU(
                opengl_context = None,
                # TODO: Do not hardcode
                output_size = (1920, 1080)
            ),
            do_use_gpu = do_use_gpu
        )

    def __reinit__(
       self,
        node_processor_cpu: Union[_NodeProcessorCPU, None] = None,
        node_processor_gpu: Union[_NodeProcessorGPU, None] = None,
        do_use_gpu: bool = True,
    ):
        super().__reinit__(
            node_processor_cpu = SelectionMaskProcessorCPU(),
            node_processor_gpu = SelectionMaskProcessorGPU(
                opengl_context = None,
                output_size = None
            ),
            do_use_gpu = do_use_gpu
        )

    def process(
        self,
        # TODO: What about the type (?)
        original_input: Union[np.ndarray, moderngl.Texture],
        processed_input: Union[np.ndarray, moderngl.Texture],
        selection_mask_input: Union[np.ndarray, moderngl.Texture],
        **kwargs
    # TODO: What about the output type (?)
    ) -> Union[np.ndarray, moderngl.Texture]:
        """
        Process the provided 'input' with GPU or CPU 
        according to the internal flag.
        """
        return self._processor.process(
            original_input = original_input,
            processed_input = processed_input,
            selection_mask_input = selection_mask_input,
            **kwargs
        )