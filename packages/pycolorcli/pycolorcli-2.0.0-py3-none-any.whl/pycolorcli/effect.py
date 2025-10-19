"""
warna_teks.efek
Efek animasi teks seperti mengetik, loading, dan berkedip dinamis.
"""

import sys, time, random
from .color import Color
from .rgb import RGB

class Effect:
    @staticmethod
    def ketik(teks, warna=None, delay=0.05):
        """Menampilkan teks dengan efek mengetik"""
        for huruf in teks:
            if warna:
                sys.stdout.write(Color.format(huruf, warna))
            else:
                sys.stdout.write(huruf)
            sys.stdout.flush()
            time.sleep(delay)
        print()

    @staticmethod
    def loading(teks="Memproses", warna="HIJAU", durasi=3):
        """Efek loading animasi"""
        animasi = ["⠋","⠙","⠹","⠸","⠼","⠴","⠦","⠧","⠇","⠏"]
        akhir = time.time() + durasi
        i = 0
        while time.time() < akhir:
            sys.stdout.write(f"\r{Color.format(animasi[i % len(animasi)] + ' ' + teks, warna)} ")
            sys.stdout.flush()
            time.sleep(0.1)
            i += 1
        sys.stdout.write("\r" + Color.hijau("✓ Selesai!\n"))

    @staticmethod
    def teks_berkedip(teks, durasi=2, warna_awal=(255,0,0), warna_akhir=(0,0,255)):
        """Animasi teks berkedip dengan gradasi RGB"""
        akhir = time.time() + durasi
        while time.time() < akhir:
            sys.stdout.write("\r" + RGB.gradasi(teks, warna_awal, warna_akhir))
            sys.stdout.flush()
            time.sleep(0.3)
            sys.stdout.write("\r" + RGB.gradasi(teks, warna_akhir, warna_awal))
            sys.stdout.flush()
            time.sleep(0.3)
        print()
