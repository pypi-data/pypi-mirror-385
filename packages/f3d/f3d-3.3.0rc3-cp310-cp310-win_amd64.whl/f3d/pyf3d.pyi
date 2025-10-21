"""
f3d library bindings
"""
from __future__ import annotations
import f3d
import os
import typing
__all__: list[str] = ['CAMERA_LIGHT', 'Camera', 'CameraState', 'Color', 'Engine', 'HEADLIGHT', 'Image', 'InteractionBind', 'Interactor', 'LibInformation', 'LightState', 'LightType', 'Log', 'Mesh', 'Options', 'ReaderInformation', 'SCENE_LIGHT', 'Scene', 'Utils', 'Window']
class Camera:
    focal_point: tuple[float, float, float]
    position: tuple[float, float, float]
    state: CameraState
    view_angle: float
    view_up: tuple[float, float, float]
    def azimuth(self, arg0: float) -> Camera:
        ...
    def dolly(self, arg0: float) -> Camera:
        ...
    def elevation(self, arg0: float) -> Camera:
        ...
    def pan(self, right: float, up: float, forward: float = 0.0) -> Camera:
        ...
    def pitch(self, arg0: float) -> Camera:
        ...
    def reset_to_bounds(self, zoom_factor: float = 0.9) -> Camera:
        ...
    def reset_to_default(self) -> Camera:
        ...
    def roll(self, arg0: float) -> Camera:
        ...
    def set_current_as_default(self) -> Camera:
        ...
    def yaw(self, arg0: float) -> Camera:
        ...
    def zoom(self, arg0: float) -> Camera:
        ...
class CameraState:
    focal_point: tuple[float, float, float]
    position: tuple[float, float, float]
    view_angle: float
    view_up: tuple[float, float, float]
    @typing.overload
    def __init__(self) -> None:
        ...
    @typing.overload
    def __init__(self, position: tuple[float, float, float] = (0.0, 0.0, 1.0), focal_point: tuple[float, float, float] = (0.0, 0.0, 0.0), view_up: tuple[float, float, float] = (0.0, 1.0, 0.0), view_angle: float = 30.0) -> None:
        ...
class Color:
    b: float
    g: float
    r: float
    @typing.overload
    def __init__(self) -> None:
        ...
    @typing.overload
    def __init__(self, r: float, g: float, b: float) -> None:
        ...
    def from_tuple(self, arg0: tuple[float, float, float]) -> None:
        """
        Set color from a tuple of (r, g, b)
        """
    def to_tuple(self) -> tuple[float, float, float]:
        """
        Convert color to a tuple of (r, g, b)
        """
class Engine:
    options: Options
    @staticmethod
    def autoload_plugins() -> None:
        """
        Automatically load internal plugins
        """
    @staticmethod
    def create(offscreen: bool = False) -> Engine:
        """
        Create an engine with a automatic window
        """
    @staticmethod
    def create_egl() -> Engine:
        """
        Create an engine with an EGL window (Windows/Linux only)
        """
    @staticmethod
    def create_external_cocoa() -> Engine:
        """
        Create an engine with an existing COCOA context (macOS only)
        """
    @staticmethod
    def create_external_egl() -> Engine:
        """
        Create an engine with an existing EGL context (Windows/Linux only)
        """
    @staticmethod
    def create_external_glx() -> Engine:
        """
        Create an engine with an existing GLX context (Linux only)
        """
    @staticmethod
    def create_external_osmesa() -> Engine:
        """
        Create an engine with an existing OSMesa context (Windows/Linux only)
        """
    @staticmethod
    def create_external_wgl() -> Engine:
        """
        Create an engine with an existing WGL context (Windows only)
        """
    @staticmethod
    def create_glx(arg0: bool) -> Engine:
        """
        Create an engine with an GLX window (Linux only)
        """
    @staticmethod
    def create_none() -> Engine:
        """
        Create an engine with no window
        """
    @staticmethod
    def create_osmesa() -> Engine:
        """
        Create an engine with an OSMesa window (Windows/Linux only)
        """
    @staticmethod
    def create_wgl(arg0: bool) -> Engine:
        """
        Create an engine with an WGL window (Windows only)
        """
    @staticmethod
    def get_all_reader_option_names() -> list[str]:
        ...
    @staticmethod
    def get_lib_info() -> LibInformation:
        ...
    @staticmethod
    def get_plugins_list(arg0: os.PathLike[str]) -> list[str]:
        ...
    @staticmethod
    def get_readers_info() -> list[ReaderInformation]:
        ...
    @staticmethod
    def get_rendering_backend_list() -> dict[str, bool]:
        ...
    @staticmethod
    def load_plugin(arg0: str, arg1: typing.Sequence[os.PathLike[str]]) -> None:
        """
        Load a plugin
        """
    @staticmethod
    def set_reader_option(arg0: str, arg1: str) -> None:
        ...
    def set_cache_path(self, arg0: os.PathLike[str]) -> Engine:
        """
        Set the cache path directory
        """
    @property
    def interactor(self) -> Interactor:
        ...
    @property
    def scene(self) -> Scene:
        ...
    @property
    def window(self) -> Window:
        ...
class Image:
    class ChannelType:
        """
        Members:
        
          BYTE
        
          SHORT
        
          FLOAT
        """
        BYTE: typing.ClassVar[Image.ChannelType]  # value = <ChannelType.BYTE: 0>
        FLOAT: typing.ClassVar[Image.ChannelType]  # value = <ChannelType.FLOAT: 2>
        SHORT: typing.ClassVar[Image.ChannelType]  # value = <ChannelType.SHORT: 1>
        __members__: typing.ClassVar[dict[str, Image.ChannelType]]  # value = {'BYTE': <ChannelType.BYTE: 0>, 'SHORT': <ChannelType.SHORT: 1>, 'FLOAT': <ChannelType.FLOAT: 2>}
        def __eq__(self, other: typing.Any) -> bool:
            ...
        def __getstate__(self) -> int:
            ...
        def __hash__(self) -> int:
            ...
        def __index__(self) -> int:
            ...
        def __init__(self, value: int) -> None:
            ...
        def __int__(self) -> int:
            ...
        def __ne__(self, other: typing.Any) -> bool:
            ...
        def __repr__(self) -> str:
            ...
        def __setstate__(self, state: int) -> None:
            ...
        def __str__(self) -> str:
            ...
        @property
        def name(self) -> str:
            ...
        @property
        def value(self) -> int:
            ...
    class SaveFormat:
        """
        Members:
        
          PNG
        
          JPG
        
          TIF
        
          BMP
        """
        BMP: typing.ClassVar[Image.SaveFormat]  # value = <SaveFormat.BMP: 3>
        JPG: typing.ClassVar[Image.SaveFormat]  # value = <SaveFormat.JPG: 1>
        PNG: typing.ClassVar[Image.SaveFormat]  # value = <SaveFormat.PNG: 0>
        TIF: typing.ClassVar[Image.SaveFormat]  # value = <SaveFormat.TIF: 2>
        __members__: typing.ClassVar[dict[str, Image.SaveFormat]]  # value = {'PNG': <SaveFormat.PNG: 0>, 'JPG': <SaveFormat.JPG: 1>, 'TIF': <SaveFormat.TIF: 2>, 'BMP': <SaveFormat.BMP: 3>}
        def __eq__(self, other: typing.Any) -> bool:
            ...
        def __getstate__(self) -> int:
            ...
        def __hash__(self) -> int:
            ...
        def __index__(self) -> int:
            ...
        def __init__(self, value: int) -> None:
            ...
        def __int__(self) -> int:
            ...
        def __ne__(self, other: typing.Any) -> bool:
            ...
        def __repr__(self) -> str:
            ...
        def __setstate__(self, state: int) -> None:
            ...
        def __str__(self) -> str:
            ...
        @property
        def name(self) -> str:
            ...
        @property
        def value(self) -> int:
            ...
    BMP: typing.ClassVar[Image.SaveFormat]  # value = <SaveFormat.BMP: 3>
    BYTE: typing.ClassVar[Image.ChannelType]  # value = <ChannelType.BYTE: 0>
    FLOAT: typing.ClassVar[Image.ChannelType]  # value = <ChannelType.FLOAT: 2>
    JPG: typing.ClassVar[Image.SaveFormat]  # value = <SaveFormat.JPG: 1>
    PNG: typing.ClassVar[Image.SaveFormat]  # value = <SaveFormat.PNG: 0>
    SHORT: typing.ClassVar[Image.ChannelType]  # value = <ChannelType.SHORT: 1>
    TIF: typing.ClassVar[Image.SaveFormat]  # value = <SaveFormat.TIF: 2>
    __hash__: typing.ClassVar[None] = None
    content: bytes
    @staticmethod
    def supported_formats() -> list[str]:
        ...
    def __eq__(self, arg0: Image) -> bool:
        ...
    @typing.overload
    def __init__(self) -> None:
        ...
    @typing.overload
    def __init__(self, arg0: os.PathLike[str]) -> None:
        ...
    @typing.overload
    def __init__(self, arg0: int, arg1: int, arg2: int, arg3: Image.ChannelType) -> None:
        ...
    def __ne__(self, arg0: Image) -> bool:
        ...
    def _repr_png_(self) -> bytes:
        ...
    def all_metadata(self) -> list[str]:
        ...
    def compare(self, arg0: Image) -> float:
        ...
    def get_metadata(self, arg0: str) -> str:
        ...
    def normalized_pixel(self, arg0: tuple[int, int]) -> list[float]:
        ...
    def save(self, path: os.PathLike[str], format: Image.SaveFormat = Image.SaveFormat.PNG) -> Image:
        ...
    def save_buffer(self, format: Image.SaveFormat = Image.SaveFormat.PNG) -> bytes:
        ...
    def set_metadata(self, arg0: str, arg1: str) -> Image:
        ...
    def to_terminal_text(self) -> str:
        ...
    @property
    def channel_count(self) -> int:
        ...
    @property
    def channel_type(self) -> Image.ChannelType:
        ...
    @property
    def channel_type_size(self) -> int:
        ...
    @property
    def height(self) -> int:
        ...
    @property
    def width(self) -> int:
        ...
class InteractionBind:
    class ModifierKeys:
        """
        Members:
        
          ANY
        
          NONE
        
          CTRL
        
          SHIFT
        
          CTRL_SHIFT
        """
        ANY: typing.ClassVar[InteractionBind.ModifierKeys]  # value = <ModifierKeys.ANY: 128>
        CTRL: typing.ClassVar[InteractionBind.ModifierKeys]  # value = <ModifierKeys.CTRL: 1>
        CTRL_SHIFT: typing.ClassVar[InteractionBind.ModifierKeys]  # value = <ModifierKeys.CTRL_SHIFT: 3>
        NONE: typing.ClassVar[InteractionBind.ModifierKeys]  # value = <ModifierKeys.NONE: 0>
        SHIFT: typing.ClassVar[InteractionBind.ModifierKeys]  # value = <ModifierKeys.SHIFT: 2>
        __members__: typing.ClassVar[dict[str, InteractionBind.ModifierKeys]]  # value = {'ANY': <ModifierKeys.ANY: 128>, 'NONE': <ModifierKeys.NONE: 0>, 'CTRL': <ModifierKeys.CTRL: 1>, 'SHIFT': <ModifierKeys.SHIFT: 2>, 'CTRL_SHIFT': <ModifierKeys.CTRL_SHIFT: 3>}
        def __eq__(self, other: typing.Any) -> bool:
            ...
        def __getstate__(self) -> int:
            ...
        def __hash__(self) -> int:
            ...
        def __index__(self) -> int:
            ...
        def __init__(self, value: int) -> None:
            ...
        def __int__(self) -> int:
            ...
        def __ne__(self, other: typing.Any) -> bool:
            ...
        def __repr__(self) -> str:
            ...
        def __setstate__(self, state: int) -> None:
            ...
        def __str__(self) -> str:
            ...
        @property
        def name(self) -> str:
            ...
        @property
        def value(self) -> int:
            ...
    ANY: typing.ClassVar[InteractionBind.ModifierKeys]  # value = <ModifierKeys.ANY: 128>
    CTRL: typing.ClassVar[InteractionBind.ModifierKeys]  # value = <ModifierKeys.CTRL: 1>
    CTRL_SHIFT: typing.ClassVar[InteractionBind.ModifierKeys]  # value = <ModifierKeys.CTRL_SHIFT: 3>
    NONE: typing.ClassVar[InteractionBind.ModifierKeys]  # value = <ModifierKeys.NONE: 0>
    SHIFT: typing.ClassVar[InteractionBind.ModifierKeys]  # value = <ModifierKeys.SHIFT: 2>
    inter: str
    mod: InteractionBind.ModifierKeys
    def __init__(self, arg0: InteractionBind.ModifierKeys, arg1: str) -> None:
        ...
    def format(self) -> str:
        ...
class Interactor:
    class BindingType:
        """
        Members:
        
          CYCLIC
        
          NUMERICAL
        
          TOGGLE
        
          OTHER
        """
        CYCLIC: typing.ClassVar[Interactor.BindingType]  # value = <BindingType.CYCLIC: 0>
        NUMERICAL: typing.ClassVar[Interactor.BindingType]  # value = <BindingType.NUMERICAL: 1>
        OTHER: typing.ClassVar[Interactor.BindingType]  # value = <BindingType.OTHER: 3>
        TOGGLE: typing.ClassVar[Interactor.BindingType]  # value = <BindingType.TOGGLE: 2>
        __members__: typing.ClassVar[dict[str, Interactor.BindingType]]  # value = {'CYCLIC': <BindingType.CYCLIC: 0>, 'NUMERICAL': <BindingType.NUMERICAL: 1>, 'TOGGLE': <BindingType.TOGGLE: 2>, 'OTHER': <BindingType.OTHER: 3>}
        def __eq__(self, other: typing.Any) -> bool:
            ...
        def __getstate__(self) -> int:
            ...
        def __hash__(self) -> int:
            ...
        def __index__(self) -> int:
            ...
        def __init__(self, value: int) -> None:
            ...
        def __int__(self) -> int:
            ...
        def __ne__(self, other: typing.Any) -> bool:
            ...
        def __repr__(self) -> str:
            ...
        def __setstate__(self, state: int) -> None:
            ...
        def __str__(self) -> str:
            ...
        @property
        def name(self) -> str:
            ...
        @property
        def value(self) -> int:
            ...
    class InputAction:
        """
        Members:
        
          PRESS
        
          RELEASE
        """
        PRESS: typing.ClassVar[Interactor.InputAction]  # value = <InputAction.PRESS: 0>
        RELEASE: typing.ClassVar[Interactor.InputAction]  # value = <InputAction.RELEASE: 1>
        __members__: typing.ClassVar[dict[str, Interactor.InputAction]]  # value = {'PRESS': <InputAction.PRESS: 0>, 'RELEASE': <InputAction.RELEASE: 1>}
        def __eq__(self, other: typing.Any) -> bool:
            ...
        def __getstate__(self) -> int:
            ...
        def __hash__(self) -> int:
            ...
        def __index__(self) -> int:
            ...
        def __init__(self, value: int) -> None:
            ...
        def __int__(self) -> int:
            ...
        def __ne__(self, other: typing.Any) -> bool:
            ...
        def __repr__(self) -> str:
            ...
        def __setstate__(self, state: int) -> None:
            ...
        def __str__(self) -> str:
            ...
        @property
        def name(self) -> str:
            ...
        @property
        def value(self) -> int:
            ...
    class InputModifier:
        """
        Members:
        
          NONE
        
          CTRL
        
          SHIFT
        
          CTRL_SHIFT
        """
        CTRL: typing.ClassVar[Interactor.InputModifier]  # value = <InputModifier.CTRL: 1>
        CTRL_SHIFT: typing.ClassVar[Interactor.InputModifier]  # value = <InputModifier.CTRL_SHIFT: 3>
        NONE: typing.ClassVar[Interactor.InputModifier]  # value = <InputModifier.NONE: 0>
        SHIFT: typing.ClassVar[Interactor.InputModifier]  # value = <InputModifier.SHIFT: 2>
        __members__: typing.ClassVar[dict[str, Interactor.InputModifier]]  # value = {'NONE': <InputModifier.NONE: 0>, 'CTRL': <InputModifier.CTRL: 1>, 'SHIFT': <InputModifier.SHIFT: 2>, 'CTRL_SHIFT': <InputModifier.CTRL_SHIFT: 3>}
        def __eq__(self, other: typing.Any) -> bool:
            ...
        def __getstate__(self) -> int:
            ...
        def __hash__(self) -> int:
            ...
        def __index__(self) -> int:
            ...
        def __init__(self, value: int) -> None:
            ...
        def __int__(self) -> int:
            ...
        def __ne__(self, other: typing.Any) -> bool:
            ...
        def __repr__(self) -> str:
            ...
        def __setstate__(self, state: int) -> None:
            ...
        def __str__(self) -> str:
            ...
        @property
        def name(self) -> str:
            ...
        @property
        def value(self) -> int:
            ...
    class MouseButton:
        """
        Members:
        
          LEFT
        
          MIDDLE
        
          RIGHT
        """
        LEFT: typing.ClassVar[Interactor.MouseButton]  # value = <MouseButton.LEFT: 0>
        MIDDLE: typing.ClassVar[Interactor.MouseButton]  # value = <MouseButton.MIDDLE: 2>
        RIGHT: typing.ClassVar[Interactor.MouseButton]  # value = <MouseButton.RIGHT: 1>
        __members__: typing.ClassVar[dict[str, Interactor.MouseButton]]  # value = {'LEFT': <MouseButton.LEFT: 0>, 'MIDDLE': <MouseButton.MIDDLE: 2>, 'RIGHT': <MouseButton.RIGHT: 1>}
        def __eq__(self, other: typing.Any) -> bool:
            ...
        def __getstate__(self) -> int:
            ...
        def __hash__(self) -> int:
            ...
        def __index__(self) -> int:
            ...
        def __init__(self, value: int) -> None:
            ...
        def __int__(self) -> int:
            ...
        def __ne__(self, other: typing.Any) -> bool:
            ...
        def __repr__(self) -> str:
            ...
        def __setstate__(self, state: int) -> None:
            ...
        def __str__(self) -> str:
            ...
        @property
        def name(self) -> str:
            ...
        @property
        def value(self) -> int:
            ...
    class WheelDirection:
        """
        Members:
        
          FORWARD
        
          BACKWARD
        
          LEFT
        
          RIGHT
        """
        BACKWARD: typing.ClassVar[Interactor.WheelDirection]  # value = <WheelDirection.BACKWARD: 1>
        FORWARD: typing.ClassVar[Interactor.WheelDirection]  # value = <WheelDirection.FORWARD: 0>
        LEFT: typing.ClassVar[Interactor.WheelDirection]  # value = <WheelDirection.LEFT: 2>
        RIGHT: typing.ClassVar[Interactor.WheelDirection]  # value = <WheelDirection.RIGHT: 3>
        __members__: typing.ClassVar[dict[str, Interactor.WheelDirection]]  # value = {'FORWARD': <WheelDirection.FORWARD: 0>, 'BACKWARD': <WheelDirection.BACKWARD: 1>, 'LEFT': <WheelDirection.LEFT: 2>, 'RIGHT': <WheelDirection.RIGHT: 3>}
        def __eq__(self, other: typing.Any) -> bool:
            ...
        def __getstate__(self) -> int:
            ...
        def __hash__(self) -> int:
            ...
        def __index__(self) -> int:
            ...
        def __init__(self, value: int) -> None:
            ...
        def __int__(self) -> int:
            ...
        def __ne__(self, other: typing.Any) -> bool:
            ...
        def __repr__(self) -> str:
            ...
        def __setstate__(self, state: int) -> None:
            ...
        def __str__(self) -> str:
            ...
        @property
        def name(self) -> str:
            ...
        @property
        def value(self) -> int:
            ...
    BACKWARD: typing.ClassVar[Interactor.WheelDirection]  # value = <WheelDirection.BACKWARD: 1>
    CTRL: typing.ClassVar[Interactor.InputModifier]  # value = <InputModifier.CTRL: 1>
    CTRL_SHIFT: typing.ClassVar[Interactor.InputModifier]  # value = <InputModifier.CTRL_SHIFT: 3>
    CYCLIC: typing.ClassVar[Interactor.BindingType]  # value = <BindingType.CYCLIC: 0>
    FORWARD: typing.ClassVar[Interactor.WheelDirection]  # value = <WheelDirection.FORWARD: 0>
    LEFT: typing.ClassVar[Interactor.WheelDirection]  # value = <WheelDirection.LEFT: 2>
    MIDDLE: typing.ClassVar[Interactor.MouseButton]  # value = <MouseButton.MIDDLE: 2>
    NONE: typing.ClassVar[Interactor.InputModifier]  # value = <InputModifier.NONE: 0>
    NUMERICAL: typing.ClassVar[Interactor.BindingType]  # value = <BindingType.NUMERICAL: 1>
    OTHER: typing.ClassVar[Interactor.BindingType]  # value = <BindingType.OTHER: 3>
    PRESS: typing.ClassVar[Interactor.InputAction]  # value = <InputAction.PRESS: 0>
    RELEASE: typing.ClassVar[Interactor.InputAction]  # value = <InputAction.RELEASE: 1>
    RIGHT: typing.ClassVar[Interactor.WheelDirection]  # value = <WheelDirection.RIGHT: 3>
    SHIFT: typing.ClassVar[Interactor.InputModifier]  # value = <InputModifier.SHIFT: 2>
    TOGGLE: typing.ClassVar[Interactor.BindingType]  # value = <BindingType.TOGGLE: 2>
    @typing.overload
    def add_binding(self, bind: InteractionBind, command: str, group: str, documentationCallback: typing.Callable[[], tuple[str, str]] = None, type: Interactor.BindingType = Interactor.BindingType.OTHER) -> Interactor:
        """
        Add a binding command
        """
    @typing.overload
    def add_binding(self, bind: InteractionBind, command: typing.Sequence[str], group: str, documentationCallback: typing.Callable[[], tuple[str, str]] = None, type: Interactor.BindingType = Interactor.BindingType.OTHER) -> Interactor:
        """
        Add binding commands
        """
    def add_command(self, action: str, callback: typing.Callable[[list[str]], None], doc: tuple[str, str] | None = None, completionCallback: typing.Callable[[list[str]], typing.Sequence[str]] = None) -> Interactor:
        """
        Add a command
        """
    def disable_camera_movement(self) -> Interactor:
        """
        Disable the camera interaction
        """
    def enable_camera_movement(self) -> Interactor:
        """
        Enable the camera interaction
        """
    def get_bind_groups(self) -> list[str]:
        ...
    def get_binding_documentation(self, arg0: InteractionBind) -> tuple[str, str]:
        ...
    def get_binding_type(self, arg0: InteractionBind) -> Interactor.BindingType:
        ...
    def get_binds(self) -> list[InteractionBind]:
        ...
    def get_binds_for_group(self, arg0: str) -> list[InteractionBind]:
        ...
    def get_command_actions(self) -> list[str]:
        """
        Get all command actions
        """
    def init_bindings(self) -> Interactor:
        """
        Remove all bindings and add default bindings
        """
    def init_commands(self) -> Interactor:
        """
        Remove all commands and add all default command callbacks
        """
    def is_playing_animation(self) -> bool:
        """
        Returns True if the animation is currently started
        """
    def play_interaction(self, arg0: os.PathLike[str], arg1: float, arg2: typing.Callable[[], None]) -> bool:
        """
        Play an interaction file
        """
    def record_interaction(self, arg0: os.PathLike[str]) -> bool:
        """
        Record an interaction file
        """
    def remove_binding(self, arg0: InteractionBind) -> Interactor:
        """
        Remove interaction commands
        """
    def remove_command(self, arg0: str) -> Interactor:
        """
        Remove a command
        """
    def request_render(self) -> Interactor:
        """
        Request a render on the next event loop
        """
    def start(self, delta_time: float = 0.03333333333333333, user_callback: typing.Callable[[], None] = None) -> Interactor:
        """
        Start the interactor and the event loop
        """
    def start_animation(self) -> Interactor:
        """
        Start the animation
        """
    def stop(self) -> Interactor:
        """
        Stop the interactor and the event loop
        """
    def stop_animation(self) -> Interactor:
        """
        Stop the animation
        """
    def toggle_animation(self) -> Interactor:
        """
        Toggle the animation
        """
    def trigger_command(self, command: str, keep_comments: bool = True) -> bool:
        """
        Trigger a command
        """
    def trigger_keyboard_key(self, arg0: Interactor.InputAction, arg1: str) -> Interactor:
        """
        Trigger a keyboard input
        """
    def trigger_mod_update(self, arg0: Interactor.InputModifier) -> Interactor:
        """
        Trigger a key modifier update
        """
    def trigger_mouse_button(self, arg0: Interactor.InputAction, arg1: Interactor.MouseButton) -> Interactor:
        """
        Trigger a mouse button
        """
    def trigger_mouse_position(self, arg0: float, arg1: float) -> Interactor:
        """
        Trigger a mouse position
        """
    def trigger_mouse_wheel(self, arg0: Interactor.WheelDirection) -> Interactor:
        """
        Trigger a mouse wheel
        """
    def trigger_text_character(self, arg0: int) -> Interactor:
        """
        Trigger a text character input
        """
class LibInformation:
    @property
    def build_date(self) -> str:
        ...
    @property
    def build_system(self) -> str:
        ...
    @property
    def compiler(self) -> str:
        ...
    @property
    def copyrights(self) -> list[str]:
        ...
    @property
    def license(self) -> str:
        ...
    @property
    def modules(self) -> dict[str, bool]:
        ...
    @property
    def version(self) -> str:
        ...
    @property
    def version_full(self) -> str:
        ...
    @property
    def vtk_version(self) -> str:
        ...
class LightState:
    color: Color
    direction: tuple[float, float, float]
    intensity: float
    position: tuple[float, float, float]
    positional_light: bool
    switch_state: bool
    type: LightType
    @typing.overload
    def __init__(self) -> None:
        ...
    @typing.overload
    def __init__(self, type: LightType = f3d.LightType.SCENE_LIGHT, position: tuple[float, float, float] = (0.0, 0.0, 0.0), color: Color = ..., direction: tuple[float, float, float] = (1.0, 0.0, 0.0), positional_light: bool = False, intensity: float = 1.0, switch_state: bool = True) -> None:
        ...
class LightType:
    """
    Members:
    
      HEADLIGHT
    
      CAMERA_LIGHT
    
      SCENE_LIGHT
    """
    CAMERA_LIGHT: typing.ClassVar[LightType]  # value = <LightType.CAMERA_LIGHT: 2>
    HEADLIGHT: typing.ClassVar[LightType]  # value = <LightType.HEADLIGHT: 1>
    SCENE_LIGHT: typing.ClassVar[LightType]  # value = <LightType.SCENE_LIGHT: 3>
    __members__: typing.ClassVar[dict[str, LightType]]  # value = {'HEADLIGHT': <LightType.HEADLIGHT: 1>, 'CAMERA_LIGHT': <LightType.CAMERA_LIGHT: 2>, 'SCENE_LIGHT': <LightType.SCENE_LIGHT: 3>}
    def __eq__(self, other: typing.Any) -> bool:
        ...
    def __getstate__(self) -> int:
        ...
    def __hash__(self) -> int:
        ...
    def __index__(self) -> int:
        ...
    def __init__(self, value: int) -> None:
        ...
    def __int__(self) -> int:
        ...
    def __ne__(self, other: typing.Any) -> bool:
        ...
    def __repr__(self) -> str:
        ...
    def __setstate__(self, state: int) -> None:
        ...
    def __str__(self) -> str:
        ...
    @property
    def name(self) -> str:
        ...
    @property
    def value(self) -> int:
        ...
class Log:
    class VerboseLevel:
        """
        Members:
        
          DEBUG
        
          INFO
        
          WARN
        
          ERROR
        
          QUIET
        """
        DEBUG: typing.ClassVar[Log.VerboseLevel]  # value = <VerboseLevel.DEBUG: 0>
        ERROR: typing.ClassVar[Log.VerboseLevel]  # value = <VerboseLevel.ERROR: 3>
        INFO: typing.ClassVar[Log.VerboseLevel]  # value = <VerboseLevel.INFO: 1>
        QUIET: typing.ClassVar[Log.VerboseLevel]  # value = <VerboseLevel.QUIET: 4>
        WARN: typing.ClassVar[Log.VerboseLevel]  # value = <VerboseLevel.WARN: 2>
        __members__: typing.ClassVar[dict[str, Log.VerboseLevel]]  # value = {'DEBUG': <VerboseLevel.DEBUG: 0>, 'INFO': <VerboseLevel.INFO: 1>, 'WARN': <VerboseLevel.WARN: 2>, 'ERROR': <VerboseLevel.ERROR: 3>, 'QUIET': <VerboseLevel.QUIET: 4>}
        def __eq__(self, other: typing.Any) -> bool:
            ...
        def __getstate__(self) -> int:
            ...
        def __hash__(self) -> int:
            ...
        def __index__(self) -> int:
            ...
        def __init__(self, value: int) -> None:
            ...
        def __int__(self) -> int:
            ...
        def __ne__(self, other: typing.Any) -> bool:
            ...
        def __repr__(self) -> str:
            ...
        def __setstate__(self, state: int) -> None:
            ...
        def __str__(self) -> str:
            ...
        @property
        def name(self) -> str:
            ...
        @property
        def value(self) -> int:
            ...
    DEBUG: typing.ClassVar[Log.VerboseLevel]  # value = <VerboseLevel.DEBUG: 0>
    ERROR: typing.ClassVar[Log.VerboseLevel]  # value = <VerboseLevel.ERROR: 3>
    INFO: typing.ClassVar[Log.VerboseLevel]  # value = <VerboseLevel.INFO: 1>
    QUIET: typing.ClassVar[Log.VerboseLevel]  # value = <VerboseLevel.QUIET: 4>
    WARN: typing.ClassVar[Log.VerboseLevel]  # value = <VerboseLevel.WARN: 2>
    @staticmethod
    def get_verbose_level() -> Log.VerboseLevel:
        ...
    @staticmethod
    def print(arg0: Log.VerboseLevel, arg1: str) -> None:
        ...
    @staticmethod
    def set_use_coloring(arg0: bool) -> None:
        ...
    @staticmethod
    def set_verbose_level(level: Log.VerboseLevel, force_std_err: bool = False) -> None:
        ...
class Mesh:
    face_indices: list[int]
    face_sides: list[int]
    normals: list[float]
    points: list[float]
    texture_coordinates: list[float]
    @typing.overload
    def __init__(self) -> None:
        ...
    @typing.overload
    def __init__(self, points: typing.Sequence[float], normals: typing.Sequence[float] = [], texture_coordinates: typing.Sequence[float] = [], face_sides: typing.Sequence[int] = [], face_indices: typing.Sequence[int] = []) -> None:
        ...
class Options:
    def __getitem__(self, arg0: str) -> bool | int | float | str | list[float] | list[int]:
        ...
    def __init__(self) -> None:
        ...
    def __iter__(self) -> typing.Iterator[typing.Any]:
        ...
    def __len__(self) -> int:
        ...
    def __setitem__(self, arg0: str, arg1: bool | int | float | str | typing.Sequence[float] | typing.Sequence[int]) -> None:
        ...
    def copy(self, arg0: Options, arg1: str) -> Options:
        ...
    def get_closest_option(self, arg0: str) -> tuple[str, int]:
        ...
    def is_same(self, arg0: Options, arg1: str) -> bool:
        ...
    def keys(self) -> list[str]:
        ...
    def toggle(self, arg0: str) -> Options:
        ...
    def update(self, arg: typing.Union[typing.Mapping[str, typing.Any], typing.Iterable[tuple[str, typing.Any]]]) -> None:
        ...
class ReaderInformation:
    @property
    def description(self) -> str:
        ...
    @property
    def extensions(self) -> list[str]:
        ...
    @property
    def has_geometry_reader(self) -> bool:
        ...
    @property
    def has_scene_reader(self) -> bool:
        ...
    @property
    def mime_types(self) -> list[str]:
        ...
    @property
    def name(self) -> str:
        ...
    @property
    def plugin_name(self) -> str:
        ...
class Scene:
    @typing.overload
    def add(self, file_path: os.PathLike[str]) -> Scene:
        """
        Add a file the scene
        """
    @typing.overload
    def add(self, file_path_vector: typing.Sequence[os.PathLike[str]]) -> Scene:
        """
        Add multiple filepaths to the scene
        """
    @typing.overload
    def add(self, file_name_vector: typing.Sequence[str]) -> Scene:
        """
        Add multiple filenames to the scene
        """
    @typing.overload
    def add(self, mesh: Mesh) -> Scene:
        """
        Add a surfacic mesh from memory into the scene
        """
    def add_light(self, light_state: LightState) -> int:
        """
        Add a light to the scene
        """
    def animation_time_range(self) -> tuple[float, float]:
        ...
    def available_animations(self) -> int:
        ...
    def clear(self) -> Scene:
        ...
    def get_light(self, index: int) -> LightState:
        """
        Get a light from the scene
        """
    def get_light_count(self) -> int:
        """
        Get the number of lights in the scene
        """
    def load_animation_time(self, arg0: float) -> Scene:
        ...
    def remove_all_lights(self) -> Scene:
        """
        Remove all lights from the scene
        """
    def remove_light(self, index: int) -> Scene:
        """
        Remove a light from the scene
        """
    def supports(self, arg0: os.PathLike[str]) -> bool:
        ...
    def update_light(self, index: int, light_state: LightState) -> Scene:
        """
        Update a light in the scene
        """
class Utils:
    class KnownFolder:
        """
        Members:
        
          ROAMINGAPPDATA
        
          LOCALAPPDATA
        
          PICTURES
        """
        LOCALAPPDATA: typing.ClassVar[Utils.KnownFolder]  # value = <KnownFolder.LOCALAPPDATA: 1>
        PICTURES: typing.ClassVar[Utils.KnownFolder]  # value = <KnownFolder.PICTURES: 2>
        ROAMINGAPPDATA: typing.ClassVar[Utils.KnownFolder]  # value = <KnownFolder.ROAMINGAPPDATA: 0>
        __members__: typing.ClassVar[dict[str, Utils.KnownFolder]]  # value = {'ROAMINGAPPDATA': <KnownFolder.ROAMINGAPPDATA: 0>, 'LOCALAPPDATA': <KnownFolder.LOCALAPPDATA: 1>, 'PICTURES': <KnownFolder.PICTURES: 2>}
        def __eq__(self, other: typing.Any) -> bool:
            ...
        def __getstate__(self) -> int:
            ...
        def __hash__(self) -> int:
            ...
        def __index__(self) -> int:
            ...
        def __init__(self, value: int) -> None:
            ...
        def __int__(self) -> int:
            ...
        def __ne__(self, other: typing.Any) -> bool:
            ...
        def __repr__(self) -> str:
            ...
        def __setstate__(self, state: int) -> None:
            ...
        def __str__(self) -> str:
            ...
        @property
        def name(self) -> str:
            ...
        @property
        def value(self) -> int:
            ...
    LOCALAPPDATA: typing.ClassVar[Utils.KnownFolder]  # value = <KnownFolder.LOCALAPPDATA: 1>
    PICTURES: typing.ClassVar[Utils.KnownFolder]  # value = <KnownFolder.PICTURES: 2>
    ROAMINGAPPDATA: typing.ClassVar[Utils.KnownFolder]  # value = <KnownFolder.ROAMINGAPPDATA: 0>
    @staticmethod
    def collapse_path(arg0: os.PathLike[str], arg1: os.PathLike[str]) -> os.PathLike[str]:
        ...
    @staticmethod
    def get_env(arg0: str) -> str | None:
        ...
    @staticmethod
    def get_known_folder(arg0: Utils.KnownFolder) -> str | None:
        ...
    @staticmethod
    def glob_to_regex(glob: str, path_separator: str = '/') -> str:
        ...
    @staticmethod
    def text_distance(arg0: str, arg1: str) -> int:
        ...
    @staticmethod
    def tokenize(str: str, keep_comments: bool = True) -> list[str]:
        ...
class Window:
    class Type:
        """
        Members:
        
          NONE
        
          EXTERNAL
        
          GLX
        
          WGL
        
          COCOA
        
          EGL
        
          OSMESA
        
          UNKNOWN
        """
        COCOA: typing.ClassVar[Window.Type]  # value = <Type.COCOA: 4>
        EGL: typing.ClassVar[Window.Type]  # value = <Type.EGL: 5>
        EXTERNAL: typing.ClassVar[Window.Type]  # value = <Type.EXTERNAL: 1>
        GLX: typing.ClassVar[Window.Type]  # value = <Type.GLX: 2>
        NONE: typing.ClassVar[Window.Type]  # value = <Type.NONE: 0>
        OSMESA: typing.ClassVar[Window.Type]  # value = <Type.OSMESA: 6>
        UNKNOWN: typing.ClassVar[Window.Type]  # value = <Type.UNKNOWN: 8>
        WGL: typing.ClassVar[Window.Type]  # value = <Type.WGL: 3>
        __members__: typing.ClassVar[dict[str, Window.Type]]  # value = {'NONE': <Type.NONE: 0>, 'EXTERNAL': <Type.EXTERNAL: 1>, 'GLX': <Type.GLX: 2>, 'WGL': <Type.WGL: 3>, 'COCOA': <Type.COCOA: 4>, 'EGL': <Type.EGL: 5>, 'OSMESA': <Type.OSMESA: 6>, 'UNKNOWN': <Type.UNKNOWN: 8>}
        def __eq__(self, other: typing.Any) -> bool:
            ...
        def __getstate__(self) -> int:
            ...
        def __hash__(self) -> int:
            ...
        def __index__(self) -> int:
            ...
        def __init__(self, value: int) -> None:
            ...
        def __int__(self) -> int:
            ...
        def __ne__(self, other: typing.Any) -> bool:
            ...
        def __repr__(self) -> str:
            ...
        def __setstate__(self, state: int) -> None:
            ...
        def __str__(self) -> str:
            ...
        @property
        def name(self) -> str:
            ...
        @property
        def value(self) -> int:
            ...
    COCOA: typing.ClassVar[Window.Type]  # value = <Type.COCOA: 4>
    EGL: typing.ClassVar[Window.Type]  # value = <Type.EGL: 5>
    EXTERNAL: typing.ClassVar[Window.Type]  # value = <Type.EXTERNAL: 1>
    GLX: typing.ClassVar[Window.Type]  # value = <Type.GLX: 2>
    NONE: typing.ClassVar[Window.Type]  # value = <Type.NONE: 0>
    OSMESA: typing.ClassVar[Window.Type]  # value = <Type.OSMESA: 6>
    UNKNOWN: typing.ClassVar[Window.Type]  # value = <Type.UNKNOWN: 8>
    WGL: typing.ClassVar[Window.Type]  # value = <Type.WGL: 3>
    height: int
    size: tuple[int, int]
    width: int
    def get_display_from_world(self, arg0: tuple[float, float, float]) -> tuple[float, float, float]:
        """
        Get display coordinate point from world coordinate
        """
    def get_world_from_display(self, arg0: tuple[float, float, float]) -> tuple[float, float, float]:
        """
        Get world coordinate point from display coordinate
        """
    def render(self) -> bool:
        """
        Render the window
        """
    def render_to_image(self, no_background: bool = False) -> Image:
        """
        Render the window to an image
        """
    def set_icon(self, arg0: int, arg1: int) -> Window:
        """
        Set the icon of the window using a memory buffer representing a PNG file
        """
    def set_position(self, arg0: int, arg1: int) -> Window:
        ...
    def set_window_name(self, arg0: str) -> Window:
        """
        Set the window name
        """
    @property
    def camera(self) -> Camera:
        ...
    @property
    def offscreen(self) -> bool:
        ...
    @property
    def type(self) -> Window.Type:
        ...
CAMERA_LIGHT: LightType  # value = <LightType.CAMERA_LIGHT: 2>
HEADLIGHT: LightType  # value = <LightType.HEADLIGHT: 1>
SCENE_LIGHT: LightType  # value = <LightType.SCENE_LIGHT: 3>
