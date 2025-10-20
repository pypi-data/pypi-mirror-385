import skia

from ..event import SkEvent
from ..var import SkBooleanVar
from .container import SkContainer
from .textbutton import SkTextButton


class SkListItem(SkTextButton):
    def __init__(
        self,
        parent: SkContainer,
        text: str = None,
        style: str = "SkListBox.Item",
        align: str = "left",
        **kwargs,
    ):
        super().__init__(
            parent,
            style=style,
            text=text,
            align=align,
            command=lambda: self._on_click(),
            **kwargs,
        )

    @property
    def selected(self):
        if self.parent.selected_item is None:
            return False
        return self.parent.selected_item == self

    def _on_click(self):
        self.parent.select(self)

    def draw_widget(
        self, canvas: skia.Canvas, rect: skia.Rect, style_selector: str | None = None
    ) -> None:
        if self.selected:
            style_selector = f"{self.style_name}:selected"
        else:
            if self.is_mouse_floating:
                if self.is_mouse_press:
                    style_selector = f"{self.style_name}:press"
                else:
                    style_selector = f"{self.style_name}:hover"

        super().draw_widget(canvas, rect, style_selector)
