import unittest
import subprocess
import os

class IntegrationTests(unittest.TestCase):
    def setUp(self):
        self.base_dir = os.path.dirname(__file__)
        self.input_file = os.path.join(self.base_dir, "test.yaml")
        self.output_file = os.path.join(self.base_dir, "test.txt")

        if os.path.exists(self.output_file):
            os.remove(self.output_file)

    def test_integration_simple(self):
        with open(self.input_file, "w", encoding="utf-8") as f:
            f.write(
                "deviceName: 'SensorX'\n"
                "interval: 30\n"
                "sensors:\n"
                "  - time:\n"
                "      - \"30 seconds\"\n"
                "      - \"15 minutes\"\n"
                "  - 'humidity'\n"
            )

        res = subprocess.run(
            ["python", os.path.join(self.base_dir, "main.py"),
             "-i", self.input_file, "-o", self.output_file],
            capture_output=True,
            text=True,
            encoding='utf-8'
        )

        self.assertEqual(res.returncode, 0, f"Stdout:\n{res.stdout}\nStderr:\n{res.stderr}")

        with open(self.output_file, "r", encoding="utf-8") as f:
            output = f.read().strip()

        expected = (
            "deviceName := 'SensorX';\n"
            "interval := 30;\n"
            "sensors := list(list('30 seconds','15 minutes'),'humidity');"
        )
        self.assertEqual(output, expected)

    def test_integration_invalid_name(self):
        # Тест для некорректного имени, ожидаем ошибку
        with open(self.input_file, "w", encoding="utf-8") as f:
            f.write("device1: 100\n")

        res = subprocess.run(
            ["python", os.path.join(self.base_dir, "main.py"),
             "-i", self.input_file, "-o", self.output_file],
            capture_output=True,
            text=True,
            encoding='utf-8'
        )

        self.assertNotEqual(res.returncode, 0, f"Stdout:\n{res.stdout}\nStderr:\n{res.stderr}")
        self.assertIn("Ошибка:", res.stderr or "")

    def test_integration_just_numbers_and_strings(self):
        with open(self.input_file, "w", encoding="utf-8") as f:
            f.write(
                "appName: 'MyApp'\n"
                "maxConnections: 10\n"
            )

        res = subprocess.run(
            ["python", os.path.join(self.base_dir, "main.py"),
             "-i", self.input_file, "-o", self.output_file],
            capture_output=True,
            text=True,
            encoding='utf-8'
        )

        self.assertEqual(res.returncode, 0, f"Stdout:\n{res.stdout}\nStderr:\n{res.stderr}")

        with open(self.output_file, "r", encoding="utf-8") as f:
            output = f.read().strip()

        expected = (
            "appName := 'MyApp';\n"
            "maxConnections := 10;"
        )
        self.assertEqual(output, expected)

if __name__ == '__main__':
    unittest.main()
