"""
warna_teks.warna
Modul utama untuk pewarnaan teks menggunakan kode ANSI.
Mendukung teks biasa, latar belakang, dan kombinasi gaya.
"""

class Color:
    # Warna dasar teks
    HITAM = "\033[30m"
    MERAH = "\033[31m"
    HIJAU = "\033[32m"
    KUNING = "\033[33m"
    BIRU = "\033[34m"
    UNGU = "\033[35m"
    CYAN = "\033[36m"
    PUTIH = "\033[37m"

    # Warna terang
    TERANG = {
        "hitam": "\033[90m", "merah": "\033[91m", "hijau": "\033[92m",
        "kuning": "\033[93m", "biru": "\033[94m", "ungu": "\033[95m",
        "cyan": "\033[96m", "putih": "\033[97m"
    }

    # Background
    BG = {
        "hitam": "\033[40m", "merah": "\033[41m", "hijau": "\033[42m",
        "kuning": "\033[43m", "biru": "\033[44m", "ungu": "\033[45m",
        "cyan": "\033[46m", "putih": "\033[47m"
    }

    # Gaya teks
    GAYA = {
        "tebal": "\033[1m",
        "miring": "\033[3m",
        "garis_bawah": "\033[4m",
        "kedip": "\033[5m",
        "tersembunyi": "\033[8m",
        "reset": "\033[0m"
    }

    RESET = "\033[0m"

    @staticmethod
    def format(teks, warna=None, gaya=None, bg=None):
        kode = ""
        if gaya and gaya in Color.GAYA:
            kode += Color.GAYA[gaya]
        if warna:
            kode += getattr(Color, warna.upper(), "")
        if bg and bg in Color.BG:
            kode += Color.BG[bg]
        return f"{kode}{teks}{Color.RESET}"

    # Cepat pakai
    @staticmethod
    def merah(teks): return Color.format(teks, "MERAH")
    @staticmethod
    def hijau(teks): return Color.format(teks, "HIJAU")
    @staticmethod
    def biru(teks): return Color.format(teks, "BIRU")
    @staticmethod
    def tebal_merah(teks): return Color.format(teks, "MERAH", "tebal")
    @staticmethod
    def garis_bawah_kuning(teks): return Color.format(teks, "KUNING", "garis_bawah")
