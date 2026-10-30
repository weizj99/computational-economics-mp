# Course fonts

The lessons serve these unmodified Adobe fonts from this directory. They do not
contact a font CDN and do not require an operating-system installation.

| Role | Family | Web files | Weight |
| --- | --- | --- | --- |
| Body, headings, controls, numeric readouts | Source Sans 3 | `SourceSans3-Regular.woff2`, `SourceSans3-Medium.woff2`, `SourceSans3-Semibold.woff2` | 400, 500, 600 |
| Italic text | Source Sans 3 | `SourceSans3-It.woff2` | 400 |
| Formulas | Source Serif 4 | `SourceSerif4-Regular.woff2`, `SourceSerif4-It.woff2` | 400 |

The corresponding TTF files support the video renderer. Source Sans 3 Regular, Medium and Semibold are included. Source Serif 4
Regular and Italic are included. The renderer should register these exact files
for its process; these assets are not instructions to install fonts locally.

## Sources and license

- Source Sans 3: [Adobe repository](https://github.com/adobe-fonts/source-sans),
  release branch pinned to commit
  `87b37a2daaed80fcb8e8ccb0085c4d72ddade12e`.
- Source Serif 4: [Adobe repository](https://github.com/adobe-fonts/source-serif),
  release branch pinned to commit
  `80d3f8894c09c937bebfa9011247d2e1c79fd6f4`.
- Both families are distributed under the SIL Open Font License 1.1. The
  original license notices are retained in `LICENSE-SourceSans3.md` and
  `LICENSE-SourceSerif4.md`.

`provenance.json` records the exact pinned download URL, byte size and SHA-256
of each downloaded font and license. WOFF2 filenames are shortened locally;
the font bytes are unchanged. Downloaded on 2026-10-27.

`../typography.css` defines the shared semantic families. Only source code keeps
a system monospace fallback. Existing raster figures and earlier videos retain
their original lettering until they are separately rerendered.
