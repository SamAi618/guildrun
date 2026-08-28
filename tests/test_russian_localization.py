#!/usr/bin/env python3
"""Regression tests for the new Russian homepage and builds page."""

from __future__ import annotations

import unittest
from html.parser import HTMLParser
from pathlib import Path


SITE_DIR = Path(__file__).resolve().parents[1]


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.html_lang = ""
        self.title = ""
        self.canonical = ""
        self.alternates: dict[str, str] = {}
        self.links: set[str] = set()
        self.text: list[str] = []
        self._in_title = False

    def handle_starttag(self, tag: str, attrs_list: list[tuple[str, str | None]]) -> None:
        attrs = {key: value or "" for key, value in attrs_list}
        if tag == "html":
            self.html_lang = attrs.get("lang", "")
        if tag == "title":
            self._in_title = True
        if tag == "link" and attrs.get("rel") == "canonical":
            self.canonical = attrs.get("href", "")
        if tag == "link" and attrs.get("rel") == "alternate" and attrs.get("hreflang"):
            self.alternates[attrs["hreflang"]] = attrs.get("href", "")
        if tag == "a" and attrs.get("href"):
            self.links.add(attrs["href"])

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self._in_title = False

    def handle_data(self, data: str) -> None:
        if self._in_title:
            self.title += data
        self.text.append(data)


def parse(page: Path) -> PageParser:
    parser = PageParser()
    parser.feed(page.read_text(encoding="utf-8"))
    return parser


class RussianLocalizationTest(unittest.TestCase):
    def test_homepage_language_cluster_is_reciprocal(self) -> None:
        paths = (
            SITE_DIR / "index.html",
            SITE_DIR / "de" / "index.html",
            SITE_DIR / "ru" / "index.html",
        )
        urls = {
            "en": "https://guildrun.site/",
            "de": "https://guildrun.site/de/",
            "ru": "https://guildrun.site/ru/",
            "x-default": "https://guildrun.site/",
        }

        for page in paths:
            self.assertTrue(page.is_file(), f"missing localized homepage: {page}")
            parsed = parse(page)
            self.assertEqual(parsed.alternates, urls)
            self.assertIn("/ru/", parsed.links)

    def test_builds_language_pair_is_reciprocal(self) -> None:
        english_path = SITE_DIR / "builds" / "index.html"
        russian_path = SITE_DIR / "ru" / "builds" / "index.html"
        english_url = "https://guildrun.site/builds/"
        russian_url = "https://guildrun.site/ru/builds/"
        expected_alternates = {
            "en": english_url,
            "ru": russian_url,
            "x-default": english_url,
        }

        self.assertTrue(russian_path.is_file(), f"missing Russian builds page: {russian_path}")
        english = parse(english_path)
        russian = parse(russian_path)
        self.assertEqual(english.alternates, expected_alternates)
        self.assertEqual(russian.alternates, expected_alternates)
        self.assertIn("/ru/builds/", english.links)
        self.assertIn("/builds/", russian.links)

    def test_russian_pages_have_russian_metadata_and_visible_content(self) -> None:
        homepage = parse(SITE_DIR / "ru" / "index.html")
        builds = parse(SITE_DIR / "ru" / "builds" / "index.html")

        self.assertEqual(homepage.html_lang, "ru")
        self.assertEqual(homepage.canonical, "https://guildrun.site/ru/")
        self.assertIn("Guildrun Wiki на русском", homepage.title)
        self.assertIn("Что такое Guildrun?", " ".join(homepage.text))

        self.assertEqual(builds.html_lang, "ru")
        self.assertEqual(builds.canonical, "https://guildrun.site/ru/builds/")
        self.assertIn("Билды Guildrun", builds.title)
        self.assertIn("Как собирать билды в Guildrun", " ".join(builds.text))


if __name__ == "__main__":
    unittest.main()
