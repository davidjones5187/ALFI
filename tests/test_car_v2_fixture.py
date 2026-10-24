import tempfile
import unittest
from pathlib import Path
from experiments.car_v2_fixture import create_fixture
from experiments.car_v2_review import ReviewedCARPilot
from experiments.car_v2_context import build_car_context


class SyntheticFixtureTests(unittest.TestCase):
    def test_fixture_status_and_isolation(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp) / "fixture"
            result = create_fixture(directory)
            self.assertEqual(result["model_calls"], 0)
            self.assertEqual(result["expected_approved_answer"], "violet")
            store = ReviewedCARPilot(directory / "synthetic_car.sqlite3")
            try:
                text = build_car_context(store, "larkspur_launch", enabled=True)
                self.assertIn("violet", text)
                self.assertNotIn("amber", text)
                self.assertEqual(build_car_context(store, "larkspur_policy", enabled=True), "")
                self.assertEqual(build_car_context(store, "rain_formation", enabled=True), "")
            finally:
                store.close()

    def test_refuses_existing_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(FileExistsError):
                create_fixture(Path(tmp))


if __name__ == "__main__":
    unittest.main()
