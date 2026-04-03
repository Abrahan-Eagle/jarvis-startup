"""Pruebas de jarvis_doctor (sin importar bienvenido_jarvis)."""

from __future__ import annotations

import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import jarvis_doctor  # noqa: E402


class TestJarvisDoctor(unittest.TestCase):
    def test_doctor_exit_code_all_ok(self) -> None:
        checks = [
            jarvis_doctor.DoctorCheck("a", True, True, "ok"),
            jarvis_doctor.DoctorCheck("b", False, False, "opt"),
        ]
        self.assertEqual(jarvis_doctor.doctor_exit_code(checks), 0)

    def test_doctor_exit_code_critical_fail(self) -> None:
        checks = [
            jarvis_doctor.DoctorCheck("a", False, True, "bad"),
        ]
        self.assertEqual(jarvis_doctor.doctor_exit_code(checks), 1)

    def test_collect_uses_custom_which(self) -> None:
        def fake_which(_: str) -> str | None:
            return "/bin/true"

        with patch.dict(os.environ, {"JARVIS_DOCTOR_SKIP_NETWORK": "1", "JARVIS_TEXT_ONLY": "1"}):
            rep = jarvis_doctor.collect_doctor_report(music_file="/nonexistent/x.mp3", which_fn=fake_which)
        names = [c.name for c in rep]
        self.assertIn("bin:cursor", names)

    def test_format_non_empty(self) -> None:
        s = jarvis_doctor.format_doctor_report(
            [jarvis_doctor.DoctorCheck("x", True, True, "y")]
        )
        self.assertIn("x", s)
        self.assertIn("OK", s)


if __name__ == "__main__":
    unittest.main()
