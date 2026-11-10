import unittest
from datetime import date

from tarih import artik_yil, ay_ekle, is_gunu_say


class TarihTest(unittest.TestCase):
    def test_artik(self):
        self.assertTrue(artik_yil(2024))
        self.assertFalse(artik_yil(2023))

    def test_ay_ekle(self):
        self.assertEqual(ay_ekle(date(2024, 1, 31), 1), date(2024, 2, 29))
        self.assertEqual(ay_ekle(date(2024, 3, 15), 2), date(2024, 5, 15))

    def test_is_gunu(self):
        self.assertEqual(is_gunu_say(date(2026, 3, 2), date(2026, 3, 6)), 5)  # Pzt-Cum


if __name__ == "__main__":
    r = unittest.main(exit=False).result
    if r.wasSuccessful():
        print("TÜM TESTLER GEÇTİ")
