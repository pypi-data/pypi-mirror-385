import dataclasses
from tkinter import Widget
from typing import Type, Any, Union, Optional, List, Literal

from pyguiadapterlite.components.combo import ComboBox
from pyguiadapterlite.components.valuewidget import (
    BaseParameterWidgetConfig,
    BaseParameterWidget,
    InvalidValue,
)
from pyguiadapterlite.core.fn import ParameterInfo


@dataclasses.dataclass(frozen=True)
class LooseChoiceValue(BaseParameterWidgetConfig):
    default_value: Optional[str] = None

    choices: List[str] = dataclasses.field(default_factory=list)
    """可选项列表"""

    readonly: bool = False
    """是否只读，若为True则用户只能从可选项列表中选择，为False则用户可以输入自定义值"""

    justify: Literal["left", "center", "right"] = "left"
    """对齐方式"""

    add_user_input: bool = False
    """是否将用户输入自定义值添加到可选项列表中"""

    @classmethod
    def target_widget_class(cls) -> Type["LooseChoiceValueWidget"]:
        return LooseChoiceValueWidget


class LooseChoiceValueWidget(BaseParameterWidget):

    ConfigClass = LooseChoiceValue

    def __init__(
        self,
        parent: Widget,
        parameter_name: str,
        config: LooseChoiceValue,
    ):
        self._is_built = False
        self._value_widget: Optional[ComboBox] = None

        super().__init__(parent, parameter_name, config)

    @property
    def config(self) -> LooseChoiceValue:
        return super().config

    def get_value(self) -> Union[Any, InvalidValue]:
        try:
            value = self._value_widget.current_value
        except Exception as e:
            value = InvalidValue(raw_value=None, exception=e)
        return value

    def set_value(self, value: Any) -> Union[Any, InvalidValue]:
        try:
            self._value_widget.current_value = value
        except Exception as e:
            return InvalidValue(raw_value=value, exception=e)
        return value

    def build(self) -> "BaseParameterWidget":
        if self._is_built:
            return self
        self._value_widget = ComboBox(
            self,
            choices=self.config.choices,
            readonly=self.config.readonly,
            justify=self.config.justify,
            add_user_input=self.config.add_user_input,
        )
        self._value_widget.pack(fill="x", expand=False, padx=1, pady=1)
        self.color_flash_effect.set_target(self)
        self._is_built = True
        self.set_value(self.config.default_value)
        return self

    @classmethod
    def on_post_process_config(
        cls,
        config: LooseChoiceValue,
        parameter_name: str,
        parameter_info: "ParameterInfo",
    ) -> BaseParameterWidgetConfig:
        if isinstance(parameter_info.default_value, cls.ConfigClass):
            return parameter_info.default_value

        if (
            isinstance(config.default_value, (tuple, list, set))
            and len(config.default_value) > 0
            and (not config.choices)
        ):
            config = dataclasses.replace(
                config,
                default_value=None,
                choices=[str(v) for v in config.default_value],
            )
            return config
        return config
