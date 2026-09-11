# CV

One-page A4 CV, generated from a single JSON file, in a choice of four layouts.

```bash
python3 cv/build.py                      # default layout -> cv/Matej_Pis_CV.pdf
python3 cv/build.py --layout banner      # pick one
python3 cv/build.py --all                # render every layout as cv/preview-*.pdf
```

- **`cv.data.json`** — all content. This is the only file you normally edit.
- **`template-<layout>.html`** — one file per layout: skeleton plus its own CSS.
- **`build.py`** — turns the JSON into HTML fragments, fills a template, prints
  to PDF via headless Chromium.
- **`fonts/`** — Inter + Source Serif 4 (SIL Open Font License), embedded into
  the PDF so it renders identically anywhere.

The output is real selectable text, not outlines, so applicant-tracking
systems can parse it.

## The four layouts

| `--layout` | Organising idea |
|---|---|
| `rail` | Full-width masthead over a heavy rule, a magazine-style lede, then numbered sections hanging off a left rail with dates pushed hard right. |
| `sidebar` | A tinted column bleeding down the left edge carries the name, contact, skills and languages; experience runs wide alongside it. |
| `timeline` | Name centred over a rule, then a literal career spine — a hairline down the page with an accent node at every entry and dates ranged into the left margin. |
| `banner` | A reversed-out ink band across the top, then an asymmetric two-column body: experience wide on the left, everything else in a narrower aside. |

All four share the same content fragments, so switching layout is one flag —
nothing in the JSON changes.

## Fitting one page

Every type size and vertical gap is a multiple of one custom property, `--fs`.
`build.py` renders, counts pages, and steps `--fs` down by 2% until it lands on
a single sheet, so proportions never distort. If it has to drop below 88% it
says so — that's the point to cut a role or tighten the summary rather than
keep shrinking.

## Changing the look

- **Accent** — `"accent"` in the JSON (default `#8A5A3C`, a warm sienna). It
  picks out section numbers, result tags and the role line. The `banner`
  layout lightens it automatically for the dark band.
- **Palette, rail width, margins** — the `:root` block in each template.
- **Section order and labels** — `fragments()` and the per-layout skeletons.
