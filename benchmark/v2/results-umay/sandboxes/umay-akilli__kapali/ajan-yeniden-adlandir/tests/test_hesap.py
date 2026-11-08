import unittest
import warnings

from fatura import kdv_hesapla, hesapKdv, hesapKdvDahil, toplam_tutar


class HesapTest(unittest.TestCase):
    def test_kdv(self):
        self.assertEqual(kdv_hesapla(100), 20.0)
        self.assertEqual(kdv_hesapla(100, 0.10), 10.0)

    def test_kdv_deprecated(self):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            self.assertEqual(hesapKdv(100), 20.0)
            self.assertEqual(len(w), 1)
            self.assertTrue(issubclass(w[0].category, DeprecationWarning))
            self.assertIn("deprecated", str(w[0].message).lower())

    def test_dahil(self):
        self.assertEqual(hesapKdvDahil(100), 120.0)

    def test_toplam(self):
        self.assertEqual(toplam_tutar([(100, 2, 0.2), (50, 1, 0.1)]), 295.0)


if __name__ == "__main__":
    unittest.main()
