"""
termcolorx.gradient — Membuat teks gradien warna RGB.
"""

from .color import TermColorX
import asyncio

class Gradient:
    @staticmethod
    def rainbow(text):
        colors = [
            (255, 0, 0), (255, 127, 0), (255, 255, 0),
            (0, 255, 0), (0, 0, 255), (75, 0, 130), (148, 0, 211)
        ]
        result = ""
        for i, ch in enumerate(text):
            r, g, b = colors[i % len(colors)]
            result += TermColorX.rgb(ch, r, g, b)
        return result
    @staticmethod
    async def rainbow_dynamic(text, delay=0.1, cycles=3):
        colors = [
            (255, 0, 0), (255, 127, 0), (255, 255, 0),
            (0, 255, 0), (0, 0, 255), (75, 0, 130), (148, 0, 211)
        ]
        length = len(colors)
        for cycle in range(cycles):
            result = ""
            for i, ch in enumerate(text):
                r, g, b = colors[(i + cycle) % length]
                result += TermColorX.rgb(ch, r, g, b)
            print(f"\r{result}", end="", flush=True)
            await asyncio.sleep(delay)
        print()
    @staticmethod
    def custom_gradient(text, start_color, end_color):
        def interpolate(c1, c2, factor):
            return int(c1 + (c2 - c1) * factor)
        result = ""
        length = len(text)
        for i, ch in enumerate(text):
            factor = i / max(length - 1, 1)
            r = interpolate(start_color[0], end_color[0], factor)
            g = interpolate(start_color[1], end_color[1], factor)
            b = interpolate(start_color[2], end_color[2], factor)
            result += TermColorX.rgb(ch, r, g, b)
        return result
    @staticmethod
    def vertical_gradient(text, start_color, end_color):
        lines = text.splitlines()
        result = ""
        length = len(lines)
        def interpolate(c1, c2, factor):
            return int(c1 + (c2 - c1) * factor)
        for i, line in enumerate(lines):
            factor = i / max(length - 1, 1)
            r = interpolate(start_color[0], end_color[0], factor)
            g = interpolate(start_color[1], end_color[1], factor)
            b = interpolate(start_color[2], end_color[2], factor)
            colored_line = TermColorX.rgb(line, r, g, b)
            result += colored_line + "\n"
        return result.rstrip("\n")
    @staticmethod
    async def vertical_gradient_dynamic(text, start_color, end_color, delay=0.2, cycles=3):
        lines = text.splitlines()
        length = len(lines)
        def interpolate(c1, c2, factor):
            return int(c1 + (c2 - c1) * factor)
        for cycle in range(cycles):
            result = ""
            for i, line in enumerate(lines):
                factor = (i + cycle) / max(length - 1 + cycles, 1)
                r = interpolate(start_color[0], end_color[0], factor)
                g = interpolate(start_color[1], end_color[1], factor)
                b = interpolate(start_color[2], end_color[2], factor)
                colored_line = TermColorX.rgb(line, r, g, b)
                result += colored_line + "\n"
            print(f"\r{result}", end="", flush=True)
            await asyncio.sleep(delay)
        print()
    @staticmethod
    def horizontal_gradient(text, start_color, end_color):
        result = ""
        length = len(text)
        def interpolate(c1, c2, factor):
            return int(c1 + (c2 - c1) * factor)
        for i, ch in enumerate(text):
            factor = i / max(length - 1, 1)
            r = interpolate(start_color[0], end_color[0], factor)
            g = interpolate(start_color[1], end_color[1], factor)
            b = interpolate(start_color[2], end_color[2], factor)
            result += TermColorX.rgb(ch, r, g, b)
        return result
    @staticmethod
    async def horizontal_gradient_dynamic(text, start_color, end_color, delay=0.1, cycles=3):
        length = len(text)
        def interpolate(c1, c2, factor):
            return int(c1 + (c2 - c1) * factor)
        for cycle in range(cycles):
            result = ""
            for i, ch in enumerate(text):
                factor = (i + cycle) / max(length - 1 + cycles, 1)
                r = interpolate(start_color[0], end_color[0], factor)
                g = interpolate(start_color[1], end_color[1], factor)
                b = interpolate(start_color[2], end_color[2], factor)
                result += TermColorX.rgb(ch, r, g, b)
            print(f"\r{result}", end="", flush=True)
            await asyncio.sleep(delay)
        print()
    