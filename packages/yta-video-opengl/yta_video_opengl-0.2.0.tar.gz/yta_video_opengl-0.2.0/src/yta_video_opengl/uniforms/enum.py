from yta_validation import PythonValidator
from yta_validation.number import NumberValidator
from yta_constants.enum import YTAEnum as Enum
from typing import Union

import numpy as np


class UniformType(Enum):
    """
    The type of the uniform we accept to set
    in our OpenGL program.

    By now we are accepting a few of the types
    that are actually available in GLSL, check
    the note at the bottom to see a more list
    containing more options that could be 
    implemented in a near future.
    """

    # Scalars
    BOOL = 'bool'
    INT = 'int'
    FLOAT = 'float'
    # Vectors
    VECTOR2 = 'vec2'
    VECTOR3 = 'vec3'
    VECTOR4 = 'vec4'
    # Matrixes
    MATRIX2 = 'mat2'
    MATRIX3 = 'mat3'
    MATRIX4 = 'mat4'

    def prepare_value(
        self,
        # TODO: Set the different types we accept
        value: any
    ) -> Union[bool, int, float, tuple, np.ndarray]:
        """
        Parse the given `value` and prepare it to be able
        to be stored as a valid uniform value according
        to this type.
        """
        return {
            UniformType.BOOL:   lambda v: bool(v),
            UniformType.INT:    lambda v: int(v),
            UniformType.FLOAT:  lambda v: float(v),
            # Previously this is what was being done
            #self.program[name].write(np.array(value, dtype = 'f4').tobytes())
            UniformType.VECTOR2: lambda v: tuple(map(float, v))[:2],
            UniformType.VECTOR3: lambda v: tuple(map(float, v))[:3],
            UniformType.VECTOR4: lambda v: tuple(map(float, v))[:4],
            UniformType.MATRIX2: lambda v: np.array(v, dtype = 'f4').reshape((2, 2)),
            UniformType.MATRIX3: lambda v: np.array(v, dtype = 'f4').reshape((3, 3)),
            UniformType.MATRIX4: lambda v: np.array(v, dtype = 'f4').reshape((4, 4)),
        }.get(self, lambda v: v)(value)
    
    @staticmethod
    def autodetect(
        # TODO: Include type of the values
        value: any
    ) -> Union['UniformType', None]:
        """
        Detect the GLSL type we are able to handle
        according to the type of the `value` provided.
        Detect the GLSL-like uniform type from a Python value.
        """
        type: Union['UniformType', None] = None

        if PythonValidator.is_boolean(value):
            type = UniformType.BOOL
        elif NumberValidator.is_int(value):
            type = UniformType.INT
        elif NumberValidator.is_float(value):
            type = UniformType.FLOAT
        else:
            if (
                PythonValidator.is_list(value) or
                PythonValidator.is_tuple(value)
            ):
                value = np.array(value, dtype = np.float32)

            if PythonValidator.is_numpy_array(value):
                if value.ndim == 1:
                    # Vector
                    type = {
                        2: UniformType.VECTOR2,
                        3: UniformType.VECTOR3,
                        4: UniformType.VECTOR4,
                    }.get(len(value))
                elif value.ndim == 2:
                    # Matrix
                    type = {
                        (2, 2): UniformType.MATRIX2,
                        (3, 3): UniformType.MATRIX3,
                        (4, 4): UniformType.MATRIX4,
                    }.get(value.shape)

        return type