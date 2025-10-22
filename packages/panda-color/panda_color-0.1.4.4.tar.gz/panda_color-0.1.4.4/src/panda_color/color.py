from typing import Iterable, Tuple, Any, Iterator, Union
from collections.abc import Sequence
import random

Number = Union[int, float]


class Color(Sequence[int]):
    RGB_MIN = 0
    RGB_MAX = 255

    def __init__(self, *args: Any):
        if len(args) == 0:
            self._r, self._g, self._b = 0, 0, 0
        elif len(args) == 1:
            self._init_single(args[0])
        elif len(args) == 3:
            self._r, self._g, self._b = [
                self._validate_color_value(v, name)
                for v, name in zip(args, ["red", "green", "blue"])
            ]
        else:
            raise ValueError(f"Color() takes 0, 1, or 3 arguments ({len(args)} given)")

    def _init_single(self, arg: Any):
        if isinstance(arg, Color):
            self._r, self._g, self._b = arg._r, arg._g, arg._b
        elif isinstance(arg, str):
            self._init_str(arg)
        elif isinstance(arg, Iterable) and not isinstance(arg, (str, bytes)):
            self._init_iter(arg)
        else:
            raise TypeError(f"Cannot initialize Color from {type(arg).__name__}")

    def _init_str(self, color_str: str):
        try:
            parts = [int(x.strip()) for x in color_str.split(",")]
            if len(parts) != 3:
                raise ValueError("Expected 3 comma-separated values")
            self._r, self._g, self._b = [
                self._validate_color_value(v, name)
                for v, name in zip(parts, ["red", "green", "blue"])
            ]
        except Exception as e:
            raise ValueError(f"Invalid color string '{color_str}': {e}")

    def _init_iter(self, iterable: Iterable[Any]):
        values = list(iterable)
        if len(values) != 3:
            raise ValueError(
                f"Iterable must contain exactly 3 values, got {len(values)}"
            )
        self._r, self._g, self._b = [
            self._validate_color_value(v, name)
            for v, name in zip(values, ["red", "green", "blue"])
        ]

    def _validate_color_value(self, value: Any, name: str = "color") -> int:
        if not isinstance(value, (int, float)):
            raise TypeError(f"{name} must be a number, got {type(value).__name__}")
        value = int(value)
        if not (self.RGB_MIN <= value <= self.RGB_MAX):
            raise ValueError(
                f"{name} must be in [{self.RGB_MIN}, {self.RGB_MAX}], got {value}"
            )
        return value

    def _get_component(self, char: str) -> int:
        return {"r": self._r, "g": self._g, "b": self._b}[char]

    def _set_component(self, char: str, value: int):
        validated = self._validate_color_value(value, char)
        if char == "r":
            self._r = validated
        elif char == "g":
            self._g = validated
        elif char == "b":
            self._b = validated
        else:
            raise ValueError(f"Invalid component: {char}")

    def __getattr__(self, name: str):
        if all(c in "rgb" for c in name):
            if len(name) == 1:
                return self._get_component(name)
            return tuple(self._get_component(c) for c in name)
        raise AttributeError(f"'Color' object has no attribute '{name}'")

    def __setattr__(self, name: str, value: Any):
        if name.startswith("_"):
            super().__setattr__(name, value)
        elif all(c in "rgb" for c in name):
            if len(name) == 1:
                self._set_component(name, value)
            else:
                if not isinstance(value, Iterable) or isinstance(value, (str, bytes)):
                    raise TypeError(
                        f"Expected iterable of values for '{name}', got {type(value).__name__}"
                    )
                values = list(value)
                if len(values) != len(name):
                    raise ValueError(f"Expected {len(name)} values, got {len(values)}")
                for c, v in zip(name, values):
                    self._set_component(c, v)
        else:
            super().__setattr__(name, value)

    # === Properties ===
    @property
    def r(self) -> int:
        return self._r

    @property
    def g(self) -> int:
        return self._g

    @property
    def b(self) -> int:
        return self._b

    @property
    def rgb(self) -> "Color":
        return Color(self._r, self._g, self._b)

    @r.setter
    def r(self, value: int):
        self._r = self._validate_color_value(value, "red")

    @g.setter
    def g(self, value: int):
        self._g = self._validate_color_value(value, "green")

    @b.setter
    def b(self, value: int):
        self._b = self._validate_color_value(value, "blue")

    @rgb.setter
    def rgb(self, value: Iterable[int]):
        r, g, b = list(value)
        self.r, self.g, self.b = r, g, b

    # === Conversions ===
    def to_hex(self) -> str:
        return f"#{self._r:02x}{self._g:02x}{self._b:02x}"

    def to_tuple(self) -> Tuple[int, int, int]:
        return (self._r, self._g, self._b)

    def to_list(self) -> list[int]:
        return [self._r, self._g, self._b]

    def to_dict(self) -> dict[str, int]:
        return {"r": self._r, "g": self._g, "b": self._b}

    def to_bytes(
        self,
        num_parts: int = 3,
        num_type: str = "f32",
        big_endian: bool = False,
        alpha: float = 1.0,
    ) -> bytes:
        from struct import pack

        type_map = {"f32": "f", "f64": "d", "u8": "B"}
        if num_type not in type_map:
            raise ValueError(f"Unsupported type: {num_type}")
        type_char = type_map[num_type]
        endian = ">" if big_endian else "<"
        fmt = f"{endian}{num_parts}{type_char}"

        data = self.rgb if num_type == "u8" else self.normalized()
        if num_parts == 4:
            alpha_val = int(alpha * 255) if num_type == "u8" else float(alpha)
            return pack(fmt, *data, alpha_val)
        elif num_parts == 3:
            return pack(fmt, *data)
        else:
            raise ValueError("num_parts must be 3 or 4")

    def css_rgb(self) -> str:
        return f"rgb({self._r}, {self._g}, {self._b})"

    def css_rgba(self, alpha: float = 1.0) -> str:
        alpha = max(0.0, min(1.0, alpha))
        return f"rgba({self._r}, {self._g}, {self._b}, {alpha})"

    def normalized(self) -> Tuple[float, float, float]:
        return (self._r / 255, self._g / 255, self._b / 255)

    def int24(self) -> int:
        return (self._r << 16) | (self._g << 8) | self._b

    @property
    def luminance(self) -> float:
        def linearize(c: int) -> float:
            lc = c / 255
            return lc / 12.92 if lc <= 0.03928 else ((lc + 0.055) / 1.055) ** 2.4

        return (
            0.2126 * linearize(self._r)
            + 0.7152 * linearize(self._g)
            + 0.0722 * linearize(self._b)
        )

    # === Variants ===
    def with_red(self, r: int) -> "Color":
        return Color(r, self._g, self._b)

    def with_green(self, g: int) -> "Color":
        return Color(self._r, g, self._b)

    def with_blue(self, b: int) -> "Color":
        return Color(self._r, self._g, b)

    # === Factory Methods ===
    @classmethod
    def from_hex(cls, hex_str: str) -> "Color":
        hex_str = hex_str.lstrip("#")
        if len(hex_str) != 6:
            raise ValueError("Hex string must be 6 digits")
        r, g, b = int(hex_str[0:2], 16), int(hex_str[2:4], 16), int(hex_str[4:6], 16)
        return cls(r, g, b)

    @classmethod
    def from_normalized(cls, r: float, g: float, b: float) -> "Color":
        return cls(int(r * 255), int(g * 255), int(b * 255))

    @classmethod
    def from_int24(cls, val: int) -> "Color":
        return cls((val >> 16) & 0xFF, (val >> 8) & 0xFF, val & 0xFF)

    @classmethod
    def random(cls) -> "Color":
        return cls(
            random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)
        )

    # === Dunder Methods ===
    def __iter__(self) -> Iterator[int]:
        return iter((self._r, self._g, self._b))

    def __getitem__(self, index: int) -> int:
        return (self._r, self._g, self._b)[index]

    def __len__(self) -> int:
        return 3

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, Color) and self.to_tuple() == other.to_tuple()

    def __hash__(self) -> int:
        return hash((self._r, self._g, self._b))

    def __str__(self) -> str:
        return f"Color({self._r}, {self._g}, {self._b})"

    def __repr__(self) -> str:
        return str(self)


# === CONSTANT COLORS ===
class Colors:
    """A class containing constants of common colors"""

    BLACK = Color(0, 0, 0)
    WHITE = Color(255, 255, 255)
    RED = Color(255, 0, 0)
    GREEN = Color(0, 255, 0)
    BLUE = Color(0, 0, 255)
    YELLOW = Color(255, 255, 0)
    CYAN = Color(0, 255, 255)
    MAGENTA = Color(255, 0, 255)
    GRAY = Color(128, 128, 128)
    LIGHT_GRAY = Color(192, 192, 192)
    DARK_GRAY = Color(64, 64, 64)
    ORANGE = Color(255, 165, 0)
    PINK = Color(255, 192, 203)
    PURPLE = Color(128, 0, 128)
    BROWN = Color(165, 42, 42)
    LIME = Color(0, 255, 0)
    TEAL = Color(0, 128, 128)
    NAVY = Color(0, 0, 128)
    OLIVE = Color(128, 128, 0)
    MAROON = Color(128, 0, 0)
    AQUA = Color(0, 255, 255)
    CRIMSON = Color(220, 20, 60)
    CORNFLOWER_BLUE = Color(100, 149, 237)
    DARK_ORANGE = Color(255, 140, 0)
    DARK_GREEN = Color(0, 100, 0)
    DARK_RED = Color(139, 0, 0)
    STEEL_BLUE = Color(70, 130, 180)
    DARK_SLATE_GRAY = Color(47, 79, 79)
    MEDIUM_PURPLE = Color(147, 112, 219)
    FIREBRICK = Color(178, 34, 34)
    SALMON = Color(250, 128, 114)
    LIME_GREEN = Color(50, 205, 50)
    SKY_BLUE = Color(135, 206, 235)
    GOLD = Color(255, 215, 0)
    SILVER = Color(192, 192, 192)
