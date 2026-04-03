"""Pruebas de jarvis_config."""

from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import jarvis_config  # noqa: E402


class TestJarvisConfig(unittest.TestCase):
    def test_load_empty_when_missing(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            home = Path(td)
            with patch.object(jarvis_config, "config_path", return_value=home / "nope.json"):
                self.assertEqual(jarvis_config.load_user_config(), {})

    def test_load_valid_json(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            home = Path(td)
            cfg = home / "config.json"
            cfg.write_text(
                json.dumps({"titulo": "Test", "project": "~/p", "unknown": 1}),
                encoding="utf-8",
            )
            with patch.object(jarvis_config, "config_path", return_value=cfg):
                data = jarvis_config.load_user_config()
        self.assertEqual(data.get("titulo"), "Test")
        self.assertNotIn("unknown", data)


if __name__ == "__main__":
    unittest.main()
