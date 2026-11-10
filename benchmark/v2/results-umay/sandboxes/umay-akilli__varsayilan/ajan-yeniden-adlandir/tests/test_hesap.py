import unittest
import warnings

from fatura import kdv_hesapla, hesapKdvDahil, toplam_tutar


class HesapTest(unittest.TestCase):
    def test_kdv(self):
        self.assertEqual(kdv_hesapla(100), 20.0)
        self.assertEqual(kdv_hesapla(100, 0.10), 10.0)

    def test_dahil(self):
        self.assertEqual(hesapKdvDahil(100), 120.0)

    def test_toplam(self):
        self.assertEqual(toplam_tutar([(100, 2, 0.2), (50, 1, 0.1)]), 295.0)

    def test_eski_ad_uyari(self):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            from fatura import hesapKdv
            sonuc = hesapKdv(100)
            self.assertEqual(sonuc, 20.0)
            self.assertEqual(len(w), 1)
            self.assertTrue(issubclass(w[0].category, DeprecationWarning))
            self.assertIn("kdv_hesapla", str(w[0].message))


if __name__ == "__main__":
    unittest.main()
