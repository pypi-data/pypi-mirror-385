from yta_video_opengl.nodes import _NodeProcessor, SelectionMaskNodeProcessor
from yta_video_opengl.blender import _Blender, AlphaBlender, MixBlender
from yta_validation.parameter import ParameterValidator
from typing import Union

import numpy as np

import moderngl


# TODO: A transition class should have not selection
# mask and a opacity of 1.0 (or should be ignored
# also)
class Node:
    """
    A generic node that receives an input and returns
    an output when processed, having a selection mask
    to be able to apply the changes to only one part
    of the input, and an opacity to indicate the
    percentage of effect to apply in the input.
    """

    def __init__(
        self,
        node_processor: _NodeProcessor,
        selection_mask: Union[np.ndarray, moderngl.Texture, None] = None,
        mix_weight: float = 1.0
    ):
        self._node_processor: _NodeProcessor = node_processor
        """
        The node processor we need to apply the change
        to the input.
        """
        self._selection_mask: Union[np.ndarray, moderngl.Texture] = selection_mask
        """
        The mask to apply to the processed output in order
        to affect the original input only where and as
        much as the selection mask is indicating. Check the
        'selection_mask.py' module.
        """
        self._mix_weight: float = np.clip(mix_weight, 0, 1)
        """
        The mix_weight to be applied by the node process,
        which means how much the effect must be mixed
        with the original input, giving us the control
        on the result:

        - `mix_weight=1.0` The effect will be applied and
        mixed at a 100% with the original input.
        - `mix_weight=0.5` The effect will be applied but
        only at a 50%.

        This is useful to avoid modifying the code that
        applies the modification but only affect the
        result as much as we want.
        """

    def process(
        self,
        # TODO: What about the type (?)
        input: np.ndarray,
        dtype: Union[np.dtype, None] = None,
        **kwargs
    # TODO: What about the output type (?)
    ) -> np.ndarray:
        """
        *For internal use only*

        Common method to apply the processing to the
        given 'input' and set the output as the 'dtype'
        provided (or the one the 'input' had if None).

        This method will process the 'input' and then,
        if provided, apply it only to the selection 
        mask and also with the opacity set when
        instantiated.

        The result is clipped to the [0, 255] range.
        """
        if self._mix_weight == 0:
            return input.copy()
        
        dtype = (
            input.dtype
            if dtype is None else
            dtype
        )

        # Process the full input by the node processor
        result = self._node_processor.process(
            input = input.copy(),
            **kwargs
        )

        # Process the selection mask if needed
        if self._selection_mask is not None:
            result = SelectionMaskNodeProcessor(
                do_use_gpu = True
            ).process(
                original_input = input,
                processed_input = result,
                selection_mask_input = self._selection_mask
            )
            
        # Apply the mix_weight (percentage of effect)
        result = MixBlender(
            do_use_gpu = True
        ).process(
            base_input = input,
            overlay_input = result,
            mix_weight = self._mix_weight
        )

        return np.clip(
            a = result,
            a_min = 0,
            a_max = 255
        ).astype(dtype)
    


    
class LayerNode:
    """
    A node that will be used within a group of layer
    nodes.
    """

    def __init__(
        self,
        node: Node,
        blender: _Blender = AlphaBlender,
        mix_weight: float = 1.0
    ):
        self._node: Node = node
        """
        The node that belongs to the layer and will be
        used in the combination.
        """
        self._blender: _Blender = blender
        """
        The blender to mix the result with the input
        provided.
        """
        self._mix_weight: float = mix_weight
        """
        The mix_weight to be applied when mixing it with
        the input provided.
        """

    def process(
        self,
        # TODO: What about the type (?)
        input: np.ndarray,
        dtype: Union[np.dtype, None] = None,
        **kwargs
    # TODO: What about the output type (?)
    ) -> np.ndarray:
        """
        *For internal use only*

        Common method to apply the processing to the
        given 'input' and set the output as the 'dtype'
        provided (or the one the 'input' had if None).

        This method will process the 'input' and then,
        if provided, apply it only to the selection 
        mask and also with the opacity set when
        instantiated.

        The result is clipped to the [0, 255] range.
        """
        layer_output = self._node.process(
            input = input,
            dtype = dtype,
            **kwargs
        )

        # Mix the layer with the previous result
        return self._blender.process(
            base_input = input,
            overlay_input = layer_output,
            mix_weight = self._mix_weight,
            dtype = dtype
        )
    
# TODO: Node types below. Maybe use a 'UsableNode' 
# or 'RunnableNode' class to identify them. These
# are the different ways to process an input and
# to obtain the result. These are the classes that
# can be added to process some input, and not the
# Nodes directly.
class SerialNode:
    """
    A single node that will receive an input, process
    it and return an output to the next node.
    """

    def __init__(
        self,
        node: Node
    ):
        ParameterValidator.validate_mandatory_instance_of('node', node, Node)

        self._node: Node = node
        """
        The single node that will process the input.
        """

    def process(
        self,
        # TODO: What about the type (?)
        input: np.ndarray,
        dtype: Union[np.dtype, None] = None,
        **kwargs
    # TODO: What about the output type (?)
    ) -> np.ndarray:
        """
        Process the `input` with the single node that
        belongs to this Serial Node, with the provided
        `**kwargs` (if some provided) and obtain the
        single result.
        """
        return self._node.process(
            input = input,
            dtype = dtype,
            **kwargs
        )
    
class ParallelNodes:
    """
    A group of nodes that will process the same
    input and mix their result in a single output
    result.
    """

    def __init__(
        self,
        nodes: list[Node],
        # TODO: This is an abstract base class but not the
        # one we will receive
        blender: _Blender
    ):
        ParameterValidator.validate_mandatory_list_of_these_instances('nodes', nodes, Node)
        # TODO: Check that validation is working
        ParameterValidator.validate_mandatory_subclass_of('blender', blender, _Blender)

        self._nodes: list[Node] = nodes
        """
        The list of nodes that will process the same
        input in parallel.
        """
        # TODO: This is an abstract base class but not the
        # one we will receive
        self._blender: _Blender = blender
        """
        The class capable of blending the results of
        the different nodes that have been executed
        in parallel over the same input.
        """

    def process(
        self,
        # TODO: What about the type (?)
        input: np.ndarray,
        dtype: Union[np.dtype, None] = None,
        **kwargs
    # TODO: What about the output type (?)
    ) -> np.ndarray:
        """
        Process the `input` with the nodes that belong
        to this Parallel Node, with the provided `**kwargs`
        (if some provided) and obtain a single mixed result.
        """
        results = [
            node.process(
                input = input,
                dtype = dtype,
                **kwargs
            )
            for node in self._nodes
        ]

        return self._blender.blend_multiple_inputs(
            inputs = results,
            # TODO: Is this ok (?)
            dtype = dtype
        )
    
class LayerNodes:
    """
    A group of nodes that are ordered by priority
    within layers, process the same input and mix
    their result in a single output result.
    """

    def __init__(
        self,
        layer_nodes: list[LayerNode],
        # TODO: This is an abstract base class but not the
        # one we will receive
        blender: _Blender
    ):
        ParameterValidator.validate_mandatory_list_of_these_instances('layer_nodes', layer_nodes, LayerNode)
        # TODO: Check that validation is working
        ParameterValidator.validate_mandatory_subclass_of('blender', blender, _Blender)

        self._layer_nodes: list[LayerNode] = layer_nodes
        """
        The list of layer nodes that will process the same
        input in parallel.
        """
        # TODO: This is an abstract base class but not the
        # one we will receive
        self._blender: _Blender = blender
        """
        The class capable of blending the results of
        the different nodes that have been executed
        in parallel over the same input.
        """

    def process(
        self,
        # TODO: What about the type (?)
        input: np.ndarray,
        dtype: Union[np.dtype, None] = None,
        **kwargs
    # TODO: What about the output type (?)
    ) -> np.ndarray:
        """
        Process the `input` with the nodes that belong
        to this Parallel Node, with the provided `**kwargs`
        (if some provided) and obtain a single mixed result.
        """
        base = input.copy()

        for layer_node in self._layer_nodes:
            layer_output = layer_node.process(
                input = result,
                dtype = dtype,
                **kwargs
            )

            # TODO: Node can use GPU or CPU

            # Blend over accumulated result
            result = self._blender.process(
                base_input = base,
                overlay_input = layer_output,
                # TODO: What about the 'opacity' here (?)
                #opacity = node.opacity if hasattr(node, "opacity") else 1.0,
                #dtype = dtype
            )

        return result




        for layer_node in self._layer_nodes:
            output = layer_node.process(input)
            # Blend it
            output_blended = self._blender.blend([base, output])
            # Adjust to this layer node opacity
            output = (1 - layer_node.opacity) * base + layer_node.opacity * output_blended

        # TODO: I'm doing this kind of operations in the 'blender.py'
        return np.clip(
            a = base,
            a_min = 0,
            a_max = 255
        ).astype(dtype)