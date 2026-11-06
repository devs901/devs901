"""Animated project walkthroughs (SMIL, self-contained). Called from build.py.
Each explainer is a looping 'film': a persistent diagram, scenes that fade in/out, a caption and a progress bar."""
import math, textwrap
from xml.sax.saxutils import escape as E
import build as B
from build import INK, DIM, RED, GOLD, LINE, GREEN, DISP, SERIF, MONO, t, chips, svg

PANEL, PANEL2, ARW = "#0e0c0a", "#14110e", "#4a4237"
CY = [20]
OFF = [0]   # time offset applied to every animation built while it is set
_n = [0]


def uid(p="k"):
    _n[0] += 1
    return f"{p}{_n[0]}"


def fmt(v):
    return f"{v:g}" if isinstance(v, (int, float)) else str(v)


# ------------------------------------------------------------------ animation primitives
def A(attr, pts):
    """animate `attr` through (time, value) points on the looping timeline; first/last values are held."""
    c = CY[0]
    pts = sorted(((min(tm + OFF[0], c), v) for tm, v in pts), key=lambda p: p[0])
    if pts[0][0] > 0: pts.insert(0, (0, pts[0][1]))
    if pts[-1][0] < c: pts.append((c, pts[-1][1]))
    vals = ";".join(fmt(v) for _, v in pts)
    keys = ";".join(f"{tm / c:.4f}" for tm, _ in pts)
    return f'<animate attributeName="{attr}" values="{vals}" keyTimes="{keys}" dur="{c}s" repeatCount="indefinite"/>'


def AT(pts):
    """translate animation: pts = (time, x, y)"""
    c = CY[0]
    pts = sorted(((min(tm + OFF[0], c), x, y) for tm, x, y in pts), key=lambda p: p[0])
    if pts[0][0] > 0: pts.insert(0, (0, pts[0][1], pts[0][2]))
    if pts[-1][0] < c: pts.append((c, pts[-1][1], pts[-1][2]))
    vals = ";".join(f"{fmt(x)} {fmt(y)}" for _, x, y in pts)
    keys = ";".join(f"{tm / c:.4f}" for tm, _, _ in pts)
    return f'<animateTransform attributeName="transform" type="translate" values="{vals}" keyTimes="{keys}" dur="{c}s" repeatCount="indefinite"/>'


def show(a, b, f=.35):
    c, p, o = CY[0], [], OFF[0]
    a, b = a + o, b + o
    if a <= 0: p.append((0, 1))
    else: p += [(0, 0), (a, 0), (a + f, 1)]
    if b >= c: p.append((c, 1))
    else: p += [(b - f, 1), (b, 0), (c, 0)]
    saved, OFF[0] = OFF[0], 0
    try: return A("opacity", p)
    finally: OFF[0] = saved


def window(inner, a, b, f=.3):
    return f'<g opacity="0">{show(a, b, f)}{inner}</g>'


def reveal(inner, a, f=.4):
    return f'<g opacity="0">{A("opacity", [(0, 0), (a, 0), (a + f, 1)])}{inner}</g>'


def typed(x, y, s, size, fill, a, dur, font=MONO, cw=.6, weight="normal"):
    cid, w = uid("clip"), len(s) * size * cw + 4
    clip = (f'<clipPath id="{cid}"><rect x="{x - 1}" y="{y - size}" height="{size * 1.5:.0f}" width="0">'
            + A("width", [(0, 0), (a, 0), (a + dur, w)]) + '</rect></clipPath>')
    return clip + t(x, y, s, size, fill, font, weight=weight, extra=f'clip-path="url(#{cid})"')


def packet(path, color=GOLD, r=6):
    t0, t1 = path[0][0], path[-1][0]
    op = [(0, 0), (t0, 0), (t0 + .15, 1), (t1 - .15, 1), (t1, 0)]
    xs, ys = [(a, x) for a, x, _ in path], [(a, y) for a, _, y in path]
    s = ""
    for rr, o in ((r * 2.1, .22), (r, 1)):
        s += (f'<circle r="{rr:.1f}" fill="{color}" cx="{path[0][1]}" cy="{path[0][2]}" opacity="0">'
              + A("cx", xs) + A("cy", ys)
              + A("opacity", [(tm, v * o) for tm, v in op]) + '</circle>')
    return s


def ring(x, y, a, color=GOLD, r0=6, r1=28, d=.9):
    return (f'<circle cx="{x}" cy="{y}" r="{r0}" fill="none" stroke="{color}" stroke-width="2" opacity="0">'
            + A("r", [(0, r0), (a, r0), (a + d, r1)]) + A("opacity", [(0, 0), (a, 0), (a + .01, .9), (a + d, 0)]) + '</circle>')


def arrow(x1, y1, x2, y2, color=ARW, flow=True, sw=1.6, both=False):
    a, hl = math.atan2(y2 - y1, x2 - x1), 9
    ex, ey = x2 - math.cos(a) * 6, y2 - math.sin(a) * 6
    head = lambda px, py, ang: (f'<polygon points="{px:.1f},{py:.1f} {px - hl * math.cos(ang - .4):.1f},{py - hl * math.sin(ang - .4):.1f} '
                                f'{px - hl * math.cos(ang + .4):.1f},{py - hl * math.sin(ang + .4):.1f}" fill="{color}"/>')
    dash = '<animate attributeName="stroke-dashoffset" from="0" to="-16" dur="1.2s" repeatCount="indefinite"/>' if flow else ""
    return (f'<line x1="{x1}" y1="{y1}" x2="{ex:.1f}" y2="{ey:.1f}" stroke="{color}" stroke-width="{sw}" stroke-dasharray="4 4">{dash}</line>'
            + head(x2, y2, a))


def node(x, y, w, h, title, sub="", hl=(), col=GOLD, tsize=19):
    cy = y + h / 2
    tsize = min(tsize, ((w - 20) / len(title) - 1.5) / .58)  # keep long titles inside the box
    s = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="{PANEL}" stroke="{LINE}" stroke-width="1.5"/>'
    for win in hl:
        a, b = win[0], win[1]
        c = win[2] if len(win) > 2 else col
        s += window(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="{c}" fill-opacity=".09" stroke="{c}" stroke-width="2"/>', a, b, .25)
    s += t(x + w / 2, cy - 2 if sub else cy + 7, title, tsize, INK, DISP, "middle", ls=2)
    if sub: s += t(x + w / 2, cy + 19, sub, 10.5, DIM, MONO, "middle", ls=1)
    return s


def check(x, y, a, color=GREEN):
    return reveal(f'<circle cx="{x}" cy="{y}" r="10" fill="#0a0908" stroke="{color}" stroke-width="1.6"/>'
                  f'<path d="M{x - 4.5} {y} l3.2 3.4 l6 -7" fill="none" stroke="{color}" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/>', a, .3)


# ------------------------------------------------------------------ frame
def frame(fname, label, scenes, base, aria, top=""):
    OFF[0] = 0
    W, H, c = 1000, 492, CY[0]
    n = len(scenes)
    b = (f'<rect width="{W}" height="{H}" rx="10" fill="url(#glow)"/>'
         f'<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="10" fill="none" stroke="{LINE}"/>'
         f'<circle cx="46" cy="32" r="5" fill="{RED}"><animate attributeName="opacity" values="1;.15;1" dur="1.4s" repeatCount="indefinite"/></circle>'
         + t(60, 36, "LIVE WALKTHROUGH  ·  " + label, 11, DIM, ls=3)
         + t(956, 36, f"{n} STEPS  ·  LOOPING", 11, DIM, anchor="end", ls=3)
         + f'<line x1="44" y1="50" x2="956" y2="50" stroke="{LINE}"/>' + base)
    for i, (a, e, ti, de, content) in enumerate(scenes):
        b += f'<g opacity="{1 if i == 0 else 0}">{show(a, e)}{content}</g>'
    b += f'<line x1="44" y1="366" x2="956" y2="366" stroke="{LINE}"/>'
    for i, (a, e, ti, de, _) in enumerate(scenes):
        cap = t(44, 438, f"0{i + 1}", 72, GOLD, DISP, extra='opacity=".9"') + t(140, 404, ti.upper(), 28, INK, DISP, ls=2)
        for j, ln in enumerate(textwrap.wrap(de, 96)):
            cap += t(140, 430 + j * 22, ln, 16, DIM, SERIF, style="italic")
        b += f'<g opacity="{1 if i == 0 else 0}">{show(a, e)}{cap}</g>'
    gap = 8
    sw = (912 - gap * (n - 1)) / n
    for i, (a, e, *_r) in enumerate(scenes):
        x = 44 + i * (sw + gap)
        b += (f'<rect x="{x:.1f}" y="472" width="{sw:.1f}" height="4" rx="2" fill="{LINE}"/>'
              f'<rect x="{x:.1f}" y="472" width="0" height="4" rx="2" fill="{RED}">' + A("width", [(0, 0), (a, 0), (e, sw)]) + '</rect>')
    # HUD finish: scan line + corner brackets
    b += (f'<rect x="0" y="56" width="2" height="304" fill="{GOLD}" opacity=".3"><animate attributeName="x" values="0;{W};0" keyTimes="0;.5;1" dur="9s" repeatCount="indefinite"/></rect>'
          + "".join(f'<path d="M{x1} {y1 + 18 * dy} V{y1} H{x1 + 18 * dx}" fill="none" stroke="{GOLD}" stroke-width="1.6" opacity=".7"/>' for x1, y1, dx, dy in ((10, 10, 1, 1), (W - 10, 10, -1, 1), (10, H - 10, 1, -1), (W - 10, H - 10, -1, -1))))
    b += top
    svg(fname, W, H, b, aria)


# ================================================================== helpers for richer scenes
def tcard(x, y, w, h, name, tags, a, col=GOLD):
    """schematic table card that reveals at time a (rows are placeholders, tags PK/FK)"""
    c = (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="{PANEL2}" stroke="{LINE}" stroke-width="1.4"/>'
         f'<rect x="{x}" y="{y}" width="{w}" height="24" rx="6" fill="{col}" fill-opacity=".16"/>' + t(x + 12, y + 16, name.upper(), 10.5, col, ls=1.5))
    for k, tag in enumerate(tags):
        yy = y + 44 + k * 20
        c += t(x + 12, yy + 4, tag or "··", 9, GREEN if tag == "PK" else (GOLD if tag else LINE)) + f'<rect x="{x + 40}" y="{yy - 3}" width="{60 + (k * 23 + len(name) * 7) % 60}" height="6" rx="2" fill="{LINE}"/>'
    return reveal(c, a) + ring(x + w / 2, y + h / 2, a, col, 8, 40, 1.0)


def pill(x, y, w, label, col, size=10):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="22" rx="11" fill="{col}" fill-opacity=".14" stroke="{col}"/>'
            + t(x + w / 2, y + 15, label, size, col, anchor="middle", ls=1.5))


# ================================================================== 1. GramSathi
def gramsathi():
    CY[0] = 32
    M = 12                       # the original five-step flow starts at t = 12 s
    # ---------- intro scenes (absolute times) ----------
    OFF[0] = 0
    chipsL = ["SERVICES", "APPLICATIONS", "COMPLAINTS", "ANNOUNCEMENTS"]
    i1 = t(200, 84, "RURAL GOVERNANCE SERVICES", 10, GOLD, anchor="middle", ls=3)
    for i, nm in enumerate(chipsL):
        y = 104 + i * 52
        i1 += reveal(f'<rect x="80" y="{y}" width="240" height="38" rx="6" fill="{PANEL}" stroke="{LINE}" stroke-width="1.4"/>' + t(200, y + 25, nm, 16, INK, DISP, "middle", ls=2), .3 + i * .35, .3)
        i1 += packet([(1.5 + i * .25, 320, y + 19), (2.5 + i * .25, 450, 192)], GOLD, 5)
    i1 += reveal(f'<rect x="450" y="130" width="240" height="124" rx="10" fill="{GOLD}" fill-opacity=".08" stroke="{GOLD}" stroke-width="2"/>'
                 + t(570, 180, "GRAMSATHI", 26, INK, DISP, "middle", ls=3) + t(570, 204, "ONE DIGITAL PLATFORM", 10, DIM, anchor="middle", ls=2)
                 + t(570, 232, "PYTHON  ·  MYSQL", 11, GOLD, anchor="middle", ls=2), 1.9, .4) + ring(570, 192, 2.2, GOLD, 20, 60, 1.2)
    i1 += reveal(arrow(692, 192, 770, 192, GOLD), 2.6, .3)
    i1 += reveal(f'<rect x="780" y="140" width="170" height="104" rx="10" fill="{PANEL}" stroke="{GREEN}" stroke-width="1.6"/>'
                 + t(865, 184, "ONLINE", 26, GREEN, DISP, "middle", ls=3) + t(865, 208, "for every user", 11, DIM, anchor="middle", ls=2)
                 + t(865, 228, "available to every user", 10.5, DIM, SERIF, "middle", style="italic"), 3.0, .4)

    names = ["users", "services", "applications", "complaints", "announcements"]
    tags = [["PK", "", ""], ["PK", "", ""], ["PK", "FK", "FK"], ["PK", "FK", ""], ["PK", "", ""]]
    i2 = t(944, 84, "SCHEMATIC", 9, DIM, anchor="end", ls=2)
    for i, nm in enumerate(names):
        i2 += tcard(40 + i * 188, 96, 168, 128, nm, tags[i], 4.3 + i * .4)
    cx = lambda i: 40 + i * 188 + 84
    for k, (u, v, dy, lab) in enumerate([(0, 2, 258, "a user submits applications"), (1, 2, 280, "applications target a service"), (0, 3, 302, "a user files complaints")]):
        arc = (f'<path d="M{cx(u)} 224 V{dy} H{cx(v)} V224" fill="none" stroke="{GOLD}" stroke-width="1.6" stroke-dasharray="4 4"><animate attributeName="stroke-dashoffset" from="0" to="-16" dur="1.2s" repeatCount="indefinite"/></path>')
        i2 += reveal(arc + t((cx(u) + cx(v)) / 2, dy - 6, lab, 10.5, DIM, SERIF, "middle", style="italic"), 6.4 + k * .5, .4)
    i2 += reveal(t(500, 338, "FIVE TABLES  ·  ONE CONSISTENT MODEL", 11, GOLD, anchor="middle", ls=4), 7.6)

    code = ["SELECT id, text, category", "FROM complaints", "WHERE status = 'new'", "ORDER BY created_at DESC;"]
    i3 = (f'<rect x="44" y="82" width="440" height="232" rx="8" fill="#0a0908" stroke="{LINE}"/>' + t(60, 106, "SAMPLE QUERY  ·  ILLUSTRATIVE", 9.5, GOLD, ls=2))
    for i, ln in enumerate(code):
        i3 += typed(62, 148 + i * 34, ln, 15, GOLD if ln.split()[0] in ("SELECT", "FROM", "WHERE", "ORDER") else INK, 8.4 + i * .55, .5)
    i3 += reveal(arrow(486, 198, 530, 198, GOLD), 10.7, .3)
    i3 += (f'<rect x="536" y="82" width="420" height="232" rx="8" fill="{PANEL}" stroke="{LINE}"/>' + t(552, 106, "RESULT SET", 9.5, GOLD, ls=2))
    for i, (cat, col) in enumerate([("Water", GREEN), ("Roads", GOLD), ("Power", RED), ("Water", GREEN)]):
        y = 124 + i * 44
        i3 += reveal(f'<rect x="552" y="{y}" width="388" height="34" rx="5" fill="{PANEL2}" stroke="{LINE}"/>'
                     + t(566, y + 22, f"#{104 + i}", 11, DIM) + f'<rect x="620" y="{y + 13}" width="{150 + (i * 37) % 60}" height="7" rx="3" fill="{LINE}"/>' + pill(848, y + 6, 78, cat.upper(), col, 9.5), 10.9 + i * .25, .3)
    i3 += reveal(t(500, 340, "SQL QUERIES FEED EVERY SCREEN: STAFF SEE WHAT IS NEW, CITIZENS SEE WHAT IS HANDLED", 10.5, DIM, anchor="middle", ls=1.5), 11.6)

    # ---------- main flow (original times, shifted by M) ----------
    OFF[0] = M
    base = ""
    for a in [(180, 170, 250, 170), (325, 210, 325, 270), (400, 150, 560, 125), (400, 190, 560, 265), (250, 305, 194, 305)]:
        base += arrow(*a)
    base += t(40, 242, "MYSQL TABLES", 9.5, GOLD, ls=2)
    for i, nm in enumerate(names):
        y = 250 + i * 19
        base += f'<rect x="40" y="{y}" width="150" height="16" rx="3" fill="none" stroke="{LINE}"/>' + t(50, y + 12, nm, 10.5, DIM)
        if nm == "complaints":
            for a, e, col in [(5.6, 8, GOLD), (18.3, 19.6, GREEN)]:
                base += window(f'<rect x="40" y="{y}" width="150" height="16" rx="3" fill="{col}" fill-opacity=".25" stroke="{col}"/>' + t(50, y + 12, nm, 10.5, INK), a, e, .2)
    base += node(40, 130, 140, 80, "CITIZEN", "files a complaint", [(.2, 2.6)])
    base += node(250, 130, 150, 80, "PYTHON APP", "validate · route", [(2.2, 3.4), (4.4, 6.2), (8.2, 11.6), (12.2, 16.2), (16.4, 18.6)])
    base += node(250, 270, 150, 70, "MYSQL", "5 core tables", [(5.6, 8), (18.2, 19.6, GREEN)])
    base += node(560, 90, 200, 70, "AI SERVICE", "REST · JSON", [(9.2, 12, GREEN), (13.2, 16, RED)])
    base += node(560, 230, 200, 70, "MANUAL FALLBACK", "staff categorize", [(15.0, 17.6, GREEN)])
    base += (f'<rect x="790" y="90" width="170" height="210" rx="8" fill="{PANEL}" stroke="{LINE}"/>'
             + t(804, 112, "SAMPLE PAYLOAD", 9.5, GOLD, ls=2))

    s1 = (f'<rect x="44" y="76" width="150" height="34" rx="6" fill="none" stroke="{GOLD}"/>'
          + typed(54, 97, '"no water supply"', 11, INK, .2, .8)
          + packet([(1.0, 180, 170), (2.4, 250, 170)]) + ring(250, 170, 2.4))
    s2 = (packet([(4.5, 325, 210), (5.6, 325, 270)]) + ring(325, 270, 5.6)
          + typed(414, 304, "INSERT INTO complaints", 11, GOLD, 5.9, .9) + typed(414, 322, "status = 'new'", 11, DIM, 6.9, .6))
    s3 = (packet([(8.6, 400, 150), (9.4, 560, 125)]) + ring(560, 125, 9.4, GREEN)
          + t(804, 140, "> REQUEST", 9, DIM, ls=2) + typed(804, 160, '{"text":"no water"}', 11, INK, 9.0, .8)
          + packet([(10.4, 560, 133), (11.3, 400, 158)], GREEN)
          + t(804, 195, "< RESPONSE", 9, DIM, ls=2) + typed(804, 215, '{"category":"Water"}', 11, GREEN, 10.5, .8)
          + reveal(f'<rect x="262" y="92" width="128" height="24" rx="4" fill="{GOLD}" fill-opacity=".15" stroke="{GOLD}"/>'
                   + t(326, 108, "CATEGORY: WATER", 10, GOLD, anchor="middle", ls=1), 11.3))
    s4 = (packet([(12.5, 400, 150), (13.2, 545, 128)], RED)
          + reveal(f'<path d="M730 100 L746 116 M746 100 L730 116" stroke="{RED}" stroke-width="3" stroke-linecap="round"/>', 13.2, .2)
          + t(804, 140, "! ERROR", 9, RED, ls=2) + typed(804, 160, "503 service down", 11, RED, 13.4, .8)
          + t(804, 195, "> FALLBACK", 9, DIM, ls=2) + typed(804, 215, "-> manual queue", 11, GOLD, 14.5, .8)
          + packet([(14.4, 400, 190), (15.4, 556, 262)]) + ring(560, 265, 15.4, GREEN))
    s5 = (packet([(16.3, 560, 270), (17.2, 402, 196)], GREEN) + packet([(17.4, 325, 210), (18.3, 325, 270)], GREEN)
          + ring(325, 270, 18.3, GREEN) + check(392, 282, 18.6)
          + typed(414, 304, "categorised + saved", 11, GREEN, 18.5, .8) + typed(414, 322, "no complaint lost", 11, DIM, 19.0, .6))
    OFF[0] = 0
    base = window(base, M - .3, CY[0])
    scenes = [
        (0, 4, "The idea: services, online", "GramSathi digitizes rural governance services: services, applications, complaints and announcements all live on one Python and MySQL platform.", i1),
        (4, 8, "Five tables, one model", "Users, services, applications, complaints and announcements each get a table, so every record has one clear home and one clear owner.", i2),
        (8, 12, "SQL does the retrieval", "Plain SQL queries pull exactly the records each screen needs, such as every new complaint, newest first.", i3),
        (12, 16, "A citizen files a complaint", "A resident reports an issue online, one of the village services GramSathi digitizes.", s1),
        (16, 20, "Saved in MySQL first", "The complaint is written to the database straight away with a status of new, before any AI is involved.", s2),
        (20, 24, "AI categorizes it over REST", "The app posts the complaint text as JSON to an AI service and gets a category back.", s3),
        (24, 28, "AI down? Fallback kicks in", "Errors are caught and the complaint goes to manual categorization, so the system keeps working when the AI service is unavailable.", s4),
        (28, 32, "Saved and routed, every time", "The categorized complaint is written back to MySQL. Whether AI or a person labelled it, nothing is lost.", s5),
    ]
    frame("x-gramsathi.svg", "GRAMSATHI · COMPLAINT FLOW", scenes, base, "Animated walkthrough of GramSathi: the idea, the five MySQL tables, SQL retrieval, then the complaint flow through the Python app, AI service over REST and manual fallback")


# ================================================================== 2. Motorola dashboard
def dashboard():
    CY[0] = 31
    OFF[0] = 0
    base = f'<rect x="40" y="66" width="920" height="282" rx="8" fill="{PANEL}" stroke="{LINE}"/>'
    base += t(940, 92, "ILLUSTRATIVE VALUES", 9, DIM, anchor="end", ls=2)

    def seq(start, Z, A_, B_, C_, D_, grow=1.0):
        return [(start, Z), (start + grow, A_), (19.2, A_), (20.0, B_), (23.2, B_), (24.0, C_), (27.2, C_), (28.0, D_)]

    # slicers
    chip_x = [("MONTH", 60, 120, 19.2), ("MOBILE MODEL", 192, 150, 23.2), ("PAYMENT METHOD", 354, 170, 27.2)]
    for lab, x, w, on in chip_x:
        base += f'<rect x="{x}" y="76" width="{w}" height="24" rx="12" fill="none" stroke="{LINE}" stroke-width="1.3"/>' + t(x + w / 2, 92, lab + "  ▾", 11, DIM, anchor="middle", ls=1)
        base += window(f'<rect x="{x}" y="76" width="{w}" height="24" rx="12" fill="{GOLD}" fill-opacity=".2" stroke="{GOLD}" stroke-width="1.5"/>'
                       + t(x + w / 2, 92, lab + "  ▾", 11, GOLD, anchor="middle", ls=1), on, 31, .2)
    # KPI cards
    kw = [[130, 96, 110, 120], [96, 70, 84, 92], [48, 36, 44, 42], [30, 24, 28, 26]]
    for i, lab in enumerate(["TOTAL SALES", "QUANTITY", "AVERAGE", "TRANSACTIONS"]):
        x = 60 + i * 225
        base += (f'<rect x="{x}" y="108" width="205" height="42" rx="6" fill="{PANEL2}" stroke="{LINE}"/><rect x="{x}" y="108" width="3" height="42" fill="{RED}"/>'
                 + t(x + 14, 125, lab, 10, DIM, ls=2)
                 + f'<rect x="{x + 14}" y="132" width="0" height="9" rx="2" fill="{INK}" opacity=".8">'
                 + A("width", [(0.3, 0)] + seq(.3, 0, kw[0][i], kw[1][i], kw[2][i], kw[3][i], 1.1)[1:]) + '</rect>'
                 + window(f'<rect x="{x}" y="108" width="205" height="42" rx="6" fill="{GOLD}" fill-opacity=".1" stroke="{GOLD}" stroke-width="1.8"/>', 1.0 + i * .7, 1.8 + i * .7, .2))
    # visuals
    panels = [("CITY-WISE TRANSACTIONS", 60, 200, 4.2), ("UNITS SOLD OVER TIME", 272, 220, 7.2), ("SALES BY MODEL", 504, 170, 10.2),
              ("PAYMENT SPLIT", 686, 130, 13.2), ("RATINGS", 828, 112, 16.2)]
    vis = ""
    for lab, x, w, s in panels:
        vis += (f'<rect x="{x}" y="162" width="{w}" height="178" rx="6" fill="{PANEL2}" stroke="{LINE}"/>' + t(x + 12, 180, lab, 9.5, GOLD, ls=1.5)
                + window(f'<rect x="{x}" y="162" width="{w}" height="178" rx="6" fill="none" stroke="{GOLD}" stroke-width="2"/>', s - .2, s + 2.8, .25))
    # map
    vis += f'<polygon points="150,196 176,200 196,214 190,236 204,252 184,262 170,290 158,322 148,324 138,296 120,270 100,262 92,242 108,226 120,212 138,206" fill="none" stroke="{LINE}" stroke-width="1.6"/>'
    dots = [(150, 222), (176, 226), (122, 238), (150, 252), (168, 276), (142, 292), (160, 306)]
    mA, mB = [7, 5, 6, 8, 5, 4, 3], [4, 8, 3, 5, 7, 3, 6]
    mC, mD = [round(r * .4, 1) for r in mB], [round(r * .4 * .5, 1) for r in mB]
    for i, (cx, cy) in enumerate(dots):
        vis += f'<circle cx="{cx}" cy="{cy}" r="0" fill="{RED if i % 2 else GOLD}" fill-opacity=".85">' + A("r", seq(4.2, 0, mA[i], mB[i], mC[i], mD[i])) + '</circle>'
    # line chart
    for gy in (232, 277): vis += f'<line x1="286" y1="{gy}" x2="478" y2="{gy}" stroke="{LINE}" stroke-dasharray="2 4"/>'
    vis += f'<line x1="286" y1="322" x2="478" y2="322" stroke="{LINE}"/>'
    lv = {"Z": [0] * 8, "A": [30, 45, 38, 62, 55, 80, 70, 95], "B": [50, 40, 60, 35, 75, 50, 90, 65]}
    lv["C"], lv["D"] = [round(v * .42) for v in lv["B"]], [round(v * .2) for v in lv["B"]]
    poly = lambda vs: " ".join(f"{286 + i * 27.4:.1f},{322 - v * 1.1:.1f}" for i, v in enumerate(vs))
    vis += (f'<polyline fill="none" stroke="{GOLD}" stroke-width="2.6" stroke-linejoin="round" stroke-linecap="round" points="{poly(lv["Z"])}">'
            + A("points", seq(7.2, poly(lv["Z"]), poly(lv["A"]), poly(lv["B"]), poly(lv["C"]), poly(lv["D"]))) + '</polyline>')
    # bars
    bh = {"Z": [0] * 5, "A": [100, 78, 60, 88, 45], "B": [70, 95, 50, 60, 80], "C": [0, 0, 105, 0, 0], "D": [0, 0, 62, 0, 0]}
    vis += f'<line x1="514" y1="322" x2="662" y2="322" stroke="{LINE}"/>'
    for i in range(5):
        x = 518 + i * 28
        vis += (f'<rect x="{x}" y="322" width="20" height="0" fill="{RED if i % 2 else GOLD}">'
                + A("height", seq(10.2, *[bh[k][i] for k in "ZABCD"])) + A("y", seq(10.2, *[322 - bh[k][i] for k in "ZABCD"])) + '</rect>')
    # donut
    Cc = 2 * math.pi * 32
    sh = {"Z": [0, 0, 0], "A": [.45, .30, .25], "B": [.34, .42, .24], "C": [.46, .30, .24], "D": [0, 1, 0]}
    vis += f'<circle cx="751" cy="248" r="32" fill="none" stroke="{LINE}" stroke-width="13"/>'
    for i, col in enumerate([RED, GOLD, "#9a917c"]):
        da = lambda k: f"{sh[k][i] * Cc:.1f} {Cc:.1f}"
        do = lambda k: f"{-sum(sh[k][:i]) * Cc:.1f}"
        vis += (f'<circle cx="751" cy="248" r="32" fill="none" stroke="{col}" stroke-width="13" transform="rotate(-90 751 248)" stroke-dasharray="0 {Cc:.1f}">'
                + A("stroke-dasharray", seq(13.2, *[da(k) for k in "ZABCD"])) + A("stroke-dashoffset", seq(13.2, *[do(k) for k in "ZABCD"])) + '</circle>')
        vis += f'<circle cx="{722 + i * 29}" cy="318" r="4" fill="{col}"/>'
    # ratings
    rw = {"Z": [0] * 5, "A": [56, 40, 20, 9, 4], "B": [44, 42, 24, 10, 6], "C": [60, 26, 8, 3, 2], "D": [34, 40, 26, 12, 8]}
    for i in range(5):
        y = 196 + i *28
        vis += t(840, y + 8, f"{5 - i}★", 10, DIM) + f'<rect x="862" y="{y}" width="70" height="9" rx="2" fill="{LINE}"/>'
        vis += f'<rect x="862" y="{y}" width="0" height="9" rx="2" fill="{GOLD}">' + A("width", seq(16.2, *[rw[k][i] for k in "ZABCD"])) + '</rect>'
    # spotlight: dim every visual except the one being explained (t = 4 .. 19)
    for i, (lab, x, w, s0) in enumerate(panels):
        dim = f'<rect x="{x}" y="162" width="{w}" height="178" rx="6" fill="#0a0908" fill-opacity=".62"/>'
        if i: vis += window(dim, 4.2, 4 + 3 * i, .25)
        vis += window(dim, 7 + 3 * i, 19, .25)
    base += f'<g opacity="0">' + A("opacity", [(0, 0), (4, 0), (4.4, 1), (30.5, 1), (31, 0)]) + vis + '</g>'

    s1 = ""
    s2 = s2b = s2c = s2d = s2e = ""
    s3 = ring(120, 88, 19.2, GOLD, 8, 34)
    s4 = ring(267, 88, 23.2, GOLD, 8, 34)
    s5 = ring(439, 88, 27.2, GOLD, 8, 34)
    cur = (f'<g opacity="0">' + A("opacity", [(0, 0), (18.6, 0), (18.9, 1), (30.5, 1), (31, 0)])
           + f'<g>{AT([(18.6, 330, 230), (19.1, 120, 92), (22.6, 120, 92), (23.1, 267, 92), (26.6, 267, 92), (27.1, 439, 92), (30.0, 439, 92), (31, 560, 60)])}'
           + f'<polygon points="0,0 0,17 4.5,13 7.5,20 10.5,18.5 7.5,12 13,12" fill="{INK}" stroke="#0a0908" stroke-width="1.2"/></g></g>')
    scenes = [
        (0, 4, "KPI cards, at a glance", "Total sales, quantity, average and transactions sit at the top, so the headline numbers read in one look.", s1),
        (4, 7, "Where are the sales?", "City-wise transactions on a map: bigger bubbles mean more transactions, so strong and weak cities stand out straight away.", s2),
        (7, 10, "Is it growing?", "Units sold over time turns the sales log into a trend line, so peaks and dips are easy to spot.", s2b),
        (10, 13, "Which model sells?", "Sales by model ranks the mobile models against each other, so the best seller is the tallest bar.", s2c),
        (13, 16, "How do people pay?", "The payment split shows each method's share of transactions at a glance.", s2d),
        (16, 19, "Are customers happy?", "Customer ratings sit beside the sales, so volume and satisfaction can be read together.", s2e),
        (19, 23, "Slicer: month", "Pick a month and every card and chart redraws instantly.", s3),
        (23, 27, "Slicer: mobile model", "Narrow to one model and the KPIs, map, trend and ratings all follow.", s4),
        (27, 31, "Slicer: payment method", "Add a payment method and the same dashboard goes one level deeper, with no new report needed.", s5),
    ]
    frame("x-dashboard.svg", "MOTOROLA SALES · POWER BI", scenes, base, "Animated walkthrough of the Motorola sales dashboard: KPI cards, five visuals and three slicers filtering instantly", top=cur)


# ================================================================== 3. Spendwise
def spendwise():
    CY[0] = 36
    OFF[0] = 0
    base = ""
    for a in [(210, 120, 250, 120), (420, 120, 460, 120), (650, 120, 690, 120)]: base += arrow(*a)
    base += node(40, 84, 170, 72, "WEB UI + CLI", "two front doors", [(.4, 1.2), (20.2, 24)])
    base += node(250, 84, 170, 72, "FLASK REST API", "JSON endpoints", [(1.2, 2.0), (8.4, 9.4)])
    base += node(460, 84, 190, 72, "SERVICE LAYER", "Python OOP", [(2.0, 2.8), (8.9, 10.4), (12.2, 14.5), (16.2, 20), (20.2, 24), (24.2, 28), (28.2, 32)])
    base += node(690, 84, 270, 72, "SQLITE", "4 tables · constraints · indexes", [(2.8, 3.9, GREEN), (4.2, 8), (10.0, 12, RED), (12.2, 16), (16.2, 20), (24.2, 28)])
    base += f'<rect x="40" y="180" width="920" height="166" rx="8" fill="{PANEL}" stroke="{LINE}"/>'

    # 1 request lifecycle
    s1 = (packet([(.5, 125, 120), (1.3, 335, 120), (2.1, 555, 120), (2.9, 825, 120)]) + packet([(3.0, 825, 150), (3.9, 125, 150)], GREEN, 5))
    for i, (lab, txt, a) in enumerate([("UI", "POST /api/expenses {amount, category, date}", .9), ("API", "validates the input, calls the service", 1.7),
                                       ("SVC", "service layer applies the business rules", 2.5), ("DB", "INSERT INTO expenses …  (constraints checked)", 3.2)]):
        y = 216 + i * 30
        s1 += t(64, y, lab, 11, GOLD, weight="bold", ls=1) + typed(112, y, txt, 13, INK, a, .7)
    s1 += reveal(f'<rect x="680" y="204" width="260" height="62" rx="8" fill="none" stroke="{GREEN}"/>' + t(700, 238, "201 Created", 20, GREEN, DISP, ls=2)
                 + t(700, 256, "expense saved", 12, DIM, SERIF, style="italic"), 3.3)

    # 2 schema
    s2 = t(944, 198, "SCHEMATIC", 9, DIM, anchor="end", ls=2)
    rows = [["PK", "", ""], ["PK", "FK", "CK"], ["PK", "FK", ""], ["PK", "FK", "CK"]]
    for i in range(4):
        x = 80 + i * 220
        card = (f'<rect x="{x}" y="206" width="180" height="92" rx="6" fill="{PANEL2}" stroke="{LINE}" stroke-width="1.4"/>'
                f'<rect x="{x}" y="206" width="180" height="22" rx="6" fill="{GOLD}" fill-opacity=".16"/>' + t(x + 12, 221, f"TABLE 0{i + 1}", 10, GOLD, ls=2))
        for k, tag in enumerate(rows[i]):
            y = 244 + k * 17
            card += t(x + 12, y + 4, tag or "··", 9, GREEN if tag == "PK" else (GOLD if tag else LINE)) + f'<rect x="{x + 40}" y="{y - 3}" width="{70 + (k * 17 + i * 11) % 50}" height="6" rx="2" fill="{LINE}"/>'
        if i in (1, 3): card += t(x + 168, 292, "IDX", 9, GOLD, anchor="end", ls=1)
        s2 += reveal(card, 4.4 + i * .5) + ring(x + 90, 252, 4.4 + i * .5, GOLD, 8, 40, 1.0)
        if i < 3: s2 += reveal(arrow(x + 180, 252, x + 220, 252, GOLD), 6.2 + i * .2, .3)
    cs, _ = chips(80, 312, ["PRIMARY + FOREIGN KEYS", "CHECK / NOT NULL CONSTRAINTS", "INDEXES FOR FAST LOOKUPS"], 840, 11, 14, GOLD)
    s2 += reveal(cs, 7.0)

    OFF[0] = 4
    # 3 SQL: CTE + LAG, budgets
    code = ["WITH monthly AS (", "  SELECT month, SUM(amount) AS total", "  FROM expenses GROUP BY month)", "SELECT month, total,",
            "  total - LAG(total) OVER (ORDER BY month) AS change", "FROM monthly;"]
    s3 = f'<rect x="52" y="194" width="410" height="142" rx="6" fill="#0a0908" stroke="{LINE}"/>'
    for i, ln in enumerate(code):
        s3 += typed(64, 218 + i * 20, ln.replace("  ", "  "), 11.5, GOLD if ln.startswith(("WITH", "SELECT")) else INK, 8.3 + i * .38, .35)
    s3 += t(500, 206, "MONTH-OVER-MONTH CHANGE + BUDGET", 9.5, GOLD, ls=2)
    hs = [50, 70, 62, 95, 80, 60]
    for i, h in enumerate(hs):
        x, s = 520 + i * 68, 8.8 + i * .25
        s3 += (f'<rect x="{x}" y="326" width="40" height="0" rx="2" fill="{GOLD}" fill-opacity=".75">' + A("height", [(s, 0), (s + .5, h)]) + A("y", [(s, 326), (s + .5, 326 - h)]) + '</rect>'
               + t(x + 20, 340, f"M{i + 1}", 9, DIM, anchor="middle"))
    for i in range(5):
        x1, y1, x2, y2 = 520 + i * 68 + 20, 326 - hs[i] - 8, 520 + (i + 1) * 68 + 20, 326 - hs[i + 1] - 8
        s3 += reveal(arrow(x1 + 8, y1, x2 - 8, y2, GREEN if hs[i + 1] < hs[i] else RED, flow=False, sw=1.4), 10.6 + i * .2, .3)
    s3 += reveal(f'<line x1="506" y1="238" x2="930" y2="238" stroke="{GOLD}" stroke-dasharray="6 4"/>' + t(930, 230, "BUDGET", 9, GOLD, anchor="end", ls=2), 11.0)
    s3 += reveal(f'<rect x="{520 + 3 * 68}" y="{326 - 95}" width="40" height="95" rx="2" fill="{RED}"/>', 11.3)

    OFF[0] = 8
    # 4 quick add
    s4 = (t(80, 200, "NATURAL-LANGUAGE QUICK ADD  ·  SAMPLE INPUT", 9.5, GOLD, ls=2)
          + f'<rect x="80" y="208" width="520" height="44" rx="6" fill="none" stroke="{GOLD}" stroke-width="1.6"/>' + t(96, 237, ">", 20, GOLD)
          + typed(118, 237, "coffee 120 yesterday", 18, INK, 12.4, 1.4)
          + reveal(arrow(340, 254, 340, 284, GOLD), 13.9, .3))
    for i, (lab, val) in enumerate([("AMOUNT", "120"), ("CATEGORY", "coffee"), ("DATE", "yesterday")]):
        x = 80 + i * 180
        s4 += reveal(f'<rect x="{x}" y="288" width="160" height="50" rx="6" fill="{PANEL2}" stroke="{LINE}"/>' + t(x + 14, 306, lab, 9, DIM, ls=2) + t(x + 14, 328, val, 17, INK), 14.2 + i * .3)
    s4 += reveal(f'<rect x="650" y="208" width="290" height="130" rx="8" fill="{GREEN}" fill-opacity=".06" stroke="{GREEN}"/>' + t(672, 244, "EXPENSE ADDED", 22, GREEN, DISP, ls=2)
                 + t(672, 272, "no form to fill in", 15, INK, SERIF, style="italic") + t(672, 294, "saved through the same service layer", 12.5, DIM, SERIF, style="italic")
                 + t(672, 316, "as the web UI and the CLI", 12.5, DIM, SERIF, style="italic"), 15.0)
    s4 += reveal(arrow(560, 313, 650, 290, GREEN, flow=False), 15.0, .3)

    # 5 recurring payments
    s5 = (t(64, 214, "REPEATING PATTERN IN THE LEDGER", 11, DIM, ls=2) + f'<line x1="70" y1="290" x2="930" y2="290" stroke="{LINE}" stroke-width="1.5"/>')
    other = [(232, 258, 244), (270, 238, 262), (246, 226, 276), (262, 244, 234), (236, 272, 250), (268, 230, 258)]
    for i in range(6):
        x = 110 + i * 150
        for k, oy in enumerate(other[i]): s5 += f'<circle cx="{x + 24 + k * 24}" cy="{oy}" r="4" fill="#6b6354" fill-opacity=".7"/>'
        s5 += f'<circle cx="{x}" cy="290" r="7" fill="#6b6354"/>' + t(x, 316, f"MONTH {i + 1}", 9.5, DIM, anchor="middle", ls=1)
        s5 += reveal(f'<circle cx="{x}" cy="290" r="8" fill="{GOLD}"/>', 17.0 + i * .35, .2) + ring(x, 290, 17.0 + i * .35, GOLD, 8, 26, .8)
    s5 += (f'<rect x="110" y="289" width="0" height="2" fill="{GOLD}">' + A("width", [(17.0, 0), (19.1, 750)]) + '</rect>'
           + reveal(f'<rect x="650" y="196" width="280" height="28" rx="14" fill="{GOLD}" fill-opacity=".16" stroke="{GOLD}"/>' + t(790, 215, "RECURRING PAYMENT FLAGGED", 11, GOLD, anchor="middle", ls=2), 19.2))

    OFF[0] = 12
    # 6 CI
    s6 = ""
    names = [("COMMIT", "git push"), ("PYTEST", "tests pass"), ("DOCKER", "container image"), ("GITHUB ACTIONS", "CI on every push")]
    for i, (nm, sb) in enumerate(names):
        x = 60 + i * 230
        s6 += node(x, 214, 180, 64, nm, sb, [(20.4 + i * .9, 21.3 + i * .9, GREEN)], tsize=18) + check(x + 176, 218, 21.0 + i * .9)
        if i < 3: s6 += arrow(x + 180, 246, x + 230, 246)
    s6 += packet([(20.4, 150, 246), (21.3, 380, 246), (22.2, 610, 246), (23.1, 840, 246)])
    s6 += reveal(t(500, 322, "ALL CHECKS PASSED  ·  READY TO SHIP", 22, GREEN, DISP, "middle", ls=3), 23.2)

    OFF[0] = 0
    # NEW 3: constraints guard the data (8-12)
    k3 = t(944, 198, "ILLUSTRATIVE", 9, DIM, anchor="end", ls=2)
    for row, (inp, good, ta) in enumerate([("amount = -50", False, 8.3), ("amount = 50 , category = 'food'", True, 10.3)]):
        y = 206 + row * 66
        col = GREEN if good else RED
        k3 += (f'<rect x="64" y="{y}" width="300" height="44" rx="6" fill="none" stroke="{GOLD if good else RED}" stroke-width="1.4"/>' + t(78, y + 28, ">", 16, GOLD)
               + typed(98, y + 28, inp, 14, INK, ta, .8))
        k3 += packet([(ta + .9, 366, y + 22), (ta + 1.5, 430, y + 22)], col, 5)
        k3 += reveal(f'<rect x="436" y="{y}" width="250" height="44" rx="6" fill="{col}" fill-opacity=".08" stroke="{col}"/>'
                     + t(561, y + 20, "CHECK / NOT NULL", 12, col, DISP, "middle", ls=2) + t(561, y + 36, "constraint inspects the row", 9.5, DIM, anchor="middle"), ta + 1.4, .25)
        k3 += reveal(arrow(688, y + 22, 726, y + 22, col, flow=False), ta + 1.7, .2)
        k3 += reveal(f'<rect x="730" y="{y}" width="200" height="44" rx="22" fill="{col}" fill-opacity=".14" stroke="{col}"/>'
                     + t(830, y + 28, "SAVED" if good else "REJECTED", 18, col, DISP, "middle", ls=3), ta + 1.9, .25)
        k3 += reveal(check(710, y - 6, 0, GREEN) if good else f'<path d="M703 {y - 12} l14 12 M717 {y - 12} l-14 12" stroke="{RED}" stroke-width="3" stroke-linecap="round"/>', ta + 1.9, .2)
    k3 += reveal(t(500, 338, "BAD DATA IS STOPPED AT THE DATABASE, NOT JUST IN THE UI", 11, DIM, anchor="middle", ls=3), 11.2)

    # NEW 5: budgets flag overspend (16-20)
    k5 = t(944, 198, "ILLUSTRATIVE", 9, DIM, anchor="end", ls=2)
    for i, (lab, lim, val) in enumerate([("FOOD", 380, 250), ("TRAVEL", 340, 300), ("BILLS", 360, 470)]):
        y = 214 + i * 40
        st = 16.4 + i * .5
        k5 += t(64, y + 14, lab, 12, INK, ls=2) + f'<rect x="150" y="{y}" width="560" height="18" rx="4" fill="{LINE}"/>'
        k5 += f'<rect x="150" y="{y}" width="0" height="18" rx="4" fill="{GOLD}">' + A("width", [(st, 0), (st + 1.0, min(val, lim))]) + '</rect>'
        if val > lim:
            k5 += f'<rect x="{150 + lim}" y="{y}" width="0" height="18" rx="2" fill="{RED}">' + A("width", [(st + 1.0, 0), (st + 1.6, val - lim)]) + '</rect>'
        k5 += f'<line x1="{150 + lim}" y1="{y - 4}" x2="{150 + lim}" y2="{y + 22}" stroke="{INK}" stroke-width="2" stroke-dasharray="3 3"/>'
    k5 += t(150 + 360, 205, "BUDGET LIMIT", 9, INK, anchor="middle", ls=2)
    k5 += reveal(f'<rect x="740" y="214" width="190" height="100" rx="8" fill="{RED}" fill-opacity=".08" stroke="{RED}"/>'
                 + t(835, 252, "OVER BUDGET", 20, RED, DISP, "middle", ls=2) + t(835, 276, "this category is flagged", 11, DIM, SERIF, "middle", style="italic")
                 + t(835, 296, "before the month ends", 11, DIM, SERIF, "middle", style="italic"), 18.4, .3)
    k5 += reveal(arrow(706, 294, 740, 276, RED, flow=False), 18.4, .2)

    # NEW 8: pytest (28-32)
    k8 = (f'<rect x="64" y="196" width="520" height="140" rx="6" fill="#0a0908" stroke="{LINE}"/>' + t(80, 218, "TERMINAL  ·  ILLUSTRATIVE", 9.5, GOLD, ls=2)
          + typed(80, 248, "$ pytest", 15, GOLD, 28.2, .5)
          + typed(80, 278, "..................", 18, GREEN, 28.8, 1.8, weight="bold")
          + f'<rect x="80" y="298" width="470" height="8" rx="4" fill="{LINE}"/><rect x="80" y="298" width="0" height="8" rx="4" fill="{GREEN}">' + A("width", [(28.8, 0), (30.6, 470)]) + '</rect>'
          + reveal(t(80, 326, "all tests passed", 13, GREEN), 30.7, .3))
    k8 += reveal(f'<rect x="630" y="206" width="300" height="120" rx="8" fill="{GREEN}" fill-opacity=".07" stroke="{GREEN}"/>' + t(780, 262, "PASSED", 44, GREEN, DISP, "middle", ls=4)
                 + t(780, 292, "validated before it ships", 13, DIM, SERIF, "middle", style="italic"), 30.8, .3) + check(912, 224, 30.9)

    scenes = [
        (0, 4, "One request, four layers", "Web UI and CLI call a Flask REST API, which hands off to a Python OOP service layer that owns the business rules and talks to SQLite.", s1),
        (4, 8, "A solid SQLite schema", "Four tables with constraints and indexes keep the data consistent and the lookups fast.", s2),
        (8, 12, "Constraints guard the data", "A bad row, such as a negative amount, is refused by the database itself; a valid one goes straight through.", k3),
        (12, 16, "SQL that explains the spend", "A CTE plus LAG gives month-over-month change, so a rise or fall is a number, not a guess.", s3),
        (16, 20, "Budgets flag overspend", "Each category is measured against its budget, and the ones that run over are flagged.", k5),
        (20, 24, "Quick add in plain English", "Type an expense the way you would say it. Natural-language quick add turns it into a structured record.", s4),
        (24, 28, "Recurring payments, spotted", "Repeating charges are detected from the history, so subscriptions and bills stand out.", s5),
        (28, 32, "Tested with pytest", "Pytest checks the code, so a change is validated before it goes out.", k8),
        (32, 36, "Containerised and CI'd", "Docker packages it, and GitHub Actions runs the checks on every push.", s6),
    ]
    frame("x-spendwise.svg", "SPENDWISE · FULL-STACK TRACKER", scenes, base, "Animated walkthrough of Spendwise: request path through UI, Flask API, service layer and SQLite, then SQL insights, quick add, recurring payments and CI")


def build_all():
    gramsathi(); dashboard(); spendwise()
