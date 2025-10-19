from enum import IntEnum, StrEnum
from typing import Dict


class PCFVersion(StrEnum):
    """
    Supported PCF file format versions.
    Each version represents a different encoding format for particle files.
    DMX_BINARY2_PCF1 is the default in this library.
    """
    DMX_BINARY2_DMX1 = "<!-- dmx encoding binary 2 format dmx 1 -->"
    DMX_BINARY2_PCF1 = "<!-- dmx encoding binary 2 format pcf 1 -->"
    DMX_BINARY3_PCF1 = "<!-- dmx encoding binary 3 format pcf 1 -->"


class AttributeType(IntEnum):
    """
    Data types for PCF element attributes.
    Defines all supported attribute types including basic types (int, float, bool),
    vectors, matrices, and array variants of each type.
    """
    ELEMENT = 0x01
    INTEGER = 0x02
    FLOAT = 0x03
    BOOLEAN = 0x04
    STRING = 0x05
    BINARY = 0x06
    TIME = 0x07
    COLOR = 0x08
    VECTOR2 = 0x09
    VECTOR3 = 0x0A
    VECTOR4 = 0x0B
    QANGLE = 0x0C
    QUATERNION = 0x0D
    MATRIX = 0x0E
    ELEMENT_ARRAY = 0x0F
    INTEGER_ARRAY = 0x10
    FLOAT_ARRAY = 0x11
    BOOLEAN_ARRAY = 0x12
    STRING_ARRAY = 0x13
    BINARY_ARRAY = 0x14
    TIME_ARRAY = 0x15
    COLOR_ARRAY = 0x16
    VECTOR2_ARRAY = 0x17
    VECTOR3_ARRAY = 0x18
    VECTOR4_ARRAY = 0x19
    QANGLE_ARRAY = 0x1A
    QUATERNION_ARRAY = 0x1B
    MATRIX_ARRAY = 0x1C


# conversion for type values
ATTRIBUTE_VALUES: Dict[AttributeType, str] = {
    AttributeType.ELEMENT: '<I',
    AttributeType.INTEGER: '<i',
    AttributeType.FLOAT: '<f',
    AttributeType.BOOLEAN: 'B',
    AttributeType.STRING: '<H',
    AttributeType.BINARY: '<I',
    AttributeType.COLOR: '<4B',
    AttributeType.VECTOR2: '<2f',
    AttributeType.VECTOR3: '<3f',
    AttributeType.VECTOR4: '<4f',
    AttributeType.MATRIX: '<4f',
    AttributeType.ELEMENT_ARRAY: '<I',
}


"""
Default values for common particle system properties.
Format: (attribute_name, default_value)
"""
ELEMENT_DEFAULTS = [
    ("max_particles", 1000),
    ("initial_particles", 0),
    ("material", b"vgui/white"),
    ("bounding_box_min", (-10.0, -10.0, -10.0)),
    ("bounding_box_max", (10.0, 10.0, 10.0)),
    ("cull_radius", 0.0),
    ("cull_cost", 1.0),
    ("cull_control_point", 0),
    ("cull_replacement_definition", b""),
    ("radius", 5.0),
    ("color", (255, 255, 255, 255)),
    ("rotation", 0.0),
    ("rotation_speed", 0.0),
    ("sequence_number", 0),
    ("sequence_number1", 0),
    ("group id", 0),
    ("maximum time step", 0.1),
    ("maximum sim tick rate", 0.0),
    ("minimum sim tick rate", 0.0),
    ("minimum rendered frames", 0),
    ("control point to disable rendering if it is the camera", -1),
    ("maximum draw distance", 100000.0),
    ("time to sleep when not drawn", 8.0),
    ("Sort particles", True),
    ("batch particle systems", False),
    ("view model effect", False)
]


"""
Default values for particle operator attributes.
Format: (attribute_name, default_value)
"""
ATTRIBUTE_DEFAULTS = [
    ("operator start fadein", 0.0),
    ("operator end fadein", 0.0),
    ("operator start fadeout", 0.0),
    ("operator end fadeout", 0.0),
    ("operator fade oscillate", 0.0),
    ("Visibility Proxy Input Control Point Number", -1),
    ("Visibility Proxy Radius", 1.0),
    ("Visibility input minimum", 0.0),
    ("Visibility input maximum", 1.0),
    ("Visibility Alpha Scale minimum", 0.0),
    ("Visibility Alpha Scale maximum", 1.0),
    ("Visibility Radius Scale minimum", 1.0),
    ("Visibility Radius Scale maximum", 1.0),
    ("Visibility Camera Depth Bias", 0.0)
]