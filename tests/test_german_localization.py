#!/usr/bin/env python3
"""Regression tests for the English and German page pairs."""

from __future__ import annotations

import unittest
from html.parser import HTMLParser
from pathlib import Path


SITE_DIR = Path(__file__).resolve().parents[1]

PAGE_PAIRS = (
    (
        SITE_DIR / "index.html",
        SITE_DIR / "de" / "index.html",
        "https://guildrun.site/",
        "https://guildrun.site/de/",
    ),
    (
        SITE_DIR / "patch-notes" / "index.html",
        SITE_DIR / "de" / "patch-notes" / "index.html",
        "https://guildrun.site/patch-notes/",
        "https://guildrun.site/de/patch-notes/",
    ),
)


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


class GermanLocalizationTest(unittest.TestCase):
    def test_each_language_pair_has_canonical_reciprocal_hreflang_and_switch_link(self) -> None:
        for english_path, german_path, english_url, german_url in PAGE_PAIRS:
            self.assertTrue(german_path.is_file(), f"missing German page: {german_path}")
            english = parse(english_path)
            german = parse(german_path)

            self.assertEqual(english.html_lang, "en")
            self.assertEqual(german.html_lang, "de")
            self.assertEqual(english.canonical, english_url)
            self.assertEqual(german.canonical, german_url)

            expected_alternates = {
                "en": english_url,
                "de": german_url,
                "x-default": english_url,
            }
            if english_url == "https://guildrun.site/":
                expected_alternates["ru"] = "https://guildrun.site/ru/"
            self.assertEqual(english.alternates, expected_alternates)
            self.assertEqual(german.alternates, expected_alternates)
            self.assertIn(german_url.removeprefix("https://guildrun.site"), english.links)
            self.assertIn(english_url.removeprefix("https://guildrun.site") or "/", german.links)

    def test_german_pages_expose_german_titles_and_visible_content(self) -> None:
        homepage_path = SITE_DIR / "de" / "index.html"
        patch_notes_path = SITE_DIR / "de" / "patch-notes" / "index.html"
        self.assertTrue(homepage_path.is_file(), f"missing German page: {homepage_path}")
        self.assertTrue(patch_notes_path.is_file(), f"missing German page: {patch_notes_path}")
        homepage = parse(homepage_path)
        patch_notes = parse(patch_notes_path)
        homepage_text = " ".join(homepage.text)
        patch_text = " ".join(patch_notes.text)

        self.assertIn("Guildrun Wiki auf Deutsch", homepage.title)
        self.assertIn("Einsteigerleitfaden", homepage_text)
        self.assertIn("Was ist Guildrun?", homepage_text)
        self.assertIn("Guildrun Patch Notes auf Deutsch", patch_notes.title)
        self.assertIn("Versionsverlauf", patch_text)
        self.assertIn("Häufig gestellte Fragen", patch_text)


if __name__ == "__main__":
    unittest.main()
