"""
Module to simplify the way we obtain a valid
OpenGL context every time we make the call,
being always the same.
"""
from yta_programming.singleton import SingletonMeta
from typing import Union

import moderngl


class OpenGLContext(metaclass = SingletonMeta):
    """
    *Singleton class*

    Class to simplify the way we handle the OpenGL
    contexts.
    """

    @property
    def context(
        self
    ) -> moderngl.Context:
        """
        The OpenGL context.
        """
        if not hasattr(self, '_opengl_context'):
            self._opengl_context: Union[moderngl.Context, None] = _get_context(do_standalone = self._do_standalone)

        return self._opengl_context

    def __init__(
        self,
        do_standalone: bool = True
    ):
        """
        *Singleton instance*
        
        The `do_standalone` parameter will be considered
        only in the first call as this is a singleton
        class.
        """
        self._do_standalone: bool = do_standalone
        """
        Internal flag to indicate if the context must be
        standalone or not.
        """

    @staticmethod
    def get_a_context(
        do_standalone: bool = True
    ) -> moderngl.Context:
        """
        Get a new instance of an OpenGL context that will
        not be related to the one of this singleton 
        instance.

        Every call will return a new OpenGL context.
        """
        return _get_context(do_standalone = do_standalone)
    
def _get_context(
    do_standalone: bool = True
) -> moderngl.Context:
    """
    *For internal use only*

    Get an instance of an OpenGL context that will
    be standalone if the `do_standalone` parameter
    is provided as True.
    """
    return moderngl.create_context(standalone = do_standalone)