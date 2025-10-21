from enum import Enum

class INTERFACE_TYPE(Enum):
    USB = 0

class CAMERA_TYPE(Enum):
    EVK4 = 0
    DVSLume = 1

class RawEventStreamEncodingType(Enum):
    EVT3 = 0
    UNKNOWN = 1

class CameraDescription:
    """
    Description of a camera device.
    """

    # Constructor
    def __init__(self) -> None: ...

    # Properties with type annotations
    serial: str
    product: str
    manufacturer: str
    vid: int
    pid: int
    interfaceType: INTERFACE_TYPE  # Assuming interfaceType is a string; change the type if it's different

class RawEventStreamFormat:
    def __init__(self) -> None: ...

    def get_encoding_type(self) -> RawEventStreamEncodingType: ...

    def get_encoding_type_str(self) -> str: ...

    def contains(name: str) -> bool: ...

    def __getitem__(self, key: str) -> str: ...