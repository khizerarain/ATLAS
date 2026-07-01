import importlib
import unittest

from core.api import get_all_countries, get_country


class AtlasCliTests(unittest.TestCase):
    def test_main_module_exposes_typer_app(self):
        main = importlib.import_module("main")
        self.assertTrue(hasattr(main, "app"))
        self.assertTrue(callable(main.app))

    def test_country_lookup_falls_back_to_local_dataset(self):
        data = get_country("Japan")
        self.assertIsNotNone(data)
        self.assertEqual(data["name"], "Japan")

    def test_learn_summary_has_africa_data(self):
        countries = get_all_countries()
        africa = [c for c in countries if c.get("continent") == "Africa"]
        self.assertTrue(africa)


if __name__ == "__main__":
    unittest.main()
