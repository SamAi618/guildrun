#!/usr/bin/env python3
"""Regression tests for hostname and index-file URL canonicalization."""

from __future__ import annotations

import json
import re
import unittest
from pathlib import Path
from urllib.parse import urlparse


SITE_DIR = Path(__file__).resolve().parents[1]
SITE_ORIGIN = "https://guildrun.site"
CANONICAL_PATTERN = re.compile(
    r'<link\s+rel=["\']canonical["\']\s+href=["\']([^"\']+)["\']',
    flags=re.IGNORECASE,
)
HREF_PATTERN = re.compile(
    r'<a\b[^>]*\bhref=["\']([^"\']+)["\']',
    flags=re.IGNORECASE,
)


def public_index_pages() -> list[Path]:
    return sorted(
        page
        for page in SITE_DIR.rglob("index.html")
        if not any(part.startswith(".") for part in page.relative_to(SITE_DIR).parts)
    )


def source_html_pages() -> list[Path]:
    return sorted(
        page
        for page in SITE_DIR.rglob("*.html")
        if not any(part.startswith(".") for part in page.relative_to(SITE_DIR).parts)
    )


def canonical_url_for(page: Path) -> str:
    relative_parent = page.relative_to(SITE_DIR).parent.as_posix()
    route = "/" if relative_parent == "." else f"/{relative_parent}/"
    return f"{SITE_ORIGIN}{route}"


class UrlCanonicalizationTest(unittest.TestCase):
    def test_every_public_index_page_uses_its_absolute_apex_canonical(self) -> None:
        for page in public_index_pages():
            html = page.read_text(encoding="utf-8")
            match = CANONICAL_PATTERN.search(html)
            self.assertIsNotNone(match, f"{page} is missing a canonical link")
            assert match is not None
            self.assertEqual(
                match.group(1),
                canonical_url_for(page),
                f"{page} must canonicalize to its absolute non-www directory URL",
            )

    def test_internal_links_do_not_expose_index_html_urls(self) -> None:
        offenders: list[str] = []
        for page in source_html_pages():
            html = page.read_text(encoding="utf-8")
            for href in HREF_PATTERN.findall(html):
                parsed = urlparse(href)
                if parsed.scheme and parsed.netloc not in {
                    "guildrun.site",
                    "www.guildrun.site",
                }:
                    continue
                if parsed.path == "index.html" or parsed.path.endswith("/index.html"):
                    offenders.append(f"{page.relative_to(SITE_DIR)} -> {href}")
        self.assertEqual(offenders, [], "internal links must use clean directory URLs")

    def test_vercel_permanently_normalizes_www_root_index_and_trailing_slashes(self) -> None:
        config_path = SITE_DIR / "vercel.json"
        self.assertTrue(config_path.is_file(), "vercel.json must define canonical redirects")
        config = json.loads(config_path.read_text(encoding="utf-8"))

        host_condition = [{"type": "host", "value": "www.guildrun.site"}]
        redirects = config.get("redirects", [])
        self.assertIn(
            {
                "source": "/index.html",
                "has": host_condition,
                "destination": "https://guildrun.site/",
                "permanent": True,
            },
            redirects,
        )
        self.assertIn(
            {
                "source": "/:path*",
                "has": host_condition,
                "destination": "https://guildrun.site/:path*",
                "permanent": True,
            },
            redirects,
        )
        self.assertIn(
            {"source": "/index.html", "destination": "/", "permanent": True},
            redirects,
        )
        self.assertIs(config.get("trailingSlash"), True)


if __name__ == "__main__":
    unittest.main()
