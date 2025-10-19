

import pytest


def test_color_import():
    from kivy_garden.ebs.core import colors
    assert hasattr(colors, 'GuiPalette')
    assert hasattr(colors, 'color_set_alpha')
    assert hasattr(colors, 'Gradient')
    assert hasattr(colors, 'color_set_alpha')
    assert hasattr(colors, 'BackgroundColorMixin')
    assert hasattr(colors, 'ColorBoxLayout')
    assert hasattr(colors, 'RoundedColorBoxLayout')
