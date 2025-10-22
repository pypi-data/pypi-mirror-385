from __future__ import annotations

import json
import re
from collections.abc import Iterable, Iterator, Mapping
from itertools import chain
from typing import TYPE_CHECKING, Literal, TypeAlias, Union

if TYPE_CHECKING:
    from typing import Self

__all__ = ["attribute_generator"]

JSEvent = Literal[
    "abort",
    "afterprint",
    "animationend",
    "animationiteration",
    "animationstart",
    "beforeprint",
    "beforeunload",
    "blur",
    "canplay",
    "canplaythrough",
    "change",
    "click",
    "contextmenu",
    "copy",
    "cut",
    "dblclick",
    "drag",
    "dragend",
    "dragenter",
    "dragleave",
    "dragover",
    "dragstart",
    "drop",
    "durationchange",
    "ended",
    "error",
    "focus",
    "focusin",
    "focusout",
    "fullscreenchange",
    "fullscreenerror",
    "hashchange",
    "input",
    "invalid",
    "keydown",
    "keypress",
    "keyup",
    "load",
    "loadeddata",
    "loadedmetadata",
    "loadstart",
    "message",
    "mousedown",
    "mouseenter",
    "mouseleave",
    "mousemove",
    "mouseover",
    "mouseout",
    "mouseup",
    "mousewheel",
    "offline",
    "online",
    "open",
    "pagehide",
    "pageshow",
    "paste",
    "pause",
    "play",
    "playing",
    "popstate",
    "progress",
    "ratechange",
    "resize",
    "reset",
    "scroll",
    "search",
    "seeked",
    "seeking",
    "select",
    "show",
    "stalled",
    "storage",
    "submit",
    "suspend",
    "timeupdate",
    "toggle",
    "touchcancel",
    "touchend",
    "touchmove",
    "touchstart",
    "transitionend",
    "unload",
    "volumechange",
    "waiting",
    "wheel",
]


SignalValue: TypeAlias = Union[
    str,
    int,
    float,
    bool,
    dict[str, "SignalValue"],
    list["SignalValue"],
    None,
]


class AttributeGenerator:
    def __init__(self, alias: str = "data-") -> None:
        """A helper which can generate all the Datastar attributes.

        :param alias: The prefix for all attributes. Defaults to `data-`.
        """
        self._alias: str = alias

    def signals(
        self,
        signals_dict: Mapping[str, SignalValue] | None = None,
        /,
        *,
        expressions_: bool = False,
        **signals: SignalValue,
    ) -> SignalsAttr:
        """Patch one or more signals into the existing signals.

        :param signals_dict: A dictionary of signals to patch.
        :param expressions_: If True, the values of the signals will be evaluated as expressions
            rather than literals.
        """
        signals = {**(signals_dict if signals_dict else {}), **signals}
        val = _js_object(signals) if expressions_ else json.dumps(signals)
        return SignalsAttr(value=val, alias=self._alias)

    def computed(self, computed_dict: Mapping | None = None, /, **computed: str) -> BaseAttr:
        """Create signals that are computed based on an expression."""
        computed = {**(computed_dict if computed_dict else {}), **computed}
        first, *rest = (
            BaseAttr("computed", key=sig, value=expr, alias=self._alias)
            for sig, expr in computed.items()
        )
        first._other_attrs = rest
        return first

    def effect(self, expression: str) -> BaseAttr:
        """Execute an expression when any referenced signals change."""
        return BaseAttr("effect", value=expression, alias=self._alias)

    @property
    def ignore(self) -> IgnoreAttr:
        """Tell Datastar to ignore data-* attributes on the element."""
        return IgnoreAttr(alias=self._alias)

    def attr(self, attr_dict: Mapping | None = None, /, **attrs: str) -> BaseAttr:
        """Set the value of any HTML attributes to expressions, and keep them in sync."""
        attrs = {**(attr_dict if attr_dict else {}), **attrs}
        return BaseAttr("attr", value=_js_object(attrs), alias=self._alias)

    def bind(self, signal_name: str) -> BaseAttr:
        """Set up two-way data binding between a signal and an element's value."""
        return BaseAttr("bind", value=signal_name, alias=self._alias)

    def class_(self, class_dict: Mapping | None = None, /, **classes: str) -> BaseAttr:
        """Add or removes classes to or from an element based on expressions."""
        classes = {**(class_dict if class_dict else {}), **classes}
        return BaseAttr("class", value=_js_object(classes), alias=self._alias)

    def init(self, expression: str) -> InitAttr:
        """Execute an expression when the element is loaded into the DOM."""
        return InitAttr(value=expression, alias=self._alias)

    def on(self, event: JSEvent | str, expression: str) -> OnAttr:
        """Execute an expression when an event occurs."""
        return OnAttr(key=event, value=expression, alias=self._alias)

    def on_interval(self, expression: str) -> OnIntervalAttr:
        """Execute an expression at a regular interval."""
        return OnIntervalAttr(value=expression, alias=self._alias)

    def on_intersect(self, expression: str) -> OnIntersectAttr:
        """Execute an expression when the element intersects with the viewport."""
        return OnIntersectAttr(value=expression, alias=self._alias)

    def on_raf(self, expression: str) -> OnRafAttr:
        """(PRO) Execute an expression on every requestAnimationFrame event."""
        return OnRafAttr(value=expression, alias=self._alias)

    def on_signal_patch(
        self, expression: str, include: str | None = None, exclude: str | None = None
    ) -> OnSignalPatchAttr:
        """Execute an expression when a signal patch takes place."""
        attr = OnSignalPatchAttr(value=expression, alias=self._alias)
        if include or exclude:
            attr.filter(include, exclude)
        return attr

    def on_resize(self, expression: str) -> OnResizeAttr:
        """(PRO) Execute an expression each time the element's dimensions change."""
        return OnResizeAttr(value=expression, alias=self._alias)

    @property
    def persist(self) -> PersistAttr:
        """(PRO) Persist signals in local storage."""
        return PersistAttr(alias=self._alias)

    def ref(self, signal_name: str) -> BaseAttr:
        """Create a signal which references the element on which the attribute is placed."""
        return BaseAttr("ref", value=signal_name, alias=self._alias)

    def replace_url(self, url_expression: str) -> BaseAttr:
        """(PRO) Replace the URL in the browser without replacing the page."""
        return BaseAttr("replace-url", value=url_expression, alias=self._alias)

    def show(self, expression: str) -> BaseAttr:
        """Show or hides an element based on whether an expression evaluates to true or false."""
        return BaseAttr("show", value=expression, alias=self._alias)

    def style(self, style_dict: Mapping | None = None, /, **styles: str) -> BaseAttr:
        """Set the value of inline CSS styles on an element based on an expression, and keeps them in sync."""
        styles = {**(style_dict if style_dict else {}), **styles}
        return BaseAttr("style", value=_js_object(styles), alias=self._alias)

    def text(self, expression: str) -> BaseAttr:
        """Bind the text content of an element to an expression."""
        return BaseAttr("text", value=expression, alias=self._alias)

    def indicator(self, signal_name: str) -> BaseAttr:
        """Create a signal whose value is true while an SSE request is in flight."""
        return BaseAttr("indicator", value=signal_name, alias=self._alias)

    def custom_validity(self, expression: str) -> BaseAttr:
        """(PRO) Set the validity message for an element based on an expression."""
        return BaseAttr("custom-validity", value=expression, alias=self._alias)

    @property
    def scroll_into_view(self) -> ScrollIntoViewAttr:
        """(PRO) Scrolls the element into view."""
        return ScrollIntoViewAttr(alias=self._alias)

    def view_transition(self, expression: str) -> BaseAttr:
        """(PRO) Set the view-transition-name style attribute explicitly."""
        return BaseAttr("view-transition", value=expression, alias=self._alias)

    @property
    def json_signals(self) -> BaseAttr:
        """Create a signal that contains the JSON representation of the signals."""
        return JsonSignalsAttr(alias=self._alias)

    @property
    def ignore_morph(self) -> BaseAttr:
        """Do not overwrite this element or its children when morphing."""
        return BaseAttr("ignore-morph", alias=self._alias)

    def preserve_attr(self, attrs: str | Iterable[str]) -> BaseAttr:
        """Preserve the client side state for specified attribute(s) when morphing."""
        value = attrs if isinstance(attrs, str) else " ".join(attrs)
        return BaseAttr("preserve-attrs", value=value, alias=self._alias)

    @property
    def query_string(self) -> QueryStringAttr:
        """(PRO) Sync the query string with signal values."""
        return QueryStringAttr(alias=self._alias)


class BaseAttr(Mapping):
    _attr: str

    def __init__(
        self,
        attr: str | None = None,
        /,
        *,
        key: str | None = None,
        value: str | Literal[True] = True,
        alias: str = "data-",
    ) -> None:
        if attr:
            self._attr: str = attr
        self._key: str | None = None
        self._mods: dict[str, list[str]] = {}
        self._other_attrs: list[BaseAttr] = []
        self._value: str | Literal[True] = value
        self._alias: str = alias
        if key:
            self._to_kebab_key(key)

    def __call__(self) -> Self:
        # Because some attributes and modifiers do not need to be called,
        # allow calling them anyway so that all attributes allow parens.
        return self

    def _full_key(self) -> str:
        key = f"{self._alias}{self._attr}"
        if self._key:
            key += f":{self._key}"
        for mod, values in self._mods.items():
            key += f"__{mod}"
            if values:
                key += f".{'.'.join(values)}"
        return key

    def _to_kebab_key(self, key_name: str) -> None:
        if "__" in key_name:
            # _ are allowed in attributes, the only time we need to convert is if there are multiple underscores
            kebab_name, from_case = key_name.lower().replace("_", "-"), "snake"
        elif key_name[0].isupper():
            kebab_name, from_case = (
                re.sub(r"((?<!\.)[A-Z])", r"-\1", key_name).lstrip("-").lower(),
                "pascal",
            )
        elif key_name.lower() != key_name:
            kebab_name, from_case = (
                re.sub(r"([A-Z])", r"-\1", key_name).lower(),
                "camel",
            )
        else:
            # kebab case means the raw name from the attribute will be passed through
            kebab_name, from_case = key_name, "kebab"
        self._key = kebab_name
        if from_case:
            self._mods["case"] = [from_case]

    def __getitem__(self, key: str, /) -> str | Literal[True]:
        if key == self._full_key():
            return self._value
        for attr in self._other_attrs:
            if key == attr._full_key():
                return attr._value
        raise KeyError(key)

    def __len__(self) -> int:
        return len(self._other_attrs) + 1

    def __iter__(self) -> Iterator[str]:
        return chain((self._full_key(),), *self._other_attrs)

    def __str__(self) -> str:
        r = _escape(self._full_key())
        if isinstance(self._value, str):
            r += f'="{_escape(self._value)}"'
        if self._other_attrs:
            other = " ".join(str(o) for o in self._other_attrs)
            r += f" {other}"
        return r

    __html__ = __str__


class TimingMod:
    def debounce(
        self: Self,
        wait: int | str,
        *,
        leading: bool = False,
        notrailing: bool = False,
    ) -> Self:
        """Debounce the event listener.

        :param wait: The minimum interval between events.
        :param leading: If True, the event listener will be called on the leading edge of the
            wait time.
        :param notrailing: If True, the event listener will not be called on the trailing edge of the
            wait time.
        """
        self._mods["debounce"] = [str(wait)]
        if leading:
            self._mods["debounce"].append("leading")
        if notrailing:
            self._mods["debounce"].append("notrailing")
        return self

    def throttle(
        self: Self,
        wait: int | str,
        *,
        noleading: bool = False,
        trailing: bool = False,
    ) -> Self:
        """Throttle the event listener.

        :param wait: The minimum interval between events.
        :param noleading: If true, the event listener will not be called on the leading edge of the
            wait time.
        :param trailing: If true, the event listener will be called on the trailing edge of the
            wait time.
        """
        self._mods["throttle"] = [str(wait)]
        if noleading:
            self._mods["throttle"].append("noleading")
        if trailing:
            self._mods["throttle"].append("trailing")
        return self


class DelayMod:
    def delay(
        self: Self,
        wait: int | str,
    ) -> Self:
        """Delay the event listener.

        :param wait: The delay time.
        """
        self._mods["delay"] = [str(wait)]
        return self


class ViewtransitionMod:
    @property
    def viewtransition(self: Self) -> Self:
        """Wrap the expression in document.startViewTransition()."""
        self._mods["view-transition"] = []
        return self


class SignalsAttr(BaseAttr):
    _attr = "signals"

    @property
    def ifmissing(self) -> Self:
        """Only set signals that do not already exist."""
        self._mods["ifmissing"] = []
        return self


class IgnoreAttr(BaseAttr):
    _attr = "ignore"

    @property
    def self(self) -> Self:
        """Only ignore the element itself, not its descendants."""
        self._mods["self"] = []
        return self


class OnAttr(BaseAttr, TimingMod, DelayMod, ViewtransitionMod):
    _attr = "on"

    @property
    def once(self) -> Self:
        """Only trigger the event listener once."""
        self._mods["once"] = []
        return self

    @property
    def passive(self) -> Self:
        """Do not call preventDefault on the event listener."""
        self._mods["passive"] = []
        return self

    @property
    def capture(self) -> Self:
        """Use a capture event listener."""
        self._mods["capture"] = []
        return self

    @property
    def window(self) -> Self:
        """Attach the event listener to the window element."""
        self._mods["window"] = []
        return self

    @property
    def outside(self) -> Self:
        """Trigger when the event is outside the element."""
        self._mods["outside"] = []
        return self

    @property
    def prevent(self) -> Self:
        """Call preventDefault on the event listener."""
        self._mods["prevent"] = []
        return self

    @property
    def stop(self) -> Self:
        """Call stopPropagation on the event listener."""
        self._mods["stop"] = []
        return self

    @property
    def trust(self) -> Self:
        """Run even when isTrusted property on the event is false."""
        self._mods["trust"] = []
        return self


class PersistAttr(BaseAttr):
    _attr = "persist"

    def __call__(
        self,
        storage_key: str | None = None,
        include: str | None = None,
        exclude: str | None = None,
    ) -> Self:
        if storage_key:
            self._key = storage_key
        if include or exclude:
            self._value = json.dumps(_filter_dict(include=include, exclude=exclude))
        return self

    @property
    def session(self) -> Self:
        """Persist signals in session storage."""
        self._mods["session"] = []
        return self


class JsonSignalsAttr(BaseAttr):
    _attr = "json-signals"

    def __call__(self, include: str | None = None, exclude: str | None = None) -> Self:
        if include or exclude:
            self._value = json.dumps(_filter_dict(include=include, exclude=exclude))
        return self

    @property
    def terse(self) -> Self:
        """Output without extra whitespace."""
        self._mods["terse"] = []
        return self


class ScrollIntoViewAttr(BaseAttr):
    _attr = "scroll-into-view"

    @property
    def smooth(self) -> Self:
        """Animate scrolling smoothly."""
        self._mods["smooth"] = []
        return self

    @property
    def instant(self) -> Self:
        """Scroll instantly."""
        self._mods["instant"] = []
        return self

    @property
    def auto(self) -> Self:
        """Let scrolling be determined by the computed scroll-behavior CSS property."""
        self._mods["auto"] = []
        return self

    @property
    def hstart(self) -> Self:
        """Scroll to the left of the element."""
        self._mods["hstart"] = []
        return self

    @property
    def hcenter(self) -> Self:
        """Scroll to the horizontal center of the element."""
        self._mods["hcenter"] = []
        return self

    @property
    def hend(self) -> Self:
        """Scroll to the right of the element."""
        self._mods["hend"] = []
        return self

    @property
    def hnearest(self) -> Self:
        """Scroll to the nearest horizontal edge of the element."""
        self._mods["hnearest"] = []
        return self

    @property
    def vstart(self) -> Self:
        """Scroll to the top of the element."""
        self._mods["vstart"] = []
        return self

    @property
    def vcenter(self) -> Self:
        """Scroll to the vertical center of the element."""
        self._mods["vcenter"] = []
        return self

    @property
    def vend(self) -> Self:
        """Scroll to the bottom of the element."""
        self._mods["vend"] = []
        return self

    @property
    def vnearest(self) -> Self:
        """Scroll to the nearest vertical edge of the element."""
        self._mods["vnearest"] = []
        return self

    @property
    def focus(self) -> Self:
        """Focus the element after scrolling."""
        self._mods["focus"] = []
        return self


class OnIntersectAttr(BaseAttr, TimingMod, DelayMod, ViewtransitionMod):
    _attr = "on-intersect"

    @property
    def once(self) -> Self:
        """Only trigger the event listener once."""
        self._mods["once"] = []
        return self

    @property
    def half(self) -> Self:
        """Trigger the event listener when half the element enters the viewport."""
        self._mods["half"] = []
        return self

    @property
    def full(self) -> Self:
        """Trigger the event listener when the full element is visible."""
        self._mods["full"] = []
        return self


class OnIntervalAttr(BaseAttr, ViewtransitionMod):
    _attr = "on-interval"

    def duration(self, duration: int | float | str, *, leading: bool = False) -> Self:
        """Set the interval duration."""
        self._mods["duration"] = [str(duration)]
        if leading:
            self._mods["duration"].append("leading")
        return self


class InitAttr(BaseAttr, ViewtransitionMod, DelayMod):
    _attr = "init"

    @property
    def once(self) -> Self:
        """Only trigger the event listener once."""
        self._mods["once"] = []
        return self


class OnRafAttr(BaseAttr, TimingMod):
    _attr = "on-raf"


class OnSignalPatchAttr(BaseAttr, TimingMod, DelayMod):
    _attr = "on-signal-patch"

    def filter(self, include: str | None = None, exclude: str | None = None) -> Self:
        """Filter the signal patch events."""
        if include or exclude:
            self._other_attrs = [
                BaseAttr(
                    "on-signal-patch-filter",
                    value=json.dumps(_filter_dict(include=include, exclude=exclude)),
                )
            ]
        return self


class OnResizeAttr(BaseAttr, TimingMod):
    _attr = "on-resize"


class QueryStringAttr(BaseAttr):
    _attr = "query-string"

    def __call__(self, include: str | None = None, exclude: str | None = None) -> Self:
        if include or exclude:
            self._value = json.dumps(_filter_dict(include=include, exclude=exclude))
        return self

    @property
    def history(self) -> Self:
        self._mods["history"] = []
        return self


def _escape(s: str) -> str:
    return (
        s.replace("&", "&amp;")
        .replace("'", "&#39;")
        .replace('"', "&#34;")
        .replace(">", "&gt;")
        .replace("<", "&lt;")
    )


def _filter_dict(include: str | None = None, exclude: str | None = None) -> dict:
    filter_dict = {}
    if include:
        filter_dict["include"] = include
    if exclude:
        filter_dict["exclude"] = exclude
    return filter_dict


def _js_object(obj: dict) -> str:
    """Create a JS object where the values are expressions rather than strings."""
    return (
        "{"
        + ", ".join(
            f"{json.dumps(k)}: {_js_object(v) if isinstance(v, dict) else v}"
            for k, v in obj.items()
        )
        + "}"
    )


attribute_generator = AttributeGenerator()
