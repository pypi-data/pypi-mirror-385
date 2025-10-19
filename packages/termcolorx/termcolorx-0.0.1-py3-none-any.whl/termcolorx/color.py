"""
termcolorx.color — Pewarnaan teks terminal dasar, 256, dan RGB.
"""

class TermColorX:
    COLORS = {
        "black": 30, "red": 31, "green": 32, "yellow": 33,
        "blue": 34, "magenta": 35, "cyan": 36, "white": 37, "reset": 39
    }
    BACKGROUNDS = {
        "black": 40, "red": 41, "green": 42, "yellow": 43,
        "blue": 44, "magenta": 45, "cyan": 46, "white": 47, "reset": 49
    }
    STYLES = {
        "bold": 1, "dim": 2, "italic": 3, "underline": 4,
        "blink": 5, "reverse": 7, "hidden": 8, "reset": 0
    }

    @staticmethod
    def colorize(text, fg=None, bg=None, style=None):
        codes = []
        if fg and fg in TermColorX.COLORS: codes.append(str(TermColorX.COLORS[fg]))
        if bg and bg in TermColorX.BACKGROUNDS: codes.append(str(TermColorX.BACKGROUNDS[bg]))
        if style and style in TermColorX.STYLES: codes.append(str(TermColorX.STYLES[style]))
        prefix = f"\033[{';'.join(codes)}m" if codes else ""
        return f"{prefix}{text}\033[0m"

    @staticmethod
    def rgb(text, r, g, b, background=False):
        return f"\033[{48 if background else 38};2;{r};{g};{b}m{text}\033[0m"

    @staticmethod
    def color256(text, code, background=False):
        return f"\033[{48 if background else 38};5;{code}m{text}\033[0m"

    # Shortcut
    @staticmethod
    def red(t): return TermColorX.colorize(t, fg="red")
    @staticmethod
    def green(t): return TermColorX.colorize(t, fg="green")
    @staticmethod
    def yellow(t): return TermColorX.colorize(t, fg="yellow")
    @staticmethod
    def blue(t): return TermColorX.colorize(t, fg="blue")
    @staticmethod
    def magenta(t): return TermColorX.colorize(t, fg="magenta")
    @staticmethod
    def cyan(t): return TermColorX.colorize(t, fg="cyan")
    @staticmethod
    def bold(t): return TermColorX.colorize(t, style="bold")
    @staticmethod
    def underline(t): return TermColorX.colorize(t, style="underline")
    @staticmethod
    def blink(t): return TermColorX.colorize(t, style="blink")
    @staticmethod
    def reverse(t): return TermColorX.colorize(t, style="reverse")
    @staticmethod
    def dim(t): return TermColorX.colorize(t, style="dim")
    @staticmethod
    def italic(t): return TermColorX.colorize(t, style="italic")
    @staticmethod
    def hidden(t): return TermColorX.colorize(t, style="hidden")