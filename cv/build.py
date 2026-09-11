#!/usr/bin/env python3
"""Render cv.data.json into a print-ready A4 PDF.

    python3 cv/build.py                 # -> cv/Matej_Pis_CV.pdf
    python3 cv/build.py --data other.json --out other.pdf

Edit cv.data.json and re-run; nothing else needs touching.
"""
import argparse, base64, html, json, pathlib, shutil, subprocess, sys, tempfile

HERE = pathlib.Path(__file__).resolve().parent

CHROME_CANDIDATES = [
    "/opt/pw-browsers/chromium-1194/chrome-linux/chrome",
    "/opt/pw-browsers/chromium/chrome-linux/chrome",
    "chromium", "chromium-browser", "google-chrome", "google-chrome-stable",
]


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


def section(num, label, body):
    return (
        '<section>'
        f'<div class="rail"><div class="num">{num:02d}</div><h2>{e(label)}</h2></div>'
        f'<div>{body}</div>'
        '</section>'
    )


def timeline(entries):
    """Title on the left, date range hard right, org and detail beneath."""
    out = []
    for x in entries:
        when = " — ".join(p for p in (x.get("from"), x.get("to")) if p)
        org = f'<div class="org">{e(x["org"])}</div>' if x.get("org") else ""
        detail = f'<div class="detail">{e(x["detail"])}</div>' if x.get("detail") else ""
        out.append(
            '<div class="row">'
            f'<div class="rowhd"><span class="title">{e(x["title"])}</span>'
            f'<span class="when">{e(when)}</span></div>'
            f"{org}{detail}</div>"
        )
    return "".join(out)


def cells(entries):
    return "".join(
        f'<div class="cell"><div class="nm">{e(x["name"])}</div>'
        f'<div class="lv">{e(x.get("level"))}</div></div>'
        for x in entries
    )


def closing_band(skills, languages):
    """Skills in two columns, languages stacked beyond a hairline divider."""
    if not (skills or languages):
        return ""
    return (
        '<div class="split">'
        f'<div><h3>Skills</h3><div class="grid2">{cells(skills)}</div></div>'
        '<div class="divider"></div>'
        f'<div><h3>Languages</h3><div class="stack">{cells(languages)}</div></div>'
        '</div>'
    )


def lines(entries):
    """Credit line: name + note on the left, result hard right."""
    return "".join(
        '<div class="line"><div>'
        f'<div class="nm">{e(x["title"])}</div>'
        + (f'<div class="note">{e(x["note"])}</div>' if x.get("note") else "")
        + "</div>"
        + (f'<span class="tag">{e(x["tag"])}</span>' if x.get("tag") else "")
        + "</div>"
        for x in entries
    )


def page_count(pdf):
    """Pages in the rendered PDF, or None if poppler isn't around."""
    if not shutil.which("pdfinfo"):
        return None
    out = subprocess.run(["pdfinfo", str(pdf)], capture_output=True, text=True).stdout
    for line in out.splitlines():
        if line.startswith("Pages:"):
            return int(line.split()[1])
    return None


BASE_FS = 8.7  # pt


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


def build(data_path, out_path):
    d = json.loads(pathlib.Path(data_path).read_text(encoding="utf-8"))
    tpl = (HERE / "template.html").read_text(encoding="utf-8")
    f = HERE / "fonts"

    # Coordinates block: contact lines, then links joined by hairline separators.
    coords = [f"<div>{e(c)}</div>" for c in d["contact"]]
    if d.get("links"):
        joined = '<span class="sep">/</span>'.join(
            f'<a href="{html.escape(l["url"])}">{e(l["label"])}</a>' for l in d["links"]
        )
        coords.append(f"<div>{joined}</div>")

    # Sections are numbered in the order they appear here; empty ones drop out.
    blocks, n = [], 0
    for label, body in (
        ("Experience", timeline(d.get("experience", []))),
        (d.get("projects_label", "Selected work"), lines(d.get("projects", []))),
        ("Education", timeline(d.get("education", []))),
        ("Toolkit", closing_band(d.get("skills", []), d.get("languages", []))),
    ):
        if body:
            n += 1
            blocks.append(section(n, label, body))

    repl = {
        "__INTER_LAT__": data_uri(f / "Inter-latin.woff2"),
        "__INTER_EXT__": data_uri(f / "Inter-latin-ext.woff2"),
        "__SERIF_LAT__": data_uri(f / "SourceSerif4-latin.woff2"),
        "__SERIF_EXT__": data_uri(f / "SourceSerif4-latin-ext.woff2"),
        "__ACCENT__":    d.get("accent", "#8A5A3C"),
        "__NAME__":      e(f'{d["name_first"]} {d["name_last"]}'),
        "__ROLE__":      e(d["role"]),
        "__SUMMARY__":   e(d["summary"]),
        "__COORDS__":    "".join(coords),
        "__SECTIONS__":  "".join(blocks),
    }
    for k, v in repl.items():
        tpl = tpl.replace(k, v)

    # Auto-fit: shrink the whole page uniformly until it lands on one sheet.
    out_path = pathlib.Path(out_path)
    scale = 1.0
    for _ in range(14):
        render(tpl, scale, out_path)
        pages = page_count(out_path)
        if pages is None or pages == 1:
            break
        scale -= 0.02
    else:
        print("warning: still spilling past one page — trim some content.", file=sys.stderr)

    fit = "" if scale > 0.999 else f", fitted to {scale:.0%}"
    print(f"{out_path}  ({out_path.stat().st_size/1024:.0f} KB{fit})")
    if scale < 0.88:
        print(f"note: {BASE_FS * scale:.1f}pt body text is getting tight — "
              "consider trimming a role or shortening the summary.", file=sys.stderr)
    return out_path


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default=HERE / "cv.data.json")
    ap.add_argument("--out",  default=HERE / "Matej_Pis_CV.pdf")
    a = ap.parse_args()
    build(a.data, a.out)
