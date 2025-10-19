"""
termcolorx.platform — Deteksi otomatis dukungan warna terminal.
"""

import os, sys, platform

class PlatformSupport:
    @staticmethod
    def enable_ansi():
        if os.name == 'nt':
            os.system("")  # Enable ANSI di Windows 10+
        return True

    @staticmethod
    def is_supported():
        if sys.stdout.isatty():
            return True
        return False

    @staticmethod
    def info():
        return {
            "os": platform.system(),
            "version": platform.version(),
            "ansi_supported": PlatformSupport.is_supported()
        }
    
