import dataclasses
from tkinter import Widget
from typing import Type, Any, Optional, Union, Literal

from pyguiadapterlite.components.colorlabel import ColorLabel
from pyguiadapterlite.components.valuewidget import (
    BaseParameterWidget,
    BaseParameterWidgetConfig,
    GetValueError,
    InvalidValue,
    SetValueError,
)
from pyguiadapterlite.utils import _error


@dataclasses.dataclass(frozen=True)
class HexColorValue(BaseParameterWidgetConfig):
    default_value: str = "#000000"

    color_picker_title: str = ""
    """颜色选择对话框的标题"""

    show_color_code: bool = True
    """是否显示颜色代码"""

    show_color_picker: bool = True
    """是否启用颜色选择对话框，启用时单击颜色标签会弹出颜色选择对话框"""

    width: Optional[int] = None
    """颜色标签的宽度"""

    height: Optional[int] = 1
    """颜色标签的高度"""

    borderwidth: int = 1
    """颜色标签的边框宽度"""

    relief: Literal["flat", "raised", "sunken", "groove", "ridge"] = "flat"
    """颜色标签的边框样式"""

    font: Union[tuple, str] = ("Arial", 13, "bold")
    """颜色标签的字体"""

    @classmethod
    def target_widget_class(cls) -> Type["HexColorValueWidget"]:
        return HexColorValueWidget


class HexColorValueWidget(BaseParameterWidget):
    ConfigClass = HexColorValue

    def __init__(self, parent: Widget, parameter_name: str, config: HexColorValue):
        super().__init__(parent, parameter_name, config)

        self._build_flag = False
        self._value_widget: Optional[ColorLabel] = None

    @property
    def config(self) -> HexColorValue:
        return super().config

    def get_value(self) -> Union[str, InvalidValue]:
        if not self._value_widget:
            raise RuntimeError("input widget not created yet")
        try:
            return self._value_widget.current_color
        except GetValueError as e:
            self.on_parameter_error(self._parameter_name, e)
            return InvalidValue(raw_value=e.raw_value, exception=e)

    def set_value(self, value: str) -> Union[str, InvalidValue]:
        if not self._value_widget:
            raise RuntimeError("input widget not created yet")
        try:
            self._value_widget.current_color = value
            return value
        except SetValueError as e:
            self.on_parameter_error(self._parameter_name, e)
            return InvalidValue(raw_value=e.raw_value, exception=e)

    def build(self) -> "HexColorValueWidget":
        if self._build_flag:
            return self
        self._build_flag = True
        config = self.config
        self._value_widget = ColorLabel(
            self,
            color_picker=config.show_color_picker,
            show_color_code=config.show_color_code,
            color_picker_title=config.color_picker_title,
            font=self.config.font,
            width=config.width,
            height=config.height,
            borderwidth=config.borderwidth,
            relief=config.relief,
        )
        self.color_flash_effect.set_target(self)
        # noinspection PyTypeChecker
        self._value_widget.pack(side="left", fill="both", expand=True, padx=1, pady=1)
        self._value_widget.current_color = self._config.default_value
        return self

    def on_parameter_error(self, parameter_name: str, error: Any) -> None:
        if parameter_name == self._parameter_name:
            if isinstance(error, GetValueError):
                _error(
                    f"failed to get value from widget of parameter `{parameter_name}`: {error}"
                )
                self.start_invalid_value_effect()
                return
