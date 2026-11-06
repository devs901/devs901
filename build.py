"""Regenerates every SVG in ./assets  ->  python build.py
Self-contained SVGs (system fonts only, content always visible; animation is decoration)."""
import textwrap, os, sys, subprocess, math
from xml.sax.saxutils import escape as E

BG, INK, DIM, RED, GOLD, LINE, GREEN = "#0a0908", "#efe6d2", "#9a917c", "#e0442b", "#e8b04a", "#2a2622", "#52d68a"
DISP = "Impact,'Haettenschweiler','Arial Narrow Bold','Arial Black',sans-serif"
SERIF = "Georgia,'Times New Roman',serif"
MONO = "'Courier New',Consolas,monospace"
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.environ.get("ASSETS_OUT") or os.path.join(HERE, "assets")

# ------------------------------------------------------------------ colour themes
# The kit is drawn in the "cinematic" palette; every other theme is a straight hex swap applied when a file is written.
BASE = {"bg": "#0a0908", "ink": "#efe6d2", "dim": "#9a917c", "accent": "#e0442b", "gold": "#e8b04a", "line": "#2a2622",
        "ok": "#52d68a", "panel": "#0e0c0a", "panel2": "#14110e", "arrow": "#4a4237", "mute": "#6b6354", "aberr": "#5ac8ff"}
THEMES = {
    "cinematic": dict(BASE),
    "jarvis":  {"bg": "#03060c", "ink": "#e6f7ff", "dim": "#8aa8bd", "accent": "#ff7a29", "gold": "#2ee6ff", "line": "#12283a",
                "ok": "#3dffa0", "panel": "#06101a", "panel2": "#091827", "arrow": "#2b4a63", "mute": "#4f6f86", "aberr": "#8b6cff"},
    "neon":    {"bg": "#070910", "ink": "#e8eefc", "dim": "#8893ad", "accent": "#ff3d81", "gold": "#22d3ee", "line": "#1d2438",
                "ok": "#4ade80", "panel": "#0b0f1b", "panel2": "#10162a", "arrow": "#3b4766", "mute": "#5b6785", "aberr": "#a78bfa"},
    "royal":   {"bg": "#0a0712", "ink": "#f3ecff", "dim": "#a196ba", "accent": "#a78bfa", "gold": "#fbbf24", "line": "#2a2140",
                "ok": "#5eead4", "panel": "#0f0a1a", "panel2": "#150f24", "arrow": "#4b4068", "mute": "#6e6490", "aberr": "#f472b6"},
    "emerald": {"bg": "#060b0a", "ink": "#e8f4ef", "dim": "#8aa399", "accent": "#2dd4bf", "gold": "#f2c14e", "line": "#1a2b27",
                "ok": "#86efac", "panel": "#08110f", "panel2": "#0c1815", "arrow": "#3a5650", "mute": "#5f7a71", "aberr": "#38bdf8"},
}
def skin(text):
    th = THEMES.get(os.environ.get("THEME", "jarvis"), THEMES["jarvis"])
    for k, base in BASE.items():
        if th[k] != base: text = text.replace(base, th[k])
    return text

def svg(name, w, h, body, title, bg=True):
    s = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{E(title)}">'
         f'<title>{E(title)}</title>'
         f'<defs><radialGradient id="glow" cx="0.2" cy="0" r="0.9"><stop offset="0" stop-color="{GOLD}" stop-opacity=".16"/><stop offset="1" stop-color="{GOLD}" stop-opacity="0"/></radialGradient>'
         f'<radialGradient id="vig" cx="0.5" cy="0.5" r="0.75"><stop offset=".55" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".6"/></radialGradient></defs>'
         + (f'<rect width="{w}" height="{h}" rx="10" fill="{BG}"/>' if bg else "") + f'{body}</svg>')
    open(os.path.join(OUT, name), "w", encoding="utf-8").write(skin(s))

def t(x, y, s, size, fill, font=MONO, anchor="start", ls=0, weight="normal", style="normal", extra=""):
    return (f'<text x="{x}" y="{y}" font-family="{font}" font-size="{size}" fill="{fill}" text-anchor="{anchor}" '
            f'letter-spacing="{ls}" font-weight="{weight}" font-style="{style}" {extra}>{E(s)}</text>')

def chips(x, y, items, maxw, size=11.5, gap=8, fill=DIM):
    """flowing chips; returns (svg, bottom_y)"""
    out, cx, cy = [], x, y
    cw = size * 0.62
    for it in items:
        w = len(it) * cw + 22
        if cx + w > x + maxw: cx, cy = x, cy + 32
        out.append(f'<rect x="{cx}" y="{cy}" width="{w:.0f}" height="24" rx="3" fill="none" stroke="{LINE}" stroke-width="1.2"/>'
                   + t(cx + w / 2, cy + 16, it, size, fill, anchor="middle", ls=.5))
        cx += w + gap
    return "".join(out), cy + 24

# ------------------------------------------------------------------ header
def header():
    W, H = 1000, 400
    holes = lambda y: "".join(f'<rect x="{x}" y="{y}" width="16" height="10" rx="2" fill="#2a2622"/>' for x in range(-40, W + 60, 40))
    strip = lambda y, d: (f'<rect x="0" y="{y}" width="{W}" height="40" fill="#000"/>'
        f'<g><animateTransform attributeName="transform" type="translate" from="0 0" to="{d*-40} 0" dur="1.6s" repeatCount="indefinite"/>{holes(y+6)}{holes(y+24)}</g>')
    roles = ["PYTHON DEVELOPER", "SQL & DATABASE DEVELOPER", "DATA ANALYST", "ASPIRING DATA ENGINEER"]
    r = ""
    for i, role in enumerate(roles):
        a, b, c, d = i * .25, i * .25 + .02, i * .25 + .23, i * .25 + .25
        kt = [0, a, b, c, d, 1] if i else [0, c, d, 1]
        vals = [0, 0, 1, 1, 0, 0] if i else [1, 1, 0, 0]
        if i == 0: kt, vals = [0, .23, .25, .98, 1], [1, 1, 0, 0, 1]
        else: kt, vals = [0, a, b, c, d, 1], [0, 0, 1, 1, 0, 0]
        r += (f'<g opacity="{1 if i==0 else 0}">'
              f'<animate attributeName="opacity" values="{";".join(map(str,vals))}" keyTimes="{";".join(f"{k:g}" for k in kt)}" dur="12s" repeatCount="indefinite"/>'
              + t(500, 268, role, 19, GOLD, anchor="middle", ls=7) + '</g>')
    body = (f'<rect width="{W}" height="{H}" rx="10" fill="url(#glow)"/>'
        '<g opacity=".5"><rect x="-300" y="0" width="240" height="400" fill="#e8b04a" opacity=".07" transform="skewX(-18)">'
        f'<animate attributeName="x" from="-400" to="1400" dur="11s" repeatCount="indefinite"/></rect></g>'
        + strip(0, 1) + strip(360, -1)
        + f'<circle cx="40" cy="74" r="5" fill="{RED}"><animate attributeName="opacity" values="1;.15;1" dur="1.4s" repeatCount="indefinite"/></circle>'
        + t(54, 78, "REC", 11, DIM, ls=3) + t(960, 78, "SCENE 01 / 06", 11, DIM, anchor="end", ls=3)
        + t(500, 130, "A PYTHON & DATA STORY", 13, RED, anchor="middle", ls=8)
        # chromatic-aberration name
        + t(496, 222, "DEVENDRA RATHOD", 98, RED, DISP, "middle", extra='opacity=".55" textLength="780" lengthAdjust="spacingAndGlyphs"')
        + t(504, 222, "DEVENDRA RATHOD", 98, "#5ac8ff", DISP, "middle", extra='opacity=".28" textLength="780" lengthAdjust="spacingAndGlyphs"')
        + t(500, 222, "DEVENDRA RATHOD", 98, INK, DISP, "middle", extra='textLength="780" lengthAdjust="spacingAndGlyphs"')
        + r
        + t(500, 302, "AI & Data Science graduate  ·  B.E., PVG College of Engineering, SPPU  ·  2026", 16, DIM, SERIF, "middle", style="italic")
        + f'<rect x="330" y="316" width="340" height="30" rx="15" fill="none" stroke="{GREEN}" stroke-opacity=".6"/>'
        + f'<circle cx="354" cy="331" r="4.5" fill="{GREEN}"><animate attributeName="opacity" values="1;.2;1" dur="1.8s" repeatCount="indefinite"/></circle>'
        + t(370, 335, "OPEN TO WORK · ENTRY-LEVEL ROLES", 11, GREEN, ls=1.5)
        + f'<rect width="{W}" height="{H}" rx="10" fill="url(#vig)"/>')
    svg("header.svg", W, H, body, "Devendra Rathod: Python, SQL and data analytics")

# ------------------------------------------------------------------ section heading
def heading(name, kicker, title, sub=""):
    H = 138 if sub else 112
    body = (t(500, 30, kicker.upper(), 12, RED, anchor="middle", ls=7)
        + t(500, 86, title.upper(), 54, INK, DISP, "middle", ls=3)
        + (t(500, 114, sub, 16, DIM, SERIF, "middle", style="italic") if sub else "")
        + f'<line x1="400" y1="{H-8}" x2="600" y2="{H-8}" stroke="{LINE}"/><rect x="480" y="{H-10}" width="40" height="3" fill="{RED}"/>')
    svg(name, 1000, H, body, title, bg=False)

# ------------------------------------------------------------------ numbers
def numbers():
    W, H = 1000, 140
    items = [("3", "INTERNSHIPS"), ("3", "PROJECTS"), ("6", "CREDENTIALS"), ("126", "TRAINING HRS")]
    b = f'<rect width="{W}" height="{H}" rx="10" fill="url(#glow)"/>'
    for i, (n, l) in enumerate(items):
        cx = 125 + i * 250
        b += t(cx, 82, n, 66, INK, DISP, "middle", extra='textLength="%d" lengthAdjust="spacingAndGlyphs"' % (len(n) * 36)) + t(cx, 112, l, 11, DIM, anchor="middle", ls=4)
        if i: b += f'<line x1="{cx-125}" y1="34" x2="{cx-125}" y2="108" stroke="{LINE}"/>'
    svg("numbers.svg", W, H, b + f'<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="10" fill="none" stroke="{LINE}"/>', "3 internships, 3 projects, 6 credentials, 126 hours of training")

# ------------------------------------------------------------------ journey
def journey():
    W = 1000
    rows = [("JUN – AUG 2025", "Data Analysis Intern", "Talent Battle", ["Cleaned structured datasets and performed EDA in Python to prepare analysis outputs that supported business insights."], GOLD),
            ("JAN – JUN 2026", "Software Engineer Intern", "XMEGA", ["Implemented features and tested and debugged code across the application.", "Investigated issues systematically and validated every change before completion."], GOLD),
            ("JUL – AUG 2026", "Python Programming Intern", "Oasis Infobyte", ["Built Python programs through hands-on tasks, applying core concepts, application logic and problem solving."], GOLD),
            ("AUG – OCT 2026", "JioFiber Associate", "Quess Corp Limited", ["Resolved customer and service issues for JioFiber operations by following defined processes and escalation procedures.", "Kept service records accurate and coordinated with internal teams for timely resolution."], GOLD),
            ("NOW", "Open To Work", "Entry-level roles", ["Python development, SQL / database development, data analytics and AI / data roles."], GREEN)]
    wrapped = [[(j == 0 and len(r[3]) > 1, ln) for d in r[3] for j, ln in enumerate(textwrap.wrap(d, 82))] for r in rows]
    y, ys = 26, []
    for w_ in wrapped:
        ys.append(y); y += 74 + 21 * len(w_)
    H = y - 6
    b = f'<line x1="250" y1="{ys[0]+10}" x2="250" y2="{ys[-1]+10}" stroke="{LINE}" stroke-width="2"/>'
    b += (f'<line x1="250" y1="{ys[0]+10}" x2="250" y2="{ys[0]+10}" stroke="{GOLD}" stroke-width="2"><animate attributeName="y2" values="{ys[0]+10};{ys[-1]+10};{ys[-1]+10}" keyTimes="0;.7;1" dur="9s" repeatCount="indefinite"/></line>'
          f'<circle cx="250" cy="{ys[0]+10}" r="3.5" fill="{INK}"><animate attributeName="cy" values="{ys[0]+10};{ys[-1]+10};{ys[-1]+10}" keyTimes="0;.7;1" dur="9s" repeatCount="indefinite"/></circle>')
    for i, ((d, role, co, _, col), lines) in enumerate(zip(rows, wrapped)):
        y = ys[i]
        b += t(222, y + 14, d, 12, col, anchor="end", ls=2)
        b += f'<circle cx="250" cy="{y+10}" r="6" fill="{col}"/>'
        if i == len(rows) - 1: b += f'<circle cx="250" cy="{y+10}" r="6" fill="none" stroke="{col}"><animate attributeName="r" values="6;18" dur="1.8s" repeatCount="indefinite"/><animate attributeName="opacity" values=".9;0" dur="1.8s" repeatCount="indefinite"/></circle>'
        b += t(284, y + 18, role, 30, INK, DISP, ls=1.5)
        b += t(284, y + 42, co, 18, GOLD if col == GOLD else GREEN, SERIF, style="italic")
        for j, (bul, ln) in enumerate(lines):
            if bul: b += t(284, y + 66 + j * 21, "▸", 15, GOLD, SERIF)
            b += t(302 if len(rows[i][3]) > 1 else 284, y + 66 + j * 21, ln, 15, DIM, SERIF)
    svg("journey.svg", W, H, b, "Experience: Talent Battle, XMEGA, Oasis Infobyte, JioFiber Associate at Quess Corp")

# ------------------------------------------------------------------ project cards
def card(name, num, kicker, title, bullets, tags, motif, label):
    W = 1000
    lines = [textwrap.wrap(x, 78) for x in bullets]
    y = 120
    b = ""
    for ls_ in lines:
        for j, ln in enumerate(ls_):
            if j == 0: b += t(44, y, "▸", 16, GOLD, SERIF)
            b += t(66, y, ln, 17, INK, SERIF); y += 24
        y += 6
    cs, bot = chips(44, y + 6, tags, 640)
    H = bot + 70
    b = (f'<rect width="{W}" height="{H}" rx="10" fill="url(#glow)"/>'
         f'<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="10" fill="none" stroke="{LINE}"/>'
         + t(930, 190, num, 190, INK, DISP, "middle", extra='opacity=".05"')
         + t(44, 40, kicker, 12, RED, ls=5) + t(44, 92, "THE BRIEF", 50, INK, DISP, ls=2)
         + b + cs + motif(H)
         + t(956, H - 22, label + " →", 12, GOLD, anchor="end", ls=3)
         + f'<path d="M1 28 V12 a11 11 0 0 1 11 -11 H28" fill="none" stroke="{GOLD}" stroke-width="2"/>'
         + f'<path d="M{W-1} {H-28} V{H-12} a11 11 0 0 1 -11 11 H{W-28}" fill="none" stroke="{GOLD}" stroke-width="2"/>')
    svg(name, W, H, b, title)

def m_network(H):
    pts = [(780, 70), (900, 100), (740, 150), (860, 160), (920, 45)]
    s = "".join(f'<line x1="830" y1="115" x2="{x}" y2="{y}" stroke="{GOLD}" stroke-opacity=".35" stroke-dasharray="3 4"><animate attributeName="stroke-dashoffset" from="0" to="-14" dur="1.2s" repeatCount="indefinite"/></line>' for x, y in pts)
    s += "".join(f'<circle cx="{x}" cy="{y}" r="6" fill="{RED if i%2 else GOLD}"/>' for i, (x, y) in enumerate(pts))
    return s + f'<circle cx="830" cy="115" r="22" fill="{RED}"/>' + t(830, 121, "AI", 16, INK, DISP, "middle", ls=1)
def m_bars(H):
    s = f'<rect x="740" y="50" width="200" height="130" rx="6" fill="none" stroke="{LINE}" stroke-width="1.5"/>'
    for i in range(3): s += f'<rect x="{752+i*62}" y="62" width="54" height="22" rx="3" fill="{LINE}"/>'
    for i, h in enumerate([30, 52, 38, 70, 46, 60]):
        s += f'<rect x="{756+i*30}" y="{170-h}" width="18" height="{h}" fill="{GOLD if i%2 else RED}"><animate attributeName="height" values="{h};{h*.6:.0f};{h}" dur="{2+i*.3:.1f}s" repeatCount="indefinite"/><animate attributeName="y" values="{170-h};{170-h*.6:.0f};{170-h}" dur="{2+i*.3:.1f}s" repeatCount="indefinite"/></rect>'
    return s
def m_donut(H):
    return (f'<circle cx="840" cy="115" r="50" fill="none" stroke="{LINE}" stroke-width="14"/>'
            f'<circle cx="840" cy="115" r="50" fill="none" stroke="{RED}" stroke-width="14" stroke-dasharray="120 400" transform="rotate(-90 840 115)"><animateTransform attributeName="transform" type="rotate" from="-90 840 115" to="270 840 115" dur="8s" repeatCount="indefinite"/></circle>'
            f'<circle cx="840" cy="115" r="50" fill="none" stroke="{GOLD}" stroke-width="14" stroke-dasharray="70 400" stroke-dashoffset="-130" transform="rotate(-90 840 115)"/>'
            + t(840, 120, "SPEND", 12, INK, anchor="middle", ls=3))

# ------------------------------------------------------------------ credentials
def credentials():
    W = 1000
    items = [("Microsoft Power BI", "SKILL COURSE · SELF LEARNING · OCT 2026", "Dashboards, data modelling and reporting in Power BI.", "ID  SC-446DD41B7B"),
             ("SQL Course", "SKILL COURSE · SELF LEARNING · OCT 2026", "Querying and shaping relational data with SQL.", "ID  SC-C3C0FBBF48"),
             ("Google Data Analytics", "PROFESSIONAL CERTIFICATE · COURSERA", "End-to-end analytics workflow: ask, prepare, process, analyze, share.", ""),
             ("AI Tools & ChatGPT Workshop", "BE10X · JUL 2026", "Hands-on workshop on using AI tools and ChatGPT productively.", ""),
             ("Campus Recruitment Training", "ETHNUS · JUN – JUL 2025", "126 hours of industry-focused technical training.", "ID  R5PQ8TWJ"),
             ("TCS iON NQT (IT)", "NATIONAL QUALIFIER TEST · JUN 2026", "Cognitive 74.59% · Quant & Reasoning 64.84% · Python 65.91%", "")]
    cw, ch, g = 316, 160, 26
    b = ""
    for i, (ti, me, de, cid) in enumerate(items):
        x, y = (i % 3) * (cw + g), (i // 3) * (ch + 18)
        b += (f'<rect x="{x+.5}" y="{y+.5}" width="{cw}" height="{ch}" rx="8" fill="#0e0c0a" stroke="{LINE}"/>'
              f'<rect x="{x+.5}" y="{y+.5}" width="3" height="{ch}" fill="{RED}"/>'
              + t(x + cw - 16, y + 26, "✓", 15, GREEN, anchor="end")
              + t(x + 22, y + 36, ti.upper(), 24, INK, DISP, ls=1, extra=f'textLength="{min(len(ti)*12.2, 255):.0f}" lengthAdjust="spacingAndGlyphs"')
              + t(x + 22, y + 60, me, 9.5, GOLD, ls=1))
        for j, ln in enumerate(textwrap.wrap(de, 38)): b += t(x + 22, y + 92 + j * 20, ln, 15, DIM, SERIF, style="italic")
        if cid: b += t(x + 22, y + ch - 14, cid, 10, GREEN, ls=2)
    svg("credentials.svg", W, 2 * ch + 18 + 2, b, "Six credentials: Power BI, SQL, Google Data Analytics, AI tools workshop, Ethnus training, TCS iON NQT")

# ------------------------------------------------------------------ skills
def skills():
    cols = [("LANGUAGES & CORE", ["Python", "SQL", "JavaScript", "OOP", "Problem Solving", "Debugging", "Testing", "Backend Development"], 296),
            ("DATABASES", ["MySQL", "SQLite", "DBMS", "Joins", "Aggregation", "Database Integration"], 296),
            ("DATA & BI", ["Power BI", "Excel", "Data Cleaning", "EDA", "Data Visualization", "Dashboard Design"], 296),
            ("APIS & AI", ["REST API", "Flask", "JSON", "API Integration", "LLM API Integration", "Prompt Engineering", "ChatGPT & AI Tools"], 456),
            ("TOOLS", ["Git", "GitHub", "Docker", "pytest", "GitHub Actions", "Version Control", "Branching", "Commits", "Repository Management"], 456)]
    pos = [(24, 0), (352, 0), (680, 0), (24, 1), (512, 1)]
    b, rowy = "", [0, 0]
    # first pass: row 0 height
    heights = []
    for (h, its, w), (x, r) in zip(cols, pos):
        heights.append(chips(0, 0, its, w, size=13)[1])
    r0 = max(h for h, (_, r) in zip(heights, pos) if r == 0)
    y0 = {0: 0, 1: r0 + 66 + 14}
    maxy = 0
    for (h, its, w), (x, r) in zip(cols, pos):
        oy = y0[r]
        b += t(x, oy + 36, h, 12, RED, ls=4, weight="bold") + f'<line x1="{x}" y1="{oy+48}" x2="{x+w}" y2="{oy+48}" stroke="{LINE}"/>'
        c, bot = chips(x, oy + 66, its, w, size=13, fill=INK); b += c; maxy = max(maxy, bot)
    svg("skills.svg", 1000, maxy + 24, f'<rect width="1000" height="{maxy+24}" rx="10" fill="url(#glow)"/>' + b + f'<rect x="1" y="1" width="998" height="{maxy+22}" rx="10" fill="none" stroke="{LINE}"/>', "Skills: languages, databases, data and BI, APIs and AI, tools")


def hud():
    """Jarvis-style HUD: rotating arc reactor, scan line, boot sequence typing real facts, counter rings"""
    W, H, CYC = 1000, 340, 14
    b = (f'<rect width="{W}" height="{H}" rx="10" fill="url(#glow)"/>'
         f'<defs><pattern id="hex" width="28" height="48" patternUnits="userSpaceOnUse" patternTransform="scale(1)"><path d="M14 0 L28 8 V24 L14 32 L0 24 V8 Z" fill="none" stroke="{LINE}" stroke-width=".8"/></pattern></defs>'
         f'<rect width="{W}" height="{H}" rx="10" fill="url(#hex)" opacity=".55"/>')
    cx, cy = 170, 170
    def ticks(r, n, ln, w=2):
        out = ""
        for i in range(n):
            a = 2 * math.pi * i / n
            out += f'<line x1="{cx + r * math.cos(a):.1f}" y1="{cy + r * math.sin(a):.1f}" x2="{cx + (r - ln) * math.cos(a):.1f}" y2="{cy + (r - ln) * math.sin(a):.1f}" stroke="{GOLD}" stroke-width="{w}"/>'
        return out
    rot = lambda d, rev=False: f'<animateTransform attributeName="transform" type="rotate" from="{360 if rev else 0} {cx} {cy}" to="{0 if rev else 360} {cx} {cy}" dur="{d}s" repeatCount="indefinite"/>'
    b += f'<circle cx="{cx}" cy="{cy}" r="130" fill="none" stroke="{LINE}" stroke-width="1.5"/>'
    b += f'<g>{rot(40)}{ticks(130, 72, 10)}</g>'
    b += f'<g>{rot(14, True)}<circle cx="{cx}" cy="{cy}" r="108" fill="none" stroke="{GOLD}" stroke-width="3" stroke-dasharray="90 40 20 40" opacity=".85"/></g>'
    b += f'<g>{rot(9)}<circle cx="{cx}" cy="{cy}" r="88" fill="none" stroke="{RED}" stroke-width="2" stroke-dasharray="4 10"/></g>'
    b += f'<g>{rot(22, True)}{ticks(74, 36, 8, 1.5)}</g>'
    b += f'<circle cx="{cx}" cy="{cy}" r="58" fill="none" stroke="{GOLD}" stroke-width="2"/>'
    # core triangle + glow
    tri = " ".join(f"{cx + 40 * math.cos(math.radians(a)):.1f},{cy + 40 * math.sin(math.radians(a)):.1f}" for a in (-90, 30, 150))
    b += f'<circle cx="{cx}" cy="{cy}" r="46" fill="{GOLD}" opacity=".10"><animate attributeName="opacity" values=".05;.28;.05" dur="2.4s" repeatCount="indefinite"/><animate attributeName="r" values="40;54;40" dur="2.4s" repeatCount="indefinite"/></circle>'
    b += f'<g>{rot(18)}<polygon points="{tri}" fill="none" stroke="{GOLD}" stroke-width="2.5"/></g>'
    b += f'<circle cx="{cx}" cy="{cy}" r="10" fill="{INK}"><animate attributeName="opacity" values="1;.55;1" dur="1.6s" repeatCount="indefinite"/></circle>'
    b += t(cx, cy + 4, "", 1, INK) + t(cx, 326, "D.R. CORE  ·  ONLINE", 10, GOLD, anchor="middle", ls=4)
    # scan line
    b += (f'<rect x="0" y="0" width="3" height="{H}" fill="{GOLD}" opacity=".35"><animate attributeName="x" values="0;{W};0" keyTimes="0;.5;1" dur="10s" repeatCount="indefinite"/></rect>'
          f'<rect x="-60" y="0" width="60" height="{H}" fill="{GOLD}" opacity=".05"><animate attributeName="x" values="-60;{W};-60" keyTimes="0;.5;1" dur="10s" repeatCount="indefinite"/></rect>')
    # boot terminal
    tx, ty = 360, 64
    b += f'<rect x="{tx - 14}" y="{ty - 28}" width="400" height="212" rx="6" fill="#0a0908" fill-opacity=".72" stroke="{LINE}"/>' + t(tx, ty - 8, "SYSTEM BOOT", 10, RED, ls=4)
    lines = [("> INITIALIZING DEVENDRA.OS", GOLD), ("> LOADING PYTHON · SQL · POWER BI", INK), ("> FLASK · MYSQL · DOCKER … OK", INK),
             ("> PROJECTS ONLINE ........ 03", INK), ("> CREDENTIALS VERIFIED ... 06", INK), ("> STATUS: OPEN TO WORK", GREEN)]
    for i, (ln, col) in enumerate(lines):
        y = ty + 22 + i * 27; a = .4 + i * 1.5; wd = len(ln) * 7.6 + 4
        kt = f"0;{a/CYC:.4f};{(a+1.1)/CYC:.4f};{(CYC-1.6)/CYC:.4f};{(CYC-1)/CYC:.4f};1"
        b += (f'<clipPath id="bt{i}"><rect x="{tx-1}" y="{y-14}" height="20" width="0"><animate attributeName="width" values="0;0;{wd:.0f};{wd:.0f};0;0" keyTimes="{kt}" dur="{CYC}s" repeatCount="indefinite"/></rect></clipPath>'
              + t(tx, y, ln, 12.5, col, extra=f'clip-path="url(#bt{i})"'))
    b += f'<rect x="{tx + 330}" y="{ty + 8}" width="8" height="16" fill="{GOLD}"><animate attributeName="opacity" values="1;0;1" dur="1s" repeatCount="indefinite"/></rect>'
    # counter rings (real numbers)
    for i, (n, lab, frac) in enumerate([("3", "INTERNSHIPS", .5), ("3", "PROJECTS", .5), ("6", "CREDENTIALS", .75), ("126", "TRAINING HRS", 1)]):
        gx, gy = 800 + (i % 2) * 100, 112 + (i // 2) * 116
        Cc = 2 * math.pi * 34
        b += (f'<circle cx="{gx}" cy="{gy}" r="34" fill="none" stroke="{LINE}" stroke-width="6"/>'
              f'<circle cx="{gx}" cy="{gy}" r="34" fill="none" stroke="{GOLD}" stroke-width="6" stroke-linecap="round" stroke-dasharray="0 {Cc:.0f}" transform="rotate(-90 {gx} {gy})">'
              f'<animate attributeName="stroke-dasharray" values="0 {Cc:.0f};{Cc*frac:.0f} {Cc:.0f};{Cc*frac:.0f} {Cc:.0f}" keyTimes="0;.3;1" dur="6s" begin="{i*.4}s" repeatCount="indefinite"/></circle>'
              f'<circle cx="{gx}" cy="{gy}" r="42" fill="none" stroke="{RED}" stroke-width="1" stroke-dasharray="2 6"><animateTransform attributeName="transform" type="rotate" from="0 {gx} {gy}" to="360 {gx} {gy}" dur="{12+i*3}s" repeatCount="indefinite"/></circle>'
              + t(gx, gy + 7, n, 22, INK, DISP, "middle", ls=1) + t(gx, gy + 62, lab, 8.5, DIM, anchor="middle", ls=2))
    b += t(44, 34, "J.A.R.V.I.S  ·  PROFILE INTERFACE", 11, RED, ls=4) + t(956, 34, "ALL SYSTEMS NOMINAL", 11, GREEN, anchor="end", ls=3)
    b += f'<circle cx="940" cy="30" r="4" fill="{GREEN}"><animate attributeName="opacity" values="1;.2;1" dur="1.2s" repeatCount="indefinite"/></circle>'
    # corner brackets
    for x1, y1, dx, dy in ((8, 8, 1, 1), (W - 8, 8, -1, 1), (8, H - 8, 1, -1), (W - 8, H - 8, -1, -1)):
        b += f'<path d="M{x1} {y1 + 24 * dy} V{y1} H{x1 + 24 * dx}" fill="none" stroke="{GOLD}" stroke-width="2"/>'
    b += f'<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="10" fill="none" stroke="{LINE}"/>'
    svg("hud.svg", W, H, b, "Jarvis-style interface: boot sequence, 3 projects online, 6 credentials verified, open to work")

def ticker():
    items = ["PYTHON", "SQL", "MYSQL", "SQLITE", "POWER BI", "EXCEL", "FLASK", "REST API", "JAVASCRIPT", "DOCKER", "PYTEST", "GIT", "GITHUB ACTIONS", "EDA", "LLM APIS"]
    x, row = 0, ""
    for it in items:
        wd = len(it) * 15
        row += t(x, 41, it, 22, INK, DISP, extra=f'textLength="{wd}" lengthAdjust="spacingAndGlyphs"') + f'<rect x="{x + wd + 20}" y="31" width="6" height="6" fill="{RED}" transform="rotate(45 {x + wd + 23} 34)"/>'
        x += wd + 56
    d = f'<animateTransform attributeName="transform" type="translate" from="0 0" to="{-x} 0" dur="{x/70:.0f}s" repeatCount="indefinite"/>'
    row2 = row.replace('<text', '<text', 1)
    b = (f'<rect width="1000" height="64" rx="10" fill="url(#glow)"/><g>{d}{row}<g transform="translate({x} 0)">{row}</g><g transform="translate({2*x} 0)">{row}</g></g>'
         f'<defs><linearGradient id="fadeL" x1="0" x2="1"><stop offset="0" stop-color="{BG}"/><stop offset="1" stop-color="{BG}" stop-opacity="0"/></linearGradient>'
         f'<linearGradient id="fadeR" x1="1" x2="0"><stop offset="0" stop-color="{BG}"/><stop offset="1" stop-color="{BG}" stop-opacity="0"/></linearGradient></defs>'
         f'<rect width="90" height="64" fill="url(#fadeL)"/><rect x="910" width="90" height="64" fill="url(#fadeR)"/>'
         f'<rect x="1" y="1" width="998" height="62" rx="10" fill="none" stroke="{LINE}"/>')
    svg("ticker.svg", 1000, 64, b, "Tech stack: Python, SQL, MySQL, SQLite, Power BI, Excel, Flask, REST API, JavaScript, Docker, pytest, Git, GitHub Actions")

def scorecard():
    W, H = 1000, 230
    b = f'<rect width="{W}" height="{H}" rx="10" fill="url(#glow)"/><rect x="1" y="1" width="{W-2}" height="{H-2}" rx="10" fill="none" stroke="{LINE}"/>'
    b += t(44, 40, "SCORECARD  ·  TCS iON NQT (IT)  ·  JUN 2026", 12, RED, ls=4)
    for i, (lab, v) in enumerate([("COGNITIVE", 74.59), ("QUANT & REASONING", 64.84), ("PYTHON", 65.91)]):
        y = 74 + i * 46
        bw = 440
        b += t(44, y + 14, lab, 12, DIM, ls=2) + f'<rect x="230" y="{y}" width="{bw}" height="18" rx="4" fill="{LINE}"/>'
        b += (f'<rect x="230" y="{y}" width="0" height="18" rx="4" fill="{GOLD}"><animate attributeName="width" values="0;{bw*v/100:.0f};{bw*v/100:.0f}" keyTimes="0;.35;1" dur="7s" begin="{i*.3}s" repeatCount="indefinite"/></rect>')
        b += t(690, y + 15, f"{v:.2f}%", 20, INK, DISP, ls=2)
    b += f'<line x1="780" y1="40" x2="780" y2="200" stroke="{LINE}"/>'
    b += (f'<circle cx="880" cy="104" r="52" fill="none" stroke="{LINE}" stroke-width="10"/>'
          f'<circle cx="880" cy="104" r="52" fill="none" stroke="{GREEN}" stroke-width="10" stroke-linecap="round" stroke-dasharray="0 400" transform="rotate(-90 880 104)">'
          '<animate attributeName="stroke-dasharray" values="0 400;327 400;327 400" keyTimes="0;.4;1" dur="7s" repeatCount="indefinite"/></circle>'
          + t(880, 112, "126", 38, INK, DISP, "middle", ls=1) + t(880, 176, "HOURS OF TRAINING", 10, GREEN, anchor="middle", ls=3) + t(880, 194, "ETHNUS · CAMPUS RECRUITMENT", 8.5, DIM, anchor="middle", ls=1.5))
    svg("scorecard.svg", W, H, b, "TCS iON NQT scorecard: Cognitive 74.59%, Quant and Reasoning 64.84%, Python 65.91%; 126 hours of Ethnus training")

def education():
    W, H = 1000, 280
    b = f'<rect width="{W}" height="{H}" rx="10" fill="url(#glow)"/><rect x="1" y="1" width="{W-2}" height="{H-2}" rx="10" fill="none" stroke="{LINE}"/>'
    # education
    b += t(44, 40, "EDUCATION", 12, RED, ls=5)
    b += t(44, 92, "B.E. ARTIFICIAL INTELLIGENCE", 30, INK, DISP, extra='textLength="410" lengthAdjust="spacingAndGlyphs"') + t(44, 124, "& DATA SCIENCE", 30, INK, DISP, ls=1.5)
    b += t(44, 154, "PVG College of Engineering, SPPU", 18, GOLD, SERIF, style="italic") + t(44, 180, "2022 – 2026  ·  Pune, Maharashtra", 14, DIM, SERIF)
    b += f'<rect x="44" y="204" width="0" height="3" fill="{RED}"><animate attributeName="width" values="0;380;380;0" keyTimes="0;.4;.9;1" dur="6s" repeatCount="indefinite"/></rect>'
    b += t(44, 236, "GRADUATE", 11, GREEN, ls=3) + f'<circle cx="34" cy="232" r="4" fill="{GREEN}"><animate attributeName="opacity" values="1;.2;1" dur="1.8s" repeatCount="indefinite"/></circle>'
    b += f'<line x1="480" y1="34" x2="480" y2="{H-24}" stroke="{LINE}"/>'
    # achievements
    b += t(520, 40, "ACHIEVEMENTS", 12, RED, ls=5)
    # trophy
    b += (f'<g transform="translate(540 64)"><path d="M10 0 H50 V26 a20 20 0 0 1 -40 0 Z" fill="none" stroke="{GOLD}" stroke-width="3"/>'
          f'<path d="M10 6 H0 a10 14 0 0 0 12 18 M50 6 H60 a10 14 0 0 1 -12 18" fill="none" stroke="{GOLD}" stroke-width="3"/>'
          f'<rect x="26" y="46" width="8" height="14" fill="{GOLD}"/><rect x="14" y="60" width="32" height="6" rx="2" fill="{GOLD}"/>'
          f'<animate attributeName="opacity" values="1;.55;1" dur="2.6s" repeatCount="indefinite"/></g>')
    b += t(630, 82, "WINNER", 26, INK, DISP, ls=3) + t(630, 106, "Inter-College Cricket Tournament", 16, GOLD, SERIF, style="italic") + t(630, 128, "Team Captain  ·  2026", 14, DIM, SERIF)
    b += f'<line x1="520" y1="152" x2="956" y2="152" stroke="{LINE}"/>'
    b += t(520, 186, "REPRESENTED MAHARASHTRA", 18, INK, DISP, ls=2) + t(520, 210, "All India National Cricket Championship, Goa", 15, DIM, SERIF, style="italic")
    # languages
    for i, lg in enumerate(["ENGLISH", "HINDI", "MARATHI"]):
        x = 520 + i * 112
        b += f'<rect x="{x}" y="238" width="100" height="22" rx="11" fill="none" stroke="{LINE}" stroke-width="1.2"/>' + t(x + 50, 253, lg, 10, GOLD, anchor="middle", ls=2)
    svg("education.svg", W, H, b, "Education: B.E. AI and Data Science, PVG College of Engineering, SPPU, 2022 to 2026. Winner of the inter-college cricket tournament as team captain; represented Maharashtra at the All India National Cricket Championship. Languages: English, Hindi, Marathi")

PANEL_ = "#0e0c0a"
def stats(data=None):
    """GitHub stats panel. data=None draws a clearly-labelled 'waiting for first sync' placeholder; scripts/stats.py passes real numbers."""
    W, H = 1000, 300
    b = f'<rect width="{W}" height="{H}" rx="10" fill="url(#glow)"/><rect x="1" y="1" width="{W-2}" height="{H-2}" rx="10" fill="none" stroke="{LINE}"/>'
    b += t(44, 40, "GITHUB  ·  @DEVS901", 12, RED, ls=5) + t(956, 40, "SYNCED DAILY" if data else "WAITING FOR FIRST SYNC", 10, GREEN if data else DIM, anchor="end", ls=3)
    tiles = [("REPOSITORIES", "repos"), ("STARS EARNED", "stars"), ("COMMITS (12 MO)", "commits"), ("PULL REQUESTS", "prs")]
    for i, (lab, k) in enumerate(tiles):
        x = 44 + i * 228
        v = str(data[k]) if data else "–"
        b += (f'<rect x="{x}" y="62" width="208" height="92" rx="8" fill="{PANEL_}" stroke="{LINE}"/><rect x="{x}" y="62" width="3" height="92" fill="{RED}"/>'
              + t(x + 104, 118, v, 52, INK, DISP, "middle", ls=2) + t(x + 104, 142, lab, 10, DIM, anchor="middle", ls=3))
    b += t(44, 190, "TOP LANGUAGES", 12, GOLD, ls=4)
    pal = [GOLD, RED, INK, GREEN, "#9a917c", "#6b6354"]
    if data and data.get("langs"):
        tot = sum(v for _, v in data["langs"]) or 1
        x = 44
        for i, (n, v) in enumerate(data["langs"][:6]):
            w = max(4, 912 * v / tot)
            b += f'<rect x="{x:.1f}" y="204" width="{w:.1f}" height="14" fill="{pal[i % 6]}"/>'
            lx = 44 + (i % 3) * 304; ly = 250 + (i // 3) * 24
            b += f'<circle cx="{lx + 6}" cy="{ly - 4}" r="5" fill="{pal[i % 6]}"/>' + t(lx + 20, ly, f"{n}  {100 * v / tot:.1f}%", 13, INK)
            x += w
    else:
        b += f'<rect x="44" y="204" width="912" height="14" rx="7" fill="{LINE}"/>'
        b += f'<rect x="44" y="204" width="180" height="14" rx="7" fill="{GOLD}" opacity=".5"><animate attributeName="x" values="44;776;44" dur="3.2s" repeatCount="indefinite"/></rect>'
        b += t(44, 254, "Run the “Update GitHub stats” workflow once (see SETUP.md) and real numbers replace the dashes.", 14, DIM, SERIF, style="italic")
    svg("stats.svg", W, H, b, "GitHub stats for devs901: repositories, stars, commits, pull requests and top languages")

# ------------------------------------------------------------------ footer + buttons
def footer():
    import random; random.seed(7)
    st = "".join(f'<circle cx="{random.randint(10,990)}" cy="{random.randint(8,172)}" r="{random.choice([.8,1.1,1.6])}" fill="{INK}" opacity="{random.uniform(.2,.8):.2f}"><animate attributeName="opacity" values=".15;.9;.15" dur="{random.uniform(2,6):.1f}s" repeatCount="indefinite"/></circle>' for _ in range(45))
    b = (f'<rect width="1000" height="180" rx="10" fill="url(#glow)"/>' + st
         + t(500, 50, "THE END… OR THE BEGINNING", 12, RED, anchor="middle", ls=7)
         + t(500, 100, "COMING SOON: YOUR NEXT DATA TEAM", 38, INK, DISP, "middle", ls=3, extra='textLength="640" lengthAdjust="spacingAndGlyphs"')
         + t(500, 138, "Based on real work  ·  Filmed in Maharashtra, India", 16, DIM, SERIF, "middle", style="italic")
         + t(500, 164, "WRITTEN & DIRECTED BY DEVENDRA RATHOD", 10, GOLD, anchor="middle", ls=5)
         + f'<rect width="1000" height="180" rx="10" fill="url(#vig)"/>')
    svg("footer.svg", 1000, 180, b, "End credits: coming soon, your next data team")

def button(name, label, glyph):
    b = (f'<rect x="1" y="1" width="238" height="52" rx="3" fill="#0e0c0a" stroke="{INK}" stroke-width="1.5"/>'
         + t(34, 35, glyph, 18, GOLD, DISP) + t(140, 36, label, 24, INK, DISP, "middle", ls=5))
    svg(name, 240, 54, b, label)

def divider():
    holes = "".join(f'<rect x="{x}" y="9" width="10" height="6" rx="1.5" fill="{LINE}"/>' for x in range(0, 1000, 22))
    s = f'<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="24" viewBox="0 0 1000 24" role="presentation"><line x1="0" y1="2" x2="1000" y2="2" stroke="{LINE}"/><line x1="0" y1="22" x2="1000" y2="22" stroke="{LINE}"/>{holes}</svg>'
    open(os.path.join(OUT, "divider.svg"), "w").write(skin(s))

def build_one():
    """regenerate every SVG for the current theme into OUT"""
    os.makedirs(OUT, exist_ok=True)
    keep = KEEP_NOW()
    for f in os.listdir(OUT):
        if f.endswith(".svg") and f not in keep: os.remove(os.path.join(OUT, f))
    import jarvis3d as J
    import jarvis_x as X
    J.header(); J.hud(); X.scan(); X.ask(); X.resume(); X.cvbutton(); J.numbers(); J.journey(); J.skills(); J.arc_reactor(); ticker(); J.credentials(); scorecard(); education(); J.footer(); J.divider()
    if "stats.svg" not in keep: stats()
    if "feed.svg" not in keep: X.feed()
    H_ = J.heading
    H_("h-story.svg", "Module 01  ·  Experience", "The Story So Far", "Four roles, one direction: Python, SQL and data")
    H_("h-projects.svg", "Module 02  ·  Projects", "Now Online", "Three projects, each with a step-by-step animated walkthrough")
    H_("h-credentials.svg", "Module 03  ·  Credentials", "Verified", "Six credentials, a scorecard and 126 hours of training")
    H_("h-behind.svg", "Module 04  ·  Background", "Behind The Scenes", "Education, achievements and languages")
    H_("h-cast.svg", "Module 05  ·  Skills + Power Core", "The Arsenal", "A 3D skill globe and the arc reactor that powers the build")
    H_("h-ask.svg", "Module 06  ·  Interface", "Ask JARVIS", "Four questions recruiters ask, answered in the terminal")
    H_("h-resume.svg", "Module 07  ·  Résumé", "Hologram CV", "Rotate the résumé in 3D, then download the real PDF")
    H_("h-stats.svg", "Module 08  ·  GitHub", "Telemetry", "Live GitHub numbers and a real activity feed")
    H_("h-contact.svg", "Module 09  ·  Contact", "Open A Channel", "Open to entry-level Python, SQL, data and AI roles")
    H_("h-p1.svg", "Project 01  ·  E-Governance Platform", "GramSathi", "Village services online, with AI-sorted complaints that never stall the system")
    H_("h-p2.svg", "Project 02  ·  Power BI Dashboard", "Motorola Sales Dashboard", "One page that answers where, when, which and how")
    H_("h-p3.svg", "Project 03  ·  Full-Stack Expense Tracker", "Spendwise", "From a sentence you type to a tested, containerised app")
    card("p-gramsathi.svg", "01", "PROJECT 01 · GRAMSATHI", "GramSathi",
         ["Built an e-governance platform on MySQL to digitize rural governance services: users, services, applications, complaints and announcements, with SQL queries for data retrieval.",
          "Integrated an AI service over REST (JSON) to auto-categorize citizen complaints, with error handling and a manual-categorization fallback so the system keeps working when the AI service is unavailable."],
         ["Python", "MySQL", "SQL", "REST API", "AI integration"], J.m_network3d, "VIEW ON GITHUB")
    card("p-dashboard.svg", "02", "PROJECT 02 · MOTOROLA SALES DASHBOARD", "Motorola Sales Dashboard",
         ["Designed an interactive dashboard with KPI cards (total sales, quantity, average, transactions).",
          "Visuals for city-wise transactions (map), units sold over time, sales by model, payment split and customer ratings.",
          "Slicers for month, mobile model and payment method enable instant filtering."],
         ["Power BI", "Data visualization", "Dashboard design"], J.m_bars3d, "SEE MORE ON GITHUB")
    card("p-spendwise.svg", "03", "PROJECT 03 · EXPENSE TRACKER", "Spendwise",
         ["Full-stack expense tracker: Python OOP service layer, Flask REST API, web UI and CLI on a SQLite database (4 tables, constraints, indexes).",
          "SQL for summaries, month-over-month change (CTE + LAG) and budgets; natural-language quick add and recurring-payment detection.",
          "Pytest tests, Docker and GitHub Actions CI."],
         ["Python", "Flask", "SQLite", "SQL", "REST API", "JavaScript", "HTML/CSS", "Docker", "pytest", "GitHub Actions"], J.m_cube3d, "VIEW ON GITHUB")
    import explainers; explainers.build_all()
    J.button("btn-linkedin.svg", "LINKEDIN", "in"); J.button("btn-email.svg", "EMAIL ME", "@"); J.button("btn-github.svg", "GITHUB", "</>")

def KEEP_NOW():   # a stats.svg written by scripts/stats.py (real numbers) is never overwritten by the placeholder
    keep = set()
    for f in ("stats.svg", "feed.svg"):
        p = os.path.join(OUT, f)
        if os.path.exists(p) and "WAITING FOR FIRST SYNC" not in open(p, encoding="utf-8").read(): keep.add(f)
    return keep

if __name__ == "__main__":
    args = sys.argv[1:]
    if "--all" in args:      # ./assets in the default theme + a ready-to-copy assets folder per theme under ./themes
        for name in THEMES:
            out = os.path.join(HERE, "assets") if name == "jarvis" else os.path.join(HERE, "themes", name, "assets")
            subprocess.check_call([sys.executable, os.path.abspath(__file__)], env=dict(os.environ, THEME=name, ASSETS_OUT=out))
    else:
        if "--theme" in args: os.environ["THEME"] = args[args.index("--theme") + 1]
        build_one()
