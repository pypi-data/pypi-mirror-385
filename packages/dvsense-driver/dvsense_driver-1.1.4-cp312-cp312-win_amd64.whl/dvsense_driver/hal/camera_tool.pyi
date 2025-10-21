from enum import Enum

class ToolType(Enum):
    BIAS = 0
    TOOL_TRIGGER_IN = 1
    TOOL_SYNC = 2
    TOOL_ANTI_FLICKER = 3
    TOOL_EVENT_TRAIL_FILTER = 4
    TOOL_EVENT_RATE_CONTROL = 5
    TOOL_ROI = 6
    TOOL_APS_CTRL = 7

class ToolInfo:
    def __init__(self): ...

    tool_type: ToolType
    parameter_names: list[str]
    description: str

class ToolParameterType(Enum):
    INT = 0
    FLOAT = 1
    BOOL = 2
    STRING = 3
    ENUM = 4

def tool_parameter_type_to_string(ToolParameterType: int) -> str: ...

class BasicParameterInfo:
    def __init__(self): ...

    name: str
    description: str
    type: ToolParameterType

    def to_string(self) -> str: ...

class IntParameterInfo:
    def __init__(self): ...
    min: int
    max: int
    default_value: int
    unit: str
    def to_string(self) -> str: ...
    def constraint_value(self, value: int) -> int: ...

class FloatParameterInfo:
    def __init__(self): ...
    min: float
    max: float
    default_value: float
    unit: str
    def to_string(self) -> str: ...
    def constraint_value(self, value: float) -> float: ...

class BoolParameterInfo:
    def __init__(self): ...
    default_value: bool
    def to_string(self) -> str: ...

class EnumParameterInfo:
    def __init__(self): ...
    options: list[str]
    default_value: str
    def to_string(self) -> str: ...

DetailedParameterInfo = IntParameterInfo|FloatParameterInfo|BoolParameterInfo|EnumParameterInfo

class CameraTool:
    def get_tool_info(self) -> ToolInfo:
        pass

    def get_all_param_info(self) -> dict[str, BasicParameterInfo]:
        pass

    def get_param_info(self, name: str) -> tuple[bool, DetailedParameterInfo]:
        pass

    def get_param(self, name: str) -> tuple[bool, int|float|bool|str]:
        pass

    def set_param(self, name: str, value: int|float|bool|str) -> bool:
        pass