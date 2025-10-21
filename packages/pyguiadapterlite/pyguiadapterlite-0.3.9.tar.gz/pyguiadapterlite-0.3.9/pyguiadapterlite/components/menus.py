import dataclasses
from tkinter import BooleanVar
from typing import List, Union, Optional, Callable, ForwardRef

from pyguiadapterlite.utils import _error

BaseWindow_ = ForwardRef("BaseWindow")
Action_ = ForwardRef("Action")

ActionTriggeredCallback = Callable[[BaseWindow_, Action_], None]
ActionToggledCallback = Callable[[BaseWindow_, Action_, bool], None]


@dataclasses.dataclass
class Action(object):
    """该类用于创建动作（`Action`），在菜单（`Menu`）中，一个`Action`代表一个菜单项。"""

    text: str
    """菜单项显示的文本。"""

    on_triggered: Optional[ActionTriggeredCallback] = None
    """回调函数，在菜单项被触发时回调，被触发一般是指用户点击了菜单项或按下对应的快捷键（仅在指定了快捷键时有效）。"""

    enabled: bool = True
    """菜单项是否处于启用状态。"""

    checkable: bool = False
    """菜单项是否为**`可选中的`**。`可选中`的菜单项具有`选中`和`未选中`两种状态。"""

    initial_checked: bool = False
    """菜单项初始是否处于`选中`状态，仅在`checkable`为`True`时有效。"""

    shortcut: Optional[str] = None
    """菜单项的快捷键，例如：Control+o，若指定了快捷键，将在按下快捷键时触发`on_triggered`回调。"""

    data: Optional[object] = None
    """用户自定义数据。"""

    def bind_checked_var(self, checked_var: BooleanVar):
        setattr(self, "__checked__", checked_var)

    def is_checked(self) -> bool:
        if not self.checkable:
            return False
        checked_var = getattr(self, "__checked__", None)
        if isinstance(checked_var, BooleanVar):
            return checked_var.get()
        else:
            _error("checked variable not bind to action")
            return False

    def set_checked(self, checked: bool):
        if not self.checkable:
            return
        checked_var = getattr(self, "__checked__", None)
        if not checked_var:
            _error("checked variable not bind to action")
            return
        checked_var.set(checked)

    def get_exclusive_group_id(self) -> Optional[int]:
        if not self.checkable:
            return None
        return getattr(self, "__group_id__", None)

    def add_to_exclusive_group(self, group_id: int):
        if not self.checkable:
            return
        setattr(self, "__group_id__", group_id)


@dataclasses.dataclass(frozen=True)
class Separator(object):
    """代表了一个分割符，可以用其来分割菜单栏上的菜单项。"""

    pass


@dataclasses.dataclass(frozen=True)
class Menu(object):
    """该类用于配置窗口菜单栏上的菜单。"""

    title: str
    """菜单的标题。"""

    actions: List[Union[Action, Separator, "Menu"]]
    """菜单下的菜单项（`Action`）、分隔符（`Separator`）或子菜单（`Menu`）"""

    tear_off_enabled: bool = True
    """菜单可以被“撕下”。为`True`时，菜单将包含一个特殊的“撕下”项（通常显示为菜单顶部的虚线）。"""

    exclusive: bool = False
    """是否将菜单下的菜单项（`Action`）添加到一个互斥组中。只有当前菜单下`checkable`属性为`True`的菜单项（`Action`）才会被添加的互斥组中。"""

    def remove_action(self, action: Union[str, Action, Separator, "Menu"]):
        if isinstance(action, str):
            for action_ in self.actions:
                if isinstance(action_, Action):
                    if action_.text == action:
                        action = action_
                        break
                if isinstance(action_, Menu):
                    if action_.title == action:
                        action = action_
                        break
            if action in self.actions:
                self.actions.remove(action)
            return
        if action in self.actions:
            self.actions.remove(action)
            return
