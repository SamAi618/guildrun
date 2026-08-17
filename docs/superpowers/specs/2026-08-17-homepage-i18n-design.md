# Guildrun Homepage Localization Design

Date: 2026-08-17

## Goal

Provide seven real, shareable homepage languages and replace the non-interactive header language text with a working language menu. This phase localizes the homepage only. Existing guide and legal pages remain in English until later phases.

## Supported Homepage Locales

| Language | Locale | Homepage route |
| --- | --- | --- |
| English | `en` | `/` |
| German | `de` | `/de/` |
| Brazilian Portuguese | `pt-BR` | `/pt-br/` |
| Russian | `ru` | `/ru/` |
| Simplified Chinese | `zh-Hans` | `/zh-cn/` |
| Traditional Chinese | `zh-Hant` | `/zh-tw/` |
| Spanish (Spain) | `es-ES` | `/es/` |

English keeps the existing root URL to avoid changing established routes. Every non-English homepage uses a stable locale-prefixed URL.

## Header Language Menu

Replace the current language summary text with an accessible menu that:

- displays the current language;
- lists all seven languages as real links;
- marks the active language with `aria-current="page"`;
- supports pointer and keyboard operation;
- closes on selection, outside click, or Escape;
- remains usable in the mobile header;
- states that guides still open in English during this phase.

The menu must use normal anchor links so locale navigation remains usable without client-side JavaScript. JavaScript may only enhance open and close behavior.

## Translation Scope

Translate every homepage-owned string for each locale:

- metadata, Open Graph text, and structured data;
- header navigation and actions;
- Hero, onboarding cards, game description, code explanation, language section, and final CTA;
- footer headings and descriptions;
- accessibility labels and image alternative text.

Preserve `Guildrun`, source URLs, verified numbers, hero and game-system names without confirmed official translations, and the exact uncertainty markers `待确认` and `暂无`. No new facts, values, names, or redemption codes may be introduced.

## Inner-Page Boundary

This phase does not translate guide or legal pages. Localized homepage navigation may use translated labels, but links to existing guides must continue pointing to the English routes and carry a clear indication in the language menu that guides remain English. No locale-prefixed inner-page URL may be generated until its content exists.

## SEO and Document Semantics

Each homepage must include:

- the correct `<html lang>` value;
- a self-referencing canonical URL;
- `hreflang` links for all seven existing homepages plus `x-default`;
- locale-specific title, description, Open Graph locale, and social text;
- JSON-LD whose website `inLanguage` matches the page language;
- the complete verified game-interface language list on the `VideoGame` entity.

Alternate-locale declarations must only point to pages generated in this phase.

## Content Source and Generation

Use the English homepage as the factual source of truth. Store localized homepage strings in a dedicated data file and generate the six non-English static pages from one homepage structure. Generation must fail if a required translation key or locale is missing. Generated pages are committed artifacts and must be reproducible without network access.

## Error and Fallback Behavior

- A missing localized homepage must never silently show English under a non-English `lang` attribute.
- A missing translation key must stop generation instead of falling back silently.
- Guide links remain explicit English destinations until their localized equivalents exist.
- The language menu must not use automatic browser-language redirects.

## Verification

Before delivery:

1. Generate all six localized homepages twice and confirm stable output.
2. Validate that all seven locale routes return HTTP 200.
3. Validate canonical, `hreflang`, `<html lang>`, JSON-LD, and active menu state on every locale.
4. Use a real browser to switch through all seven languages.
5. Check desktop, 1024px, and 390px layouts for overflow or clipped menus.
6. Confirm the language menu works with keyboard controls.
7. Confirm the browser console contains no errors or warnings introduced by this feature.

## Acceptance Criteria

- Selecting any of the seven header languages opens a homepage fully translated into that language.
- The selected language remains encoded in the URL and survives refresh or sharing.
- All seven pages retain the same verified Guildrun facts and official links.
- No untranslated English homepage section remains on non-English pages, except protected official names and explicitly English-only guide destinations.
- No nonexistent localized guide or legal route is advertised.

