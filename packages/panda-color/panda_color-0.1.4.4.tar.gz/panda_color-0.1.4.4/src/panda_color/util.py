import os
from .color import Color

def lighten(color: Color, factor: float) -> Color:
    """Return a lightened version of the color (factor 0.0–1.0)."""
    factor = max(0.0, min(1.0, factor))
    new_r = min(255, int(color.r + (255 - color.r) * factor))
    new_g = min(255, int(color.g + (255 - color.g) * factor))
    new_b = min(255, int(color.b + (255 - color.b) * factor))
    return color.__class__(new_r, new_g, new_b)

def darken(color: Color, factor: float) -> Color:
    """Return a darkened version of the color (factor 0.0–1.0)."""
    factor = max(0.0, min(1.0, factor))
    new_r = int(color.r * (1.0 - factor))
    new_g = int(color.g * (1.0 - factor))
    new_b = int(color.b * (1.0 - factor))
    return color.__class__(new_r, new_g, new_b)

def invert(color: Color) -> Color:
    """Return inverted (complement) color."""
    return color.__class__(255 - color.r, 255 - color.g, 255 - color.b)

def grayscale(color: Color) -> Color:
    """Convert to grayscale using luminance formula (ITU-R BT.709)."""
    gray = int(0.2126 * color.r + 0.7152 * color.g + 0.0722 * color.b)
    return color.__class__(gray, gray, gray)

def mix(color1: Color, color2: Color, factor: float = 0.5) -> Color:
    """GLSL-style mix: linear RGB interpolation (no gamma correction)."""
    factor = max(0.0, min(1.0, factor))

    r1, g1, b1 = color1.normalized()
    r2, g2, b2 = color2.normalized()

    r = r1 * (1 - factor) + r2 * factor
    g = g1 * (1 - factor) + g2 * factor
    b = b1 * (1 - factor) + b2 * factor

    return Color.from_normalized(r, g, b)

def clamp(color: Color) -> Color:
    """Clamp color values to valid RGB range (0-255)."""
    r = max(Color.RGB_MIN, min(Color.RGB_MAX, color.r))
    g = max(Color.RGB_MIN, min(Color.RGB_MAX, color.g))
    b = max(Color.RGB_MIN, min(Color.RGB_MAX, color.b))
    return color.__class__(r, g, b)

def distance(c1: Color, c2: Color) -> float:
    """Euclidean distance between two colors in RGB space."""
    dr = c1.r - c2.r
    dg = c1.g - c2.g
    db = c1.b - c2.b
    return (dr**2 + dg**2 + db**2) ** 0.5

# === TERMINAL COLOR UTILITIES ===

def _supports_truecolor_env() -> bool:
    """Check if the environment supports 24-bit truecolor."""
    colorterm = os.environ.get("COLORTERM", "").lower()
    return colorterm in ("truecolor", "24bit")

def _supports_256color() -> bool:
    """Check if the environment supports 256-color mode."""
    term = os.environ.get("TERM", "").lower()
    return "256color" in term

def to_ansi256(color: Color) -> int:
    """Convert 24-bit Color to the closest 256-color ANSI code."""
    r, g, b = color.r, color.g, color.b

    def to_ansi_level(c):
        if c < 48:
            return 0
        elif c < 114:
            return 1
        else:
            return (c - 35) // 40

    r_level, g_level, b_level = to_ansi_level(r), to_ansi_level(g), to_ansi_level(b)
    return 16 + 36 * r_level + 6 * g_level + b_level

def color_text(text: str, color: Color) -> str:
    """Apply color to text foreground with automatic terminal capability detection."""
    if _supports_truecolor_env():
        return f"\033[38;2;{color.r};{color.g};{color.b}m{text}\033[0m"
    elif _supports_256color():
        return f"\033[38;5;{to_ansi256(color)}m{text}\033[0m"
    else:
        return text

def highlight_text(text: str, color: Color) -> str:
    """Apply color to text background with automatic terminal capability detection."""
    if _supports_truecolor_env():
        return f"\033[48;2;{color.r};{color.g};{color.b}m{text}\033[0m"
    elif _supports_256color():
        return f"\033[48;5;{to_ansi256(color)}m{text}\033[0m"
    else:
        return text

def color_highlight_text(text: str, fg: Color, bg: Color) -> str:
    """Apply color to text foreground and background with automatic terminal capability detection."""
    if _supports_truecolor_env():
        return f"\033[38;2;{fg.r};{fg.g};{fg.b}m\033[48;2;{bg.r};{bg.g};{bg.b}m{text}\033[0m"
    elif _supports_256color():
        return f"\033[38;5;{to_ansi256(fg)}m\033[48;5;{to_ansi256(bg)}m{text}\033[0m"
    else:
        return text