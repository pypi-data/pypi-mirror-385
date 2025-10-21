import numpy as np
class Event2D:
    x: int
    y: int
    polarity: int
    timestamp: int

class EventTriggerIn:
    id: int
    polarity: int
    timestamp: int

class ApsFrame:
    def data_numpy() -> np.ndarray: ...
    def get_data_size() -> int: ...
    def width() -> int: ...
    def height() -> int: ...
    exposure_start_timestamp:int
    exposure_end_timestamp:int
class MatrixData:
    rows:int
    cols:int
    type:int
    data:np.ndarray
    
class CalibratorParameters:
    def __init__(self): ...
    camera_serial: str
    dvs_cols: int
    dvs_rows: int
    aps_cols: int
    aps_rows: int
    camera_matrix: MatrixData
    dist_coeffs: MatrixData
    affine_matrix: dict[str, MatrixData]
    rotation:np.ndarray
    translation:np.ndarray

class DvsFileInfo:
    def __init__(self): ...
    serial_number: str
    start_timestamp: int
    end_timestamp: int
    aps_start_timestamp: int
    max_events: int
    dvs_width: int
    dvs_height: int
    