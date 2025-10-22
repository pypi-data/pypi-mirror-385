"""

Fast and minimalist 3D viewer
"""
from __future__ import annotations
from f3d.pyf3d import Camera
from f3d.pyf3d import CameraState
from f3d.pyf3d import Color
from f3d.pyf3d import Engine
from f3d.pyf3d import Image
from f3d.pyf3d import InteractionBind
from f3d.pyf3d import Interactor
from f3d.pyf3d import LibInformation
from f3d.pyf3d import LightState
from f3d.pyf3d import LightType
from f3d.pyf3d import Log
from f3d.pyf3d import Mesh
from f3d.pyf3d import Options
from f3d.pyf3d import ReaderInformation
from f3d.pyf3d import Scene
from f3d.pyf3d import Utils
from f3d.pyf3d import Window
import os as os
import pathlib
from pathlib import Path
import re as re
import sys as sys
from typing import Any
import warnings as warnings
from . import pyf3d
__all__: list = ['CAMERA_LIGHT', 'Camera', 'CameraState', 'Color', 'Engine', 'HEADLIGHT', 'Image', 'InteractionBind', 'Interactor', 'LibInformation', 'LightState', 'LightType', 'Log', 'Mesh', 'Options', 'ReaderInformation', 'SCENE_LIGHT', 'Scene', 'Utils', 'Window']
def _add_deprecation_warnings():
    ...
def _deprecated_decorator(f, reason):
    ...
def _f3d_options_update(self, arg: typing.Union[typing.Mapping[str, typing.Any], typing.Iterable[tuple[str, typing.Any]]]) -> None:
    ...
CAMERA_LIGHT: pyf3d.LightType  # value = <LightType.CAMERA_LIGHT: 2>
F3D_ABSOLUTE_DLLS: list = ['D:/a/f3d-superbuild/f3d-superbuild/fsbb/install/bin', 'D:/a/f3d-superbuild/f3d-superbuild/fsbb/install/lib', 'C:/Users/runneradmin/AppData/Local/Temp/tmp8wvtqmxv/build/bin']
F3D_RELATIVE_DLLS: list = list()
HEADLIGHT: pyf3d.LightType  # value = <LightType.HEADLIGHT: 1>
SCENE_LIGHT: pyf3d.LightType  # value = <LightType.SCENE_LIGHT: 3>
__version__: str = '3.3.0'
abs_path: str = 'C:/Users/runneradmin/AppData/Local/Temp/tmp8wvtqmxv/build/bin'
root: pathlib.WindowsPath  # value = WindowsPath('C:/Users/runneradmin/AppData/Local/Temp/tmp8wvtqmxv/build/f3d')
