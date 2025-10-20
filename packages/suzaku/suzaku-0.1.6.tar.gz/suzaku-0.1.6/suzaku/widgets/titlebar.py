import ctypes
from sys import platform

from ..event import SkEvent
from .card import SkCard
from .container import SkContainer
from .image import SkImage
from .text import SkText
from .textbutton import SkCloseButton, SkMaximizeButton, SkMinimizeButton


class SkWindowCommand(SkCard):
    def __init__(
        self,
        parent: SkContainer,
        style: str = "SkWindowCommand",
        **kwargs,
    ):
        super().__init__(parent, style=style, **kwargs)
        self.close = SkCloseButton(
            self, command=lambda: self.window.can_be_close(True)
        ).box(side="right", padx=0, pady=0, expand=True)
        self.maximize = SkMaximizeButton(self).box(
            side="right", padx=0, pady=0, expand=True
        )
        self.minimize = SkMinimizeButton(self).box(
            side="right", padx=0, pady=0, expand=True
        )


class SkTitleBar(SkCard):
    def __init__(
        self,
        parent: SkContainer,
        style: str = "SkTitleBar",
        **kwargs,
    ):
        super().__init__(parent, style=style, **kwargs)

        self.icon = SkImage(self, path=self.window.wm_iconpath())
        self.icon.resize(15, 15)
        self.icon.box(side="left", padx=(10, 0))

        self.title = SkText(self, text=self.window.title())
        self.title.box(
            side="left",
        )

        self.command = SkWindowCommand(self)
        self.command.box(side="right", padx=3, pady=3)

        self.bind("mouse_press", self._mouse_press)
        self.bind("double_click", self._double_click)
        self.title.bind("mouse_press", self._mouse_press)
        self.title.bind("double_click", self._double_click)
        self.window.bind("mouse_motion", self._mouse_motion)
        self.window.bind("mouse_release", self._mouse_release)
        self.window.bind("configure", self._window_configure)

        self._x1 = None
        self._y1 = None

    def _window_configure(self, event: SkEvent):
        """When the window is configured, update the title."""
        self.title.configure(text=self.window.title())

    def _double_click(self, event: SkEvent):
        """当双击标题栏时，最大化或恢复窗口"""
        if self.window.window_attr("maximized"):
            self.window.restore()
        else:
            self.window.maximize()

    def _mouse_press(self, event: SkEvent):
        """When the mouse is pressed, record the initial position."""
        if (
            not self.window.mouse_anchor(event["x"], event["y"])
            # or self.window.window_attr("maximized")
        ) or not self.window.resizable():
            self._x1 = event["x"]
            self._y1 = event["y"]

    def _mouse_motion(self, event: SkEvent):
        """When the mouse is moved, move the window based on the initial position."""
        if self._x1 and self._y1:
            # 当窗口最大化时移动窗口，则恢复并根据原先鼠标位置占窗口宽度的比例来计算恢复后鼠标的x坐标
            if self.window.window_attr("maximized"):
                p = self._x1 / self.window.width
                self.window.restore()
                self._x1 = self.width * p
            self.window.move(
                event["rootx"] - self._x1,
                event["rooty"] - self._y1,
            )
            """if platform == "win32":
                WM_SYSCOMMAND = 274
                SC_MOVE = 61456
                HTCAPTION = 2

                # ctypes.windll.user32.ReleaseCapture()
                ctypes.windll.user32.SendMessageA(
                    ctypes.windll.user32.GetParent(self.window.window_id),
                    SC_MOVE,
                    0,
                )"""

    def _mouse_release(self, event: SkEvent):
        """When the mouse is released, clear the initial position."""
        self._x1 = None
        self._y1 = None


def titlebar(window):
    window.window_attr("border", False)
    return SkTitleBar(window).box(side="top", padx=0, pady=0)
