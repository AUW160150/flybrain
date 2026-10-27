"""Build every EXP1-EXP3 result figure as standalone SVG from the vendored result files.

    python3 scripts/build_figures.py [--out site/src/img/results] [--variant-dir DIR]

Reads reports/figure_data_manifest.json, checks every source file's SHA-256 against it, and resolves only
the selectors each figure's manifest entry lists. Each figure is written twice: <id>.svg (720 wide, for
desktop) and <id>-sm.svg (330 wide, for phones), so no text is drawn below 11 px on either.

Output is deterministic: no timestamps, no randomness, fixed float formatting, sorted iteration.

Every data mark and every number label carries data-enc, a JSON list of
[attribute, axis, value, selector, format] records. scripts/check_results_site.py re-reads each selector
with its own resolver and checks both the printed number and the drawn position against the source.
Colours are CSS custom properties on the SVG root, overridden under the site's dark-theme selectors, so
an inlined figure follows the page's theme toggle and a standalone one follows the OS setting.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
import re
from html import escape
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
MANIFEST = REPO / "reports" / "figure_data_manifest.json"
SOURCES = REPO / "site" / "src" / "results" / "sources"
OUT = REPO / "site" / "src" / "img" / "results"
NUM_RE = re.compile(r"[+\-−]?\d[\d,]*(?:\.\d+)?")


# ----------------------------------------------------------------------------------------- data access
class Data:
    """Selector resolver that only answers selectors the current figure's manifest entry lists."""

    def __init__(self, manifest: dict):
        self.m = manifest
        self.figs = {f["id"]: f for f in manifest["figures"]}
        self.cache: dict = {}
        for rel, meta in manifest["files"].items():
            got = hashlib.sha256((SOURCES / rel).read_bytes()).hexdigest()
            if got != meta["sha256"]:
                raise SystemExit(f"source changed since the manifest was written: {rel}")
        self.fig = None

    def use(self, fid: str):
        self.fig = self.figs[fid]
        return self

    def _allowed(self, sel: str) -> None:
        base = re.sub(r"(\[\d+\]|@\d+)$", "", sel)
        for pat in self.fig["fields"]:
            rx = "^" + re.escape(pat).replace(r"\*", "[^/]+") + "$"
            if base == pat or re.match(rx, base):
                return
        raise SystemExit(f"{self.fig['id']}: selector not in manifest: {sel}")

    def _file(self, rel: str):
        if rel not in self.cache:
            raw = (SOURCES / rel).read_text(encoding="utf-8")
            if rel.endswith(".json"):
                self.cache[rel] = json.loads(raw)
            elif rel.endswith(".csv"):
                self.cache[rel] = list(csv.DictReader(io.StringIO(raw)))
            else:
                self.cache[rel] = raw.splitlines()
        return self.cache[rel]

    def get(self, sel: str):
        """json: value, or [(concrete selector, value)] when the pointer has a * segment.
        md: the cell string. csv: [(concrete selector, value)] for every matching row."""
        self._allowed(sel)
        kind, rest = sel.split(":", 1)
        rel, spec = rest.split("#", 1)
        doc = self._file(rel)
        if kind == "json":
            return _json_walk(doc, spec, f"json:{rel}#")
        if kind == "md":
            return _md_cell(doc, spec)
        if kind == "mdtext":
            m = re.search(spec, "\n".join(doc))
            if not m:
                raise SystemExit(f"mdtext pattern not found: {sel}")
            return m.group(1)
        if kind == "csv":
            filt, col = spec.rsplit("|", 1)
            conds = [c.split("=", 1) for c in filt.split(",")]
            rows = [r for r in doc if all(r[k] == v for k, v in conds)]
            return [(f"{sel}[{i}]", r[col]) for i, r in enumerate(rows)]
        raise SystemExit(f"bad selector {sel}")


def _ptr_tok(t: str) -> str:
    return t.replace("~1", "/").replace("~0", "~")


def _json_walk(doc, ptr: str, prefix: str):
    toks = [_ptr_tok(t) for t in ptr.split("/")[1:]]
    if "*" not in toks:
        cur = doc
        for t in toks:
            cur = cur[int(t)] if isinstance(cur, list) else cur[t]
        return cur
    out = []

    def rec(cur, i, path):
        if i == len(toks):
            out.append((prefix + "/" + "/".join(p.replace("~", "~0").replace("/", "~1") for p in path), cur))
            return
        t = toks[i]
        if t == "*":
            keys = range(len(cur)) if isinstance(cur, list) else sorted(cur)
            for k in keys:
                rec(cur[k], i + 1, path + [str(k)])
        else:
            rec(cur[int(t)] if isinstance(cur, list) else cur[t], i + 1, path + [t])

    rec(doc, 0, [])
    return out


def _md_cell(lines, spec: str) -> str:
    caption, row, col = spec.split("|")
    start = next(i for i, ln in enumerate(lines) if caption in ln)
    i = next(j for j in range(start + 1, len(lines)) if lines[j].startswith("|"))
    cells = lambda ln: [c.strip() for c in ln.strip().strip("|").split("|")]
    head = cells(lines[i])
    body = []
    for ln in lines[i + 2:]:
        if not ln.startswith("|"):
            break
        body.append(dict(zip(head, cells(ln))))
    if "=" in row:
        conds = [c.split("=", 1) for c in row.split(",")]
        hit = [r for r in body if all(r[k] == v for k, v in conds)]
    else:
        hit = [r for r in body if r[head[0]] == row]
    if len(hit) != 1:
        raise SystemExit(f"md row not unique: {spec}")
    return hit[0][col]


def md_num(cell: str, k: int = 0) -> float:
    toks = NUM_RE.findall(cell)
    return float(toks[k].replace("−", "-").replace(",", ""))


# ----------------------------------------------------------------------------------------- SVG writer
def f2(x: float) -> str:
    s = f"{x:.2f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


STYLE = """
.rf{--rf-bg:#f4f1ea;--rf-ink:#1a1a12;--rf-ink2:#4b4a40;--rf-ink3:#6f6d62;--rf-line:#d5d0c2;--rf-grid:#e4dfd2;
--rf-s1:#c2412a;--rf-s2:#2a78d6;--rf-s3:#138a5f;--rf-s4:#6250d6;--rf-s5:#a86f00;--rf-s6:#87857a;
--rf-band:#ebe7dc;--rf-good:#e9e1cf;font-family:'IBM Plex Sans',-apple-system,'Segoe UI',system-ui,sans-serif}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]) .rf,.rf:root:not([data-theme="light"]){
--rf-bg:#15150f;--rf-ink:#ede9df;--rf-ink2:#bdb9ad;--rf-ink3:#9a978b;--rf-line:#3a3a2f;--rf-grid:#26261d;
--rf-s1:#e5664d;--rf-s2:#3987e5;--rf-s3:#199e70;--rf-s4:#9085e9;--rf-s5:#c98500;--rf-s6:#8a887c;
--rf-band:#1e1e16;--rf-good:#262619}}
:root[data-theme="dark"] .rf{--rf-bg:#15150f;--rf-ink:#ede9df;--rf-ink2:#bdb9ad;--rf-ink3:#9a978b;
--rf-line:#3a3a2f;--rf-grid:#26261d;--rf-s1:#e5664d;--rf-s2:#3987e5;--rf-s3:#199e70;--rf-s4:#9085e9;
--rf-s5:#c98500;--rf-s6:#8a887c;--rf-band:#1e1e16;--rf-good:#262619}
.rf .bg{fill:var(--rf-bg)}.rf text{fill:var(--rf-ink2)}.rf .t1{fill:var(--rf-ink);font-weight:500}
.rf .t3,.rf .tk{fill:var(--rf-ink3)}.rf .mono{font-family:'IBM Plex Mono',ui-monospace,Menlo,monospace}
.rf .ax{stroke:var(--rf-ink3);stroke-width:1;fill:none}.rf .gr{stroke:var(--rf-grid);stroke-width:1;fill:none}
.rf .zero{stroke:var(--rf-ink2);stroke-width:1.2;fill:none}.rf .band{fill:var(--rf-band)}.rf .good{fill:var(--rf-good)}
.rf .ref{stroke:var(--rf-ink2);stroke-width:1.2;stroke-dasharray:5 4;fill:none}
.rf .pred{stroke:var(--rf-ink3);stroke-width:1.5;stroke-dasharray:2 4;fill:none;opacity:.8}
""" + "".join(
    f".rf .f{i}{{fill:var(--rf-s{i})}}.rf .s{i}{{stroke:var(--rf-s{i});fill:none}}"
    f".rf .h{i}{{fill:var(--rf-bg);stroke:var(--rf-s{i})}}" for i in range(1, 7))


class Fig:
    def __init__(self, fid: str, layout: str, width: int, height: int, title: str, desc: str):
        self.fid, self.layout, self.w, self.h = fid, layout, width, height
        self.title, self.desc = title, desc
        self.el: list[str] = []
        sm = layout == "sm"
        self.fs = {"s": 11.5 if sm else 12, "m": 12.5 if sm else 13, "l": 13.5 if sm else 14.5}

    def add(self, s: str):
        self.el.append(s)

    @staticmethod
    def _enc(enc):
        return "" if not enc else f' data-enc="{escape(json.dumps(enc, ensure_ascii=False))}"'

    def text(self, x, y, s, size="s", cls="", anchor="start", enc=None, weight=None, title=None):
        a = f' text-anchor="{anchor}"' if anchor != "start" else ""
        c = f' class="{cls}"' if cls else ""
        w = f' font-weight="{weight}"' if weight else ""
        t = f"<title>{escape(title)}</title>" if title else ""
        self.add(f'<text x="{f2(x)}" y="{f2(y)}" font-size="{self.fs[size]}"{a}{c}{w}{self._enc(enc)}>'
                 f"{t}{escape(s)}</text>")

    def wrap(self, x, y, s, max_w, size="s", cls="", lh=1.35, anchor="start"):
        """Greedy word wrap with a fixed width estimate; returns the y after the last line."""
        per = self.fs[size] * 0.58
        lines, cur = [], ""
        for word in s.split():
            if cur and len(cur + " " + word) * per > max_w:
                lines.append(cur)
                cur = word
            else:
                cur = f"{cur} {word}".strip()
        lines.append(cur)
        for ln in lines:
            self.text(x, y, ln, size, cls, anchor)
            y += self.fs[size] * lh
        return y

    def line(self, x1, y1, x2, y2, cls="", extra="", enc=None):
        self.add(f'<line x1="{f2(x1)}" y1="{f2(y1)}" x2="{f2(x2)}" y2="{f2(y2)}" class="{cls}"{extra}{self._enc(enc)}/>')

    def rect(self, x, y, w, h, cls="", extra="", enc=None, title=None):
        t = f"<title>{escape(title)}</title>" if title else ""
        self.add(f'<rect x="{f2(x)}" y="{f2(y)}" width="{f2(max(w, 0))}" height="{f2(max(h, 0))}" class="{cls}"'
                 f"{extra}{self._enc(enc)}>{t}</rect>")

    def path(self, d, cls="", extra=""):
        self.add(f'<path d="{d}" class="{cls}"{extra}/>')

    def marker(self, shape, x, y, r, cls, enc=None, title=None, extra=""):
        """Data point. Every shape exposes cx/cy so the checker can read its position."""
        t = f"<title>{escape(title)}</title>" if title else ""
        e = self._enc(enc)
        if shape == "circle":
            self.add(f'<circle cx="{f2(x)}" cy="{f2(y)}" r="{f2(r)}" class="{cls}"{extra}{e}>{t}</circle>')
            return
        pts = {"square": [(-1, -1), (1, -1), (1, 1), (-1, 1)],
               "diamond": [(0, -1.3), (1.3, 0), (0, 1.3), (-1.3, 0)],
               "triangle": [(0, -1.25), (1.15, 0.85), (-1.15, 0.85)],
               "down": [(0, 1.25), (1.15, -0.85), (-1.15, -0.85)],
               "cross": [(-.4, -1.1), (.4, -1.1), (.4, -.4), (1.1, -.4), (1.1, .4), (.4, .4), (.4, 1.1),
                         (-.4, 1.1), (-.4, .4), (-1.1, .4), (-1.1, -.4), (-.4, -.4)]}[shape]
        rr = r * 0.85
        d = "M" + " L".join(f"{f2(x + a * rr)} {f2(y + b * rr)}" for a, b in pts) + " Z"
        self.add(f'<path d="{d}" cx="{f2(x)}" cy="{f2(y)}" class="{cls}"{extra}{e}>{t}</path>')

    def group(self, sx=None, sy=None, cls=""):
        attrs = ""
        if sx:
            attrs += f' data-sx="{escape(json.dumps(sx))}"'
        if sy:
            attrs += f' data-sy="{escape(json.dumps(sy))}"'
        c = f' class="{cls}"' if cls else ""
        self.add(f"<g{c}{attrs}>")

    def end(self):
        self.add("</g>")

    def svg(self) -> str:
        head = (f'<svg xmlns="http://www.w3.org/2000/svg" class="rf rf-{self.fid}" viewBox="0 0 {self.w} {self.h}" '
                f'width="{self.w}" height="{self.h}" role="img" aria-labelledby="{self.fid}-{self.layout}-t '
                f'{self.fid}-{self.layout}-d">'
                f'<title id="{self.fid}-{self.layout}-t">{escape(self.title)}</title>'
                f'<desc id="{self.fid}-{self.layout}-d">{escape(self.desc)}</desc>'
                f"<style>{STYLE}</style>"
                f'<rect class="bg" x="0" y="0" width="{self.w}" height="{self.h}"/>')
        return head + "\n" + "\n".join(self.el) + "\n</svg>\n"


class Scale:
    def __init__(self, v0, v1, p0, p1, log=False):
        self.v0, self.v1, self.p0, self.p1, self.log = v0, v1, p0, p1, log

    def __call__(self, v):
        if self.log:
            a, b, v = math.log10(self.v0), math.log10(self.v1), math.log10(v)
        else:
            a, b = self.v0, self.v1
        return self.p0 + (v - a) / (b - a) * (self.p1 - self.p0)

    def spec(self):
        return {"v0": self.v0, "v1": self.v1, "p0": round(self.p0, 4), "p1": round(self.p1, 4), "log": self.log}


def enc(attr, axis, value, sel, fmt=""):
    return [attr, axis, value, sel, fmt]


def pct(v, d=1):
    return f"{v * 100:.{d}f}%"


def signed(v, d=1, unit=""):
    s = f"{abs(v):.{d}f}"
    return ("+" if v > 0 else "−" if v < 0 else "") + s + unit


def fmt_int(v):
    return f"{int(round(v)):,}"


def legend(fig: Fig, x, y, items, max_w, gap=18):
    """items: (shape, cls, label, dashed). Wraps into rows; returns y below the legend."""
    cx, row_h = x, fig.fs["s"] * 1.7
    for shape, cls, label, dash in items:
        w = 26 + len(label) * fig.fs["s"] * 0.58
        if cx > x and cx + w > x + max_w:
            cx, y = x, y + row_h
        stroke = cls.replace("f", "s").replace("h", "s").split()[0]
        da = ' stroke-dasharray="5 3"' if dash else ""
        if dash is not None:
            fig.line(cx, y - 4, cx + 18, y - 4, stroke, f' stroke-width="2"{da}')
        if shape:
            fig.marker(shape, cx + 9, y - 4, 4.2, cls)
        fig.text(cx + 24, y, label, "s")
        cx += w + gap
    return y + row_h


def x_ticks(fig, sx, y, ticks, fmt=lambda v: f2(v), grid=None, size="s"):
    for v in ticks:
        x = sx(v)
        if grid:
            fig.line(x, grid[0], x, grid[1], "gr")
        fig.text(x, y, fmt(v), size, "tk", "middle")


def y_ticks(fig, sy, x, ticks, fmt=lambda v: f2(v), grid=None, size="s"):
    for v in ticks:
        y = sy(v)
        if grid:
            fig.line(grid[0], y, grid[1], y, "gr")
        fig.text(x, y + 4, fmt(v), size, "tk", "end")


# ----------------------------------------------------------------------------------------- EXP1 figures
G1, G1B = "fly_track/reports/exp1c/g1.json", "fly_track/reports/exp1c/g1b.json"
T, TB = "fly_track/reports/stage1_headroom.md", "fly_track/reports/stage1b_occlusion.md"
COND = [("visible", G1, "Target always visible"), ("hidden", G1B, "Target hidden for two 1–2 s spells")]


def reliable(ci):
    return ci[0] > 0 or ci[1] < 0


def fig_memory(D: Data, layout: str, variant: str = "slope") -> str:
    D.use("exp1-memory-dissociation")
    sm = layout == "sm"
    W = 330 if sm else 720
    ends = [("post_collision", "Hit a post (obstacle)"), ("wall_collision", "Hit an arena wall")]
    vals = {}
    for key, g, _ in COND:
        for e, _ in ends:
            for a in ("bio", "bypass"):
                sel = f"json:{g}#/descriptives/{a}/{e}"
                vals[(key, e, a)] = (D.get(sel), sel)
            dsel = f"json:{g}#/secondary/{e}/"
            vals[(key, e, "diff")] = (D.get(dsel + "diff"), dsel + "diff", D.get(dsel + "ci95"), dsel + "ci95")
    H = 770 if sm else 440
    f = Fig("exp1-memory-dissociation", layout, W, H,
            "Collisions: the fly circuit against the direct connection, with the target visible and hidden",
            "Two panels, posts and walls. In each, the share of evaluation episodes with a collision for the fly "
            "circuit and for the memoryless direct connection, with the target always visible and with the target "
            "hidden. Wall collisions: the circuit is worse by about the same amount in both conditions. Post "
            "collisions: identical when visible, the circuit better when hidden.")
    y = 22
    y = legend(f, 12, y, [("circle", "f1", "Fly circuit (has loops, so a short memory)", False),
                          ("square", "h2", "Direct connection (no loops, no memory)", True)], W - 24)
    sy_top = y + (14 if sm else 18)
    ph = 205 if sm else 250
    panels = [(12, sy_top, W - 24)] * 1
    if sm:
        boxes = [(46, sy_top + 18, W - 70), (46, sy_top + 18 + ph + 130, W - 70)]
    else:
        boxes = [(58, sy_top + 18, 270), (58 + 270 + 92, sy_top + 18, 270)]
    for (e, ename), (bx, by, bw) in zip(ends, boxes):
        f.text(bx - 34 if sm else bx - 40, by - 10, ename, "m", "t1")
        sy = Scale(0, 0.30, by + ph, by)
        f.group(sy=sy.spec())
        y_ticks(f, sy, bx - 8, [0, 0.1, 0.2, 0.3], lambda v: f"{round(v * 100)}%", grid=(bx, bx + bw))
        xs = [bx + bw * 0.24, bx + bw * 0.76]
        for i, (key, g, cname) in enumerate(COND):
            lab = "Target visible" if i == 0 else "Target hidden"
            f.text(xs[i], by + ph + 18, lab, "s", "t1", "middle")
            f.text(xs[i], by + ph + 32, "(normal task)" if i == 0 else "(occlusion task)", "s", "t3", "middle")
        for a, shape, cls, dash in (("bio", "circle", "f1", ""), ("bypass", "square", "h2", ' stroke-dasharray="5 3"')):
            pts = [(xs[i], sy(vals[(k, e, a)][0])) for i, (k, _, _) in enumerate(COND)]
            f.line(pts[0][0], pts[0][1], pts[1][0], pts[1][1], f"s{1 if a == 'bio' else 2}",
                   f' stroke-width="2.4"{dash}')
        for i, (k, _, _) in enumerate(COND):
            d, dsel, ci, cisel = vals[(k, e, "diff")]
            yb, yp = sy(vals[(k, e, "bio")][0]), sy(vals[(k, e, "bypass")][0])
            for a, shape, cls in (("bio", "circle", "f1"), ("bypass", "square", "h2")):
                v, sel = vals[(k, e, a)]
                f.marker(shape, xs[i], sy(v), 5.5, cls, enc=[enc("cy", "y", v, sel)],
                         extra=' stroke-width="2"', title=f"{'Fly circuit' if a == 'bio' else 'Direct connection'}: {pct(v)}")
            # value labels: circuit on one side, direct on the other
            side = -1 if i == 0 else 1
            anchor = "end" if side < 0 else "start"
            lx = xs[i] + side * 11
            above = yb < yp
            vb, sb = vals[(k, e, "bio")]
            vp, sp_ = vals[(k, e, "bypass")]
            off_b, off_p = (-3, 13) if above else (13, -3)
            if abs(yb - yp) < 16:
                off_b, off_p = ((-5, 15) if above else (15, -5))
                if abs(yb - yp) < 4:
                    off_b, off_p = (15, -5) if vb <= vp else (-5, 15)
            f.text(lx, yb + off_b, pct(vb), "s", "t1", anchor, enc=[enc("text", "", vb, sb, "x100")])
            f.text(lx, yp + off_p, pct(vp), "s", "", anchor, enc=[enc("text", "", vp, sp_, "x100")])
            # the gap, and whether it is reliable
            rel = reliable(ci)
            word = ("circuit reliably worse" if d > 0 else "circuit reliably better") if rel else "no reliable difference"
            gy = by + ph + 54
            f.rect(xs[i] - 62, gy - 13, 124, 36, "good" if rel else "bg",
                   ' rx="3" stroke="var(--rf-ink3)" stroke-width="1"' + ("" if rel else ' stroke-dasharray="2 3"'))
            f.text(xs[i], gy + 1, "gap " + signed(d * 100, 1, " pts"), "s", "t1", "middle",
                   enc=[enc("text", "", d, dsel, "x100")])
            f.text(xs[i], gy + 15, word, "s", "t1" if rel else "t3", "middle")
        f.end()
    return f.svg()


def fig_loops(D: Data, layout: str) -> str:
    D.use("exp1-loops-not-wiring")
    sm = layout == "sm"
    W = 330 if sm else 720
    arms = [("rew1003", "Rewired copy 3", True), ("rew1002", "Rewired copy 2", True), ("bio", "Real fly wiring", True),
            ("rew1001", "Rewired copy 1", True), ("bypass", "Direct connection", False),
            ("two_unit", "Two-signal summary", False)]
    rows = []
    for a, name, loops in arms:
        sel = f"json:{G1B}#/descriptives/{a}/post_collision"
        nsel = f"json:{G1B}#/seeds_per_arm/{a}"
        rows.append((a, name, loops, D.get(sel), sel, D.get(nsel), nsel))
    rows.sort(key=lambda r: r[3])
    if [r[2] for r in rows] != [True] * 4 + [False] * 2:
        raise SystemExit("loop arms do not cluster below the loop-free arms; caption would be false")
    lab_w = 128 if sm else 190
    x0, x1 = lab_w + 8, W - (54 if sm else 70)
    sx = Scale(0, 0.25, x0, x1)
    rh, top = 30, 44
    H = top + 6 * rh + 80 + 76
    f = Fig("exp1-loops-not-wiring", layout, W, H,
            "Post collisions with the target hidden, all six versions of the controller",
            "Horizontal bars, sorted. The four versions with loops (the real wiring and three rewired copies) sit "
            "between 17.8% and 18.3% of episodes; the two without loops sit at 21.4% and 22.1%.")
    f.text(12, 20, "Share of episodes with a post collision, target hidden", "m", "t1")
    f.group(sx=sx.spec())
    gy = top
    for gi, glabel in enumerate(("Versions with loops", "Versions without loops")):
        n = 4 if gi == 0 else 2
        f.rect(4, gy - 4, W - 8, n * rh + 22, "band")
        f.text(10, gy + 10, glabel.upper(), "s", "t3 mono")
        gy += n * rh + 22 + 10
    for v in (0, 0.05, 0.1, 0.15, 0.2, 0.25):
        f.line(sx(v), top - 6, sx(v), top + 6 * rh + 56, "gr")
    y = top + 18
    for i, (a, name, loops, v, sel, n, nsel) in enumerate(rows):
        if i == 4:
            y += 32
        cls = ("f1" if a == "bio" else "f1") if loops else "f2"
        op = "" if a in ("bio", "bypass", "two_unit") else ' fill-opacity="0.55"'
        f.rect(x0, y + 4, sx(v) - x0, rh - 12, cls, op, enc=[enc("x2", "x", v, sel)],
               title=f"{name}: {pct(v)} of episodes")
        f.text(x0 - 8, y + rh / 2 + 4, name, "s", "t1" if a == "bio" else "", "end")
        f.text(sx(v) + 6, y + rh / 2 + 4, pct(v), "s", "t1", enc=[enc("text", "", v, sel, "x100")])
        y += rh
    f.end()
    yb = top + 6 * rh + 70
    x_ticks(f, sx, yb, (0, 0.1, 0.2), lambda v: f"{round(v * 100)}%")
    f.wrap(12, yb + 22, "Rewired copies: the same neurons and number of connections, with the connections "
                        "shuffled while keeping each neuron's count of inputs and outputs.", W - 24, "s", "t3")
    return f.svg()


def fig_stopped(D: Data, layout: str) -> str:
    D.use("exp1-why-stopped")
    sm = layout == "sm"
    W = 330 if sm else 720
    P = "fly_track/reports/exp1c/power.json"
    rows = {}
    for i in range(12):
        b = f"json:{P}#/stage2_table/{i}/"
        key = (D.get(b + "graphs"), D.get(b + "seeds_per_graph"), D.get(b + "sd_graph"))
        rows[key] = (D.get(b + "mde80_two_sided"), b + "mde80_two_sided")
    best, best_sel = rows[(20, 5, 0.0)]
    worst, worst_sel = rows[(20, 5, 0.03)]
    gsel = f"json:{G1B}#/tracked_frac/diff"
    gap = D.get(gsel)
    lab_w = 0 if sm else 250
    x0, x1 = (16 if sm else lab_w + 20), W - (16 if sm else 30)
    sx = Scale(0, 0.03, x0, x1)
    H = 350 if sm else 320
    f = Fig("exp1-why-stopped", layout, W, H,
            "The planned next test's finest measurement against the whole gap it would have searched",
            "A ruler from 0 to 3 points of the main score. The circuit's whole lead over the direct connection with "
            "the target hidden was 0.70 points. The planned next test could reliably detect only differences of "
            "2.0 points or more in the most favourable case, 2.8 points in a less favourable one.")
    if sm:
        f.text(12, 20, "The main score, in points", "m", "t1")
        f.wrap(12, 37, "Share of time the target stayed in view at the right distance (1 point = 0.01)", W - 24, "s", "t3")
    else:
        f.text(12, 20, "Main score: share of time the target stayed in view at the right distance", "m", "t1")
        f.text(12, 37, "measured in percentage points (1 point = 0.01)", "s", "t3")
    f.group(sx=sx.spec())
    ytop = 62 if not sm else 72
    for v in (0, 0.005, 0.01, 0.015, 0.02, 0.025, 0.03):
        f.line(sx(v), ytop - 4, sx(v), ytop + (170 if sm else 116), "gr")
    bars = [
        ("Everything the next test could hope to find", "the circuit's whole lead over the direct connection, target hidden",
         [("x2", "x", gap, gsel)], gap, gsel, "f1", ""),
        ("Smallest difference the next test could reliably detect", "20 scrambled circuits × 5 training runs each",
         None, best, best_sel, "f2", ""),
    ]
    y = ytop
    for i, (l1, l2, _, v, sel, cls, _) in enumerate(bars):
        if sm:
            f.text(x0, y + 10, l1, "s", "t1")
            y = f.wrap(x0, y + 25, l2, W - 32, "s", "t3") - 6
            by = y
        else:
            yl = f.wrap(lab_w + 10, y + 12, l1, 240, "s", "t1", anchor="end")
            f.wrap(lab_w + 10, yl, l2, 240, "s", "t3", anchor="end")
            by = y + 4
        if i == 1:
            f.rect(sx(v), by + 5, sx(worst) - sx(v), 12, "h2", ' stroke-dasharray="3 3" stroke-width="1.2"',
                   enc=[enc("x2", "x", worst, worst_sel)])
        f.rect(x0, by, sx(v) - x0, 22, cls, enc=[enc("x2", "x", v, sel)])
        if i == 0:
            f.text(sx(v) + 6, by + 15, f"{v * 100:.2f} points", "s", "t1", enc=[enc("text", "", v, sel, "x100")])
        else:
            f.text(x0, by + 38, f"{v * 100:.1f} points in the best case", "s", "t1",
                   enc=[enc("text", "", v, sel, "x100")])
            f.text(x0, by + 38 + f.fs["s"] * 1.35, f"{worst * 100:.1f} points if the scrambled circuits differ more",
                   "s", "t3", enc=[enc("text", "", worst, worst_sel, "x100")])
        y = by + (54 if sm else 80) + (0 if i == 0 else 30)
    f.end()
    x_ticks(f, sx, (H - 14), (0, 0.01, 0.02, 0.03), lambda v: f"{round(v * 100)} pt" if v else "0")
    return f.svg()


def fig_inert(D: Data, layout: str) -> str:
    D.use("exp1-not-inert")
    sm = layout == "sm"
    W = 330 if sm else 720
    lab_w = 0 if sm else 270
    x0, x1 = (24 if sm else lab_w + 20), W - (64 if sm else 80)
    sx = Scale(-0.05, 0.15, x0, x1)
    items = []
    for key, g, cname in COND:
        b = f"json:{g}#/bio_minus_other_arms_tracked_frac/two_unit/"
        items.append((cname, "against the two-signal summary", D.get(b + "diff"), b + "diff", D.get(b + "ci95"), b + "ci95"))
        b = f"json:{g}#/tracked_frac/"
        items.append((cname, "against the direct connection", D.get(b + "diff"), b + "diff", D.get(b + "ci95"), b + "ci95"))
    rh = 50 if sm else 44
    top = 66 if not sm else 92
    H = top + 4 * rh + 20 + 60
    f = Fig("exp1-not-inert", layout, W, H,
            "How far the fly circuit is ahead or behind on the main score",
            "Dots with 95% ranges. Against the crude two-signal summary the circuit is about 10 points ahead in both "
            "conditions. Against the direct connection it is 2.1 points behind with the target visible and level "
            "with it, within the uncertainty, with the target hidden.")
    f.text(12, 20, "Fly circuit's lead on the main score, in points", "m", "t1")
    f.text(12, 37, "dot: best estimate · line: range we can be 95% confident about · filled: reliably not zero",
           "s", "t3") if not sm else f.wrap(12, 37, "Dot: best estimate. Line: the range we can be 95% confident "
                                              "about. Filled dot: reliably different from zero.", W - 24, "s", "t3")
    f.group(sx=sx.spec())
    yb = top + 4 * rh + 6
    for v in (-0.05, 0, 0.05, 0.1, 0.15):
        f.line(sx(v), top - 6, sx(v), yb, "zero" if v == 0 else "gr")
    y = top + (14 if sm else 0)
    last = None
    for cname, against, d, dsel, ci, cisel in items:
        if cname != last:
            if sm:
                f.text(12, y - 2, cname, "s", "t1")
            last = cname
        rel = reliable(ci)
        cy = y + (14 if sm else 10)
        if not sm:
            f.text(lab_w + 8, cy - 5, against, "s", "", "end")
            f.text(lab_w + 8, cy + 12, cname, "s", "t3", "end")
        else:
            f.text(12, cy - 9 + 26, against, "s", "t3")
        f.line(sx(ci[0]), cy, sx(ci[1]), cy, "s1" if "summary" in against else "s2", ' stroke-width="2"',
               enc=[enc("x1", "x", ci[0], cisel + "/0"), enc("x2", "x", ci[1], cisel + "/1")])
        shape, cls = ("circle", "f1" if rel else "h1") if "summary" in against else ("square", "f2" if rel else "h2")
        f.marker(shape, sx(d), cy, 5.5, cls, enc=[enc("cx", "x", d, dsel)], extra=' stroke-width="2"')
        tx = sx(ci[1]) + 8
        f.text(tx, cy + 4, signed(d * 100, 1, " pts"), "s", "t1", enc=[enc("text", "", d, dsel, "x100")])
        y += rh
    f.end()
    x_ticks(f, sx, yb + 18, (-0.05, 0, 0.05, 0.1, 0.15), lambda v: signed(v * 100, 0) if v else "0")
    f.text(sx(0) - 6, yb + 36, "← behind" if sm else "← circuit behind", "s", "t3", "end")
    f.text(sx(0) + 6, yb + 36, "ahead →" if sm else "circuit ahead →", "s", "t3")
    return f.svg()


def fig_curves(D: Data, layout: str) -> str:
    D.use("exp1-learning-curves")
    sm = layout == "sm"
    W = 330 if sm else 720
    arms = [("bio", "Real fly wiring", "circle", 1, ""), ("rew1001", "Rewired copies", "triangle", 3, ""),
            ("rew1002", None, "triangle", 3, ""), ("rew1003", None, "triangle", 3, ""),
            ("bypass", "Direct connection", "square", 2, ' stroke-dasharray="5 3"'),
            ("two_unit", "Two-signal summary", "diamond", 4, ' stroke-dasharray="1.5 3"')]
    steps = [1000, 2000, 4000, 8000, 12000, 16000]
    f = Fig("exp1-learning-curves", layout, W, 680 if sm else 450,
            "Validation score during training, every version, both conditions",
            "Lines per version of the controller, score against training step. Up to step 4,000 every run is still "
            "training; later points rest on the few runs that had not stopped, drawn hollow with their run count.")
    y = legend(f, 12, 20, [("circle", "f1", "Real fly wiring", False), ("triangle", "f3", "Rewired copies (3)", False),
                           ("square", "h2", "Direct connection", True), ("diamond", "h4", "Two-signal summary", True)],
               W - 24)
    y = f.wrap(12, y, "Solid points: every run still training. Hollow points: only n runs had not yet stopped, "
                      "so they are weak evidence.", W - 24, "s", "t3") + 6
    ph = 190 if sm else 220
    boxes = ([(46, y + 22, W - 64), (46, y + 22 + ph + 96, W - 64)] if sm
             else [(52, y + 22, 290), (52 + 290 + 64, y + 22, 290)])
    for (key, g, cname), md, (bx, by, bw) in zip(COND, (T, TB), boxes):
        f.text(bx - 34, by - 16, cname, "m", "t1")
        sx = Scale(0, 16000, bx, bx + bw)
        sy = Scale(0.4, 1.0, by + ph, by)
        f.group(sx=sx.spec(), sy=sy.spec())
        y_ticks(f, sy, bx - 6, (0.4, 0.6, 0.8, 1.0), lambda v: f"{round(v * 100)}%", grid=(bx, bx + bw))
        x_ticks(f, sx, by + ph + 16, (0, 4000, 8000, 12000, 16000),
                lambda v: f"{int(v / 1000)}k" if v else "0")
        for a, name, shape, ci, dash in arms:
            pts = []
            for s in steps:
                sel = f"md:{md}#Mean validation tracked fraction by step|{a}|{s}"
                cell = D.get(sel)
                if cell.strip() == "-":
                    continue
                pts.append((s, md_num(cell, 0), int(md_num(cell, 1)), sel))
            full = pts[0][2]
            solid = [p for p in pts if p[2] == full]
            thin = [p for p in pts if p[2] != full]
            op = ' stroke-opacity="0.65"' if a.startswith("rew") else ""
            d = " L".join(f"{f2(sx(s))} {f2(sy(v))}" for s, v, _, _ in solid)
            f.path("M" + d, f"s{ci}", f' stroke-width="{2.2 if a == "bio" else 1.6}"{dash}{op}')
            if thin:
                d = " L".join(f"{f2(sx(s))} {f2(sy(v))}" for s, v, _, _ in [solid[-1]] + thin)
                f.path("M" + d, f"s{ci}", ' stroke-width="1" stroke-dasharray="2 3" stroke-opacity="0.6"')
            for s, v, n, sel in pts:
                cls = f"f{ci}" if n == full else f"h{ci}"
                f.marker(shape, sx(s), sy(v), 4.2 if n == full else 3.6, cls, extra=' stroke-width="1.5"',
                         enc=[enc("cy", "y", v, sel + "@0")],
                         title=f"{name or 'Rewired copy'} at step {s:,}: {pct(v)} ({n} runs)")
            for s, v, n, sel in thin:
                if a in ("bio", "bypass", "two_unit"):
                    f.text(sx(s) + 6, sy(v) + {"bio": 14, "bypass": -7, "two_unit": 14}[a], f"n={n}", "s", "t3",
                           enc=[enc("text", "", n, sel + "@1", "")])
        f.end()
        conv = D.get(f"json:{g}#/convergence/*/stop_reason")
        nconv = sum(1 for _, v in conv if v == "converged")
        f.text(bx + bw / 2, by + ph + 32, "training step", "s", "t3", "middle")
        f.text(bx - 34, by + ph + 52, f"{nconv} of {len(conv)} runs converged; none hit the step cap",
               "s", "t3", enc=[enc("text", "", nconv, f"json:{g}#/convergence/*/stop_reason", "count=converged"),
                                      ["text2", "", len(conv), f"json:{g}#/convergence/*/stop_reason", "len"]])
    return f.svg()


def fig_activity(D: Data, layout: str) -> str:
    D.use("exp1-activity")
    sm = layout == "sm"
    W = 330 if sm else 720
    A = "fly_track/reports/exp1c/activity.json"
    allg = D.get(f"json:{A}#/graphs/*/rel_offset_unnormalized")
    groups = [
        ("L4", "Keeps each block's own synapse strengths", lambda k: k.startswith("L4_")),
        ("L3", "Keeps cell-type and side blocks, shuffles strengths", lambda k: k.startswith("L3_")),
        ("L2", "Keeps cell-type blocks", lambda k: k.startswith("L2_")),
        ("L1", "Keeps each neuron's number of links", lambda k: k.startswith("L1_")),
        ("L0", "Keeps only excitatory/inhibitory counts", lambda k: k.startswith("L0_")),
        ("Earlier", "Earlier experiment's rewired copies", lambda k: k in ("rew1001", "rew1002", "rew1003")),
        ("Earlier", "Earlier experiment's random copy", lambda k: k == "rewU2001"),
    ]
    rows = []
    used = 0
    for code, name, pred in groups:
        pts = [(sel, v, sel.split("/graphs/")[1].split("/")[0]) for sel, v in allg if pred(sel.split("/graphs/")[1].split("/")[0])]
        used += len(pts)
        rows.append((code, name, pts))
    if used != 64 or any(v <= 0 for _, _, p in rows for _, v, _ in p):
        raise SystemExit("activity: expected 64 null graphs, all louder than bio")
    lab_w = 0 if sm else 300
    x0, x1 = (16 if sm else lab_w + 16), W - (16 if sm else 24)
    sx = Scale(0, 2.0, x0, x1)
    rh = 44 if sm else 30
    top = 74 if sm else 66
    H = top + len(rows) * rh + 64
    f = Fig("exp1-activity", layout, W, H,
            "Before any training: how much more active each scrambled circuit is than the real one",
            "Dots, one per scrambled circuit, 64 in all, grouped by what each kind of scrambling keeps. Every dot is "
            "to the right of zero, so the real circuit is the quietest. Circuits that keep each block's own synapse "
            "strengths sit within 0.2% to 8.2%; the rest range up to 186%.")
    f.text(12, 20, "Activity before training, against the real circuit" if sm else
           "Output activity before training, compared with the real circuit", "m", "t1")
    f.wrap(12, 38, "0% = exactly as active as the real circuit. Each dot is one scrambled circuit (64 in all).",
           W - 24, "s", "t3")
    f.group(sx=sx.spec())
    for v in (0, 0.5, 1.0, 1.5, 2.0):
        f.line(sx(v), top - 8, sx(v), top + len(rows) * rh, "zero" if v == 0 else "gr")
    y = top
    for i, (code, name, pts) in enumerate(rows):
        if i % 2 == 0:
            f.rect(4, y - 2, W - 8, rh - 2, "band")
        cy = y + (rh - 10 if sm else rh / 2)
        if sm:
            f.text(x0, y + 12, name, "s", "t1" if code == "L4" else "")
        else:
            f.text(lab_w + 4, cy + 4, name, "s", "t1" if code == "L4" else "", "end")
        lo = min(pts, key=lambda p: p[1])
        hi = max(pts, key=lambda p: p[1])
        cls = "f1" if code == "L4" else ("f2" if code != "Earlier" else "f5")
        for sel, v, gid in pts:
            f.marker("circle", sx(v), cy, 4, cls, extra=' fill-opacity="0.75"', enc=[enc("cx", "x", v, sel)],
                     title=f"{gid}: {pct(v)} more active")
        label = f"{pct(lo[1])}–{pct(hi[1])}" if len(pts) > 1 else pct(lo[1])
        lx = sx(hi[1]) + 8
        anchor = "start"
        if lx > x1 - 70:
            lx, anchor = sx(lo[1]) - 8, "end"
        e = [enc("text", "", lo[1], lo[0], "x100")]
        if len(pts) > 1:
            e.append(["text2", "", hi[1], hi[0], "x100"])
        f.text(lx, cy + 4, label, "s", "t1", anchor, enc=e)
        y += rh
    f.end()
    x_ticks(f, sx, top + len(rows) * rh + 16, (0, 0.5, 1.0, 1.5) if sm else (0, 0.5, 1.0, 1.5, 2.0),
            lambda v: f"+{round(v * 100)}%" if v else "0")
    f.text(sx(0) - 4, top + len(rows) * rh + 34, "0 = the real circuit", "s", "t3")
    return f.svg()


# ----------------------------------------------------------------------------------------- EXP2
PILOT = "fly_track/raw_results/exp2/conditional_seed_pilot/pilot_analysis.json"
P2 = "fly_track/reports/exp2_conditional_power.json"


def fig_exp2(D: Data, layout: str) -> str:
    D.use("exp2-variability-stop")
    sm = layout == "sm"
    W = 330 if sm else 720
    g = f"json:{PILOT}#/gate/"
    meas, meas_s = D.get(g + "tracking_seed_sd"), g + "tracking_seed_sd"
    coll, coll_s = D.get(g + "collision_seed_sd"), g + "collision_seed_sd"
    stop, stop_s = D.get(g + "effective_stop_threshold_inclusive"), g + "effective_stop_threshold_inclusive"
    plan_s = f"json:{P2}#/condition1_exact_model/tracking_seed_sd"
    plan = D.get(plan_s)
    metric = D.get(f"json:{PILOT}#/per_seed_rows/*/metric")
    seeds = D.get(f"json:{PILOT}#/per_seed_rows/*/train_seed")
    gaps = D.get(f"json:{PILOT}#/per_seed_rows/*/paired_CL_minus_OL")
    per = [(s[1], gp[0], gp[1]) for (ms, m), s, gp in zip(metric, seeds, gaps) if m == "tracked_frac"]
    rows = {k: D.get(f"json:{P2}#/scenario_rows/*/{k}") for k in
            ("scientific_seed_pairs", "episodes", "tracking_shared_episode_sd", "tracking_seed_sd",
             "tracking_guardrail_power_true_difference_zero")}
    curve = []
    for i in range(len(rows["episodes"])):
        if (rows["scientific_seed_pairs"][i][1] == 20 and rows["episodes"][i][1] == 2000
                and rows["tracking_shared_episode_sd"][i][1] == 0.2):
            curve.append((rows["tracking_seed_sd"][i], rows["tracking_guardrail_power_true_difference_zero"][i]))
    curve.sort(key=lambda c: c[0][1])
    if not curve or max(c[0][1] for c in curve) >= meas:
        raise SystemExit("exp2: expected the power rows to stop short of the measured SD")
    H = 670 if sm else 400
    f = Fig("exp2-variability-stop", layout, W, H,
            "Forward-only training: how much results swung between random starts, against the limits set in advance",
            "Top: the gap between the two forward-only training modes for each of five random starts, from almost "
            "zero to about 32 points. Bottom: the planned study's chance of a clear answer falls as variability "
            "rises; the measured variability, 0.1348, lies past the stop line and past the end of the computed curve.")
    # panel A
    f.text(12, 20, "1 · Same experiment, five random starting points", "m", "t1")
    f.wrap(12, 38, "Gap on the main score between the two forward-only training modes, one dot per start", W - 24,
           "s", "t3")
    ax0, ax1 = (24, W - 24)
    sxa = Scale(-0.35, 0.0, ax0, ax1)
    ya = 82 if sm else 74
    f.group(sx=sxa.spec())
    for v in (-0.35, -0.3, -0.2, -0.1, 0.0):
        f.line(sxa(v), ya - 16, sxa(v), ya + 16, "zero" if v == 0 else "gr")
    for k, (seed_sel, sel, v) in enumerate(sorted(per, key=lambda p: p[2])):
        f.marker("circle", sxa(v), ya, 6, "f1", enc=[enc("cx", "x", v, sel)], extra=' fill-opacity="0.85"',
                 title=f"Start {k + 1}: {signed(v * 100, 1)} points")
    f.end()
    x_ticks(f, sxa, ya + 32, (-0.3, -0.2, -0.1, 0.0), lambda v: f"{signed(v * 100, 0)} pt" if v else "0")
    # panel B
    yb0 = ya + 76
    f.text(12, yb0, "2 · Variability against the limits set before the pilot", "m", "t1")
    yb = f.wrap(12, yb0 + 18, "Line: the planned study's chance of a clear answer if training methods truly do not "
                              "differ, computed in advance for these variability values only.", W - 24, "s", "t3")
    bx0, bx1 = (46, W - 16) if sm else (60, W - 30)
    top, bot = yb + 22, H - (96 if sm else 70)
    sx = Scale(0, 0.15, bx0, bx1)
    sy = Scale(0, 1, bot, top)
    f.group(sx=sx.spec(), sy=sy.spec())
    y_ticks(f, sy, bx0 - 6, (0, 0.5, 1), lambda v: f"{round(v * 100)}%", grid=(bx0, bx1))
    f.rect(sx(stop), top, bx1 - sx(stop), bot - top, "good", ' fill-opacity="0.9"')
    pts = [(sx(c[0][1]), sy(c[1][1])) for c in curve]
    f.path("M" + " L".join(f"{f2(x)} {f2(y)}" for x, y in pts), "s2", ' stroke-width="2"')
    for (ssel, s), (psel, p) in curve:
        f.marker("square", sx(s), sy(p), 4, "f2", enc=[enc("cx", "x", s, ssel), enc("cy", "y", p, psel)],
                 title=f"variability {s}: {pct(p, 0)} chance of a clear answer")
    for v, sel, cls, l1, ly in ((plan, plan_s, "s6", "planned for", top + 12), (stop, stop_s, "s1", "stop line", top + 12)):
        f.line(sx(v), top, sx(v), bot, cls, ' stroke-width="1.6" stroke-dasharray="5 3"', enc=[enc("x1", "x", v, sel)])
    f.text(sx(plan) - 4, bot - 8, "planned", "s", "t3", "end")
    f.text(sx(plan) - 4, bot - 8 - f.fs["s"] * 1.3, f"{plan:.2f}", "s", "t1", "end", enc=[enc("text", "", plan, plan_s)])
    f.text(sx(stop) + 4, top + 14, "stop line", "s", "t1")
    f.text(sx(stop) + 4, top + 14 + f.fs["s"] * 1.3, f"{stop:.3f}", "s", "t1", enc=[enc("text", "", stop, stop_s)])
    for v, sel, lab, w, yy in ((coll, coll_s, "measured, collisions", 1.6, 0.45 if sm else 0.62),
                               (meas, meas_s, "measured, main score", 3, 0.7 if sm else 0.88)):
        f.line(sx(v), top, sx(v), bot, "s1", f' stroke-width="{w}"', enc=[enc("x1", "x", v, sel)])
        anchor = "end" if v > 0.1 else "start"
        tx = sx(v) + (-5 if anchor == "end" else 5)
        f.text(tx, sy(yy) - (0 if v > 0.1 else 0), lab, "s", "t1", anchor)
        f.text(tx, sy(yy) + f.fs["s"] * 1.3, f"{v:.4f}", "s", "t1", anchor, enc=[enc("text", "", v, sel)])
    f.end()
    x_ticks(f, sx, bot + 16, (0, 0.05, 0.1, 0.15), lambda v: f2(v))
    f.text((bx0 + bx1) / 2, bot + 34, "seed-to-seed variability" if sm else
           "seed-to-seed variability (standard deviation of the main score)", "s", "t3", "middle")
    f.wrap(12, bot + 54, "No chance was computed past 0.10: the measured value is off the end of the planning table.",
           W - 24, "s", "t3")
    return f.svg()


# ----------------------------------------------------------------------------------------- EXP3
EXPORT, B2S = "fly_retrieval/b2/export.csv", "fly_retrieval/reports/trackB2_summary.json"
TOUCH, PRE3 = "fly_retrieval/b2/flyhash_candidates_touched.csv", "fly_retrieval/docs/exp3_preregistration.md"
SETS = [("sift-128-euclidean", "SIFT: 1 million image descriptors"), ("glove-100-angular", "GloVe: 1.2 million word vectors")]
ALGOS = [("flyhash", "FlyHash (fly-inspired)", "circle", 1, 2.6, ""),
         ("densefly", "DenseFly (fly-inspired)", "triangle", 5, 2.6, ""),
         ("hnswlib", "HNSW graph", "square", 2, 1.6, ' stroke-dasharray="6 3"'),
         ("scann", "ScaNN", "diamond", 3, 1.6, ' stroke-dasharray="2 2"'),
         ("faiss-ivfpqfs", "FAISS IVF-PQ fast-scan", "down", 4, 1.6, ' stroke-dasharray="8 2 2 2"'),
         ("faiss-ivfpq", "FAISS IVF-PQ", "cross", 6, 1.6, ' stroke-dasharray="1 3"')]


def pareto(points):
    """ANN-Benchmarks front: walking from high recall down, keep points faster than every higher-recall point."""
    out, best = [], -1.0
    for p in sorted(points, key=lambda p: (-p[0], -p[1])):
        if p[1] > best:
            out.append(p)
            best = p[1]
    return sorted(out)


def fig_frontier(D: Data, layout: str) -> str:
    D.use("exp3-frontier")
    sm = layout == "sm"
    W = 330 if sm else 720
    H = 760 if sm else 470
    f = Fig("exp3-frontier", layout, W, H,
            "Accuracy against speed for six search methods on two benchmarks",
            "Two panels, SIFT and GloVe. Recall at 10 on the horizontal axis, queries per second on a logarithmic "
            "vertical axis. The four conventional methods sit two to three orders of magnitude above FlyHash at every "
            "accuracy; DenseFly's line stops at 0.525 (SIFT) and 0.420 (GloVe).")
    y = legend(f, 12, 20, [(s, f"f{c}" if a in ("flyhash", "densefly") else f"h{c}", lab, dash != "" or None)
                          for a, lab, s, c, _, dash in ALGOS], W - 24, gap=14)
    ph = 230 if sm else 300
    boxes = ([(52, y + 22, W - 68), (52, y + 22 + ph + 84, W - 68)] if sm
             else [(64, y + 22, 280), (64 + 280 + 76, y + 22, 280)])
    for (ds, dname), (bx, by, bw) in zip(SETS, boxes):
        f.text(bx - 40, by - 10, dname, "m", "t1")
        sx = Scale(0, 1, bx, bx + bw)
        sy = Scale(10, 100000, by + ph, by, log=True)
        f.group(sx=sx.spec(), sy=sy.spec())
        y_ticks(f, sy, bx - 6, (10, 100, 1000, 10000, 100000), lambda v: f"{int(v):,}", grid=(bx, bx + bw))
        x_ticks(f, sx, by + ph + 16, (0, 0.25, 0.5, 0.75, 1), lambda v: f2(v), grid=(by, by + ph))
        f.line(sx(0.9), by, sx(0.9), by + ph, "ref")
        f.text(sx(0.9) - 4, by + 12, "90% accuracy", "s", "tk", "end")
        fronts = {k: v for k, v in D.get(f"json:{B2S}#/{ds}/algorithms/*/front")}
        for a, lab, shape, ci, sw, dash in ALGOS:
            base = f"csv:{EXPORT}#dataset={ds},algorithm={a}|"
            rec, qps, par = D.get(base + "k-nn"), D.get(base + "qps"), D.get(base + "parameters")
            pts = [(float(r[1]), float(q[1]), p[1], r[0], q[0]) for r, q, p in zip(rec, qps, par)]
            front = pareto(pts)
            ref = fronts[f"json:{B2S}#/{ds}/algorithms/{a}/front"]
            if [[p[0], p[1]] for p in front] != ref:
                raise SystemExit(f"frontier mismatch with the analysis' own front: {ds} {a}")
            front = [p for p in front if p[1] >= 10]
            fly = a in ("flyhash", "densefly")
            d = " L".join(f"{f2(sx(r))} {f2(sy(q))}" for r, q, *_ in front)
            f.path("M" + d, f"s{ci}", f' stroke-width="{sw}"{dash}')
            for r, q, p, rsel, qsel in front:
                f.marker(shape, sx(r), sy(q), 3.6 if fly else 3, f"f{ci}" if fly else f"h{ci}",
                         extra=' stroke-width="1.3"', enc=[enc("cx", "x", r, rsel), enc("cy", "y", q, qsel)],
                         title=f"{lab} · {p} · recall {r:.3f} · {q:,.0f} queries/s")
            if a == "densefly":
                r, q, p, rsel, qsel = front[-1]
                msel = f"json:{B2S}#/{ds}/algorithms/densefly/max_recall"
                mr = D.get(msel)
                if abs(mr - r) > 1e-12:
                    raise SystemExit("densefly end point is not its maximum recall")
                f.line(sx(r) + 6, sy(q), sx(r) + 16, sy(q), "s5", ' stroke-width="1.6"')
                f.text(sx(r) + 20, sy(q) - 2, "DenseFly stops:", "s", "t1")
                f.text(sx(r) + 20, sy(q) - 2 + f.fs["s"] * 1.3, f"best accuracy {mr:.3f}", "s", "t1",
                       enc=[enc("text", "", mr, msel)])
            if a == "flyhash":
                r, q, *_ = front[-1]
                f.text(sx(r) - 14, sy(q) - 20, "FlyHash", "s", "t1", "end")
        f.end()
        f.text(bx + bw / 2, by + ph + 34, "accuracy (recall at 10)", "s", "t3", "middle")
    f.wrap(12, H - 24 if sm else H - 8, "Vertical axis: questions answered per second, logarithmic (each step is "
           "10× faster).", W - 24, "s", "t3")
    return f.svg()


def fig_touched(D: Data, layout: str) -> str:
    D.use("exp3-candidates-touched")
    sm = layout == "sm"
    W = 330 if sm else 720
    H = 670 if sm else 380
    f = Fig("exp3-candidates-touched", layout, W, H,
            "FlyHash: list entries examined per question, against the size of the whole database",
            "Bars, one per FlyHash setting, sorted. Settings that reach 90% accuracy are highlighted; every one of "
            "them examines more list entries per question than the database holds items.")
    y = legend(f, 12, 20, [("square", "f1", "FlyHash setting that reaches 90% accuracy", None),
                          ("square", "f6", "Other FlyHash setting", None)], W - 24)
    ph = 210 if sm else 240
    boxes = ([(58, y + 30, W - 70), (58, y + 30 + ph + 70, W - 70)] if sm
             else [(70, y + 30, 270), (70 + 270 + 84, y + 30, 270)])
    for (ds, dname), (bx, by, bw) in zip(SETS, boxes):
        f.text(bx - 46, by - 14, dname, "m", "t1")
        nsel = f"md:{PRE3}#**Benchmark data:**|Dataset=`{ds}`|Train × dim"
        n = md_num(D.get(nsel), 0)
        names = D.get(f"csv:{TOUCH}#dataset={ds}|name")
        touched = D.get(f"csv:{TOUCH}#dataset={ds}|candidates_touched_per_query")
        par = D.get(f"csv:{EXPORT}#dataset={ds},algorithm=flyhash|parameters")
        rec = D.get(f"csv:{EXPORT}#dataset={ds},algorithm=flyhash|k-nn")
        recall = {p[1]: (float(r[1]), r[0]) for p, r in zip(par, rec)}
        bars = sorted(((float(t[1]), t[0], nm[1]) + recall[nm[1]] for nm, t in zip(names, touched)),
                      key=lambda b: (b[0], b[2]))
        if len(bars) != len(recall):
            raise SystemExit("touched / export join incomplete")
        sy = Scale(0, 6e6, by + ph, by)
        f.group(sy=sy.spec())
        y_ticks(f, sy, bx - 6, (0, 2e6, 4e6, 6e6), lambda v: f"{v / 1e6:.0f}M" if v else "0", grid=(bx, bx + bw))
        step = bw / len(bars)
        accurate = [b for b in bars if b[3] >= 0.9]
        for i, (t, tsel, name, r, rsel) in enumerate(bars):
            cls = "f1" if r >= 0.9 else "f6"
            f.rect(bx + i * step + 0.5, sy(t), step - 1, sy(0) - sy(t), cls,
                   enc=[enc("y", "y", t, tsel)],
                   title=f"{name}: {t:,.0f} entries per question, accuracy {r:.3f}")
        f.line(bx, sy(n), bx + bw, sy(n), "zero", ' stroke-width="1.8" stroke-dasharray="6 3"',
               enc=[enc("y1", "y", n, nsel + "@0")])
        lab = f"database: {n:,.0f} items"
        f.rect(bx + 2, sy(n) - 20, len(lab) * f.fs["s"] * 0.55 + 6, 16, "bg", ' fill-opacity="0.88"')
        f.text(bx + 5, sy(n) - 8, lab, "s", "t1", enc=[enc("text", "", n, nsel + "@0")])
        if not all(b[0] > n for b in accurate):
            raise SystemExit("an accurate FlyHash setting touches fewer entries than the database size")
        f.end()
        f.text(bx + bw / 2, by + ph + 16, f"{len(bars)} settings, fewest to most entries examined", "s", "t3",
               "middle", enc=[enc("text", "", len(bars), f"csv:{TOUCH}#dataset={ds}|name", "len")])
    f.text(12, H - 8, "entries examined per question (M = million)", "s", "t3")
    return f.svg()


A_JS = "fly_retrieval/reports/trackA_summary.json"
DS_A = [("odors", "Fly odours", "circle", 6), ("sift", "SIFT images", "square", 2), ("mnist", "MNIST digits", "diamond", 3),
        ("random", "Random data", "triangle", 4), ("nytimes", "NYTimes news text", "down", 5)]


METHOD_NAMES = {"FBF": "Fly Bloom filter", "GBF": "Dense-projection control", "LSBF": "Locality-sensitive Bloom filter",
                "BF": "Plain Bloom filter", "SimHash": "SimHash fingerprints", "MinHash": "MinHash", "CMS": "Count-min sketch"}


def fig_novelty(D: Data, layout: str) -> str:
    D.use("exp3-novelty-filter")
    sm = layout == "sm"
    W = 330 if sm else 720
    H = 730 if sm else 610
    get = lambda k: D.get(f"json:{A_JS}#/cells/*/{k}")
    ds, bb, de, dci = get("dataset"), get("B"), get("delta"), get("delta_ci")
    fnr = D.get(f"json:{A_JS}#/cells/*/methods/*/fnr_at_fpr_1pct")
    budgets = [3, 10, 30, 100]
    f = Fig("exp3-novelty-filter", layout, W, H,
            "The fly memory filter against the best conventional method, by memory budget",
            "Top: the fly Bloom filter's score minus the best conventional method's, per dataset, at 3, 10, 30 and "
            "100 bits per stored item; mostly above zero at 3 and 10 bits and mostly below at 30 and 100. Bottom: the "
            "share of familiar items each method misses when false alarms are held to 1%; at 10 bits and below no "
            "method misses fewer than 83.9%.")
    y = legend(f, 12, 20, [(s, f"f{c}" if c != 6 else "f6", lab, None) for _, lab, s, c in DS_A], W - 24, gap=12)
    bx0, bx1 = (44, W - 12) if sm else (70, W - 24)
    cat = lambda i: bx0 + (i + 0.5) * (bx1 - bx0) / 4
    # top panel
    t0 = y + 30
    th = 220 if sm else 210
    f.text(12, t0 - 12, "1 · Fly filter minus best conventional" if sm else
           "1 · Fly filter's score minus the best conventional method's", "m", "t1")
    sy = Scale(-0.5, 0.5, t0 + th, t0)
    f.group(sy=sy.spec())
    f.rect(bx0, t0, bx1 - bx0, sy(0) - t0, "good", ' fill-opacity="0.7"')
    y_ticks(f, sy, bx0 - 6, (-0.5, -0.25, 0, 0.25, 0.5), lambda v: signed(v, 2) if v else "0", grid=(bx0, bx1))
    f.line(bx0, sy(0), bx1, sy(0), "zero")
    f.text(bx0 + 4, t0 + 14, "fly filter better", "s", "t3")
    f.text(bx0 + 4, t0 + th - 6, "conventional better", "s", "t3")
    col_w = (bx1 - bx0) / 4
    for (dsel, dname), (bsel, b), (esel, e), (csel, ci) in zip(ds, bb, de, dci):
        j = budgets.index(b)
        k = [d[0] for d in DS_A].index(dname)
        shape, c = DS_A[k][2], DS_A[k][3]
        x = cat(j) + (k - 2) * col_w * 0.15
        rel = reliable(ci)
        f.line(x, sy(ci[0]), x, sy(ci[1]), f"s{c}", ' stroke-width="1.6"',
               enc=[enc("y1", "y", ci[0], csel + "/0"), enc("y2", "y", ci[1], csel + "/1")])
        f.marker(shape, x, sy(e), 4.4, f"f{c}" if rel else f"h{c}", extra=' stroke-width="1.6"',
                 enc=[enc("cy", "y", e, esel)], title=f"{DS_A[k][1]}, {b} bits: {signed(e, 3)}")
    f.end()
    f.wrap(12, t0 + th + 26, "Filled: reliably different from zero. Hollow: the range includes zero.", W - 24, "s", "t3")
    # bottom panel
    b0 = t0 + th + (72 if not sm else 106)
    bh = H - b0 - 46
    f.text(12, b0 - (12 if not sm else 48), "2 · Familiar items missed when false alarms are held to 1%"
           if not sm else "2 · Familiar items missed, false alarms at 1%", "m", "t1")
    sy2 = Scale(0, 1, b0 + bh, b0)
    f.group(sy=sy2.spec())
    y_ticks(f, sy2, bx0 - 6, (0, 0.5, 1), lambda v: f"{round(v * 100)}%", grid=(bx0, bx1))
    by_b = {b: [] for b in budgets}
    for sel, v in fnr:
        idx = int(sel.split("/cells/")[1].split("/")[0])
        b, dname = bb[idx][1], ds[idx][1]
        meth = sel.split("/methods/")[1].split("/")[0]
        by_b[b].append((v, sel, meth, dname))
    for j, b in enumerate(budgets):
        items = sorted(by_b[b], key=lambda t: (t[2] != "FBF", t[3], t[2]))
        for i, (v, sel, meth, dname) in enumerate(items):
            k = [d[0] for d in DS_A].index(dname)
            jitter = ((i * 7) % 15 - 7) / 7 * col_w * 0.32
            fly = meth == "FBF"
            f.marker("circle", cat(j) + jitter, sy2(v), 4.2 if fly else 3, "f1" if fly else "h6",
                     extra=' stroke-width="1.2"' + ('' if fly else ' stroke-opacity="0.8"'),
                     enc=[enc("cy", "y", v, sel)], title=f"{METHOD_NAMES[meth]} on {DS_A[k][1]}, {b} bits: misses {pct(v)}")
        lo = min(items)
        if b <= 10:
            f.text(cat(j), sy2(lo[0]) + 16, f"best: {pct(lo[0])}", "s", "t1", "middle",
                   enc=[enc("text", "", lo[0], lo[1], "x100")])
    f.end()
    for j, b in enumerate(budgets):
        f.text(cat(j), H - 26, f"{b} bits", "s", "tk", "middle")
    f.text((bx0 + bx1) / 2, H - 8, "memory per stored item (applies to both panels)", "s", "t3", "middle")
    ky = b0 - 12 if not sm else b0 - 30
    kx = bx1 - (170 if not sm else 150)
    f.marker("circle", kx, ky - 4, 4.2, "f1")
    f.text(kx + 8, ky, "fly filter", "s")
    f.marker("circle", kx + 72, ky - 4, 3, "h6", extra=' stroke-width="1.2"')
    f.text(kx + 80, ky, "the other six", "s")
    return f.svg()


B_MD = "fly_retrieval/reports/exp3_trackB_connectome.md"
ODOUR = "Odours: BIO against each null"
LEVELS = [("N0", "Random wiring"), ("N1", "Each glomerulus and cell keeps its link count"),
          ("N3", "…and the links between cell classes"), ("NQ", "…and how inputs converge")]


def fig_imputation(D: Data, layout: str) -> str:
    D.use("exp3-null-ladder-imputation")
    sm = layout == "sm"
    W = 330 if sm else 720
    lab_w = 0 if sm else 250
    H = 790 if sm else 520
    f = Fig("exp3-null-ladder-imputation", layout, W, H,
            "Real wiring against four kinds of scrambled wiring, with missing odour data filled two ways",
            "Two panels, left and right hemisphere. For each scrambled control, the real wiring's score difference "
            "with missing data set to zero and with missing data filled with averages. With zeros, no comparison "
            "reaches the +2.5% benefit margin; with averages, the left hemisphere beats the standard shuffle by 3.38%.")
    y = legend(f, 12, 20, [("circle", "f1", "Missing odour data set to zero (main analysis)", None),
                          ("square", "f2", "Missing data filled with averages", None)], W - 24)
    x0, x1 = (16, W - 16) if sm else (lab_w + 24, W - 30)
    sx = Scale(-0.07, 0.06, x0, x1)
    rh = 58 if sm else 40
    py = y + 24
    for m, hname in (("w5_L", "Left hemisphere"), ("w5_R", "Right hemisphere")):
        f.text(12, py, hname, "m", "t1")
        top = py + 14
        f.group(sx=sx.spec())
        bot = top + len(LEVELS) * rh
        f.rect(sx(0.025), top, x1 - sx(0.025), bot - top, "good", ' fill-opacity="0.9"')
        for v in (-0.06, -0.04, -0.02, 0, 0.02, 0.04, 0.06):
            f.line(sx(v), top, sx(v), bot, "zero" if v == 0 else "gr")
        f.line(sx(0.025), top, sx(0.025), bot, "ref")
        yy = top
        for lv, lname in LEVELS:
            if sm:
                f.text(x0, yy + 13, lname, "s", "")
                cy0 = yy + 26
            else:
                f.text(lab_w + 16, yy + rh / 2 + 4, lname, "s", "", "end")
                cy0 = yy + rh / 2 - 7
            for k, (col, shape, ci) in enumerate((("Δ zero-filled [95% CI]", "circle", 1),
                                                  ("Δ mean-imputed [95% CI]", "square", 2))):
                sel = f"md:{B_MD}#{ODOUR}|matrix={m},level={lv}|{col}"
                cell = D.get(sel)
                v, lo, hi = (md_num(cell, i) / 100 for i in range(3))
                cy = cy0 + k * 14
                f.line(sx(lo), cy, sx(hi), cy, f"s{ci}", ' stroke-width="1.8"',
                       enc=[enc("x1", "x", lo, sel + "@1", "/100"), enc("x2", "x", hi, sel + "@2", "/100")])
                f.marker(shape, sx(v), cy, 4.2, f"f{ci}", enc=[enc("cx", "x", v, sel + "@0", "/100")],
                         title=f"{lname}: {cell}")
                if m == "w5_L" and lv == "N1" and k == 1:
                    f.text(sx(hi) + 6, cy + 4, f"{signed(v * 100, 2)}%", "s", "t1",
                           enc=[enc("text", "", v * 100, sel + "@0")])
            yy += rh
        f.end()
        py = bot + 30
    x_ticks(f, sx, py - 10, (-0.06, -0.03, 0, 0.03, 0.06), lambda v: f"{signed(v * 100, 0)}%" if v else "0")
    f.text((x0 + x1) / 2, py + 8, "real wiring's score compared with the scrambled version", "s", "t3", "middle")
    f.wrap(12, py + 28, "Shaded area right of the dashed line: a benefit of at least +2.5%, the size set in advance as "
                        "worth caring about.", W - 24, "s", "t3")
    return f.svg()


C_JS = "fly_retrieval/reports/trackC_summary.json"


def fig_skew(D: Data, layout: str) -> str:
    D.use("exp3-skew")
    sm = layout == "sm"
    W = 330 if sm else 720
    H = 640 if sm else 400
    ses_s = f"json:{C_JS}#/sesoi"
    sesoi = D.get(ses_s)
    f = Fig("exp3-skew", layout, W, H,
            "Real wiring against its shuffle as questions concentrate on a few odour channels",
            "Two panels, left and right hemisphere. Lines for questions concentrated on the channels the real wiring "
            "over-connects (matched) and on the opposite channels (mismatched). The prediction was that the matched "
            "line would rise above the +2.5% margin. In the left hemisphere it falls to -7.17%; in the right it rises "
            "to +1.62%, below the margin and below the mismatched line.")
    y = legend(f, 12, 20, [("circle", "f1", "Questions on the over-connected channels (matched)", False),
                          ("square", "h2", "Questions on the opposite channels (mismatched)", True),
                          (None, "s6", "What the idea predicted", True)], W - 24)
    ph = 200 if sm else 240
    boxes = ([(48, y + 22, W - 72), (48, y + 22 + ph + 80, W - 72)] if sm
             else [(56, y + 22, 280), (56 + 280 + 70, y + 22, 280)])
    betas = ["0.0", "0.5", "1.0", "1.5", "2.0"]
    for (h, hname), (bx, by, bw) in zip((("L", "Left hemisphere"), ("R", "Right hemisphere")), boxes):
        f.text(bx - 36, by - 10, hname, "m", "t1")
        sx = Scale(0, 2, bx, bx + bw)
        sy = Scale(-0.08, 0.04, by + ph, by)
        f.group(sx=sx.spec(), sy=sy.spec())
        f.rect(bx, by, bw, sy(sesoi) - by, "good", ' fill-opacity="0.9"')
        y_ticks(f, sy, bx - 6, (-0.06, -0.03, 0, 0.03), lambda v: f"{signed(v * 100, 0)}%" if v else "0",
                grid=(bx, bx + bw))
        f.line(bx, sy(0), bx + bw, sy(0), "zero")
        f.line(bx, sy(sesoi), bx + bw, sy(sesoi), "ref", enc=[enc("y1", "y", sesoi, ses_s)])
        # predicted direction: a faint guide, not data
        f.path(f"M{f2(sx(0))} {f2(sy(0) - 2)} Q{f2(sx(1.3))} {f2(sy(0.005))} {f2(sx(2))} {f2(sy(0.036))}", "pred")
        f.text(sx(2) - 4, sy(0.036) - 6, "predicted", "s", "t3", "end")
        f.text(bx + 4, sy(sesoi) - 5, "+2.5% needed", "s", "t3")
        for o, shape, ci, dash in (("matched", "circle", 1, ""), ("mismatched", "square", 2, ' stroke-dasharray="5 3"')):
            pts = []
            for b in betas:
                base = f"json:{C_JS}#/hemispheres/{h}/cells/{b}|{o}|N1/"
                pts.append((float(b), D.get(base + "delta"), base + "delta", D.get(base + "ci"), base + "ci"))
            f.path("M" + " L".join(f"{f2(sx(b))} {f2(sy(d))}" for b, d, *_ in pts), f"s{ci}", f' stroke-width="2"{dash}')
            for b, d, dsel, ci_, csel in pts:
                f.line(sx(b), sy(ci_[0]), sx(b), sy(ci_[1]), f"s{ci}", ' stroke-width="1.4"',
                       enc=[enc("y1", "y", ci_[0], csel + "/0"), enc("y2", "y", ci_[1], csel + "/1")])
                f.marker(shape, sx(b), sy(d), 4.2, f"f{ci}" if o == "matched" else f"h{ci}", extra=' stroke-width="1.6"',
                         enc=[enc("cy", "y", d, dsel)], title=f"{hname}, {o}, concentration {b}: {signed(d * 100, 2)}%")
            if o == "matched":
                low = min(pts, key=lambda p: p[1]) if h == "L" else pts[-1]
                f.text(sx(low[0]) + (6 if low[0] < 2 else -6), sy(low[1]) + 16, f"{signed(low[1] * 100, 2)}%", "s",
                       "t1", "start" if low[0] < 2 else "end", enc=[enc("text", "", low[1], low[2], "x100")])
        f.end()
        x_ticks(f, sx, by + ph + 16, (0, 1, 2), lambda v: {0: "even", 1: "moderate", 2: "strong"}[int(v)])
        f.text(bx + bw / 2, by + ph + 34, "how concentrated the questions are", "s", "t3", "middle")
    f.text(12, H - 8, "Shaded band: the +2.5% gain the idea needed to show.", "s", "t3")
    return f.svg()


VERDICTS = [
    ("Robot steering · Experiment 1", "Does the fly's steering circuit help a simulated robot follow a target better "
     "than a direct connection?",
     "No clear help.", "Its loops add a short memory that trades fewer obstacle hits for more wall hits; "
     "rewired copies do just as well."),
    ("Learning rules · Experiment 2", "Can the circuit be trained with forward-only learning steadily "
     "enough to compare methods?",
     "Stopped before the main test.", "Results swung so much between random starts that the planned study could "
     "not have given a clear answer."),
    ("Memory filter · Experiment 3", "Does the fly-inspired familiarity filter beat the methods used in practice?",
     "Only where nothing works.", "It wins at the tiniest memory budgets, where every method misses most familiar "
     "items; with more memory a simple fingerprint wins."),
    ("Similarity search · Experiment 3", "Does the fly's real wiring, or a fly-inspired index, help find similar items?",
     "No.", "The real wiring is no better than scrambled wiring, and fly-inspired search runs at about one two-hundredth "
     "of the speed of the best conventional index."),
]


def fig_verdicts(D: Data, layout: str) -> str:
    D.use("verdicts")
    for sel in D.fig["fields"]:
        D.get(sel)  # every verdict field must resolve; the text below paraphrases them
    sm = layout == "sm"
    W = 330 if sm else 720
    cw = W - 24 if sm else (W - 36) / 2
    ch = 196 if sm else 178
    H = (4 * (ch + 12) if sm else 2 * (ch + 12)) + 8
    f = Fig("verdicts", layout, W, H, "The four verdicts",
            "Four cards, one per question: what was asked, the short answer and one sentence on what was found.")
    for i, (head, q, ans, found) in enumerate(VERDICTS):
        x = 12 + (0 if sm else (i % 2) * (cw + 12))
        y = 8 + (i if sm else i // 2) * (ch + 12)
        f.rect(x, y, cw, ch, "band", ' rx="4"')
        f.rect(x, y, 4, ch, "f1")
        f.text(x + 16, y + 24, head.upper(), "s", "t3 mono")
        yy = f.wrap(x + 16, y + 46, q, cw - 30, "s", "")
        yy = f.wrap(x + 16, yy + 14, ans, cw - 30, "l", "t1")
        f.wrap(x + 16, yy + 4, found, cw - 30, "s", "")
    return f.svg()


FIGS = [("exp1-memory-dissociation", fig_memory), ("exp1-loops-not-wiring", fig_loops),
        ("exp1-why-stopped", fig_stopped), ("exp1-not-inert", fig_inert), ("exp1-learning-curves", fig_curves),
        ("exp1-activity", fig_activity), ("exp2-variability-stop", fig_exp2), ("exp3-frontier", fig_frontier),
        ("exp3-candidates-touched", fig_touched), ("exp3-novelty-filter", fig_novelty),
        ("exp3-null-ladder-imputation", fig_imputation), ("exp3-skew", fig_skew), ("verdicts", fig_verdicts)]


def build(out: Path, variant_dir: Path | None = None) -> list[Path]:
    D = Data(json.loads(MANIFEST.read_text()))
    if {f for f, _ in FIGS} != set(D.figs):
        raise SystemExit("figure list and manifest disagree")
    out.mkdir(parents=True, exist_ok=True)
    written = []
    for fid, fn in FIGS:
        for layout, suffix in (("lg", ""), ("sm", "-sm")):
            p = out / f"{fid}{suffix}.svg"
            p.write_text(fn(D, layout), encoding="utf-8")
            written.append(p)
    if variant_dir:
        variant_dir.mkdir(parents=True, exist_ok=True)
        (variant_dir / "exp1-memory-dissociation-bars.svg").write_text(fig_memory_bars(D, "lg"), encoding="utf-8")
    return written


def fig_memory_bars(D: Data, layout: str) -> str:
    """The grouped-bar alternative to the slope chart, kept for the side-by-side comparison only."""
    D.use("exp1-memory-dissociation")
    W, H = 720, 360
    f = Fig("exp1-memory-dissociation", layout, W, H, "bars variant", "bars variant")
    legend(f, 12, 20, [("square", "f1", "Fly circuit", None), ("square", "f2", "Direct connection", None)], W)
    sy = Scale(0, 0.3, 300, 60)
    for p, (key, g, cname) in enumerate(COND):
        bx = 60 + p * 330
        f.text(bx, 50, cname, "m", "t1")
        for j, e in enumerate(("post_collision", "wall_collision")):
            for k, a in enumerate(("bio", "bypass")):
                v = D.get(f"json:{g}#/descriptives/{a}/{e}")
                x = bx + j * 140 + k * 46
                f.rect(x, sy(v), 40, sy(0) - sy(v), "f1" if a == "bio" else "f2")
                f.text(x + 20, sy(v) - 5, pct(v), "s", "t1", "middle")
            f.text(bx + j * 140 + 43, 318, "posts" if j == 0 else "walls", "s", "", "middle")
    return f.svg()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(OUT))
    ap.add_argument("--variant-dir", default=None)
    a = ap.parse_args()
    files = build(Path(a.out), Path(a.variant_dir) if a.variant_dir else None)
    print(f"{len(files)} SVG files -> {a.out}")


if __name__ == "__main__":
    main()
