

from kivy.uix.label import Label
from kivy.core.text import Label as CoreLabel
from kivy.clock import Clock
from .colors import BackgroundColorMixin


class WrappingLabel(Label):
    def __init__(self, **kwargs):
        super(WrappingLabel, self).__init__(**kwargs)
        self.bind(
            width=lambda *x: self.setter('text_size')(self, (self.width, None)),  # noqa
            texture_size=lambda *x: self.setter('height')(self, self.texture_size[1])  # noqa
        )


class ColorLabel(BackgroundColorMixin, Label):
    def __init__(self, **kwargs):
        bgcolor = kwargs.pop('bgcolor', None)
        Label.__init__(self, **kwargs)
        BackgroundColorMixin.__init__(self, bgcolor=bgcolor)


class SelfScalingLabel(Label):
    def __init__(self, **kwargs):
        kwargs['max_lines'] = 1
        super(SelfScalingLabel, self).__init__(**kwargs)
        self.bind(texture_size=self._scale_font)

    def _scale_font(self, *_):
        # print("Scaling {0} ?> {1}".format(self.texture_size[0], self.width))
        if self.texture_size[0] > self.width:
            self.font_size -= 1  # reduce font size if too wide


class SelfScalingOneLineLabel(Label):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(size=lambda inst, val: setattr(inst, 'text_size', val))
        self._bind_autofit_text()

    def _bind_autofit_text(self, min_font=10, max_font=None, respect_height=True, timeout_retry=0.05):
        """
        Bind label so its font_size auto-scales to ensure the full text fits *in one line* horizontally.

        - No wrapping, no shortening, no clipping.
        - Keeps alignment (halign/valign) functional.
        - Recomputes on size/text change.
        """

        def _fit_text_size(*_):
            # Ensure layout exists before computing
            w, h = self.size
            if w <= 8 or h <= 8:
                Clock.schedule_once(lambda dt: _fit_text_size(), timeout_retry)
                return

            text = self.text or ""
            if not text.strip():
                return

            high = max_font if max_font is not None else max(self.font_size, h)
            low = min_font
            best = low

            while low <= high:
                mid = (low + high) // 2
                core = CoreLabel(
                    text=text,
                    font_size=mid,
                    font_name=getattr(self, "font_name", None),
                    bold=getattr(self, "bold", False),
                    markup=getattr(self, "markup", False),
                )
                # Do NOT set text_size → no wrapping
                core.refresh()
                tex_w, tex_h = core.texture.size

                fits_width = tex_w <= w
                fits_height = not respect_height or tex_h <= h

                if fits_width and fits_height:
                    best = mid
                    low = mid + 1
                else:
                    high = mid - 1

            self.font_size = best
            # text_size should match full size for proper halign/valign (but no wrapping)
            self.text_size = (w, None)

        self.bind(size=_fit_text_size, text=_fit_text_size)
        Clock.schedule_once(lambda dt: _fit_text_size(), 0)


class SelfScalingColorLabel(SelfScalingLabel, ColorLabel):
    def __init__(self, **kwargs):
        super(SelfScalingColorLabel, self).__init__(**kwargs)
