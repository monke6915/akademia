# CV

One-page A4 CV, generated from a single JSON file.

```bash
python3 cv/build.py                       # -> cv/Matej_Pis_CV.pdf
python3 cv/build.py --data x.json --out y.pdf
```

- **`cv.data.json`** — all content. This is the only file you normally edit.
- **`template.html`** — layout and type. Edit for design changes.
- **`build.py`** — fills the template, prints to PDF via headless Chromium.
- **`fonts/`** — Inter + Source Serif 4 (SIL Open Font License), embedded into
  the PDF so it renders identically anywhere.

The output is real selectable text, not outlines, so applicant-tracking
systems can parse it.

Layout notes: the page is a fixed A4 flex column — the masthead sits at the
top and the Skills / Languages / Education band is pinned to the foot, so the
sheet stays balanced whatever the middle contains. Keep experience to about
four entries; past that, trim `--pad` or the base `font-size` in
`template.html` rather than letting it spill onto a second page.
