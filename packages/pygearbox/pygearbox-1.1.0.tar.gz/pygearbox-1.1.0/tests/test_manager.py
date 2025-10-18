import unittest
from unittest.mock import MagicMock, patch
from pyGearBox.manager import PyGearBox


class TestPyGearBox(unittest.TestCase):
    @patch("pyGearBox.manager.import_module")
    def test_load_plugins_success(self, mock_import_module):
        # Mock plugin class
        mock_plugin = MagicMock()
        mock_plugin.is_valid.return_value = True

        # Mock import_module to return the mock plugin class
        mock_import_module.return_value.PyGearBoxPlugin.return_value = mock_plugin

        # Initialize PyGearBox with a list of plugins
        plugins = ["plugin1", "plugin2"]
        manager = PyGearBox(plugins)

        # Load plugins
        manager.load_plugins()

        # Check if plugins are loaded correctly
        self.assertIn("plugin1", manager.loaded_plugins)
        self.assertIn("plugin2", manager.loaded_plugins)
        self.assertEqual(manager.loaded_plugins["plugin1"], mock_plugin)
        self.assertEqual(manager.loaded_plugins["plugin2"], mock_plugin)

        # Check if on_load method was called
        mock_plugin.on_load.assert_called()

    def test_get_plugin(self):
        # Initialize PyGearBox with a list of plugins
        plugins = ["plugin1"]
        manager = PyGearBox(plugins)

        # Mock plugin instance and add to loaded plugins
        mock_plugin = MagicMock()
        manager._loaded_plugins["plugin1"] = mock_plugin

        # Retrieve plugin
        plugin = manager.get_plugin("plugin1")
        self.assertEqual(plugin, mock_plugin)

        # Retrieve non-existent plugin
        plugin = manager.get_plugin("plugin2")
        self.assertIsNone(plugin)

    def test_run_plugin_success(self):
        # Initialize PyGearBox with a list of plugins
        plugins = ["plugin1"]
        manager = PyGearBox(plugins)

        # Mock plugin instance and add to loaded plugins
        mock_plugin = MagicMock()
        manager._loaded_plugins["plugin1"] = mock_plugin

        # Run plugin
        manager.run_plugin("plugin1", "arg1", kwarg1="value1")

        # Check if plugin methods were called
        mock_plugin.pre_run.assert_called_once()
        mock_plugin.run.assert_called_once_with("arg1", kwarg1="value1")
        mock_plugin.post_run.assert_called_once()

    def test_run_plugin_not_found(self):
        # Initialize PyGearBox with a list of plugins
        plugins = ["plugin1"]
        manager = PyGearBox(plugins)

        # Attempt to run non-existent plugin
        with self.assertRaises(ValueError) as context:
            manager.run_plugin("plugin2")

        self.assertEqual(str(context.exception), "Plugin 'plugin2' not found")

    def test_loaded_plugins_property(self):
        # Initialize PyGearBox with a list of plugins
        plugins = ["plugin1"]
        manager = PyGearBox(plugins)

        # Mock plugin instance and add to loaded plugins
        mock_plugin = MagicMock()
        manager._loaded_plugins["plugin1"] = mock_plugin

        # Check loaded plugins property
        self.assertEqual(manager.loaded_plugins, {"plugin1": mock_plugin})

    def test_plugin_list_property(self):
        # Initialize PyGearBox with a list of plugins
        plugins = ["plugin1", "plugin2"]
        manager = PyGearBox(plugins)

        # Check plugin list property
        self.assertEqual(manager.plugin_list, plugins)


if __name__ == "__main__":
    unittest.main()
