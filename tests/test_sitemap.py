#!/usr/bin/env python3
"""Regression tests for the public sitemap and its robots.txt discovery hint."""

from __future__ import annotations

import unittest
import xml.etree.ElementTree as ET
import re
from pathlib import Path
from urllib.parse import urljoin, urlparse


SITE_DIR = Path(__file__).resolve().parents[1]
SITE_ORIGIN = "https://guildrun.site"
SITEMAP_NAMESPACE = "http://www.sitemaps.org/schemas/sitemap/0.9"

INDEXABLE_ROUTES = {
    "/",
    "/builds/",
    "/builds/best-comp/",
    "/builds/best-tank/",
    "/builds/best-team/",
    "/builds/synergy/",
    "/characters/",
    "/characters/dragomir/build/",
    "/characters/irini/",
    "/characters/sal/",
    "/characters/zuri/",
    "/classes/",
    "/classes/upgrades/",
    "/demo/",
    "/de/",
    "/de/patch-notes/",
    "/guide/",
    "/guide/beginner/",
    "/guide/tips/",
    "/items/",
    "/items/relics/",
    "/leaderboard/",
    "/mechanics/backup/",
    "/mechanics/difficulty/",
    "/mechanics/stall/",
    "/modes/endless/",
    "/modes/red-rift/",
    "/patch-notes/",
    "/privacy/",
    "/release-date/",
    "/terms/",
    "/tier-list/",
    "/tier-list/demo/",
    "/tier-list/heroes/",
    "/tier-list/run/",
}


class SitemapTest(unittest.TestCase):
    def sitemap_locations(self) -> list[str]:
        sitemap = SITE_DIR / "sitemap.xml"
        self.assertTrue(sitemap.is_file(), "sitemap.xml must exist at the site root")

        root = ET.parse(sitemap).getroot()
        self.assertEqual(root.tag, f"{{{SITEMAP_NAMESPACE}}}urlset")
        locations = [
            element.text or ""
            for element in root.findall(f"{{{SITEMAP_NAMESPACE}}}url/{{{SITEMAP_NAMESPACE}}}loc")
        ]
        self.assertTrue(locations, "sitemap.xml must contain at least one URL")
        return locations

    def test_sitemap_contains_exactly_the_canonical_public_pages(self) -> None:
        locations = self.sitemap_locations()
        self.assertEqual(len(locations), len(set(locations)), "sitemap URLs must be unique")

        parsed = [urlparse(location) for location in locations]
        self.assertTrue(
            all(f"{url.scheme}://{url.netloc}" == SITE_ORIGIN for url in parsed),
            "every sitemap URL must use the canonical HTTPS root domain",
        )
        self.assertEqual({url.path for url in parsed}, INDEXABLE_ROUTES)

    def test_every_sitemap_url_maps_to_a_deployed_html_page(self) -> None:
        for location in self.sitemap_locations():
            route = urlparse(location).path
            page = SITE_DIR / route.lstrip("/") / "index.html"
            self.assertTrue(page.is_file(), f"{location} has no local index.html")

    def test_every_sitemap_page_declares_the_same_canonical_url(self) -> None:
        for location in self.sitemap_locations():
            route = urlparse(location).path
            page = SITE_DIR / route.lstrip("/") / "index.html"
            html = page.read_text(encoding="utf-8")
            match = re.search(
                r'<link\s+rel=["\']canonical["\']\s+href=["\']([^"\']+)["\']',
                html,
                flags=re.IGNORECASE,
            )
            self.assertIsNotNone(match, f"{location} is missing a canonical link")
            assert match is not None
            self.assertEqual(urljoin(location, match.group(1)), location)

    def test_robots_txt_advertises_the_canonical_sitemap(self) -> None:
        robots = SITE_DIR / "robots.txt"
        self.assertTrue(robots.is_file(), "robots.txt must exist at the site root")
        lines = {
            line.strip()
            for line in robots.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.lstrip().startswith("#")
        }
        self.assertIn("User-agent: *", lines)
        self.assertIn("Allow: /", lines)
        self.assertIn(f"Sitemap: {SITE_ORIGIN}/sitemap.xml", lines)


if __name__ == "__main__":
    unittest.main()
