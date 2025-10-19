"""
warna_teks.util
Fungsi tambahan seperti deteksi dukungan warna terminal.
"""

import os, sys

class DeteksiTerminal:
    @staticmethod
    def mendukung_warna():
        if sys.platform == "win32":
            return os.system("") == 0
        return sys.stdout.isatty()

    @staticmethod
    def info():
        print("Platform :", sys.platform)
        print("Mendukung Warna:", "Ya" if DeteksiTerminal.mendukung_warna() else "Tidak")