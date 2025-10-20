

from kivy.metrics import dp
from kivy.properties import StringProperty
from kivy.properties import BooleanProperty

from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.behaviors.button import ButtonBehavior

from .colors import ColorBoxLayout
from kivy.graphics import Color, RoundedRectangle
from kivy.graphics import Triangle, PushMatrix, PopMatrix, Rotate


class ClickableBox(ButtonBehavior, ColorBoxLayout):
    """A BoxLayout that behaves like a button (clickable area)."""
    pass


class ArrowWidget(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.angle = 0
        with self.canvas:
            self.color = Color(0.8, 0.8, 0.8, 1)
            PushMatrix()
            self.rot = Rotate(angle=self.angle, origin=self.center)
            self.tri = Triangle()
            PopMatrix()
        self.bind(pos=self._update_triangle, size=self._update_triangle)

    def _update_triangle(self, *_):
        # Simple right-pointing triangle
        cx, cy = self.center
        s = min(self.width, self.height) * 0.4
        self.tri.points = [
            cx - s, cy + s,
            cx - s, cy - s,
            cx + s, cy
        ]
        self.rot.origin = self.center

    def set_angle(self, deg):
        self.angle = deg
        self.rot.angle = deg


class ExpansionPanel(ColorBoxLayout):
    """
    Prettified pure-Kivy expansion panel.
    - Clean header with arrow indicator
    - Works without KivyMD
    """
    title = StringProperty("")
    collapsible = BooleanProperty(True)
    _is_open = BooleanProperty(False)

    def __init__(self, title="", collapsible=True, **kwargs):
        kwargs.setdefault("bgcolor", [0, 0, 0, 0])
        kwargs.setdefault("bgradius", None)
        super().__init__(orientation="vertical", size_hint_y=None, **kwargs)

        self.bind(minimum_height=self.setter("height"))
        self.title = title
        self.collapsible = collapsible
        self._is_open = not collapsible

        body_bg_color = kwargs.pop("body_bg_color", [0, 0, 0, 0.7])
        body_bg_radius = kwargs.pop("body_bg_radius", [dp(6)])

        header_bg_color = kwargs.pop("header_bg_color", [0.2, 0.2, 0.25, 1])
        header_bg_radius = kwargs.pop("header_bg_radius", [dp(6)])

        # --- Header ---
        self.header = ClickableBox(
            orientation="horizontal", size_hint_y=None, height=dp(40), padding=(dp(10), 0),
            bgcolor=header_bg_color, bgradius=header_bg_radius
        )
        self.header.bind(on_release=self._toggle)

        # Label on the left
        self.header_label = Label(
            text=self.title,
            halign="left",
            valign="middle",
            size_hint_x=1,
            # color=(1, 1, 1, 1)
        )
        self.header_label.bind(size=self.header_label.setter("text_size"))
        self.header.add_widget(self.header_label)

        self.arrow = ArrowWidget(size_hint_x=None, width=dp(15))

        if collapsible:
            self.header.add_widget(self.arrow)

        self.add_widget(self.header)

        self.body_container = ColorBoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(5),
                                             bgcolor=body_bg_color, bgradius=body_bg_radius)
        self.body_container.bind(minimum_height=self.body_container.setter("height"))

    def on_collapsible(self, *_):
        if self.collapsible:
            if not self.arrow.parent:
                self.header.add_widget(self.arrow)
        else:
            if not self._is_open:
                self._toggle()
            if self.arrow.parent:
                self.header.remove_widget(self.arrow)

    def _update_bg(self, *_):
        """Ensure header background follows widget bounds."""
        self._bg_rect.pos = self.header.pos
        self._bg_rect.size = self.header.size

    def add_body_widget(self, widget):
        self.body_container.add_widget(widget)

    def _toggle(self, *_):
        if not self.collapsible and self._is_open:
            return
        if self._is_open:
            if self.body_container.parent is self:
                self.remove_widget(self.body_container)
        else:
            if not self.body_container.parent:
                self.add_widget(self.body_container)
        self.arrow.set_angle(0 if self._is_open else 90)
        self._is_open = not self._is_open
