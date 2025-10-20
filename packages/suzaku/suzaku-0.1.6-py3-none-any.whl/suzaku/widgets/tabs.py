from ..const import Orient
from ..event import SkEvent
from .card import SkCard
from .container import SkContainer
from .frame import SkFrame
from .separator import SkSeparator
from .tabbar import SkTabBar
from .widget import SkWidget


class SkTabs(SkCard):
    """A tabs widget"""

    def __init__(
        self,
        parent: SkContainer,
        *,
        style: str = "SkTabs",
        expand: bool = True,
        **kwargs,
    ) -> None:
        super().__init__(parent, style=style, **kwargs)

        self.tabs = []
        self.selected: SkFrame | None = None
        self.tabbar: SkTabBar = SkTabBar(self, expand=expand)
        self.tabbar.box(side="top", padx=2, pady=(2, 0))
        self.tabbar.bind("selected", self._select)
        self.separator = SkSeparator(self, orient=Orient.H)
        self.separator.box(side="top", padx=0, pady=0)

    def select(self, index: int) -> None:
        """Select a tab by index
        :param index: The tab index
        :return: None
        """
        self.tabbar.select(index)

    def _select(self, event: SkEvent) -> None:
        """Select a tab by index
        :param index: The tab index
        :return: None
        """
        if self.tabbar.items[event["index"]] == self.selected:
            return
        if self.selected:
            self.selected.layout_forget()
        self.selected = self.tabs[event["index"]]
        self.selected.box(side="bottom", expand=True, padx=0, pady=(0, 0))

    def add(self, tab: SkContainer, text: str | None = "") -> SkWidget:
        """Add a tab
        :param tab: The container
        :param text: The tab text
        :return: The tab widget
        """
        self.tabs.append(tab)
        return self.tabbar.add(text)
