"""Pruebas ligeras de jarvis_lista (sin pygame/edge_tts)."""

from __future__ import annotations

import os
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import jarvis_lista  # noqa: E402


class TestJarvisLista(unittest.TestCase):
    def setUp(self) -> None:
        self._mark = os.environ.get("JARVIS_MARK_LEVEL")

    def tearDown(self) -> None:
        if self._mark is None:
            os.environ.pop("JARVIS_MARK_LEVEL", None)
        else:
            os.environ["JARVIS_MARK_LEVEL"] = self._mark

    def test_mark_level_clamped(self) -> None:
        os.environ["JARVIS_MARK_LEVEL"] = "99"
        self.assertEqual(jarvis_lista.mark_level(), 7)
        os.environ["JARVIS_MARK_LEVEL"] = "0"
        self.assertEqual(jarvis_lista.mark_level(), 1)

    def test_mark_music_volume_in_range(self) -> None:
        os.environ["JARVIS_MARK_LEVEL"] = "4"
        f = jarvis_lista.mark_music_volume_factor()
        self.assertGreaterEqual(f, 0.25)
        self.assertLessEqual(f, 1.0)

    def test_enhance_lines_respects_privacy(self) -> None:
        l1, l2 = jarvis_lista.enhance_lines(
            "uno",
            "dos",
            privacy=True,
            lista_completa=True,
            titulo="x",
            theme="iron",
        )
        self.assertEqual(l1, "uno")
        self.assertEqual(l2, "dos")

    def test_network_ok_when_not_required(self) -> None:
        old = os.environ.pop("JARVIS_REQUIRE_NETWORK", None)
        try:
            self.assertTrue(jarvis_lista.network_ok())
        finally:
            if old is not None:
                os.environ["JARVIS_REQUIRE_NETWORK"] = old


if __name__ == "__main__":
    unittest.main()
