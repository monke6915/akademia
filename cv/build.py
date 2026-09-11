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
    sys.exit("No Chromium/Chrome found — install one or set CHROME_CANDIDATES.")


def data_uri(path):
    return "data:font/woff2;base64," + base64.b64encode(path.read_bytes()).decode()


def e(s):
    """Escape, and let a literal \\n in the data become a paragraph break."""
    return html.escape(str(s)).replace("\n", "<br>")


def timeline(entries):
    out = []
    for x in entries:
        detail = f'<div class="detail">{e(x["detail"])}</div>' if x.get("detail") else ""
        org = f'<div class="org">{e(x["org"])}</div>' if x.get("org") else ""
        out.append(
            '<div class="row">'
            f'<div class="when">{e(x.get("from",""))} –<br>{e(x.get("to",""))}</div>'
            f'<div><div class="title">{e(x["title"])}</div>{org}{detail}</div>'
            "</div>"
        )
    return "\n".join(out)


def items(entries, nm="name", sub="level", tag=None, note=None):
    out = []
    for x in entries:
        tg = f'<span class="tag">{e(x[tag])}</span>' if tag and x.get(tag) else ""
        sb = x.get(sub) or x.get(note) or ""
        sb = f'<div class="sub">{e(sb)}</div>' if sb else ""
        out.append(
            f'<div class="item"><div class="hd"><span class="nm">{e(x[nm])}</span>{tg}</div>{sb}</div>'
        )
    return "\n".join(out)


def build(data_path, out_path):
    d = json.loads(pathlib.Path(data_path).read_text(encoding="utf-8"))
    tpl = (HERE / "template.html").read_text(encoding="utf-8")
    f = HERE / "fonts"

    links = "".join(
        f'<li><a href="{html.escape(l["url"])}">{e(l["label"])}</a></li>' for l in d["links"]
    )
    contact = "".join(f"<li>{e(c)}</li>" for c in d["contact"])

    repl = {
        "__INTER_LAT__":  data_uri(f / "Inter-latin.woff2"),
        "__INTER_EXT__":  data_uri(f / "Inter-latin-ext.woff2"),
        "__SERIF_LAT__":  data_uri(f / "SourceSerif4-latin.woff2"),
        "__SERIF_EXT__":  data_uri(f / "SourceSerif4-latin-ext.woff2"),
        "__NAME__":       e(f'{d["name_first"]} {d["name_last"]}'),
        "__NAME_FIRST__": e(d["name_first"]),
        "__NAME_LAST__":  e(d["name_last"]),
        "__ROLE__":       e(d["role"]),
        "__SUMMARY__":    e(d["summary"]),
        "__CONTACT__":    contact,
        "__LINKS__":      links,
        "__EXPERIENCE__": timeline(d["experience"]),
        "__EDUCATION__":  timeline(d["education"]),
        "__PROJECTS_LABEL__": e(d.get("projects_label", "Projects & awards")),
        "__PROJECTS__":   items(d["projects"], nm="title", sub="note", tag="tag"),
        "__SKILLS__":     items(d["skills"]),
        "__LANGUAGES__":  items(d["languages"]),
    }
    for k, v in repl.items():
        tpl = tpl.replace(k, v)

    tmp = pathlib.Path(tempfile.mkdtemp()) / "cv.html"
    tmp.write_text(tpl, encoding="utf-8")

    out_path = pathlib.Path(out_path)
    subprocess.run(
        [find_chrome(), "--headless=new", "--no-sandbox", "--disable-gpu",
         "--disable-dev-shm-usage", "--no-pdf-header-footer", "--run-all-compositor-stages-before-draw",
         "--virtual-time-budget=6000",
         f"--print-to-pdf={out_path}", tmp.as_uri()],
        check=True, capture_output=True,
    )
    print(f"{out_path}  ({out_path.stat().st_size/1024:.0f} KB)")
    return out_path


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default=HERE / "cv.data.json")
    ap.add_argument("--out",  default=HERE / "Matej_Pis_CV.pdf")
    a = ap.parse_args()
    build(a.data, a.out)
