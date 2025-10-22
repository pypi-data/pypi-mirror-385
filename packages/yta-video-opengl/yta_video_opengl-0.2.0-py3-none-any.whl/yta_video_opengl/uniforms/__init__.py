from yta_video_opengl.uniforms.enum import UniformType
from yta_validation import PythonValidator
from typing import Union
from dataclasses import dataclass

import moderngl


@dataclass
class _Uniform:
    """
    Dataclass to keep the value stored in OpenGL as it
    is stored in a different way than a literal value
    as we set it in Python.
    """

    @property
    def stored_value(
        self
    ) -> any:
        """
        The value that is actually stored as an opengl
        value, that is not understandable by the average
        human x).
        """
        return self._program[self.name].value

    def __init__(
        self,
        program: moderngl.Program,
        name: str,
        value: any
    ):
        self._program: moderngl.Program = program
        """
        The program instance this handler class
        belongs to.
        """
        self.name: str = name
        """
        The name of the uniform as it is stored.
        """
        self.value: any = value
        """
        The value of the uniform we use to store, as a 
        pythonic value.
        """

    def __str__(
        self
    ) -> str:
        """
        The uniform as a string to be printable.
        """
        return f'"{self.name}": {str(self.value)} ({str(self.stored_value)})'

class _Uniforms:
    """
    *For internal use only*

    Class to wrap the functionality related to
    handling the opengl program uniforms.
    """

    @property
    def uniforms(
        self
    ) -> dict:
        """
        The uniforms in the program, as a dict, in
        the format `{key, value}`.
        """
        return {
            key: self.program[key].value
            for key in self.program
            if PythonValidator.is_instance_of(self.program[key], moderngl.Uniform)
        }

    def __init__(
        self,
        program: moderngl.Program
    ):
        self.program: moderngl.Program = program
        """
        The program instance this handler class
        belongs to.
        """
        self._uniforms: dict = {}
        """
        The list of uniforms as our custom dataclass
        that is able to handle the values we use to be
        stored.
        """

    def get(
        self,
        name: str
    ) -> Union[_Uniform, None]:
        """
        Get the value of the uniform with the
        given 'name'.
        """
        return self._uniforms.get(name, None)

    def set(
        self,
        name: str,
        # TODO: Include type of the values
        value: any,
        type: Union[UniformType, None] = None
    ) -> '_Uniforms':
        """
        Set the provided uniform according to the given
        'type'. The 'type' will be autodetect if None
        provided. Nothing will be set if there is not
        uniform with the 'name' given.
        """
        if name not in self.program:
            # TODO: WHy are we entering here (?)
            print(f'The uniform with the name "{name}" is not registered in the program shader.')
            # TODO: Raise exception instead (?)
            #raise Exception(f'The uniform with the name "{name}" is not registered in the program shader.')
            return self
        
        """
        When we store a value (such as the float 2.0), in
        OpenGL it is not stored as that value, and when we
        try to obtain it from the program uniform, we will
        obtain a very different value. Thats why we also
        store a copy of the value we used internally, to
        be able to know what value did we give to each
        uniform we set.
        """
        # Set in the OpenGL program
        _set_uniform(self.program, name, value, type)

        # Store in our own dataclass
        if name not in self._uniforms:
            self._uniforms[name] = _Uniform(
                program = self.program,
                name = name,
                value = value
            )
        else:
            self._uniforms[name].value = value
        
        return self

    def print(
        self
    ) -> '_Uniforms':
        """
        Print the defined uniforms in console. This method
        will print only the uniforms that are set in the
        program and exist there.
        """
        for key in self._uniforms:
            print(self._uniforms[key].__str__())

def _set_uniform(
    program: moderngl.Program,
    name: str,
    value: any,
    type: Union[UniformType, None] = None
) -> any:
    """
    *For internal use only*

    Set the provided `value` to the uniform with the given
    `name` into the opengl `program` if existing, returning
    that same value if everything was ok.
    """
    # if name not in program:
    #     print(f'The uniform with the name "{name}" is not registered in the program shader.')
    #     # TODO: Raise exception instead (?)
    #     #raise Exception(f'The uniform with the name "{name}" is not registered in the program shader.')
    #     return None
    
    type = (
        UniformType.autodetect(value)
        if type is None else
        UniformType.to_enum(type)
    )

    # Parse and prepare value to be stored (this
    # could go wrong and modify the value, be
    # careful at this point)
    value = type.prepare_value(value)

    # Old way to set the value
    # if type in [
        #     UniformType.BOOL,
        #     UniformType.INT,
        #     UniformType.FLOAT,
        #     UniformType.VECTOR2,
        #     UniformType.VECTOR3,
        #     UniformType.VECTOR4
        # ]:
        #     self.program[name].value = value
        # elif type in [
        #     UniformType.MATRIX2,
        #     UniformType.MATRIX3,
        #     UniformType.MATRIX4
        # ]:
        #     self.program[name].write(value.tobytes())

    {
        # self.program[name].value = value
        # TODO: Why not 'prog[name].value = val' (?)
        # Scalars
        UniformType.BOOL:  lambda prog, name, val: setattr(prog[name], 'value', int(bool(val))),
        UniformType.INT:   lambda prog, name, val: setattr(prog[name], 'value', int(val)),
        UniformType.FLOAT: lambda prog, name, val: setattr(prog[name], 'value', float(val)),
        # Vectors
        UniformType.VECTOR2: lambda prog, name, val: setattr(prog[name], 'value', tuple(val)),
        UniformType.VECTOR3: lambda prog, name, val: setattr(prog[name], 'value', tuple(val)),
        UniformType.VECTOR4: lambda prog, name, val: setattr(prog[name], 'value', tuple(val)),
        # Matrixes
        UniformType.MATRIX2: lambda prog, name, val: prog[name].write(val.tobytes()),
        UniformType.MATRIX3: lambda prog, name, val: prog[name].write(val.tobytes()),
        UniformType.MATRIX4: lambda prog, name, val: prog[name].write(val.tobytes()),
    }.get(type)(program, name, value)

    return value
    

"""
Note for the developer about GLSL:

If you declare a uniform at the begining of
your shader but you don't use it in the code
it will be detected as unused and will be 
not included in the program, being not
available as a uniform in the program of your
class and if you try to set a value it will
be ignored because that uniform is not
existing.

By now we are not accepting nor handling
all the existing types in GLSL but some
of them. Here below is an intersting list:

SCALARS:
bool, int, uint
float, double

VECTORS:
bvec2, bvec3, bvec4
ivec2, ivec3, ivec4
uvec2, uvec3, uvec4
vec2, vec3, vec4
dvec2, dvec3, dvec4

MATRIXES:
mat2, mat3, mat4
mat2x3, mat2x4
mat3x2, mat3x4
mat4x2, mat4x3
dmat2, dmat3, dmat4
dmat2x3, dmat2x4, dmat3x2, dmat3x4, dmat4x2, dmat4x3

SAMPLERS:
sampler1D, sampler2D, sampler3D
samplerCube, sampler2DRect
sampler1DShadow, sampler2DShadow, samplerCubeShadow
sampler1DArray, sampler2DArray
sampler1DArrayShadow, sampler2DArrayShadow
isampler2D, usampler2D, isampler3D, usampler3D
sampler2DMS, sampler2DMSArray
samplerBuffer, isamplerBuffer, usamplerBuffer
"""