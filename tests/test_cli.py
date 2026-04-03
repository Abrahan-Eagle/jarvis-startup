"""Pruebas del parser CLI (subcomandos y compatibilidad legacy)."""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import unittest

import bienvenido_jarvis  # noqa: E402


class TestCliParse(unittest.TestCase):
    def test_default_run(self) -> None:
        cmd, ns = bienvenido_jarvis._parse_args([])
        self.assertEqual(cmd, "run")
        self.assertFalse(ns.dry_run)

    def test_run_dry_run_subcommand(self) -> None:
        cmd, ns = bienvenido_jarvis._parse_args(["run", "--dry-run"])
        self.assertEqual(cmd, "run")
        self.assertTrue(ns.dry_run)

    def test_doctor_subcommand(self) -> None:
        cmd, ns = bienvenido_jarvis._parse_args(["doctor"])
        self.assertEqual(cmd, "doctor")

    def test_version_subcommand(self) -> None:
        cmd, _ = bienvenido_jarvis._parse_args(["version"])
        self.assertEqual(cmd, "version")

    def test_legacy_dry_run(self) -> None:
        cmd, ns = bienvenido_jarvis._parse_args(["--dry-run"])
        self.assertEqual(cmd, "run")
        self.assertTrue(ns.dry_run)

    def test_legacy_doctor_flag(self) -> None:
        cmd, _ = bienvenido_jarvis._parse_args(["--doctor"])
        self.assertEqual(cmd, "doctor")


if __name__ == "__main__":
    unittest.main()
