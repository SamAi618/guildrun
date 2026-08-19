#!/usr/bin/env python3
"""Regression tests for the site-wide Microsoft Clarity installation."""

from __future__ import annotations

import unittest
from pathlib import Path


SITE_DIR = Path(__file__).resolve().parents[1]
CLARITY_PROJECT_ID = "y4r92405b7"
CLARITY_LOADER = 't.src="https://www.clarity.ms/tag/"+i;'


class ClarityInstallationTest(unittest.TestCase):
    def test_every_page_loads_clarity_once_from_the_head(self) -> None:
        pages = sorted(SITE_DIR.rglob("index.html"))
        self.assertTrue(pages, "the site must contain HTML pages")

        for page in pages:
            html = page.read_text(encoding="utf-8")
            head, separator, _ = html.partition("</head>")
            self.assertTrue(separator, f"{page} has no closing head tag")
            self.assertEqual(
                html.count(CLARITY_PROJECT_ID),
                1,
                f"{page} must contain the Clarity project ID exactly once",
            )
            self.assertEqual(
                html.count(CLARITY_LOADER),
                1,
                f"{page} must contain one Clarity loader",
            )
            self.assertIn(CLARITY_PROJECT_ID, head, f"{page} loads Clarity outside head")
            self.assertIn(CLARITY_LOADER, head, f"{page} loads Clarity outside head")


if __name__ == "__main__":
    unittest.main()
