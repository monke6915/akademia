# CV

One-page A4 CV, generated from a single JSON file.

```bash
python3 cv/build.py                        # -> cv/Matej_Pis_CV.pdf
python3 cv/build.py --data x.json --out y.pdf
```

- **`cv.data.json`** — all content. This is the only file you normally edit.
- **`template.html`** — layout and type. Edit for design changes.
- **`build.py`** — fills the template, prints to PDF via headless Chromium.
- **`fonts/`** — Inter + Source Serif 4 (SIL Open Font License), embedded into
  the PDF so it renders identically anywhere.

The output is real selectable text, not outlines, so applicant-tracking
systems can parse it.

## The layout

A full-width masthead — name in serif on the left, contact details ranged
right — over a heavy rule. Below it a magazine-style lede: the headline set
large, with the summary as a standfirst on a comfortable measure. Then the
sections hang off a left rail, each numbered, with dates pushed hard right
and hairlines separating entries. Skills and languages share a single closing
band split by a vertical hairline.

Sections are numbered in the order `build.py` emits them, and any section with
no content drops out and renumbers itself — delete `projects` from the JSON and
Education simply becomes 02.

## Fitting one page

Every type size and vertical gap is a multiple of one custom property, `--fs`.
`build.py` renders, counts pages, and steps `--fs` down by 2% until it lands on
a single sheet, so proportions never distort. If it has to drop below 88% it
says so — that's the point to cut a role or tighten the summary rather than
keep shrinking.

## Changing the look

- **Accent** — `"accent"` in the JSON (default `#8A5A3C`, a warm sienna). It
  colours the section numbers, the `PROFILE` kicker and the result tags.
- **Palette, rail width, margins** — the `:root` block in `template.html`.
- **Section order and labels** — the tuple list in `build.py`'s `build()`.
