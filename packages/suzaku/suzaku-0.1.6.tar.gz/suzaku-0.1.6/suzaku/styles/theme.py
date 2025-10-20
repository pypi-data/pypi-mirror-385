from __future__ import annotations as _

import json
import os
import pathlib
import re
import typing
import warnings

from . import color

if typing.TYPE_CHECKING:
    from ..widgets.widget import SkWidget


class SkStyleNotFoundError(NameError):
    """Will be raised when a theme is not found."""

    pass


class SkTheme:
    """Theme class for SkWindow and SkWidgets.

    Example
    -------
    .. code-block:: python
        my_theme = SkTheme({<Some styles>})
        my_sub_theme = SkTheme(parent="default.light")
        my_external_theme = SkTheme().load_from_file("./path/to/a/theme.json")
    This shows examples of creating themes, either from a json, a parent theme or a file.

    .. code-block:: python
        all_themes = SkTheme.loaded_themes
        internal_themes = SkTheme.INTERNAL_THEMES
        default_theme = SkTheme.DEFAULT_THEME
    This shows getting all loaded themes, internal themes, and the default theme.

    .. code-block:: python
        default_light_theme = SkTheme.find_loaded_theme("default.light")
        if SkTheme.validate_theme_existed("default.light"):
            print("Default light theme exists!")
    This shows finding a theme and checking if it exists

    """

    loaded_themes: list["SkTheme"] = []
    INTERNAL_THEME_DIR = pathlib.Path(__file__).parent.parent / "resources" / "themes"
    INTERNAL_THEMES: dict[str, "SkTheme"] = {}
    DEFAULT_THEME: "SkTheme"
    DEFAULT_THEME_FILENAME: str = "light"

    @classmethod
    def _load_internal_themes(cls):
        """Load internal themes. Should be run once at import, see the end of this file."""
        # Load default (ROOT) theme
        SkTheme.DEFAULT_THEME = SkTheme({}).load_from_file(
            SkTheme.INTERNAL_THEME_DIR / f"{SkTheme.DEFAULT_THEME_FILENAME}.json"
        )

        # Load other internal themes
        for file in os.listdir(SkTheme.INTERNAL_THEME_DIR):
            if file == f"{SkTheme.DEFAULT_THEME_FILENAME}.json":
                # For default theme, no need to reload it
                SkTheme.INTERNAL_THEMES[SkTheme.DEFAULT_THEME.name] = (
                    SkTheme.DEFAULT_THEME
                )
                continue
            _ = SkTheme({}).load_from_file(SkTheme.INTERNAL_THEME_DIR / file)
            SkTheme.INTERNAL_THEMES[_.name] = _

    @classmethod
    def find_loaded_theme(cls, theme_name: str) -> "SkTheme | typing.Literal[False]":
        """Search for a loaded theme by name, returns the SkTheme object if found, or False if not.

        Example
        -------
        .. code-block:: python
            default_theme = SkTheme.find_loaded_theme("default.light")
        This returns the SkTheme object of the default theme to `default_theme`.

        :param theme_name: Name of the theme to load
        :return: The SkTheme object if found, otherwise False
        """
        for theme in cls.loaded_themes:
            if theme.name == theme_name:
                return theme
        return False

    @classmethod
    def validate_theme_existed(cls, theme_name: str) -> bool:
        """Validate if the theme with given name existed and loaded.

        Example
        -------
        .. code-block:: python
            SkTheme.validate_theme_existed("default.light")
        This returns if the theme `default.light` is loaded.

        :param theme_name: Name of the theme to validate
        :return: If the theme loaded
        """
        return SkTheme.find_loaded_theme(theme_name) != False  # ☝🤓

    def __init__(
        self, styles: dict | None = None, parent: typing.Union["SkTheme", None] = None
    ) -> None:
        """Theme for SkWindow and SkWidgets.

        Example
        -------
        .. code-block:: python
            my_theme = SkTheme({<Some styles>})
            my_sub_theme = SkTheme(parent="default.light")
            my_external_theme = SkTheme().load_from_file("./path/to/a/theme.json")
        This shows examples of creating themes, either from a json, a parent theme or a file.

        :param styles: Styles of the theme
        :param parent: Parent theme
        """

        self.name: str = f"untitled.{len(SkTheme.loaded_themes) + 1}"
        self.friendly_name = f"Untitled theme {len(SkTheme.loaded_themes) + 1}"
        # friendly_name感觉有点多余? ——Little White Cloud
        # Keep it 4 now currently. ——rgzz666
        self.parent: typing.Union["SkTheme", None] = parent
        self.children = []
        self.is_special = False

        self.styles: dict = styles
        if styles is None:
            self.styles: dict = SkTheme.DEFAULT_THEME.styles
        self.color_palette = {}

        SkTheme.loaded_themes.append(self)  # TODO: figure out.
        return

    def load_from_file(self, file_path: typing.Union[str, pathlib.Path]) -> "SkTheme":
        """Load styles to theme from a file.

        Example
        -------
        .. code-block:: python
            my_theme = SkTheme().load_from_file("./path/to/a/theme.json")
            my_theme.load_from_file("./path/to/another/theme.json")

        This shows loading a theme to `my_theme` from the theme file at `./path/to/a/theme.json`,
        and change it to theme from `./path/to/another/theme.json` later.

        :param file_path: Path to the theme file
        :return self: The SkTheme itself
        """
        # We need a file to load from file \o/ \o/ \o/
        with open(file_path, mode="r", encoding="utf-8") as f:
            style_raw = f.read()
            theme_data = json.loads(style_raw)
            if (
                search_result := SkTheme.find_loaded_theme(theme_data["name"])
            ) != False:
                # If name already occupied, meaning the theme might already be loaded
                # (or just simply has an occupied name)
                warnings.warn(
                    f"Theme <{theme_data['name']}> already loaded or existed.",
                    RuntimeWarning,
                )
                return search_result

        return self.load_from_json(theme_data)

    def load_from_json(self, theme_data: dict) -> "SkTheme":
        """Load all data (including metadata) to the theme.

        Example
        -------
        .. code-block:: python
            my_theme = SkTheme().load_from_json({<Some JSON theme data>})
            my_theme.load_from_json({<Some JSON theme data>})
        This shows loading a theme to `my_theme` from json data, and change it to theme from
        another json later.

        :param theme_data: dict that contains the theme data
        :return self: The SkTheme itself
        """
        # Type check
        EXPECTED_DATA_TYPE = {
            "styles": dict,
            "color_palette": dict,
            "name": str,
            "friendly_name": str,
            "base": str,
        }
        for item in EXPECTED_DATA_TYPE.keys():
            if type(theme_data[item]) != EXPECTED_DATA_TYPE[item]:
                theme_name = (
                    theme_data["name"]
                    if type(theme_data["name"]) is str
                    else "(Type error)"
                )
                warnings.warn(
                    f"Error data type of <{item}> in theme data that is about to be loaded. "
                    f"Expected {EXPECTED_DATA_TYPE[item]} but got {type(item)}. The json data with "
                    f"theme named <{theme_name}> will not be loaded to the theme <{self.name}>",
                    ResourceWarning,
                )
                return self
        # Load data
        self.styles = theme_data["styles"].copy()
        self.color_palette = theme_data["color_palette"].copy()
        # Load Metadata
        self.rename(theme_data["name"], theme_data["friendly_name"])
        self.set_parent(theme_data["base"])

        return self

    def load_styles_from_json(self, style_json: dict) -> "SkTheme":
        """Load styles to theme from a given dict.

        Example
        -------
        .. code-block:: python
            my_theme = SkTheme().load_styles_from_json({<Some styles>})
            my_theme.load_from_json({<Some styles>})
        This shows loading styles data to `my_theme` from json data, and change its styles from
        that stored in another json later.

        :param style_json: dict that contains the styles
        :return self: The SkTheme itself
        """
        # This just fucks everything from source json into the styles
        self.styles = style_json.copy()
        return self

    def set_parent(self, new_parent: str) -> "SkTheme":
        """Set the parent for the theme via string stored in theme json.

        Example
        -------
        .. code-block:: python
            my_theme = SkTheme().set_parent("DEFAULT")
            my_theme.set_parent("default.dark")
        The first line shows setting the parent of `my_theme` to the default theme, which is
        suggested for third-party themes that act as a root. The second line shows setting the
        parent of `my_theme` to `default.dark` after its creation.

        Parent Name
        -----------
        - `ROOT` means the theme does not have a parent. This is not recommended for third-party
          themes as fallback mechanisms will all stop working, use `DEFAULT` instead.
        - `DEFAULT` means the parent of the theme is the default internal theme.

        If the parent name is none of above, it should be the theme of the name and will be set as
        parent directly. However, if the theme specified is not yet loaded, parent will fall back
        to `DEFAULT`.

        :param parent_name: Name of the new parent, or the SkTheme object of it
        :return self: The SkTheme itself
        """
        match new_parent:
            case "ROOT":
                # If root theme, then no parent (which means no fallback)
                self.parent = None
            case "DEFAULT":
                # If default theme for parent, then... hmm... default theme for parent... 🤔
                self.parent = self.DEFAULT_THEME
            case SkTheme():
                # If is a SkTheme object, set it as parent
                self.parent = new_parent
            case _:
                # If else, find the theme
                search_result = SkTheme.find_loaded_theme(new_parent)
                if search_result != False:
                    self.parent = search_result
                else:
                    # When not found, fallback to default for parent
                    warnings.warn(
                        f"Parent theme specified with name <{new_parent}> is not yet loaded. "
                        "Will fall back to <DEFAULT> for parent instead."
                    )
                    self.set_parent("DEFAULT")
        if isinstance(self.parent, SkTheme):
            self.parent.children.append(self)
        return self

    def rename(self, new_name: str, friendly_name: str) -> "SkTheme":
        """Rename the theme.

        Example
        -------
        .. code-block:: python
            my_theme = Theme().rename("theme.name")
            my_theme.rename("i_hate.that_name")
        This shows renaming `my_theme` to `theme.name`, and renaming it to `i_hate.that_name` after
        its creation.

        :param friendly_name:
        :param new_name: The new name for the theme
        :return self: The SkTheme itself
        """
        if not SkTheme.validate_theme_existed(new_name):
            # If name not occupied, then rename self.
            self.name = new_name
            self.friendly_name = friendly_name  # 🤔
        else:
            # Otherwise stop this.
            warnings.warn(
                f"Theme name <{new_name}> occupied. Rename for <{self.name}> is canceled."
            )
        return self

    @staticmethod
    def parse_selector(selector: str) -> list[str]:
        """Parse styles selector.

        This is a selector parser mainly used by internal functions.

        Example
        -------
        See -> :func:`get_style` in source code.

        Selector
        --------
        - `<Widget>` indicates the styles of Widget at rest state, e.g. `SkButton`.
        - `<Widget>:<state>` indicates the styles of the state of Widget, e.g. `SkButton:hover`.
        - `<Widget>:ITSELF` indicates the styles of the widget, e.g. `SkButton.ITSELF`.
          Note that this is not available everywhere.

        :param selector: The selector string
        :return: Parsed selector, levels in a list
        """
        # Validate if selector valid
        if not re.match("[a-zA-Z0-9-_.:,]+", selector):
            raise ValueError(f"Invalid styles selector [{selector}].")
        # Handling
        result: list[str] = []
        if ":" in selector:
            colon_parsed = selector.split(":")
            if len(colon_parsed) > 2:  # Validation
                raise ValueError(f"Invalid styles selector [{selector}].")
            # # Deprecated code of multi-state
            # if "," in colon_parsed[1]:
            #     # If has more than one state specified:
            #     result[1] = colon_parsed[1].split(",")
            # else:
            #     # Otherwise, we still make it a list type
            #     result[1] = [colon_parsed[1]]
            if colon_parsed[1] == "ITSELF":
                # For ITSELF selectors
                result = [result[0]]
            result = colon_parsed
        else:
            result = [selector, "rest"]
        # Return the parsed selector
        return result

    @typing.overload
    def select(
        self,
        selector: str | list,
        *,
        copy: bool = ...,
        fallback: bool = ...,
        make_path: bool = ...,
        allow_not_found: typing.Literal[True],
    ) -> dict | None: ...
    @typing.overload
    def select(
        self,
        selector: str | list,
        *,
        copy: bool = ...,
        fallback: bool = ...,
        make_path: bool = ...,
        allow_not_found: typing.Literal[False],
    ) -> dict: ...

    def select(
        self,
        selector: str | list,
        *,
        copy: bool = True,
        fallback: bool = True,
        make_path: bool = False,
        allow_not_found: bool = True,
    ) -> dict | None:
        """Get styles config using a selector.

        Example
        -------
        .. code-block:: python
            my_theme = SkTheme()
            my_style = my_theme.get_style("SkButton:hover")
            my_theme.get_style("SkButton:hover", copy=False)["background"] = (255, 0, 0, 255)
        This shows getting style json of SkButton at hover state and setting its background to red.

        :param selector: The selector string, indicating which styles to get
        :param copy: Whether to copy a new styles json, otherwise returns the styles itself
        :param fallback: Whether to enable fallback machanism, defaults to True
        :param make_path: Whether to create the path if not found instead of throwing errors,
                          will force disable fallback when enabled, defaults to False
        :param allow_not_found: True to return None when style not found, otherwise raise error in
                                such cases
        :return result: The style dict
        """
        # Params handling related stuff
        if make_path:
            # Force disable fallback when make_path enabled
            fallback = False
        # First, set the result to all styles
        result = self.styles
        if not selector:
            # If no selector is provided, then return all styles, so do nothing
            pass
        else:
            try:
                # To get a parsed selector
                selector_parsed = (
                    self.parse_selector(selector) if type(selector) is str else selector
                )  # If is already parsed list
                # Validate if selector exists in theme
                _ = self.styles
                for selector_level in selector_parsed:
                    # # Deprecated code of multi-state
                    # if type(selector_level) is list:
                    #     # If is more than one state specified
                    #     selector_level = selector_level[0] # Then take the first during checking
                    if selector_level not in _:
                        if isinstance(self.parent, SkTheme) and fallback:
                            # If parent exists, then fallback
                            return self.parent.select(
                                selector,
                                copy=copy,
                                fallback=fallback,
                                make_path=make_path,
                                allow_not_found=allow_not_found,
                            )
                        else:
                            # If is root theme, then go fuck ur selector
                            if make_path:
                                # If make_path enabled, make the path
                                _[selector_level] = {}
                            else:
                                # Otherwise u should really go fuck ur selector
                                if allow_not_found:
                                    return None
                                else:
                                    raise SkStyleNotFoundError(
                                        "Cannot find styles with selector "
                                        f"[{selector}]"
                                    )
                    _ = _[selector_level]  # Heading to the next level
            except SkStyleNotFoundError:
                # If this fails, then the selector is invalid
                raise SkStyleNotFoundError(
                    "Style is not exsited in the default theme. Check your selector!"
                )

            for selector_level in selector_parsed:
                # e.g. result = styles["SkButton"]
                # result = styles["SkButton"]["hover"]
                result = result[selector_level]

        if copy and type(result) is dict:
            return result.copy()
        else:
            return result

    def get_style_attr(
        self, selector: str | list[str], attr_name: str, allow_not_found: bool = True
    ) -> typing.Any:
        """Get style attribute _value.

        Example
        -------
        .. code-block:: python
            my_theme = SkTheme()
            button_background = my_theme.get_style_attr("SkButton:rest", "background")
        This shows getting the _value of `background` attribute from styles of `SkButton` at `rest`
        state.

        Fallback Mechanism
        ------------------
        - The program first tries to get attribute from the style indicated by the selector.
        - If fails, which means that the attribute cannot be found, the program tries to fallback
          to the base state of the target state, which is specified with `"base": "<State name>"`.
        - If still fails, fallback to the rest state.
        - If still, which means that the attribute is not specified in the current theme, the
          program will try the parent theme, then the parent of parent theme, and repeat this until
          it reaches the default theme (or more accurately, the root theme).
        - As the root theme must contain all attributes available, if the selector or attribute
          still cannot be found even in root theme, the program throws an error.

        :param selector: The selector to the style, or a parsed list
        :param attr_name: The attribute name
        :param allow_not_found: True to return False when attribute not found, otherwise raise
                                error in such cases
        :return: The attribute _value
        """
        parsed_selector = (
            selector if type(selector) is list else self.parse_selector(selector)
        )
        style = self.select(parsed_selector, copy=False, allow_not_found=False)
        if attr_name not in style:
            # Fallback mechanism
            # Fallback to base or rest state and try
            if parsed_selector[-1] != "rest":
                new_selector = parsed_selector
                new_selector[-1] = "rest" if "base" not in style else style["base"]
                return self.get_style_attr(new_selector, attr_name)
            # If still fails, fallback to parent
            if self.parent is not None:
                return self.parent.get_style_attr(selector, attr_name)
            elif self.parent is None and self.name != SkTheme.DEFAULT_THEME.name:
                SkTheme.DEFAULT_THEME.get_style_attr(selector, attr_name)
            # If is already default theme (no parent), then go fuck your selector
            if self.name == SkTheme.DEFAULT_THEME.name:
                if allow_not_found:
                    return False
                else:
                    raise SkStyleNotFoundError(
                        f"Attribute <{attr_name}> is not exsited in the default theme. "
                        "Check your selector!"
                    )

        if type(style[attr_name]) is dict:
            return style[attr_name].copy()
        else:
            return style[attr_name]

    def get_preset_color(self, color_name: str):
        """Find a preset color from color palette.

        Example
        -------
        .. code-block:: python
            my_theme = SkTheme()
            white = my_theme.get_preset_color("-white")
            default_bg = my_theme.get_preset_color("default_bg")
        This shows getting the white color and the preset color named `default_bg`.

        :param color_name: Name of the color
        """
        keywords = {
            "-transparent": (0, 0, 0, 0),
            "-black": (0, 0, 0, 255),
            "-white": (255, 255, 255, 255),
            "-absneutralgrey": (128, 128, 128, 255),
            "-errcolor": color.ERR_COLOR,
        }
        if color_name in keywords:
            # If is a keyword
            result = keywords[color_name]
        else:
            # If not a keyword
            if color_name in self.color_palette:
                # If existed
                result = self.color_palette[color_name]
            else:
                # If not, fallback
                if isinstance(self.parent, SkTheme):
                    # If it has parent, fallback to parent
                    result = self.parent.get_preset_color(color_name)
                else:
                    # If not, then is root theme, go fuck your color name
                    warnings.warn(
                        f"Color <{color_name}> if not found anywhere.",
                        color.SkColorWarning,
                    )
                    result = color.ERR_COLOR
        if isinstance(result, dict):
            return result.copy()
        else:
            return result

    def mixin(self, selector: str, new_style: dict, copy: bool = False) -> "SkTheme":
        """Mix, or in other words, override custom styles into the theme.

        Example
        -------
        .. code-block:: python
            my_theme = SkTheme()
            my_theme.mixin("SkButton.ITSELF", {"rest": {"background": (255, 0, 0, 255)},
                                               "hover": {"background": (0, 0, 255, 255)}})
            my_subtheme = my_theme.mixin("SkButton:hover", {"background": (255, 0, 0, 255)},
                                         copy=True)
        The first line shows mixing in a red background style at rest state and a blue background
        style at hover state into SkButton. The second line shows creating a subtheme base on
        `my_theme`, but with red background for `SkButton` at `hover` state.

        :param selector: The selector string, indicates where to mix in
        :param new_style: A styles json, to be mixed in
        :param copy: Whether to copy a new theme, otherwise modify the current object
        :return theme_operate: The edited theme object, either self of copy of self
        """
        if copy:
            theme_operate = SkTheme(self.styles)
        else:
            theme_operate = self
        style_operate = theme_operate.select(
            selector, copy=False, allow_not_found=False
        )
        style_operate.update(new_style)
        return theme_operate

    def special(self, selector: str, **kwargs) -> "SkTheme":
        """Create a sub-theme with few modifications on the theme.

        Can be used when applying custom styles on a specific widget.

        Example
        -------
        .. code-block:: python
            SkButton(window, styles=my_theme.special(background=(255, 0, 0, 255)))
        This shows setting a `SkButton`'s style base on `my_theme`, but with background red.

        :param selector: The selector string, indicates where to mix in
        :param kwargs: Styles to change
        :return new_theme: The modified SkTheme object
        """
        ## Handling <SkWidget.ITSELF> selectors
        if "ITSELF" in selector:
            # special() does not support SkWidget.ITSELF, as it simply changes attributes.
            warnings.warn(
                "<SkWidget.ITSELF> is not supported by SkTheme.special()! "
                "It will be regarded as <SkWidget.rest>"
            )
            # So we just simply regard any <ITSELF> as <rest>, as in this case the user may want to
            # change the default appearance.
            selector = selector.replace("ITSELF", "rest")
        ## Creating a modified sub-theme
        # Create a new theme with required stuff
        # (This is to prevent modifications on original theme)
        new_theme = SkTheme({}, parent=self)
        new_theme.is_special = True
        selector_parsed = self.parse_selector(selector)
        # new_theme.styles = {}
        # Modifying styles of the new theme
        style_operate = new_theme.select(selector, copy=False, make_path=True)
        style_operate.update(kwargs)
        # Renaming the new theme
        existed_special_count = 0
        for child in self.children:
            if child.is_special:
                existed_special_count += 1
        new_theme.rename(
            f".special{existed_special_count}",
            f"{self.friendly_name} (Special {existed_special_count})",
        )
        # (Shall we delete unnecessary data from the modified theme in the future?)
        ## Returning the modified theme
        return new_theme

    def apply_on(self, widget: SkWidget) -> SkTheme:
        """Apply theme on a widget.

        Example
        -------
        .. code-block:: python
            my_theme = SkTheme()
            my_button = SkButton(my_window, text="Hello world")
            my_theme.apply_on(my_button)
        This shows applying theme on a `SkButton`

        :param widget: The widget to apply theme to
        :return self: The theme itself
        """
        widget.apply_theme(self)
        return self


# Load internal themes
SkTheme._load_internal_themes()

# Alias for default theme
default_theme = SkTheme.DEFAULT_THEME
dark_theme = SkTheme.INTERNAL_THEMES["default.dark"]
