"""
termcolorx.animation — Efek animasi teks terminal (spinner, typing, dll).
"""

import sys, time
import asyncio
from .color import TermColorX

class Animation:
    @staticmethod
    def typing(text, delay=0.05, color="cyan"):
        for ch in text:
            sys.stdout.write(TermColorX.colorize(ch, fg=color))
            sys.stdout.flush()
            time.sleep(delay)
        print()

    @staticmethod
    def spinner(duration=3, color="yellow"):
        spinner_chars = ['|', '/', '-', '\\']
        end_time = time.time() + duration
        i = 0
        while time.time() < end_time:
            sys.stdout.write("\r" + TermColorX.colorize(spinner_chars[i % 4], fg=color))
            sys.stdout.flush()
            time.sleep(0.1)
            i += 1
        sys.stdout.write("\r")
        print(TermColorX.green("✔ Done!"))
    @staticmethod
    def loading_dots(count=3, delay=0.5, color="magenta"):
        for i in range(count):
            sys.stdout.write(TermColorX.colorize(".", fg=color))
            sys.stdout.flush()
            time.sleep(delay)
        print()
    @staticmethod
    def progress_bar(total=30, duration=5, color="green"):
        for i in range(total + 1):
            percent = (i / total) * 100
            bar = '█' * i + '░' * (total - i)
            sys.stdout.write(f"\r{TermColorX.colorize(f'[{bar}] {percent:.2f}%', fg=color)}")
            sys.stdout.flush()
            time.sleep(duration / total)
        print()
    @staticmethod
    def clear_line():
        sys.stdout.write("\r" + " " * 80 + "\r")
        sys.stdout.flush()
    @staticmethod
    def type_and_spinner(text, typing_delay=0.05, spinner_duration=3, color="cyan"):
        Animation.typing(text, delay=typing_delay, color=color)
        Animation.spinner(duration=spinner_duration, color=color)
    @staticmethod
    def loading_message(message, dots=3, dot_delay=0.5, color="magenta"):
        sys.stdout.write(TermColorX.colorize(message, fg=color))
        sys.stdout.flush()
        Animation.loading_dots(count=dots, delay=dot_delay, color=color)
    @staticmethod
    def progress_with_message(message, total=30, duration=5, color="green"):
        sys.stdout.write(TermColorX.colorize(message + " ", fg=color))
        sys.stdout.flush()
        Animation.progress_bar(total=total, duration=duration, color=color)
    @staticmethod
    async def async_spinner(message, duration=3, color="yellow"):
        sys.stdout.write(TermColorX.colorize(message + " ", fg=color))
        sys.stdout.flush()
        spinner_chars = ['|', '/', '-', '\\']
        end_time = time.time() + duration
        i = 0
        while time.time() < end_time:
            sys.stdout.write("\r" + TermColorX.colorize(message + " " + spinner_chars[i % 4], fg=color))
            sys.stdout.flush()
            await asyncio.sleep(0.1)
            i += 1
        sys.stdout.write("\r")
        print(TermColorX.green("✔ Done!"))
    @staticmethod
    async def async_type_and_spinner(text, typing_delay=0.05, spinner_duration=3, color="cyan"):
        for ch in text:
            sys.stdout.write(TermColorX.colorize(ch, fg=color))
            sys.stdout.flush()
            await asyncio.sleep(typing_delay)
        print()
        await Animation.async_spinner("Processing...", duration=spinner_duration, color=color)
    @staticmethod
    async def async_progress_with_message(message, total=30, duration=5, color="green"):
        sys.stdout.write(TermColorX.colorize(message + " ", fg=color))
        sys.stdout.flush()
        for i in range(total + 1):
            percent = (i / total) * 100
            bar = '█' * i + '░' * (total - i)
            sys.stdout.write(f"\r{TermColorX.colorize(message + ' [' + bar + f'] {percent:.2f}%', fg=color)}")
            sys.stdout.flush()
            await asyncio.sleep(duration / total)
        print()
    @staticmethod
    def multiline_typing(lines, delay=0.05, color="cyan"):
        for line in lines:
            Animation.typing(line, delay=delay, color=color)
            time.sleep(0.3)
    @staticmethod
    async def async_multiline_typing(lines, delay=0.05, color="cyan"):
        for line in lines:
            for ch in line:
                sys.stdout.write(TermColorX.colorize(ch, fg=color))
                sys.stdout.flush()
                await asyncio.sleep(delay)
            print()
            await asyncio.sleep(0.3)