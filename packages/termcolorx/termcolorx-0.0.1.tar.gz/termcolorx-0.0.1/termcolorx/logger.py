"""
termcolorx.logger — Logger berwarna dengan opsi simpan ke file.
"""

from datetime import datetime
from .color import TermColorX

class LoggerColor:
    COLORS = {
        "INFO": ("green", None), "WARNING": ("yellow", None),
        "ERROR": ("red", None), "DEBUG": ("cyan", None),
        "SUCCESS": ("blue", None), "CRITICAL": ("white", "red")
    }

    def __init__(self, name="LoggerColor", log_file=None):
        self.name = name
        self.log_file = log_file

    def _format_message(self, level, message):
        fg, bg = self.COLORS.get(level, ("white", None))
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        level_text = TermColorX.colorize(f"[{level}]", fg=fg, bg=bg, style="bold")
        plain = f"{timestamp} [{level}] {message}"
        colored = f"{timestamp} {level_text} {message}"
        return plain, colored

    def log(self, level, message):
        plain, colored = self._format_message(level.upper(), message)
        print(colored)
        if self.log_file:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(plain + "\n")

    def info(self, msg): self.log("INFO", msg)
    def warning(self, msg): self.log("WARNING", msg)
    def error(self, msg): self.log("ERROR", msg)
    def debug(self, msg): self.log("DEBUG", msg)
    def success(self, msg): self.log("SUCCESS", msg)
    def critical(self, msg): self.log("CRITICAL", msg)
