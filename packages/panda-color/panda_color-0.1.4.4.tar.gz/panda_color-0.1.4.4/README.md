# PandaColor

A lightweight and extensible Python color library with GLSL-style swizzling support.

PandaColor provides an intuitive interface for working with RGB colors, featuring swizzling patterns familiar to graphics programmers, comprehensive color manipulations, predefined color constants, and utilities for terminal output and web development.

---

## Features

### Core Functionality

- **Multiple initialization methods**: integers, strings, iterables, hex codes, or normalized floats
- **GLSL-style swizzling**: Access components with `.r`, `.g`, `.b`, `.rgb`, `.rg`, `.gbr`, etc.
- **Comprehensive validation**: Type checking and range validation for all color values
- **Immutable variants**: Create new colors with `with_red()`, `with_green()`, `with_blue()`
- **Predefined color constants**: 35 common colors ready to use

### Color Manipulations

- **Brightness**: `lighten()`, `darken()`
- **Color operations**: `invert()`, `grayscale()`, `mix()`
- **Utilities**: `clamp()`, `distance()` between colors

### Output Formats

- **Web formats**: CSS `rgb()`, `rgba()`, hex strings
- **Data formats**: tuples, lists, dictionaries, normalized floats
- **Binary formats**: Various byte representations for graphics programming
- **Terminal colors**: ANSI escape sequences with truecolor and 256-color fallback
- **Luminance calculation**: sRGB standard relative luminance

---

## Installation

Install from PyPI:

```bash
pip install panda-color
```

Or install from source:

```bash
git clone https://github.com/ColinThePanda/pandacolor.git
cd pandacolor
pip install .
```

---

## Quick Start

```python
from panda_color import Color, Colors

# Multiple ways to create colors
color1 = Color(255, 128, 0)           # RGB integers
color2 = Color([255, 128, 0])         # From list/tuple
color3 = Color("255, 128, 0")         # From string
color4 = Color.from_hex("#ff8000")    # From hex
color5 = Color.from_normalized(1.0, 0.5, 0.0)  # Normalized floats
color6 = Color.random()               # Random color

# Use predefined colors
print(Colors.RED.to_hex())     # #ff0000
print(Colors.BLUE.css_rgb())   # rgb(0, 0, 255)

# GLSL-style swizzling
print(color1.r)       # 255
print(color1.rgb)     # (255, 128, 0)
print(color1.rg)      # (255, 128)
print(color1.gbr)     # (128, 0, 255)

# Swizzling assignment
color1.r = 200        # Set red component
color1.gb = [64, 32]  # Set green and blue components
```

## Predefined Color Constants

PandaColor includes 35 predefined colors for immediate use:

```python
from panda_color import Colors

# Basic colors
Colors.BLACK, Colors.WHITE, Colors.RED, Colors.GREEN, Colors.BLUE
Colors.YELLOW, Colors.CYAN, Colors.MAGENTA

# Extended palette
Colors.ORANGE, Colors.PINK, Colors.PURPLE, Colors.BROWN, Colors.LIME
Colors.TEAL, Colors.NAVY, Colors.OLIVE, Colors.MAROON, Colors.AQUA
Colors.CRIMSON, Colors.CORNFLOWER_BLUE, Colors.DARK_ORANGE
Colors.DARK_GREEN, Colors.DARK_RED, Colors.STEEL_BLUE
Colors.DARK_SLATE_GRAY, Colors.MEDIUM_PURPLE, Colors.FIREBRICK
Colors.SALMON, Colors.LIME_GREEN, Colors.SKY_BLUE, Colors.GOLD
Colors.SILVER

# Grayscale
Colors.GRAY, Colors.LIGHT_GRAY, Colors.DARK_GRAY

print(f"Crimson: {Colors.CRIMSON.to_hex()}")        # #dc143c
print(f"Sky Blue: {Colors.SKY_BLUE.css_rgb()}")     # rgb(135, 206, 235)
```

## Color Manipulations

```python
from panda_color import Color, Colors, lighten, darken, invert, grayscale, mix

original = Color(100, 150, 200)

# Brightness adjustments
lighter = lighten(original, 0.3)    # 30% lighter
darker = darken(original, 0.5)      # 50% darker

# Color transformations
inverted = invert(original)         # Color complement
gray = grayscale(original)          # Grayscale conversion

# Blending colors
purple = mix(Colors.RED, Colors.BLUE, 0.5)      # 50/50 mix -> Color(127, 0, 127)
```

## Output Formats

```python
from panda_color import Colors

# Web formats
print(Colors.ORANGE.to_hex())           # #ffa500
print(Colors.ORANGE.css_rgb())          # rgb(255, 165, 0)
print(Colors.ORANGE.css_rgba(0.8))      # rgba(255, 165, 0, 0.8)

# Data formats
print(Colors.ORANGE.to_tuple())         # (255, 165, 0)
print(Colors.ORANGE.to_list())          # [255, 165, 0]
print(Colors.ORANGE.to_dict())          # {'r': 255, 'g': 165, 'b': 0}
print(Colors.ORANGE.normalized())       # (1.0, 0.6470588235294118, 0.0)

# Binary formats for graphics programming
print(Colors.ORANGE.to_bytesv3_u8())    # b'\xff\xa5\x00'
print(Colors.ORANGE.to_bytesv4_u8())    # b'\xff\xa5\x00\xff'
print(Colors.ORANGE.to_bytesv3_32())    # 32-bit floats (little-endian)
print(Colors.ORANGE.to_bytesv3_64())    # 64-bit doubles (little-endian)

# Properties
print(Colors.ORANGE.luminance)          # 0.5515... (relative luminance)
```

## Terminal Colors

```python
from panda_color import Colors, color_text, highlight_text, color_highlight_text

# Colored text output (with automatic fallback support)
print(color_text("This text is red!", Colors.RED))
print(highlight_text("This has a green background!", Colors.GREEN))
print(color_highlight_text("This has red text and a green background!", Colors.RED, Colors.GREEN))
```

## Sequence Protocol

Colors support iteration and indexing:

```python
from panda_color import Colors

# Iteration
for component in Colors.PURPLE:
    print(component)  # 128, 0, 128

# Indexing
print(Colors.PURPLE[0])  # 128 (red)
print(Colors.PURPLE[1])  # 0 (green)
print(Colors.PURPLE[2])  # 128 (blue)

# Length
print(len(Colors.PURPLE))  # 3
```

## Immutable Variants

Create new colors based on existing ones:

```python
from panda_color import Colors

red_blue = Colors.BLUE.with_red(255)     # Color(255, 0, 255) - magenta
light_blue = Colors.BLUE.with_green(128) # Color(0, 128, 255) - lighter blue
```

---

## API Reference

### Color Class

#### Constructor

- `Color()` - Black color (0, 0, 0)
- `Color(r, g, b)` - RGB integers (0-255)
- `Color(iterable)` - From list, tuple, etc.
- `Color(string)` - Parse "r, g, b" format
- `Color(color)` - Copy constructor

#### Class Methods

- `Color.from_hex(hex_string)` - From hex string (#RRGGBB or RRGGBB)
- `Color.from_normalized(r, g, b)` - From normalized floats (0.0-1.0)
- `Color.random()` - Generate random color

#### Properties

- `.r`, `.g`, `.b` - Individual components (with setters)
- `.rgb` - RGB as tuple (with setter)
- `.luminance` - Relative luminance (0.0-1.0)

#### Methods

- `.to_hex()` - Hex string (#RRGGBB)
- `.to_tuple()` - RGB as tuple
- `.to_list()` - RGB as list
- `.to_dict()` - RGB as dictionary
- `.css_rgb()` - CSS rgb() format
- `.css_rgba(alpha)` - CSS rgba() format
- `.normalized()` - Normalized floats (0.0-1.0)
- `.to_bytes()` - Color as bytest (supports rgb and rgba with f32, f64, u8)
- `.with_red(r)`, `.with_green(g)`, `.with_blue(b)` - Immutable variants

### Utility Functions

```python
from panda_color import (
    lighten, darken, invert, grayscale, mix, clamp, distance,
    color_text, highlight_text, to_ansi256
)

lighten(color, factor)             # Lighten by factor (0.0-1.0)
darken(color, factor)              # Darken by factor (0.0-1.0)
invert(color)                      # Color complement
grayscale(color)                   # Grayscale conversion
mix(color1, color2, factor)        # Mix two colors (GLSL-style linear interpolation)
clamp(color)                       # Clamp to valid RGB range
distance(color1, color2)           # Euclidean distance in RGB space

# Terminal output
color_text(text, color)            # Colored text (foreground)
highlight_text(text, color)        # Highlighted text (background)
color_highlight_text(text, fg, bg) # Colored and highlighted text (foreground + background)
to_ansi256(color)                  # Convert to ANSI 256-color code
```

---

## Examples

### Web Development

```python
from panda_color import Colors, lighten, darken

primary = Colors.BLUE
secondary = lighten(primary, 0.2)
accent = darken(primary, 0.3)

print(f"Primary: {primary.css_rgb()}")      # rgb(0, 0, 255)
print(f"Secondary: {secondary.css_rgb()}")  # rgb(51, 51, 255)
print(f"Accent: {accent.css_rgb()}")        # rgb(0, 0, 178)
```

### Terminal Applications

```python
from panda_color import Colors, color_text

print(color_text("❌ Error: Something went wrong", Colors.RED))
print(color_text("✅ Success: Operation completed", Colors.GREEN))
print(color_text("⚠️  Warning: Check your input", Colors.YELLOW))
```

### Graphics Programming

```python
from panda_color import Color

color = Color(255, 128, 64)

# Export to various binary formats
vertex_data = color.to_bytes(3, 'f32')    # For OpenGL vertex attributes
texture_data = color.to_bytes(4, 'u8')   # For RGBA textures
uniform_data = color.to_bytes(3, 'f64')   # For high-precision uniforms
```

### Color Analysis

```python
from panda_color import Color, distance, grayscale

color1 = Color(255, 100, 50)
color2 = Color(200, 150, 100)

print(f"Distance: {distance(color1, color2):.2f}")
print(f"Color1 luminance: {color1.luminance:.3f}")
print(f"Grayscale: {grayscale(color1).to_hex()}")
```

---

## Roadmap

- HSV and HSL color space support
- Auto-generated color palettes
- Color Pickers

---

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

## License

MIT © 2025 Colin Politi
See [LICENSE](LICENSE) for details.
