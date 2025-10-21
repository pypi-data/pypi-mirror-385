from typing import overload
import numpy as np
from dvsense_driver.base import ApsFrame
class Mp4FileReader:
    def __init__(self, file_path: str) -> None:
        ...

    def load_file(self) -> bool:
        ...

    def get_timestamps(self) -> np.ndarray:
        ...

    def get_next_frame(self, frame: ApsFrame) -> bool:
        ...

    def get_n_frame(self, n: int, frame: ApsFrame) -> bool:
        ...

    def get_frame_given_timestamp(self, time: int, frame: ApsFrame) -> int:
        ...

    def get_width(self) -> int:
        ...

    def get_height(self) -> int:
        ...
