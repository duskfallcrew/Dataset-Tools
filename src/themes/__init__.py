# src/themes/__init__.py

# Our theme manager - the interior decorator of our app
from .manager import ThemeManager

# Our color schemes - like different mood settings for our space
from .palettes import (
    ComfortDark,
    ComfortLight,
    OceanBreeze,
    MidnightCoder  # For those late-night coding sessions!
)

# Theme utilities that help everything look just right
from .utils import (
    apply_theme,
    get_current_theme,
    save_theme_preference
)
