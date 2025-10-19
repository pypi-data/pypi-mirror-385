"""
warna_teks.rgb
Modul untuk mendukung warna RGB (24-bit) di terminal modern.
"""

class RGB:
    RESET = "\033[0m"

    @staticmethod
    def rgb(teks, r, g, b):
        return f"\033[38;2;{r};{g};{b}m{teks}{RGB.RESET}"

    @staticmethod
    def bg_rgb(teks, r, g, b):
        return f"\033[48;2;{r};{g};{b}m{teks}{RGB.RESET}"

    @staticmethod
    def gradasi(teks, warna_awal, warna_akhir):
        """Warna gradasi teks: warna_awal = (r1,g1,b1), warna_akhir = (r2,g2,b2)"""
        hasil = ""
        panjang = len(teks)
        for i, huruf in enumerate(teks):
            r = int(warna_awal[0] + (warna_akhir[0] - warna_awal[0]) * i / panjang)
            g = int(warna_awal[1] + (warna_akhir[1] - warna_awal[1]) * i / panjang)
            b = int(warna_awal[2] + (warna_akhir[2] - warna_awal[2]) * i / panjang)
            hasil += f"\033[38;2;{r};{g};{b}m{huruf}"
        return hasil + RGB.RESET