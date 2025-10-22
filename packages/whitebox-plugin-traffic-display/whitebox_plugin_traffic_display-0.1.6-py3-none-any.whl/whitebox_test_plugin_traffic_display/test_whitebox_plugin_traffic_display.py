from django.test import TestCase
from unittest.mock import patch, MagicMock

from plugin.manager import plugin_manager


class TestWhiteboxPluginTrafficDisplay(TestCase):
    def setUp(self) -> None:
        self.plugin = next(
            (
                x
                for x in plugin_manager.whitebox_plugins
                if x.__class__.__name__ == "WhiteboxPluginTrafficDisplay"
            ),
            None,
        )
        return super().setUp()

    def test_plugin_loaded(self):
        self.assertIsNotNone(self.plugin)

    def test_plugin_name(self):
        self.assertEqual(self.plugin.name, "Traffic Display")

    def test_plugin_capabilities(self):
        self.assertIn("traffic", self.plugin.provides_capabilities)
