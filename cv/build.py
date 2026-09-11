#!/usr/bin/env python3
"""Render cv.data.json into a print-ready one-page A4 PDF.

    python3 cv/build.py                     # default layout
    python3 cv/build.py --layout banner     # one specific layout
    python3 cv/build.py --all               # every layout, for comparison

Content lives entirely in cv.data.json; the layouts are template-*.html.
"""
import argparse, base64, html, json, pathlib, shutil, subprocess, sys, tempfile

HERE = pathlib.Path(__file__).resolve().parent
LAYOUTS = ["rail", "sidebar", "timeline", "banner"]
BASE_FS = 8.7  # pt, before auto-fit

CHROME_CANDIDATES = [
    "/opt/pw-browsers/chromium-1194/chrome-linux/chrome",
    "/opt/pw-browsers/chromium/chrome-linux/chrome",
    "chromium", "chromium-browser", "google-chrome", "google-chrome-stable",
]

LAT = ("U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,U+0304,U+0308,"
       "U+0329,U+2000-206F,U+20AC,U+2122,U+2191,U+2193,U+2212,U+2215,U+FEFF,U+FFFD")
EXT = ("U+0100-02BA,U+02BD-02C5,U+02C7-02CC,U+02CE-02D7,U+02DD-02FF,U+0304,U+0308,U+0329,"
       "U+1D00-1DBF,U+1E00-1E9F,U+1EF2-1EFF,U+2020,U+20A0-20AB,U+20AD-20C0,U+2113,"
       "U+2C60-2C7F,U+A720-A7FF")

# IBM Plex, one superfamily in three voices: Serif for the name and section
# headings, Sans for running text, Mono for dates and the small caps labels.
# Plex Sans ships variable, so one file covers every weight; Serif and Mono are
# static cuts.
FONTS = [
    ("IBM Plex Sans",  "100 900", "IBMPlexSans-400"),
    ("IBM Plex Serif", "400",     "IBMPlexSerif-400"),
    ("IBM Plex Mono",  "400",     "IBMPlexMono-400"),
    ("IBM Plex Mono",  "500",     "IBMPlexMono-500"),
]


def font_face(fontdir):
    out = []
    for family, weight, stem in FONTS:
        for suffix, urange in (("latin", LAT), ("latin-ext", EXT)):
            uri = data_uri(fontdir / f"{stem}-{suffix}.woff2")
            out.append(
                f"@font-face{{font-family:'{family}';src:url({uri}) format('woff2');"
                f"font-weight:{weight};font-style:normal;unicode-range:{urange};}}"
            )
    return "/* ---- Typefaces (embedded, so the PDF travels as one file) ---- */\n" + "\n".join(out)


def find_chrome():
    for c in CHROME_CANDIDATES:
        p = shutil.which(c) if "/" not in c else (c if pathlib.Path(c).exists() else None)
        if p:
            return p
    sys.exit("No Chromium/Chrome found — install one, or add it to CHROME_CANDIDATES.")


def data_uri(path):
    return "data:font/woff2;base64," + base64.b64encode(path.read_bytes()).decode()


def e(s):
    """Escape; a literal newline in the data becomes a line break."""
    return html.escape(str(s or "")).replace("\n", "<br>")


# ---- Content fragments, shared by every layout ---------------------------

def timeline(entries):
    """Role/school with its date range; .content wraps for the spine layout."""
    out = []
    for x in entries:
        when = " - ".join(p for p in (x.get("from"), x.get("to")) if p)
        org = f'<div class="org">{e(x["org"])}</div>' if x.get("org") else ""
        detail = f'<div class="detail">{e(x["detail"])}</div>' if x.get("detail") else ""
        out.append(
            '<div class="row">'
            f'<div class="when">{e(when)}</div>'
            '<div class="content">'
            f'<div class="rowhd"><span class="title">{e(x["title"])}</span>'
            f'<span class="when">{e(when)}</span></div>'
            f"{org}{detail}</div></div>"
        )
    return "".join(out)


def cells(entries):
    """Level is optional — LinkedIn exports skills without one."""
    return "".join(
        f'<div class="cell"><div class="nm">{e(x["name"])}</div>'
        + (f'<div class="lv">{e(x["level"])}</div>' if x.get("level") else "")
        + "</div>"
        for x in entries
    )


def lines(entries):
    """Credit line: name and note, with the result set apart."""
    return "".join(
        '<div class="line"><div>'
        f'<div class="nm">{e(x["title"])}</div>'
        + (f'<div class="note">{e(x["note"])}</div>' if x.get("note") else "")
        + "</div>"
        + (f'<span class="tag">{e(x["tag"])}</span>' if x.get("tag") else "")
        + "</div>"
        for x in entries
    )


def skill_groups(skills):
    """Skills may be a flat list or {group, items} clusters — a CV reads better
    clustered than as one undifferentiated column of keywords."""
    if skills and isinstance(skills[0], dict) and "items" in skills[0]:
        inner = "".join(
            f'<div class="grp"><h4>{e(g["group"])}</h4>'
            + "".join(f'<div class="cell"><div class="nm">{e(s)}</div></div>' for s in g["items"])
            + "</div>"
            for g in skills
        )
        return f'<div class="groups">{inner}</div>'
    return f'<div class="grid2">{cells(skills)}</div>'


def rail_sections(d, F):
    """The rail layout numbers its sections and drops any that are empty."""
    def band(skills, languages):
        if not (skills or languages):
            return ""
        return (
            '<div class="split">'
            f'<div><h3>Skills</h3>{skill_groups(skills)}</div>'
            '<div class="divider"></div>'
            f'<div><h3>Languages</h3><div class="stack">{cells(languages)}</div></div>'
            '</div>'
        )

    out = []
    for label, body in (
        ("Experience", F["__EXPERIENCE__"]),
        (d.get("projects_label", "Selected work"), F["__PROJECTS__"]),
        ("Education", F["__EDUCATION__"]),
        ("Toolkit", band(d.get("skills", []), d.get("languages", []))),
    ):
        if body:
            out.append(
                '<section>'
                f'<div class="rail"><h2>{e(label)}</h2></div>'
                f'<div>{body}</div></section>'
            )
    return "".join(out)


def fragments(d):
    links = d.get("links", [])
    sep = '<span class="sep">/</span>'
    link_run = sep.join(
        f'<a href="{html.escape(l["url"])}">{e(l["label"])}</a>' for l in links
    )
    coords = [f"<div>{e(c)}</div>" for c in d["contact"]]
    if link_run:
        coords.append(f"<div>{link_run}</div>")

    F = {
        "__NAME__":       e(f'{d["name_first"]} {d["name_last"]}'),
        "__NAME_FIRST__": e(d["name_first"]),
        "__NAME_LAST__":  e(d["name_last"]),
        "__ROLE__":       e(d["role"]),
        "__SUMMARY__":    e(d["summary"]),
        "__COORDS__":     "".join(coords),
        "__COORDS_INLINE__": sep.join([e(c) for c in d["contact"]] + ([link_run] if link_run else [])),
        "__CONTACT_LIST__": "".join(f"<li>{e(c)}</li>" for c in d["contact"]),
        "__LINKS_LIST__": "".join(
            f'<li><a href="{html.escape(l["url"])}">{e(l["label"])}</a></li>' for l in links
        ),
        "__EXPERIENCE__": timeline(d.get("experience", [])),
        "__EDUCATION__":  timeline(d.get("education", [])),
        "__PROJECTS__":   lines(d.get("projects", [])),
        "__PROJECTS_LABEL__": e(d.get("projects_label", "Selected work")),
        "__SKILLS__":     skill_groups(d.get("skills", [])),
        "__LANGUAGES__":  cells(d.get("languages", [])),
        "__ACCENT__":     d.get("accent", "#8A5A3C"),
    }
    F["__SECTIONS__"] = rail_sections(d, F)
    return F


# ---- Rendering -----------------------------------------------------------

def page_count(pdf):
    """Pages in the rendered PDF, or None if poppler isn't around."""
    if not shutil.which("pdfinfo"):
        return None
    out = subprocess.run(["pdfinfo", str(pdf)], capture_output=True, text=True).stdout
    for line in out.splitlines():
        if line.startswith("Pages:"):
            return int(line.split()[1])
    return None


def render(tpl, scale, out_path):
    tmp = pathlib.Path(tempfile.mkdtemp()) / "cv.html"
    tmp.write_text(tpl.replace("__FS__", f"{BASE_FS * scale:.3f}"), encoding="utf-8")
    subprocess.run(
        [find_chrome(), "--headless=new", "--no-sandbox", "--disable-gpu",
         "--disable-dev-shm-usage", "--no-pdf-header-footer",
         "--run-all-compositor-stages-before-draw", "--virtual-time-budget=6000",
         f"--print-to-pdf={out_path}", tmp.as_uri()],
        check=True, capture_output=True,
    )


def build(data_path, out_path, layout="rail"):
    d = json.loads(pathlib.Path(data_path).read_text(encoding="utf-8"))
    tpl = (HERE / f"template-{layout}.html").read_text(encoding="utf-8")
    f = HERE / "fonts"

    tpl = tpl.replace("__FONTS__", font_face(f))
    for k, v in fragments(d).items():
        tpl = tpl.replace(k, v)

    # Auto-fit: step the one sizing unit down until it lands on a single sheet.
    out_path = pathlib.Path(out_path)
    scale = 1.0
    for _ in range(14):
        render(tpl, scale, out_path)
        pages = page_count(out_path)
        if pages is None or pages == 1:
            break
        scale -= 0.02
    else:
        print(f"warning: {layout} still spills past one page — trim some content.", file=sys.stderr)

    fit = "" if scale > 0.999 else f", fitted to {scale:.0%}"
    print(f"{out_path}  ({out_path.stat().st_size/1024:.0f} KB{fit})")
    if scale < 0.88:
        print(f"note: {BASE_FS * scale:.1f}pt body text is getting tight — "
              "consider trimming a role or shortening the summary.", file=sys.stderr)
    return out_path


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default=HERE / "cv.data.json")
    ap.add_argument("--out", default=None)
    ap.add_argument("--layout", default="rail", choices=LAYOUTS)
    ap.add_argument("--all", action="store_true", help=f"render all: {', '.join(LAYOUTS)}")
    a = ap.parse_args()

    if a.all:
        for name in LAYOUTS:
            build(a.data, HERE / f"preview-{name}.pdf", name)
    else:
        build(a.data, a.out or HERE / "Matej_Pis_CV.pdf", a.layout)
