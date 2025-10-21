import sys
import os
from pathlib import Path
package_dir = Path(__file__).parent

# Windows: 将 base 和 hal 加入 DLL 搜索路径
if sys.platform == "win32":
    base_dir = str(package_dir / "base")
    hal_dir = str(package_dir / "hal")

    # Python ≥3.8 可以用 os.add_dll_directory
    if hasattr(os, "add_dll_directory"):
        os.add_dll_directory(base_dir)
        os.add_dll_directory(hal_dir)
    else:
        # Python <3.8，用 PATH 环境变量
        os.environ["PATH"] = base_dir + os.pathsep + hal_dir + os.pathsep + os.environ.get("PATH", "")

from .dvs_aps_fusion_proccessor import DvsApsFusionProccessor
from .calibrator import Calibrator
from .base import ApsFrame, EventTriggerIn, CalibratorParameters, DvsFileInfo
from .camera_manager import DvsCameraManager
from .dvsense_driver_py import json_file_to_param, param_to_json_file
__all__ = [
    'DvsCameraManager',
    'DvsApsFusionProccessor',
    'Calibrator',
    'ApsFrame',
    'EventTriggerIn',
    'CalibratorParameters',
    'DvsFileInfo',
]
