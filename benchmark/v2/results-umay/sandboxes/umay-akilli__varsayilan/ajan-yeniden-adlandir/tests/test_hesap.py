import unittest
import warnings

from fatura import kdv_hesapla, hesapKdvDahil, toplam_tutar


class HesapTest(unittest.TestCase):
    def test_kdv(self):
        self.assertEqual(kdv_hesapla(100), 20.0)
        self.assertEqual(kdv_hesapla(100, 0.10), 10.0)

    def test_kdv_deprecated(self):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            from fatura import hesapKdv
            self.assertEqual(hesapKdv(100), 20.0)
            self.assertTrue(any(issubclass(warn.category, DeprecationWarning) for warn in w))

    def test_dahil(self):
        self.assertEqual(hesapKdvDahil(100), 120.0)

    def test_toplam(self):
        self.assertEqual(toplam_tutar([(100, 2, 0.2), (50, 1, 0.1)]), 295.0)


if __name__ == "__main__":
    unittest.main()
