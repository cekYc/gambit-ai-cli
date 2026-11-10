import unittest

from fatura import hesapKdv, hesapKdvDahil, toplam_tutar


class HesapTest(unittest.TestCase):
    def test_kdv(self):
        self.assertEqual(hesapKdv(100), 20.0)
        self.assertEqual(hesapKdv(100, 0.10), 10.0)

    def test_dahil(self):
        self.assertEqual(hesapKdvDahil(100), 120.0)

    def test_toplam(self):
        self.assertEqual(toplam_tutar([(100, 2, 0.2), (50, 1, 0.1)]), 295.0)


if __name__ == "__main__":
    unittest.main()
