import unittest
from pyGearBox.plugin import PyGearBoxBasePlugin


class TestPyGearBoxBasePlugin(unittest.TestCase):
    class ConcretePlugin(PyGearBoxBasePlugin):
        @property
        def name(self):
            return "ConcretePlugin"

        @property
        def plugin_type(self):
            return "Test"

        def run(self):
            pass

    def setUp(self):
        self.plugin = self.ConcretePlugin()

    def test_is_valid(self):
        self.assertTrue(self.plugin.is_valid())

    def test_on_load(self):
        with self.assertLogs("root", level="DEBUG") as cm:
            self.plugin.on_load()
        self.assertIn("ConcretePlugin loaded", cm.output[0])

    def test_on_unload(self):
        with self.assertLogs("root", level="DEBUG") as cm:
            self.plugin.on_unload()
        self.assertIn("ConcretePlugin exited", cm.output[0])

    def test_pre_run(self):
        self.assertIsNone(self.plugin.pre_run())

    def test_post_run(self):
        self.assertIsNone(self.plugin.post_run())

    def test_name(self):
        self.assertEqual(self.plugin.name, "ConcretePlugin")

    def test_plugin_type(self):
        self.assertEqual(self.plugin.plugin_type, "Test")


if __name__ == "__main__":
    unittest.main()
