"""Jarvis 3D kit. Real 3D maths (rotation, perspective, depth) is baked into SMIL keyframes, so every SVG is
self-contained and animates in real time on GitHub (no JavaScript, no external files).
Called from build.py. Only palette constants are used for colour, so every theme works."""
import math, textwrap, random
from xml.sax.saxutils import escape as E
import build as B
from build import BG, INK, DIM, RED, GOLD, LINE, GREEN, DISP, SERIF, MONO, t, svg, chips

PANEL, PANEL2, ARW, MUTE, AB = "#0e0c0a", "#14110e", "#4a4237", "#6b6354", "#5ac8ff"
rad = math.radians
_id = [0]


def uid(p="u"):
    _id[0] += 1
    return f"{p}{_id[0]}"


def n1(v):
    s = f"{v:.1f}"
    return s[:-2] if s.endswith(".0") else (s if s != "-0.0" else "0")


def n3(v):
    s = f"{v:.3f}".rstrip("0").rstrip(".")
    return s if s not in ("", "-0") else "0"


def ph(i, N):
    return 2 * math.pi * i / N


def anim(attr, vals, dur, extra=""):
    return f'<animate attributeName="{attr}" values="{";".join(vals)}" dur="{dur}s" repeatCount="indefinite" {extra}/>'


def tf(kind, vals, dur, extra=""):
    return f'<animateTransform attributeName="transform" type="{kind}" values="{";".join(vals)}" dur="{dur}s" repeatCount="indefinite" {extra}/>'


def spin(inner, dur, rev=False, cx=0, cy=0):
    a, b = (360, 0) if rev else (0, 360)
    return f'<g><animateTransform attributeName="transform" type="rotate" from="{a} {cx} {cy}" to="{b} {cx} {cy}" dur="{dur}s" repeatCount="indefinite"/>{inner}</g>'


def pulse(attr, lo, hi, dur, begin=0):
    return f'<animate attributeName="{attr}" values="{lo};{hi};{lo}" dur="{dur}s" begin="{begin}s" repeatCount="indefinite"/>'


def brackets(x, y, w, h, col=GOLD, l=20, sw=2, op=1):
    return (f'<path d="M{x} {y+l} V{y} H{x+l} M{x+w-l} {y} H{x+w} V{y+l} M{x+w} {y+h-l} V{y+h} H{x+w-l} M{x+l} {y+h} H{x} V{y+h-l}" '
            f'fill="none" stroke="{col}" stroke-width="{sw}" opacity="{op}"/>')


CORE_DEFS = (f'<defs><radialGradient id="core"><stop offset="0" stop-color="{INK}"/><stop offset=".22" stop-color="{INK}" stop-opacity=".95"/>'
             f'<stop offset=".5" stop-color="{GOLD}" stop-opacity=".6"/><stop offset="1" stop-color="{GOLD}" stop-opacity="0"/></radialGradient>'
             f'<radialGradient id="aura"><stop offset="0" stop-color="{GOLD}" stop-opacity=".34"/><stop offset=".55" stop-color="{GOLD}" stop-opacity=".08"/><stop offset="1" stop-color="{GOLD}" stop-opacity="0"/></radialGradient>'
             f'<filter id="blur" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="3.5"/></filter>'
             f'<filter id="blur2" x="-80%" y="-80%" width="260%" height="260%"><feGaussianBlur stdDeviation="9"/></filter></defs>')


# =============================================================== 3D primitives
def layer(content, z0, cx, cy, yaw, pitch, ex, T, sc=1.0, D=1150):
    """A flat drawing (origin = its centre) placed at depth z0 and rotated by yaw (per-frame list, radians) with a fixed
    camera pitch. Orthographic rotation about the vertical axis + perspective, exact for a planar layer:
    translate(layer centre) . skewY . scale  ==  the projected 2x2 matrix, baked per frame."""
    sp, cp = math.sin(pitch), math.cos(pitch)
    tr, sk, sl = [], [], []
    for th, e in zip(yaw, ex):
        z = z0 * e * sc
        zc = z * math.cos(th)
        s = D / (D - zc)
        tr.append(f"{n1(cx + z * math.sin(th) * s)} {n1(cy + zc * sp * s)}")
        sk.append(n3(math.degrees(math.atan(-math.tan(th) * sp))))
        sl.append(f"{n3(sc * math.cos(th) * s)} {n3(sc * cp * s)}")
    return f'<g>{tf("translate", tr, T)}<g>{tf("skewY", sk, T)}<g>{tf("scale", sl, T)}{content}</g></g></g>'


def holo(x, y, w, h, th0, amp, phase, inner, N=40, T=9, D=900, fill=PANEL2, stroke=LINE, edge=GOLD, glow=True):
    """A card hanging in 3D. Outline = exact perspective trapezoid; contents ride an affine fit (skewY + scale),
    so text stays crisp. Yaw swings by `amp` around `th0` (radians) in real time."""
    cxc, cyc = x + w / 2, y + h / 2
    pts, top, sk, sl = [], [], [], []
    for i in range(N + 1):
        th = th0 + amp * math.sin(ph(i, N) + phase)
        c, s_ = math.cos(th), math.sin(th)
        cs = []
        for px, py in ((-w / 2, -h / 2), (w / 2, -h / 2), (w / 2, h / 2), (-w / 2, h / 2)):
            sf = D / (D + px * s_)
            cs.append((cxc + px * c * sf, cyc + py * sf))
        pts.append(" ".join(f"{n1(a)},{n1(b)}" for a, b in cs))
        top.append(f"{n1(cs[0][0])},{n1(cs[0][1])} {n1(cs[1][0])},{n1(cs[1][1])}")
        dx = cs[1][0] - cs[0][0]
        sk.append(n3(math.degrees(math.atan2(cs[1][1] - cs[0][1], dx))))
        sl.append(f"{n3(dx / w)} {n3((cs[3][1] - cs[0][1] + cs[2][1] - cs[1][1]) / (2 * h))}")
    clip = uid("hc")
    body = (f'<polygon points="{pts[0]}" fill="{fill}" fill-opacity=".9" stroke="{stroke}" stroke-width="1.5">{anim("points", pts, T)}</polygon>'
            f'<polyline points="{top[0]}" fill="none" stroke="{edge}" stroke-width="2.5" stroke-linecap="round">{anim("points", top, T)}</polyline>'
            f'<g transform="translate({n1(cxc)} {n1(cyc)})"><g>{tf("skewY", sk, T)}'
            f'<g>{tf("scale", sl, T)}<g transform="translate({n1(-w/2)} {n1(-h/2)})">'
            f'<clipPath id="{clip}"><rect width="{w}" height="{h}"/></clipPath>'
            f'<g clip-path="url(#{clip})"><rect x="-120" y="-10" width="70" height="{h+20}" fill="{GOLD}" opacity=".07" transform="skewX(-20)">'
            f'<animate attributeName="x" values="-120;{w+80};{w+80}" keyTimes="0;.45;1" dur="{T*.9:.1f}s" begin="{phase:.2f}s" repeatCount="indefinite"/></rect></g>'
            f'{inner}</g></g></g></g>')
    return body


# =============================================================== floor grid + sky
def floor(W, H, yh, vx=None, col=GOLD, clipw=None):
    vx = W / 2 if vx is None else vx
    s = f'<clipPath id="fl"><rect x="0" y="{yh}" width="{clipw or W}" height="{H-yh}"/></clipPath><g clip-path="url(#fl)">'
    for k in range(-16, 17):
        s += f'<line x1="{vx + k*12}" y1="{yh}" x2="{vx + k*190}" y2="{H}" stroke="{col}" stroke-opacity="{.28 if k % 4 == 0 else .13}" stroke-width="1"/>'
    n, dz, F = 15, .42, 14
    for j in range(n + 1):
        ys, os_ = [], []
        for f in range(F + 1):
            z = 1 + (j - f / F) * dz
            z = max(z, .25)
            y = yh + (H - yh) / z
            ys.append(n1(y))
            os_.append(n3(max(0, min(.55, (y - yh) / (H - yh) * .55))))
        s += (f'<rect x="0" width="{W}" height="1.3" fill="{col}" y="{ys[0]}" opacity="{os_[0]}">{anim("y", ys, 3.2)}{anim("opacity", os_, 3.2)}</rect>')
    s += '</g>'
    s += f'<rect x="0" y="{yh}" width="{clipw or W}" height="60" fill="url(#hz)"/>'
    return s


HZ_DEF = lambda: f'<defs><linearGradient id="hz" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{GOLD}" stop-opacity=".22"/><stop offset="1" stop-color="{GOLD}" stop-opacity="0"/></linearGradient></defs>'


def stars(W, H, n=60, seed=3, maxy=None):
    random.seed(seed)
    maxy = maxy or H
    s = ""
    for _ in range(n):
        x, y = random.randint(8, W - 8), random.randint(8, maxy)
        r = random.choice([.7, 1, 1.4])
        s += (f'<circle cx="{x}" cy="{y}" r="{r}" fill="{INK}" opacity=".4"><animate attributeName="opacity" values=".1;.85;.1" dur="{random.uniform(2.5,6):.1f}s" '
              f'begin="{random.uniform(0,3):.1f}s" repeatCount="indefinite"/></circle>')
    # rising data motes
    for _ in range(14):
        x, y0 = random.randint(30, W - 30), random.randint(maxy // 2, maxy)
        d = random.uniform(7, 14)
        s += (f'<rect x="{x}" y="{y0}" width="2" height="6" fill="{GOLD}" opacity="0"><animate attributeName="y" values="{y0};{y0-160}" dur="{d:.1f}s" repeatCount="indefinite"/>'
              f'<animate attributeName="opacity" values="0;.6;0" dur="{d:.1f}s" repeatCount="indefinite"/></rect>')
    return s


# =============================================================== ARC REACTOR
def wedge(r1, r2, a0, a1):
    p = lambda r, a: (r * math.cos(rad(a)), r * math.sin(rad(a)))
    x1, y1 = p(r2, a0); x2, y2 = p(r2, a1); x3, y3 = p(r1, a1); x4, y4 = p(r1, a0)
    return f"M{x1:.1f} {y1:.1f} A{r2} {r2} 0 0 1 {x2:.1f} {y2:.1f} L{x3:.1f} {y3:.1f} A{r1} {r1} 0 0 0 {x4:.1f} {y4:.1f} Z"


def reactor(cx, cy, sc, N=48, T=12, amp=30, pitch=14, explode=False, coils=None, cycle=12, ring_text=None):
    """Mark-style arc reactor: six depth layers, yaw swinging in real time, optional exploded view and coil sequencing."""
    yaw = [rad(amp) * math.sin(ph(i, N)) for i in range(N + 1)]
    ex = [1 + .95 * (.5 - .5 * math.cos(ph(i, N))) if explode else 1 for i in range(N + 1)]
    nco = len(coils) if coils else 10
    # housing
    h = f'<circle r="152" fill="{BG}" fill-opacity=".92" stroke="{LINE}" stroke-width="3"/><circle r="146" fill="none" stroke="{GOLD}" stroke-opacity=".55" stroke-width="1.5"/>'
    for k in range(12):
        a = rad(k * 30 + 15)
        h += f'<circle cx="{134*math.cos(a):.1f}" cy="{134*math.sin(a):.1f}" r="5.5" fill="{PANEL}" stroke="{GOLD}" stroke-opacity=".7"/><circle cx="{134*math.cos(a):.1f}" cy="{134*math.sin(a):.1f}" r="1.8" fill="{GOLD}" opacity=".8"/>'
    tk = "".join(f'<line x1="{150*math.cos(rad(a*4)):.1f}" y1="{150*math.sin(rad(a*4)):.1f}" x2="{(143 if a%5 else 139)*math.cos(rad(a*4)):.1f}" y2="{(143 if a%5 else 139)*math.sin(rad(a*4)):.1f}" stroke="{GOLD}" stroke-opacity=".7"/>' for a in range(90))
    h += spin(tk, 90)
    # coil ring
    c = f'<circle r="109" fill="none" stroke="{PANEL}" stroke-width="40"/><circle r="130" fill="none" stroke="{RED}" stroke-opacity=".75" stroke-width="2"/><circle r="88" fill="none" stroke="{RED}" stroke-opacity=".55" stroke-width="1.5"/>'
    span = 360 / nco
    for k in range(nco):
        a0, a1 = -90 + k * span + 3, -90 + (k + 1) * span - 3
        d = wedge(92, 127, a0, a1)
        s, e = k / nco, (k + 1) / nco
        if k == 0: kt, vv = "0;%s;%s;1" % (n3(e), n3(e + .02)), ".95;.95;.16;.16"
        elif k == nco - 1: kt, vv = "0;%s;%s;1" % (n3(s), n3(s + .02)), ".16;.16;.95;.95"
        else: kt, vv = "0;%s;%s;%s;%s;1" % (n3(s), n3(s + .02), n3(e), n3(e + .02)), ".16;.16;.95;.95;.16;.16"
        c += (f'<path d="{d}" fill="{PANEL}" stroke="{GOLD}" stroke-opacity=".5" stroke-width="1.2"/>'
              f'<path d="{d}" fill="{GOLD}" opacity=".16"><animate attributeName="opacity" values="{vv.replace(";", ";")}" keyTimes="{kt}" dur="{cycle}s" repeatCount="indefinite"/></path>')
        am = rad((a0 + a1) / 2)
        c += t(109.5 * math.cos(am), 109.5 * math.sin(am) + 4, f"{k+1:02d}", 11, INK, anchor="middle", ls=1)
    # mid rings
    m = (spin(f'<circle r="80" fill="none" stroke="{GOLD}" stroke-width="2.4" stroke-dasharray="64 16"/>', 22)
         + spin(f'<circle r="70" fill="none" stroke="{RED}" stroke-width="1.6" stroke-dasharray="3 8"/>', 14, True)
         + f'<circle r="62" fill="none" stroke="{GOLD}" stroke-opacity=".6"/>')
    # inner frame
    sp = "".join(f'<line x1="{20*math.cos(rad(a)):.1f}" y1="{20*math.sin(rad(a)):.1f}" x2="{58*math.cos(rad(a)):.1f}" y2="{58*math.sin(rad(a)):.1f}" stroke="{GOLD}" stroke-width="5" stroke-opacity=".8"/>' for a in (-90, -30, 30, 90, 150, 210))
    i3 = f'<circle r="58" fill="{BG}" fill-opacity=".55" stroke="{INK}" stroke-width="2"/>{sp}<circle r="22" fill="none" stroke="{INK}" stroke-opacity=".7"/>'
    # core
    tri = " ".join(f"{34*math.cos(rad(a)):.1f},{34*math.sin(rad(a)):.1f}" for a in (-90, 30, 150))
    co = (f'<circle r="46" fill="{GOLD}" filter="url(#blur2)" opacity=".7">{pulse("opacity", ".35", ".85", 2.4)}</circle>'
          f'<circle r="54" fill="url(#core)">{pulse("r", "46", "58", 2.4)}</circle>'
          f'<polygon points="{tri}" fill="{GOLD}" fill-opacity=".14" stroke="{INK}" stroke-width="3" stroke-linejoin="round"/>'
          f'<polygon points="{tri}" fill="none" stroke="{GOLD}" stroke-width="7" stroke-linejoin="round" filter="url(#blur)" opacity=".7"/>'
          f'<circle r="9" fill="{INK}">{pulse("opacity", "1", ".6", 1.6)}</circle>')
    # holo ring
    txt = ring_text or ["PYTHON", "SQL", "MYSQL", "POWER BI", "FLASK", "DOCKER", "GIT", "PYTEST"]
    s_ring = "   ·   ".join(txt) + "   ·   "
    pid = uid("rp")
    ho = (f'<path id="{pid}" d="M-172 0 A172 172 0 1 1 172 0 A172 172 0 1 1 -172 0" fill="none"/>'
          + spin(f'<text font-family="{MONO}" font-size="11" fill="{GOLD}" letter-spacing="2" opacity=".85"><textPath href="#{pid}" textLength="1072" lengthAdjust="spacing">{E(s_ring)}</textPath></text>', 60)
          + spin(f'<circle r="186" fill="none" stroke="{GOLD}" stroke-opacity=".5" stroke-dasharray="2 6"/>'
                 + "".join(f'<path d="M{186*math.cos(rad(a)):.1f} {186*math.sin(rad(a)):.1f} L{200*math.cos(rad(a)):.1f} {200*math.sin(rad(a)):.1f}" stroke="{GOLD}" stroke-width="2.5"/>' for a in (0, 90, 180, 270)), 36, True))
    out = (f'<ellipse cx="{cx}" cy="{cy + 150*sc}" rx="{170*sc}" ry="{22*sc}" fill="url(#aura)" opacity=".8"/>'
           f'<circle cx="{cx}" cy="{cy}" r="{250*sc}" fill="url(#aura)">{pulse("opacity", ".55", ".95", 3)}</circle>')
    for z, content in ((-75, h), (-38, c), (0, m), (38, i3), (74, co), (118, ho)):
        out += layer(content, z, cx, cy, yaw, rad(pitch), ex, T, sc=sc)
    return out


# =============================================================== HERO
def extruded(cx, y, text, size, width, depth, N, T, amp=2.0, front=INK, edge=GOLD, ls=0):
    """Name with real extrusion: the back copies slide sideways as the 'camera' swings, so the letters have depth."""
    out = ""
    for k in range(depth, 0, -1):
        xs = [n1(cx + k * amp * math.sin(ph(i, N))) for i in range(N + 1)]
        out += (f'<text x="{xs[0]}" y="{y + k*1.1:.1f}" font-family="{DISP}" font-size="{size}" fill="{PANEL}" stroke="{edge}" stroke-width=".9" '
                f'stroke-opacity="{max(.12, .75 - k*.07):.2f}" text-anchor="middle" textLength="{width}" lengthAdjust="spacingAndGlyphs">{anim("x", xs, T)}{E(text)}</text>')
    import jarvis_x as X
    out += X.glitch_name(cx, y, text, size, width, front, N)
    return out


def header():
    W, H, N, T = 1000, 590, 48, 12
    b = CORE_DEFS + HZ_DEF()
    b += f'<rect width="{W}" height="{H}" rx="10" fill="url(#glow)"/>' + stars(W, H, 40, maxy=380) + __import__('jarvis_x').warp(500, 200, W, H, 70, maxy=400) + floor(W, H, 408)
    # HUD frame
    b += (t(40, 36, "J.A.R.V.I.S  ·  PERSONAL INTERFACE  v2026", 11, GOLD, ls=4) + t(960, 36, "ALL SYSTEMS NOMINAL", 11, GREEN, anchor="end", ls=3)
          + f'<circle cx="940" cy="32" r="4" fill="{GREEN}">{pulse("opacity", "1", ".2", 1.2)}</circle>'
          + f'<line x1="40" y1="48" x2="960" y2="48" stroke="{LINE}"/><rect x="40" y="47" width="120" height="2" fill="{GOLD}"><animate attributeName="x" values="40;840;40" dur="9s" repeatCount="indefinite"/></rect>')
    # side readouts + leader lines
    L = [("CORE", "ONLINE", GREEN), ("POWER", "100 %", GOLD), ("LOC", "PUNE · IN", INK)]
    Rr = [("ROLES", "04", INK), ("PROJECTS", "03", INK), ("STATUS", "OPEN TO WORK", GREEN)]
    for i, (k, v, col) in enumerate(L):
        y = 110 + i * 54
        b += f'<rect x="40" y="{y-14}" width="3" height="40" fill="{RED}"/>' + t(54, y, k, 10, DIM, ls=4) + t(54, y + 24, v, 20, col, DISP, ls=2)
        b += f'<line x1="200" y1="{y+8}" x2="350" y2="{200 + (i-1)*18}" stroke="{GOLD}" stroke-opacity=".3" stroke-dasharray="3 5"><animate attributeName="stroke-dashoffset" from="0" to="-16" dur="1.4s" repeatCount="indefinite"/></line>'
    for i, (k, v, col) in enumerate(Rr):
        y = 110 + i * 54
        b += f'<rect x="957" y="{y-14}" width="3" height="40" fill="{RED}"/>' + t(946, y, k, 10, DIM, anchor="end", ls=4) + t(946, y + 24, v, 20, col, DISP, anchor="end", ls=2)
        b += f'<line x1="800" y1="{y+8}" x2="650" y2="{200 + (i-1)*18}" stroke="{GOLD}" stroke-opacity=".3" stroke-dasharray="3 5"><animate attributeName="stroke-dashoffset" from="0" to="-16" dur="1.4s" repeatCount="indefinite"/></line>'
    b += reactor(500, 200, .84, N=N, T=T)
    b += extruded(500, 438, "DEVENDRA RATHOD", 84, 800, 9, N, T)
    roles = ["PYTHON DEVELOPER", "SQL & DATABASE DEVELOPER", "DATA ANALYST", "ASPIRING DATA ENGINEER"]
    for i, role in enumerate(roles):
        a, bb, c, d = i * .25, i * .25 + .02, i * .25 + .23, i * .25 + .25
        if i == 0: kt, vals = "0;.23;.25;.98;1", "1;1;0;0;1"
        else: kt, vals = f"0;{a:g};{bb:g};{c:g};{d:g};1", "0;0;1;1;0;0"
        b += (f'<g opacity="{1 if i == 0 else 0}"><animate attributeName="opacity" values="{vals}" keyTimes="{kt}" dur="12s" repeatCount="indefinite"/>'
              + t(500, 478, role, 19, GOLD, anchor="middle", ls=8) + '</g>')
    b += t(500, 508, "AI & Data Science graduate  ·  B.E., PVG College of Engineering, SPPU  ·  2026", 15, DIM, SERIF, "middle", style="italic")
    b += (f'<rect x="318" y="526" width="364" height="32" rx="16" fill="{BG}" fill-opacity=".75" stroke="{GREEN}" stroke-opacity=".7"/>'
          f'<circle cx="344" cy="542" r="4.5" fill="{GREEN}">{pulse("opacity", "1", ".2", 1.8)}</circle>' + t(360, 546, "OPEN TO WORK · ENTRY-LEVEL ROLES", 11, GREEN, ls=1.5))
    b += (f'<rect width="{W}" height="{H}" rx="10" fill="url(#vig)"/>'
          + "".join(f'<line x1="0" y1="{y}" x2="{W}" y2="{y}" stroke="#000" stroke-opacity=".16"/>' for y in range(0, H, 4)))
    b += brackets(10, 10, W - 20, H - 20, GOLD, 28, 2)
    svg("header.svg", W, H, b, "Devendra Rathod: Python, SQL and data analytics. A Jarvis-style 3D interface with a rotating arc reactor")


# =============================================================== HUD: globe + terminal + radar
def globe(cx, cy, Rr, N=48, T=24, pin=(18.52, 73.86), tilt=-18, dots=70, seed=5):
    random.seed(seed)
    s = f'<circle cx="{cx}" cy="{cy}" r="{Rr}" fill="{GOLD}" fill-opacity=".05" stroke="{GOLD}" stroke-opacity=".6" stroke-width="1.5"/>'
    s += f'<g transform="rotate({tilt} {cx} {cy})">'
    for lat in (-60, -30, 0, 30, 60):
        yy = Rr * math.sin(rad(lat)); hw = Rr * math.cos(rad(lat))
        s += f'<line x1="{cx-hw:.1f}" y1="{cy-yy:.1f}" x2="{cx+hw:.1f}" y2="{cy-yy:.1f}" stroke="{GOLD}" stroke-opacity="{.5 if lat == 0 else .2}"/>'
    # meridians drift with the rotation; the dots show the true 3D spin
    PSI = [ph(i, N) for i in range(N + 1)]
    for k in range(8):
        rx = [n1(Rr * abs(math.sin(rad(k * 22.5) + p))) for p in PSI]
        s += f'<ellipse cx="{cx}" cy="{cy}" rx="{rx[0]}" ry="{Rr}" fill="none" stroke="{GOLD}" stroke-opacity=".2">{anim("rx", rx, T)}</ellipse>'
    pts = []
    for _ in range(dots):
        lat, lon = math.degrees(math.asin(random.uniform(-.92, .92))), random.uniform(0, 360)
        pts.append((lat, lon, random.choice([1.3, 1.8, 2.2])))
    for lat, lon, r_ in pts + [(pin[0], pin[1], 0)]:
        X, Y, Zs = [], [], []
        for p in PSI:
            lo = rad(lon) + p
            x, y, z = math.cos(rad(lat)) * math.sin(lo), -math.sin(rad(lat)), math.cos(rad(lat)) * math.cos(lo)
            X.append(n1(cx + x * Rr)); Y.append(n1(cy + y * Rr)); Zs.append(max(0, z))
        if r_ == 0:
            pX, pY, pZ = X, Y, Zs
            continue
        op = [n3(.15 + .85 * z) if z > .02 else "0" for z in Zs]
        s += f'<circle cx="{X[0]}" cy="{Y[0]}" r="{r_}" fill="{GOLD}">{anim("cx", X, T)}{anim("cy", Y, T)}{anim("opacity", op, T)}</circle>'
    po = [n3(min(1, z * 3)) for z in pZ]
    s += (f'<circle cx="{pX[0]}" cy="{pY[0]}" r="4.5" fill="{RED}">{anim("cx", pX, T)}{anim("cy", pY, T)}{anim("opacity", po, T)}</circle>'
          f'<circle cx="{pX[0]}" cy="{pY[0]}" r="5" fill="none" stroke="{RED}" stroke-width="1.5">{anim("cx", pX, T)}{anim("cy", pY, T)}'
          f'<animate attributeName="r" values="5;20" dur="1.8s" repeatCount="indefinite"/><animate attributeName="opacity" values=".9;0" dur="1.8s" repeatCount="indefinite"/></circle>')
    s += '</g>'
    s += spin(f'<circle cx="{cx}" cy="{cy}" r="{Rr+12}" fill="none" stroke="{GOLD}" stroke-opacity=".6" stroke-dasharray="40 14 4 14" stroke-width="1.6"/>', 30, False, cx, cy)
    return s


def hud():
    W, H, CYC = 1000, 350, 14
    b = (CORE_DEFS + f'<rect width="{W}" height="{H}" rx="10" fill="url(#glow)"/>'
         f'<defs><pattern id="hex" width="28" height="48" patternUnits="userSpaceOnUse"><path d="M14 0 L28 8 V24 L14 32 L0 24 V8 Z" fill="none" stroke="{LINE}" stroke-width=".8"/></pattern></defs>'
         f'<rect width="{W}" height="{H}" rx="10" fill="url(#hex)" opacity=".5"/>')
    b += t(40, 34, "J.A.R.V.I.S  ·  LIVE CONSOLE", 11, GOLD, ls=4) + t(960, 34, "ALL SYSTEMS NOMINAL", 11, GREEN, anchor="end", ls=3)
    b += f'<circle cx="940" cy="30" r="4" fill="{GREEN}">{pulse("opacity", "1", ".2", 1.2)}</circle>'
    # globe
    b += globe(150, 178, 98) + t(150, 312, "BASE  ·  PUNE, MAHARASHTRA, IN", 10, GOLD, anchor="middle", ls=3)
    # terminal
    tx, ty = 330, 82
    b += f'<rect x="{tx-14}" y="{ty-30}" width="396" height="236" rx="6" fill="{BG}" fill-opacity=".72" stroke="{LINE}"/>' + t(tx, ty - 10, "BOOT SEQUENCE", 10, RED, ls=4)
    lines = [("> JARVIS: Good day. Profile online.", GOLD), ("> LOADING PYTHON · SQL · POWER BI … OK", INK), ("> ROLES COMPLETED ........... 04", INK),
             ("> PROJECTS ONLINE ........... 03", INK), ("> CREDENTIALS VERIFIED ...... 06", INK), ("> STATUS: OPEN TO WORK", GREEN)]
    for i, (ln, col) in enumerate(lines):
        y = ty + 24 + i * 28; a = .4 + i * 1.5; wd = len(ln) * 7.6 + 4
        kt = f"0;{a/CYC:.4f};{(a+1.1)/CYC:.4f};{(CYC-1.6)/CYC:.4f};{(CYC-1)/CYC:.4f};1"
        b += (f'<clipPath id="bt{i}"><rect x="{tx-1}" y="{y-14}" height="20" width="0"><animate attributeName="width" values="0;0;{wd:.0f};{wd:.0f};0;0" keyTimes="{kt}" dur="{CYC}s" repeatCount="indefinite"/></rect></clipPath>'
              + t(tx, y, ln, 12.5, col, extra=f'clip-path="url(#bt{i})"'))
    # voice waveform (jarvis speaking)
    wv = []
    for f in range(24):
        pts = []
        for k in range(61):
            x = tx + k * 6
            amp_ = 14 * math.sin(k / 60 * math.pi) * (0.55 + .45 * math.sin(f / 24 * 2 * math.pi + k * .5)) * math.sin(k * .9 + f / 24 * 4 * math.pi) * (0.6 + .4 * math.sin(k * .21 + f / 24 * 2 * math.pi))
            pts.append(f"{x},{n1(ty + 186 + amp_)}")
        wv.append(" ".join(pts))
    b += f'<polyline points="{wv[0]}" fill="none" stroke="{GOLD}" stroke-width="1.6" stroke-linejoin="round">{anim("points", wv + [wv[0]], 2.4)}</polyline>'
    b += t(tx, ty + 222, "VOICE  ·  JARVIS  ·  ACTIVE", 9, MUTE, ls=3)
    # radar
    rx, ry, rr = 850, 178, 108
    b += (f'<circle cx="{rx}" cy="{ry}" r="{rr}" fill="{GOLD}" fill-opacity=".04" stroke="{GOLD}" stroke-opacity=".55" stroke-width="1.5"/>'
          + "".join(f'<circle cx="{rx}" cy="{ry}" r="{rr*k/4}" fill="none" stroke="{LINE}"/>' for k in (1, 2, 3))
          + f'<line x1="{rx-rr}" y1="{ry}" x2="{rx+rr}" y2="{ry}" stroke="{LINE}"/><line x1="{rx}" y1="{ry-rr}" x2="{rx}" y2="{ry+rr}" stroke="{LINE}"/>')
    sweep = f'<path d="M{rx} {ry} L{rx+rr} {ry} A{rr} {rr} 0 0 0 {rx+rr*math.cos(rad(-60)):.1f} {ry+rr*math.sin(rad(-60)):.1f} Z" fill="{GOLD}" opacity=".22"/><line x1="{rx}" y1="{ry}" x2="{rx+rr}" y2="{ry}" stroke="{GOLD}" stroke-width="2"/>'
    b += spin(sweep, 6, False, rx, ry)
    for name, ang, dist in (("GRAMSATHI", 25, .5), ("SPENDWISE", 160, .5), ("MOTOROLA BI", 255, .75)):
        bx, by = rx + rr * dist * math.cos(rad(ang)), ry + rr * dist * math.sin(rad(ang))
        t0 = (ang % 360) / 360
        op = f"0;0;1;.2;0" if t0 > .02 else "1;.2;0"
        b += (f'<circle cx="{bx:.1f}" cy="{by:.1f}" r="4" fill="{GREEN}" opacity="0"><animate attributeName="opacity" values=".15;.15;1;.15;.15" keyTimes="0;{max(t0-.01,0):.3f};{t0:.3f};{min(t0+.3,.99):.3f};1" dur="6s" repeatCount="indefinite"/></circle>'
              + t(bx + 8, by + 4, name, 8.5, DIM, ls=1))
    b += t(rx, 312, "PROJECT RADAR  ·  3 CONTACTS", 10, GOLD, anchor="middle", ls=3)
    b += (f'<rect x="0" y="0" width="3" height="{H}" fill="{GOLD}" opacity=".3"><animate attributeName="x" values="0;{W};0" keyTimes="0;.5;1" dur="10s" repeatCount="indefinite"/></rect>')
    b += brackets(8, 8, W - 16, H - 16, GOLD, 24, 2) + f'<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="10" fill="none" stroke="{LINE}"/>'
    svg("hud.svg", W, H, b, "Jarvis console: rotating globe pinned on Pune, boot sequence, project radar. 4 roles, 3 projects online, 6 credentials verified, open to work")


# =============================================================== numbers
def numbers():
    W, H = 1000, 170
    items = [("4", "ROLES", "3 internships + JioFiber"), ("3", "PROJECTS", "Python · Power BI · Flask"), ("6", "CREDENTIALS", "courses, tests, workshop"), ("126", "TRAINING HRS", "Ethnus campus program")]
    ths = (14, 5, -5, -14)
    b = CORE_DEFS
    for i, (n, l, sub) in enumerate(items):
        w, h = 222, 118
        x = 14 + i * 247
        inner = (f'<path d="M0 0 H{w} V{h} H0 Z" fill="none"/>' + brackets(6, 6, w - 12, h - 12, GOLD, 12, 1.5, .8)
                 + t(w / 2, 66, n, 62, INK, DISP, "middle", extra=f'textLength="{len(n)*34}" lengthAdjust="spacingAndGlyphs"')
                 + t(w / 2, 88, l, 11, GOLD, anchor="middle", ls=4) + t(w / 2, 106, sub, 9.5, DIM, anchor="middle", ls=1))
        b += holo(x, 26, w, h, rad(ths[i]), rad(4), i * .9, inner, N=36, T=8)
    svg("numbers.svg", W, H, b, "4 roles, 3 projects, 6 credentials, 126 hours of training")


# =============================================================== EXPERIENCE (3D cards + featured JioFiber)
def role_inner(w, h, num, date, dur, title, co, bullets, tags, hot=False):
    col = RED if hot else GOLD
    s = t(w - 16, h - 14, num, 90, INK, DISP, "end", extra='opacity=".05"')
    s += t(22, 30, date, 11, col, ls=3) + t(w - 22, 30, dur, 11, DIM, anchor="end", ls=3)
    s += t(22, 66, title.upper(), 26, INK, DISP, ls=1.5, extra=f'textLength="{min(len(title)*14.2, w-50):.0f}" lengthAdjust="spacingAndGlyphs"') + t(22, 90, co, 17, col, SERIF, style="italic")
    y = 118
    for bl in bullets:
        for j, ln in enumerate(textwrap.wrap(bl, 56)):
            if j == 0: s += t(22, y, "▸", 14, col, SERIF)
            s += t(40, y, ln, 14, DIM, SERIF); y += 20
        y += 4
    cs, bot = chips(22, y + 4, tags, w - 44, size=10.5, gap=6, fill=INK)
    return s + cs, bot


def role_height(w, bullets, tags):
    y = 118
    for bl in bullets: y += 20 * len(textwrap.wrap(bl, 56)) + 4
    return chips(22, y + 4, tags, w - 44, size=10.5, gap=6)[1] + 26


def journey():
    W = 1000
    roles = [("01", "JUN – AUG 2025", "3 MO", "Data Analysis Intern", "Talent Battle",
              ["Cleaned structured datasets and performed EDA in Python to prepare analysis outputs that supported business insights."], ["Python", "EDA", "Data cleaning", "Business insights"]),
             ("02", "JAN – JUN 2026", "6 MO", "Software Engineer Intern", "XMEGA",
              ["Implemented features and tested and debugged code across the application.", "Investigated issues systematically and validated every change before completion."], ["Feature development", "Testing", "Debugging", "Validation"]),
             ("03", "JUL – AUG 2026", "2 MO", "Python Programming Intern", "Oasis Infobyte",
              ["Built Python programs through hands-on tasks, applying core concepts, application logic and problem solving."], ["Python", "Application logic", "Problem solving"])]
    cw = 452
    hs = [role_height(cw, r[5], r[6]) for r in roles]
    ys, y = [], 40
    for k, h in enumerate(hs):
        if k >= 2: y = max(y, ys[k - 2] + hs[k - 2] + 26)
        ys.append(y); y += max(150, h * .6)
    spine_end = ys[-1] + hs[-1] / 2
    jy = max(ys[k] + hs[k] for k in range(3)) + 70
    JH, JW = 372, 960
    end_y = jy + JH + 40
    H = end_y + 90
    b = CORE_DEFS + f'<line x1="500" y1="14" x2="500" y2="{jy}" stroke="{LINE}" stroke-width="2"/>'
    b += (f'<line x1="500" y1="14" x2="500" y2="14" stroke="{GOLD}" stroke-width="2.5"><animate attributeName="y2" values="14;{jy};{jy}" keyTimes="0;.75;1" dur="10s" repeatCount="indefinite"/></line>'
          f'<circle cx="500" cy="14" r="4" fill="{INK}"><animate attributeName="cy" values="14;{jy};{jy}" keyTimes="0;.75;1" dur="10s" repeatCount="indefinite"/></circle>')
    for k, (r, y_, h) in enumerate(zip(roles, ys, hs)):
        left = k % 2 == 0
        x = 14 if left else W - 14 - cw
        th0 = rad(15) if left else rad(-15)
        ny = y_ + 38
        # connector + node
        ex_ = x + cw if left else x
        b += (f'<line x1="500" y1="{ny}" x2="{ex_}" y2="{ny}" stroke="{GOLD}" stroke-opacity=".45" stroke-dasharray="3 5"><animate attributeName="stroke-dashoffset" from="0" to="-16" dur="1.4s" repeatCount="indefinite"/></line>'
              f'<circle cx="500" cy="{ny}" r="7" fill="{BG}" stroke="{GOLD}" stroke-width="2.5"/><circle cx="500" cy="{ny}" r="3" fill="{GOLD}">{pulse("opacity", "1", ".3", 2.2, k * .5)}</circle>')
        inner, _ = role_inner(cw, h, r[0], r[1], r[2], r[3], r[4], r[5], r[6])
        b += holo(x, y_, cw, h, th0, rad(4.5), k * 1.3, inner, N=40, T=10)
    # featured JioFiber card
    b += f'<line x1="500" y1="{jy}" x2="500" y2="{jy+30}" stroke="{RED}" stroke-width="2"/><circle cx="500" cy="{jy}" r="8" fill="{BG}" stroke="{RED}" stroke-width="2.5"/><circle cx="500" cy="{jy}" r="4" fill="{RED}">{pulse("opacity", "1", ".3", 1.6)}</circle>'
    inner = jio_inner(JW, JH)
    b += holo(20, jy + 30, JW, JH, 0, rad(2.5), 0, inner, N=40, T=12, fill=PANEL2, stroke=RED, edge=RED)
    # open to work
    ey = jy + 30 + JH + 34
    b += (f'<line x1="500" y1="{jy+30+JH}" x2="500" y2="{ey-4}" stroke="{GREEN}" stroke-opacity=".6"/>'
          f'<circle cx="500" cy="{ey}" r="6" fill="{GREEN}"/><circle cx="500" cy="{ey}" r="6" fill="none" stroke="{GREEN}"><animate attributeName="r" values="6;22" dur="1.8s" repeatCount="indefinite"/><animate attributeName="opacity" values=".9;0" dur="1.8s" repeatCount="indefinite"/></circle>'
          + t(500, ey + 38, "NOW  ·  OPEN TO WORK", 26, INK, DISP, "middle", ls=3)
          + t(500, ey + 62, "Entry-level Python development, SQL / database development, data analytics and AI / data roles", 14, GREEN, SERIF, "middle", style="italic"))
    H = int(ey + 80)
    svg("journey.svg", W, H, b, "Experience: Data Analysis Intern at Talent Battle, Software Engineer Intern at XMEGA, Python Programming Intern at Oasis Infobyte, and JioFiber Associate at Quess Corp Limited (Aug to Oct 2026)")


def jio_inner(w, h):
    s = t(w - 20, h - 18, "04", 150, INK, DISP, "end", extra='opacity=".04"')
    s += t(28, 34, "AUG – OCT 2026", 12, RED, ls=4) + t(190, 34, "·  3 MO", 12, DIM, ls=3)
    s += f'<rect x="{w-200}" y="16" width="176" height="26" rx="13" fill="none" stroke="{RED}" stroke-opacity=".8"/>' + t(w - 112, 33, "LATEST ROLE", 10.5, RED, anchor="middle", ls=4)
    s += t(28, 88, "JIOFIBER ASSOCIATE", 42, INK, DISP, ls=2) + t(28, 118, "Quess Corp Limited", 20, RED, SERIF, style="italic")
    y = 158
    for bl in ["Resolved customer and service issues for JioFiber operations by following defined processes and escalation procedures.",
               "Kept service records accurate and coordinated with internal teams for timely resolution."]:
        for j, ln in enumerate(textwrap.wrap(bl, 50)):
            if j == 0: s += t(28, y, "▸", 15, RED, SERIF)
            s += t(48, y, ln, 15.5, DIM, SERIF); y += 22
        y += 8
    cs, _ = chips(28, y + 8, ["Customer support", "Escalation procedures", "Service records", "Cross-team coordination", "Process discipline"], 470, size=11, fill=INK)
    s += cs
    # service-flow pipeline (derived from the role description)
    px, steps = 590, ["CUSTOMER ISSUE", "DEFINED PROCESS", "ESCALATION", "INTERNAL TEAMS", "RESOLVED + RECORDED"]
    s += t(px, 70, "SERVICE FLOW  ·  HOW A TICKET MOVES", 10, RED, ls=4)
    s += f'<line x1="{px+18}" y1="96" x2="{px+18}" y2="{96+len(steps)*46-46}" stroke="{LINE}" stroke-width="2"/>'
    C = 10
    for k, st in enumerate(steps):
        yy = 96 + k * 46
        a, e = 1 + k * 1.6, 1 + (k + 1) * 1.6 + .6
        s += (f'<circle cx="{px+18}" cy="{yy}" r="12" fill="{BG}" stroke="{RED if k == len(steps)-1 else GOLD}" stroke-width="2"/>'
              f'<circle cx="{px+18}" cy="{yy}" r="12" fill="{GREEN if k == len(steps)-1 else GOLD}" opacity="0"><animate attributeName="opacity" values="0;0;.9;.9;0;0" keyTimes="0;{a/C:.3f};{(a+.3)/C:.3f};{min(e/C,.97):.3f};{min((e+.3)/C,.98):.3f};1" dur="{C}s" repeatCount="indefinite"/></circle>'
              + t(px + 18, yy + 4, str(k + 1), 11, INK, anchor="middle")
              + t(px + 44, yy + 5, st, 13, INK, MONO, ls=2))
    s += (f'<circle cx="{px+18}" cy="96" r="5" fill="{INK}"><animate attributeName="cy" values="96;96;{96+4*46};{96+4*46};96" keyTimes="0;.08;.82;.95;1" dur="{C}s" repeatCount="indefinite"/></circle>')
    s += f'<line x1="{px-30}" y1="40" x2="{px-30}" y2="{h-30}" stroke="{LINE}"/>' + brackets(10, 10, w - 20, h - 20, RED, 18, 1.8, .9)
    return s


# =============================================================== credentials (3D wall)
def credentials():
    W = 1000
    items = [("Microsoft Power BI", "SKILL COURSE · SELF LEARNING · OCT 2026", "Dashboards, data modelling and reporting in Power BI.", "ID  SC-446DD41B7B"),
             ("SQL Course", "SKILL COURSE · SELF LEARNING · OCT 2026", "Querying and shaping relational data with SQL.", "ID  SC-C3C0FBBF48"),
             ("Google Data Analytics", "PROFESSIONAL CERTIFICATE · COURSERA", "End-to-end analytics workflow: ask, prepare, process, analyze, share.", ""),
             ("AI Tools & ChatGPT Workshop", "BE10X · JUL 2026", "Hands-on workshop on using AI tools and ChatGPT productively.", ""),
             ("Campus Recruitment Training", "ETHNUS · JUN – JUL 2025", "126 hours of industry-focused technical training.", "ID  R5PQ8TWJ"),
             ("TCS iON NQT (IT)", "NATIONAL QUALIFIER TEST · JUN 2026", "Cognitive 74.59% · Quant & Reasoning 64.84% · Python 65.91%", "")]
    cw, ch, g = 306, 172, 22
    th = (rad(13), 0, rad(-13))
    b = CORE_DEFS
    for i, (ti, me, de, cid) in enumerate(items):
        col, row = i % 3, i // 3
        x, y = 14 + col * (cw + g), 14 + row * (ch + 22)
        s = (f'<rect x="2" y="3" width="3" height="{ch-6}" fill="{RED}"/>' + t(cw - 16, 28, "✓", 15, GREEN, anchor="end")
             + t(20, 38, ti.upper(), 22, INK, DISP, ls=1, extra=f'textLength="{min(len(ti)*11.6, 250):.0f}" lengthAdjust="spacingAndGlyphs"')
             + t(20, 62, me, 9, GOLD, ls=1))
        for j, ln in enumerate(textwrap.wrap(de, 38)): s += t(20, 94 + j * 20, ln, 14.5, DIM, SERIF, style="italic")
        if cid: s += t(20, ch - 16, cid, 10, GREEN, ls=2)
        s += brackets(5, 5, cw - 10, ch - 10, GOLD, 10, 1.2, .5)
        b += holo(x, y, cw, ch, th[col], rad(4), i * .8, s, N=40, T=9)
    svg("credentials.svg", W, 2 * ch + 22 + 28, b, "Six credentials: Power BI, SQL, Google Data Analytics, AI tools workshop, Ethnus training, TCS iON NQT")


# =============================================================== SKILLS: 3D tag globe + categories
SKILLS = [("LANGUAGES & CORE", ["Python", "SQL", "JavaScript", "OOP", "Problem Solving", "Debugging", "Testing", "Backend Development"], GOLD),
          ("DATABASES", ["MySQL", "SQLite", "DBMS", "Joins", "Aggregation", "Database Integration"], AB),
          ("DATA & BI", ["Power BI", "Excel", "Data Cleaning", "EDA", "Data Visualization", "Dashboard Design"], GREEN),
          ("APIS & AI", ["REST API", "Flask", "JSON", "API Integration", "LLM API Integration", "Prompt Engineering", "ChatGPT & AI Tools"], RED),
          ("TOOLS", ["Git", "GitHub", "Docker", "pytest", "GitHub Actions", "Version Control", "Branching", "Commits", "Repository Management"], INK)]
BIG = {"Python", "SQL", "MySQL", "Power BI", "Flask", "Docker", "Git", "REST API", "Excel", "JavaScript"}


def skills():
    W, H, N, T = 1000, 520, 72, 28
    cx, cy, Rr, tilt = 300, 262, 190, rad(20)
    tags = [(n, col) for _, its, col in SKILLS for n in its]
    M = len(tags)
    b = CORE_DEFS + f'<rect width="{W}" height="{H}" rx="10" fill="url(#glow)"/>'
    b += f'<circle cx="{cx}" cy="{cy}" r="{Rr+60}" fill="url(#aura)"/>'
    # wire shell
    sp, cp = math.sin(tilt), math.cos(tilt)
    for lat in (-60, -30, 0, 30, 60):
        yy, rr = Rr * math.sin(rad(lat)), Rr * math.cos(rad(lat))
        b += f'<ellipse cx="{cx}" cy="{cy - yy*cp:.1f}" rx="{rr:.1f}" ry="{rr*sp:.1f}" fill="none" stroke="{GOLD}" stroke-opacity="{.4 if lat == 0 else .14}"/>'
    b += f'<circle cx="{cx}" cy="{cy}" r="{Rr}" fill="none" stroke="{GOLD}" stroke-opacity=".35"/>'
    b += spin(f'<circle cx="{cx}" cy="{cy}" r="{Rr+22}" fill="none" stroke="{GOLD}" stroke-opacity=".55" stroke-dasharray="46 12 4 12"/>', 40, False, cx, cy)
    b += spin(f'<circle cx="{cx}" cy="{cy}" r="{Rr+36}" fill="none" stroke="{RED}" stroke-opacity=".4" stroke-dasharray="2 8"/>', 26, True, cx, cy)
    golden = math.pi * (3 - math.sqrt(5))
    items = []
    for k, (name, col) in enumerate(tags):
        y = 1 - 2 * (k + .5) / M
        r_ = math.sqrt(1 - y * y)
        a = k * golden
        items.append((name, col, r_ * math.cos(a), y, r_ * math.sin(a)))
    frames = []
    for i in range(N + 1):
        psi = ph(i, N)
        fr = []
        for name, col, x, y, z in items:
            x1, z1 = x * math.cos(psi) + z * math.sin(psi), -x * math.sin(psi) + z * math.cos(psi)
            y2, z2 = y * math.cos(tilt) - z1 * math.sin(tilt), y * math.sin(tilt) + z1 * math.cos(tilt)
            s = 1100 / (1100 - z2 * Rr)
            fr.append((cx + x1 * Rr * s, cy + y2 * Rr * s, z2, s))
        frames.append(fr)
    # draw order: sort by mean depth of tag over the loop is constant? use initial depth; opacity handles the rest
    order = sorted(range(M), key=lambda k: frames[0][k][2])
    for k in order:
        name, col = items[k][0], items[k][1]
        base = 14 if name in BIG else 10.5
        tr = [f"{n1(f[k][0])} {n1(f[k][1])}" for f in frames]
        sc = [n3(f[k][3] * (.62 + .38 * (f[k][2] + 1) / 2)) for f in frames]
        op = [n3(.1 + .9 * ((f[k][2] + 1) / 2) ** 1.4) for f in frames]
        b += (f'<g opacity="{op[0]}">{anim("opacity", op, T)}<g>{tf("translate", tr, T)}<g>{tf("scale", [s + " " + s for s in sc], T)}'
              f'<text y="4" font-family="{MONO}" font-size="{base}" fill="{col}" text-anchor="middle" letter-spacing="1" font-weight="{"bold" if name in BIG else "normal"}">{E(name)}</text></g></g></g>')
    b += t(cx, H - 22, "36 SKILLS  ·  LIVE 3D ORBIT", 10, GOLD, anchor="middle", ls=4)
    # category panel
    px = 604
    b += f'<line x1="{px-24}" y1="30" x2="{px-24}" y2="{H-30}" stroke="{LINE}"/>' + t(px, 40, "SKILL MANIFEST", 12, RED, ls=5)
    y = 70
    for title, its, col in SKILLS:
        b += f'<rect x="{px}" y="{y-11}" width="9" height="9" fill="{col}" opacity=".9"/>' + t(px + 18, y - 2, title, 11, col, ls=3, weight="bold")
        y += 18
        for ln in textwrap.wrap("  ·  ".join(its), 44):
            b += t(px, y, ln, 12, DIM, MONO); y += 17
        y += 16
    b += brackets(8, 8, W - 16, H - 16, GOLD, 24, 2) + f'<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="10" fill="none" stroke="{LINE}"/>'
    svg("skills.svg", W, H, b, "Skills as a rotating 3D globe: Python, SQL, JavaScript, MySQL, SQLite, Power BI, Excel, Flask, REST APIs, Git, Docker, pytest, GitHub Actions and more")


# =============================================================== ARC REACTOR feature
def arc_reactor():
    W, H, N, T = 1000, 600, 56, 14
    coils = [("PYTHON", "Language · core of every project"), ("SQL", "Querying and shaping relational data"), ("MYSQL", "GramSathi: five-table e-governance schema"),
             ("POWER BI", "Motorola sales dashboard, KPI cards, slicers"), ("FLASK", "REST API + web UI for Spendwise"), ("REST + JSON", "AI complaint sorting over an API"),
             ("DOCKER", "Containerised Spendwise"), ("GIT + CI", "GitHub Actions on every push"), ("PYTEST", "Tests before every change ships"), ("EDA", "Cleaning data and finding the story")]
    b = CORE_DEFS + HZ_DEF() + f'<rect width="{W}" height="{H}" rx="10" fill="url(#glow)"/>' + stars(W, H, 45, seed=11, maxy=400)
    b += floor(W, H, 470, vx=300, clipw=600)
    b += reactor(300, 285, .98, N=N, T=T, amp=28, pitch=16, explode=True, coils=coils, cycle=12, ring_text=[c[0] for c in coils])
    # telemetry panel
    px = 640
    b += f'<line x1="{px-30}" y1="34" x2="{px-30}" y2="{H-34}" stroke="{LINE}"/>'
    b += t(px, 42, "ARC REACTOR  ·  MARK D", 12, RED, ls=5) + t(px, 88, "POWER CORE", 40, INK, DISP, ls=3)
    b += t(px, 110, "Ten coils, ten skills, one build pipeline.", 15, DIM, SERIF, style="italic")
    b += f'<line x1="{px}" y1="126" x2="{px+320}" y2="126" stroke="{LINE}"/>'
    for k, (nm, ds) in enumerate(coils):
        s, e = k / 10, (k + 1) / 10
        if k == 0: kt, vv = f"0;{e:g};{e+.02:g};1", "1;1;0;0"
        elif k == 9: kt, vv = f"0;{s:g};{s+.02:g};1", "0;0;1;1"
        else: kt, vv = f"0;{s:g};{s+.02:g};{e:g};{e+.02:g};1", "0;0;1;1;0;0"
        b += (f'<g opacity="{vv.split(";")[0]}"><animate attributeName="opacity" values="{vv}" keyTimes="{kt}" dur="12s" repeatCount="indefinite"/>'
              + t(px, 190, f"COIL {k+1:02d} / 10", 11, GOLD, ls=4) + t(px, 232, nm, 36, INK, DISP, ls=2)
              + "".join(t(px, 262 + j * 22, ln, 15, DIM, SERIF, style="italic") for j, ln in enumerate(textwrap.wrap(ds, 34))) + '</g>')
    # gauges
    gy = 340
    for i, (lab, val, col, d) in enumerate((("CORE TEMP", "NOMINAL", GREEN, 3.2), ("OUTPUT", "DASHBOARDS · APIS · ANSWERS", GOLD, 2.6), ("FUEL", "CURIOSITY", RED, 4.1))):
        y = gy + i * 56
        b += t(px, y, lab, 10, DIM, ls=4) + t(px + 320, y, val, 11, col, anchor="end", ls=2)
        b += f'<rect x="{px}" y="{y+10}" width="320" height="8" rx="4" fill="{LINE}"/>'
        wv = [n1(320 * (.78 + .2 * math.sin(ph(j, 16) * (1 + i * .0)))) for j in range(17)]
        b += f'<rect x="{px}" y="{y+10}" width="{wv[0]}" height="8" rx="4" fill="{col}" opacity=".85">{anim("width", wv, d * 4)}</rect>'
    # coil progress dots
    b += t(px, 530, "COIL SEQUENCE", 10, DIM, ls=4)
    for k in range(10):
        s, e = k / 10, (k + 1) / 10
        if k == 0: kt, vv = f"0;{e:g};{e+.02:g};1", ".95;.95;.18;.18"
        elif k == 9: kt, vv = f"0;{s:g};{s+.02:g};1", ".18;.18;.95;.95"
        else: kt, vv = f"0;{s:g};{s+.02:g};{e:g};{e+.02:g};1", ".18;.18;.95;.95;.18;.18"
        b += f'<rect x="{px + k*33}" y="544" width="27" height="10" rx="2" fill="{GOLD}" opacity=".18"><animate attributeName="opacity" values="{vv}" keyTimes="{kt}" dur="12s" repeatCount="indefinite"/></rect>'
    b += t(300, H - 24, "EXPLODED VIEW  ·  LIVE", 10, GOLD, anchor="middle", ls=5)
    b += (f'<rect width="{W}" height="{H}" rx="10" fill="url(#vig)"/>' + brackets(8, 8, W - 16, H - 16, GOLD, 26, 2) + f'<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="10" fill="none" stroke="{LINE}"/>')
    svg("arc-reactor.svg", W, H, b, "Arc reactor power core: an exploded 3D view whose ten coils light in turn, one per skill: Python, SQL, MySQL, Power BI, Flask, REST and JSON, Docker, Git and CI, pytest, EDA")


# =============================================================== project-card 3D motifs (right side of card)
def m_network3d(H, N=48, T=16):
    cx, cy, Rr, tl = 830, 118, 80, rad(22)
    random.seed(4)
    nodes = []
    for k in range(9):
        y = 1 - 2 * (k + .5) / 9
        r_ = math.sqrt(1 - y * y); a = k * 2.399
        nodes.append((r_ * math.cos(a), y, r_ * math.sin(a)))
    fr = []
    for i in range(N + 1):
        psi = ph(i, N); row = []
        for x, y, z in nodes:
            x1, z1 = x * math.cos(psi) + z * math.sin(psi), -x * math.sin(psi) + z * math.cos(psi)
            y2, z2 = y * math.cos(tl) - z1 * math.sin(tl), y * math.sin(tl) + z1 * math.cos(tl)
            s = 900 / (900 - z2 * Rr)
            row.append((cx + x1 * Rr * s, cy + y2 * Rr * s, z2))
        fr.append(row)
    s = CORE_DEFS + f'<circle cx="{cx}" cy="{cy}" r="{Rr+14}" fill="url(#aura)"/><circle cx="{cx}" cy="{cy}" r="{Rr}" fill="none" stroke="{GOLD}" stroke-opacity=".18" stroke-dasharray="2 5"/>'
    pairs = [(0, 3), (1, 4), (2, 5), (3, 6), (4, 7), (5, 8), (6, 0), (7, 1), (8, 2)]
    for k, (a, bb) in enumerate(pairs[:6]):
        c = [(f"{n1(f[a][0])}", f"{n1(f[a][1])}", f"{n1(f[bb][0])}", f"{n1(f[bb][1])}") for f in fr]
        s += (f'<line x1="{c[0][0]}" y1="{c[0][1]}" x2="{c[0][2]}" y2="{c[0][3]}" stroke="{GOLD}" stroke-opacity=".25">'
              + anim("x1", [q[0] for q in c], T) + anim("y1", [q[1] for q in c], T) + anim("x2", [q[2] for q in c], T) + anim("y2", [q[3] for q in c], T) + '</line>')
    for k in range(9):
        x2 = [n1(f[k][0]) for f in fr]; y2 = [n1(f[k][1]) for f in fr]
        s += (f'<line x1="{cx}" y1="{cy}" x2="{x2[0]}" y2="{y2[0]}" stroke="{GOLD}" stroke-opacity=".5" stroke-dasharray="3 4">{anim("x2", x2, T)}{anim("y2", y2, T)}'
              f'<animate attributeName="stroke-dashoffset" from="0" to="-14" dur="1.1s" repeatCount="indefinite"/></line>')
    for k in sorted(range(9), key=lambda k: fr[0][k][2]):
        x2 = [n1(f[k][0]) for f in fr]; y2 = [n1(f[k][1]) for f in fr]
        rr = [n3(3.5 + 3.2 * (f[k][2] + 1) / 2) for f in fr]; op = [n3(.35 + .65 * (f[k][2] + 1) / 2) for f in fr]
        s += f'<circle cx="{x2[0]}" cy="{y2[0]}" r="{rr[0]}" fill="{RED if k % 2 else GOLD}">{anim("cx", x2, T)}{anim("cy", y2, T)}{anim("r", rr, T)}{anim("opacity", op, T)}</circle>'
    s += f'<circle cx="{cx}" cy="{cy}" r="22" fill="{RED}">{pulse("r", "20", "24", 2)}</circle>' + t(cx, cy + 6, "AI", 16, INK, DISP, "middle", ls=1)
    return s


def m_bars3d(H, N=24, T=7):
    ox, oy, u = 830, 150, 30
    base = [.8, 1.5, 1.05, 1.9, 1.3, 1.7]
    cells = [(0, 0), (1, 0), (2, 0), (0, 1), (1, 1), (2, 1)]
    P = lambda gx, gy, h: (ox + (gx - gy) * u * .866, oy + (gx + gy) * u * .5 - h * 34)
    wd = .7
    s = CORE_DEFS + f'<circle cx="{ox}" cy="{oy-30}" r="95" fill="url(#aura)"/>'
    plat = [P(-.2, -.2, 0), P(3.2, -.2, 0), P(3.2, 2.2, 0), P(-.2, 2.2, 0)]
    s += f'<polygon points="{" ".join(f"{n1(a)},{n1(b)}" for a, b in plat)}" fill="{PANEL}" stroke="{GOLD}" stroke-opacity=".6"/>'
    for k in range(1, 3):
        a, b2 = P(k, -.2, 0), P(k, 2.2, 0); s += f'<line x1="{n1(a[0])}" y1="{n1(a[1])}" x2="{n1(b2[0])}" y2="{n1(b2[1])}" stroke="{GOLD}" stroke-opacity=".18"/>'
    a, b2 = P(-.2, 1, 0), P(3.2, 1, 0); s += f'<line x1="{n1(a[0])}" y1="{n1(a[1])}" x2="{n1(b2[0])}" y2="{n1(b2[1])}" stroke="{GOLD}" stroke-opacity=".18"/>'
    order = sorted(range(6), key=lambda k: cells[k][0] + cells[k][1])
    for k in order:
        gx, gy = cells[k]; x0, y0 = gx + (1 - wd) / 2, gy + (1 - wd) / 2
        col = RED if k % 2 else GOLD
        faces = {"top": [], "l": [], "r": []}
        for i in range(N + 1):
            h = base[k] * (.72 + .28 * math.sin(ph(i, N) + k * 1.1))
            pt = lambda a, b_, hh: P(a, b_, hh)
            T_ = [pt(x0, y0, h), pt(x0 + wd, y0, h), pt(x0 + wd, y0 + wd, h), pt(x0, y0 + wd, h)]
            Lf = [pt(x0, y0 + wd, h), pt(x0 + wd, y0 + wd, h), pt(x0 + wd, y0 + wd, 0), pt(x0, y0 + wd, 0)]
            Rf = [pt(x0 + wd, y0, h), pt(x0 + wd, y0 + wd, h), pt(x0 + wd, y0 + wd, 0), pt(x0 + wd, y0, 0)]
            for key, poly in (("top", T_), ("l", Lf), ("r", Rf)): faces[key].append(" ".join(f"{n1(a)},{n1(b)}" for a, b in poly))
        for key, op in (("l", .32), ("r", .58), ("top", .95)):
            s += f'<polygon points="{faces[key][0]}" fill="{col}" fill-opacity="{op}" stroke="{col}" stroke-width=".8">{anim("points", faces[key], T)}</polygon>'
    return s


def m_cube3d(H, N=48, T=14):
    cx, cy, r0 = 836, 116, 52
    def proj(pt, psi, phi, r):
        x, y, z = pt[0] * r, pt[1] * r, pt[2] * r
        x1, z1 = x * math.cos(psi) + z * math.sin(psi), -x * math.sin(psi) + z * math.cos(psi)
        y2, z2 = y * math.cos(phi) - z1 * math.sin(phi), y * math.sin(phi) + z1 * math.cos(phi)
        s = 700 / (700 - z2)
        return cx + x1 * s, cy + y2 * s
    V = [(a, b, c) for a in (-1, 1) for b in (-1, 1) for c in (-1, 1)]
    E_ = [(i, j) for i in range(8) for j in range(i + 1, 8) if sum(abs(V[i][k] - V[j][k]) for k in range(3)) == 2]
    def cube_d(i, r, rev=False):
        psi = ph(i, N) * (-1 if rev else 1); phi = rad(24) + rad(8) * math.sin(ph(i, N))
        P_ = [proj(v, psi, phi, r) for v in V]
        return "".join(f"M{n1(P_[a][0])} {n1(P_[a][1])}L{n1(P_[b][0])} {n1(P_[b][1])}" for a, b in E_)
    outer = [cube_d(i, r0) for i in range(N + 1)]
    inner = [cube_d(i, r0 * .5, True) for i in range(N + 1)]
    ring, sat = [], ([], [])
    for i in range(N + 1):
        psi = ph(i, N); phi = rad(24) + rad(8) * math.sin(ph(i, N))
        pts = [proj((1.55 * math.cos(a), 0, 1.55 * math.sin(a)), psi * .5, phi + rad(14), r0) for a in [k * 2 * math.pi / 40 for k in range(41)]]
        ring.append("M" + "L".join(f"{n1(a)} {n1(b)}" for a, b in pts))
        sp_ = proj((1.55 * math.cos(psi * 2), 0, 1.55 * math.sin(psi * 2)), psi * .5, phi + rad(14), r0)
        sat[0].append(n1(sp_[0])); sat[1].append(n1(sp_[1]))
    return (CORE_DEFS + f'<circle cx="{cx}" cy="{cy}" r="95" fill="url(#aura)"/>'
            f'<path d="{ring[0]}" fill="none" stroke="{RED}" stroke-opacity=".6" stroke-dasharray="3 4">{anim("d", ring, T)}</path>'
            f'<path d="{outer[0]}" fill="none" stroke="{GOLD}" stroke-width="2" stroke-linecap="round">{anim("d", outer, T)}</path>'
            f'<path d="{inner[0]}" fill="none" stroke="{INK}" stroke-width="1.5" stroke-opacity=".8" stroke-linecap="round">{anim("d", inner, T)}</path>'
            f'<circle cx="{sat[0][0]}" cy="{sat[1][0]}" r="5" fill="{RED}">{anim("cx", sat[0], T)}{anim("cy", sat[1], T)}</circle>')


# =============================================================== headings, dividers, footer, buttons
def heading(name, kicker, title, sub=""):
    N, T = 36, 8
    H = 138 if sub else 112
    b = t(500, 30, kicker.upper(), 12, RED, anchor="middle", ls=7)
    for k in range(5, 0, -1):
        xs = [n1(500 + k * 1.4 * math.sin(ph(i, N))) for i in range(N + 1)]
        b += (f'<text x="{xs[0]}" y="{86 + k*1.1:.1f}" font-family="{DISP}" font-size="54" fill="{PANEL}" stroke="{GOLD}" stroke-width=".8" stroke-opacity="{.7 - k*.1:.2f}" '
              f'text-anchor="middle" letter-spacing="3">{anim("x", xs, T)}{E(title.upper())}</text>')
    b += t(500, 86, title.upper(), 54, INK, DISP, "middle", ls=3)
    if sub: b += t(500, 114, sub, 16, DIM, SERIF, "middle", style="italic")
    b += (f'<line x1="300" y1="{H-8}" x2="700" y2="{H-8}" stroke="{LINE}"/><rect x="480" y="{H-10}" width="40" height="3" fill="{RED}"/>'
          f'<rect x="300" y="{H-9}" width="50" height="1.5" fill="{GOLD}"><animate attributeName="x" values="300;650;300" dur="4s" repeatCount="indefinite"/></rect>'
          f'<path d="M300 {H-8} l-10 0 M700 {H-8} l10 0" stroke="{GOLD}"/>')
    svg(name, 1000, H, b, title)


def divider():
    import os
    s = (f'<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="24" viewBox="0 0 1000 24" role="presentation">'
         f'<line x1="0" y1="12" x2="1000" y2="12" stroke="{LINE}"/>'
         f'<rect x="-160" y="11" width="160" height="2" fill="{GOLD}"><animate attributeName="x" values="-160;1000" dur="4.5s" repeatCount="indefinite"/></rect>'
         f'<rect x="1000" y="11" width="160" height="2" fill="{RED}" opacity=".8"><animate attributeName="x" values="1000;-160" dur="6.5s" repeatCount="indefinite"/></rect>'
         f'<path d="M500 3 L509 12 L500 21 L491 12 Z" fill="{BG}" stroke="{GOLD}" stroke-width="1.5"/><circle cx="500" cy="12" r="2.5" fill="{GOLD}">{pulse("opacity", "1", ".2", 1.6)}</circle>'
         + "".join(f'<rect x="{500+d*k}" y="9" width="6" height="6" fill="none" stroke="{GOLD}" stroke-opacity="{.6-k*.1:.1f}"/>' for k in range(1, 5) for d in (-30, 30)) + '</svg>')
    open(os.path.join(B.OUT, "divider.svg"), "w", encoding="utf-8").write(B.skin(s))


def footer():
    W, H = 1000, 300
    b = CORE_DEFS + HZ_DEF() + f'<rect width="{W}" height="{H}" rx="10" fill="url(#glow)"/>' + stars(W, H, 50, seed=21, maxy=150) + floor(W, H, 150)
    b += reactor(500, 118, .26, N=36, T=12, amp=26, pitch=14)
    b += (t(500, 196, "AWAITING YOUR COMMAND", 12, RED, anchor="middle", ls=7)
          + t(500, 240, "READY TO JOIN YOUR DATA TEAM", 38, INK, DISP, "middle", ls=3, extra='textLength="640" lengthAdjust="spacingAndGlyphs"')
          + t(500, 266, "JARVIS: Shall I send the résumé, sir?", 15, DIM, SERIF, "middle", style="italic")
          + t(500, 288, "BUILT BY DEVENDRA RATHOD  ·  PUNE, MAHARASHTRA", 10, GOLD, anchor="middle", ls=5)
          + f'<rect width="{W}" height="{H}" rx="10" fill="url(#vig)"/>' + brackets(8, 8, W - 16, H - 16, GOLD, 22, 2))
    svg("footer.svg", W, H, b, "End of line: awaiting your command. Ready to join your data team")


def button(name, label, glyph):
    b = (f'<polygon points="12,1 239,1 239,42 227,53 1,53 1,12" fill="{PANEL}" stroke="{GOLD}" stroke-width="1.5"/>'
         f'<polygon points="12,1 239,1 239,42 227,53 1,53 1,12" fill="{GOLD}" opacity="0"><animate attributeName="opacity" values="0;.12;0" dur="3s" repeatCount="indefinite"/></polygon>'
         + t(34, 35, glyph, 18, GOLD, DISP) + t(140, 36, label, 22, INK, DISP, "middle", ls=5))
    svg(name, 240, 54, b, label, bg=False)
