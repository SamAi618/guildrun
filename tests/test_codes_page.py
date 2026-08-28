#!/usr/bin/env python3
"""Behavior tests for the truthful Guildrun Codes landing page."""

from __future__ import annotations

import unittest
from html.parser import HTMLParser
from pathlib import Path


SITE_DIR = Path(__file__).resolve().parents[1]


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.title = ""
        self.canonical = ""
        self.links: set[str] = set()
        self.ids: set[str] = set()
        self.nav_links: set[str] = set()
        self.text: list[str] = []
        self.nav_text: list[str] = []
        self._in_title = False
        self._nav_depth = 0

    def handle_starttag(self, tag: str, attrs_list: list[tuple[str, str | None]]) -> None:
        attrs = {key: value or "" for key, value in attrs_list}
        if attrs.get("id"):
            self.ids.add(attrs["id"])
        if tag == "title":
            self._in_title = True
        if tag == "nav":
            self._nav_depth += 1
        if tag == "link" and attrs.get("rel") == "canonical":
            self.canonical = attrs.get("href", "")
        if tag == "a" and attrs.get("href"):
            self.links.add(attrs["href"])
            if self._nav_depth:
                self.nav_links.add(attrs["href"])

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self._in_title = False
        if tag == "nav":
            self._nav_depth -= 1

    def handle_data(self, data: str) -> None:
        if self._in_title:
            self.title += data
        self.text.append(data)
        if self._nav_depth:
            self.nav_text.append(data)


def parse(page: Path) -> PageParser:
    parser = PageParser()
    parser.feed(page.read_text(encoding="utf-8"))
    return parser


class CodesPageTest(unittest.TestCase):
    def test_homepage_keeps_codes_out_of_navigation_and_placeholder_modules(self) -> None:
        homepage = parse(SITE_DIR / "index.html")
        homepage_text = " ".join(homepage.text)
        nav_text = " ".join(homepage.nav_text)

        self.assertNotIn("Codes", nav_text)
        self.assertNotIn("#codes", homepage.nav_links)
        self.assertNotIn("/codes/", homepage.nav_links)
        self.assertNotIn("Current Codes", homepage_text)
        self.assertNotIn("Update pending", homepage_text)
        self.assertIn("/codes/", homepage.links)

        for localized_homepage in (
            SITE_DIR / "de" / "index.html",
            SITE_DIR / "ru" / "index.html",
        ):
            self.assertNotIn("codes", parse(localized_homepage).ids)

    def test_codes_page_directly_states_that_no_code_system_exists(self) -> None:
        codes_path = SITE_DIR / "codes" / "index.html"
        self.assertTrue(codes_path.is_file(), "missing /codes/ page")
        codes = parse(codes_path)
        visible_text = " ".join(codes.text)

        self.assertEqual(codes.canonical, "https://guildrun.site/codes/")
        self.assertIn("Guildrun Codes", codes.title)
        self.assertIn("No redemption code system currently exists.", visible_text)
        self.assertNotIn("Current Codes", visible_text)
        self.assertNotIn("Update pending", visible_text)


if __name__ == "__main__":
    unittest.main()
