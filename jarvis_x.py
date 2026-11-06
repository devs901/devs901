"""Advanced Jarvis features (all pure SMIL, self-contained, animate in real time on GitHub, no JavaScript):
  warp()    warp-speed starfield for the header
  scan()    identity scan -> ACCESS GRANTED
  ask()     'Ask JARVIS' Q&A terminal (scripted, loops through four questions)
  resume()  fully rotating 3D resume hologram
  feed()    live GitHub activity feed (real data, written by scripts/stats.py)
  cvbutton  DOWNLOAD CV button
Only palette constants are used for colour, so every theme works."""
import math, random
from xml.sax.saxutils import escape as E
import build as B
import jarvis3d as J
from build import BG, INK, DIM, RED, GOLD, LINE, GREEN, DISP, SERIF, MONO, t, svg
from jarvis3d import PANEL, PANEL2, MUTE, AB, n1, n3, rad, pulse, brackets, CORE_DEFS, HZ_DEF, anim

CW = .6   # monospace glyph width / font size


def win(dur, a, b, hi="1", lo="0"):
    """discrete on/off animation: value `hi` from a to b seconds inside a `dur` second loop."""
    if b >= dur:
        return f'<animate attributeName="opacity" calcMode="discrete" values="{lo};{hi}" keyTimes="0;{a/dur:.4f}" dur="{dur}s" repeatCount="indefinite"/>'
    return f'<animate attributeName="opacity" calcMode="discrete" values="{lo};{hi};{lo}" keyTimes="0;{a/dur:.4f};{b/dur:.4f}" dur="{dur}s" repeatCount="indefinite"/>'


def typed(x, y, s, size, col, t0, t1, dur, speed=.03, font=MONO, extra=""):
    """text typed in from t0 (speed s/char), held until t1, then cleared; repeats every `dur`."""
    wd = len(s) * size * CW + 6
    ty = min(t0 + len(s) * speed, t1 - .05)
    kt = f"0;{t0/dur:.4f};{ty/dur:.4f};{t1/dur:.4f};{(t1+.01)/dur:.4f};1"
    uid = J.uid("ty")
    return (f'<clipPath id="{uid}"><rect x="{x-2}" y="{y-size-2}" height="{size*1.5:.0f}" width="0">'
            f'<animate attributeName="width" values="0;0;{wd:.0f};{wd:.0f};0;0" keyTimes="{kt}" dur="{dur}s" repeatCount="indefinite"/></rect></clipPath>'
            + t(x, y, s, size, col, font, extra=f'clip-path="url(#{uid})" {extra}'))


# =============================================================== 1. warp-speed starfield
def warp(cx, cy, W, H, n=64, seed=11, maxy=None):
    """Stars streak outward from (cx, cy). Each is a short radial line whose group scales up, so it lengthens as it flies by."""
    random.seed(seed)
    maxy = maxy or H
    out = f'<clipPath id="wp"><rect x="0" y="0" width="{W}" height="{maxy}"/></clipPath><g clip-path="url(#wp)">'
    for _ in range(n):
        a = random.uniform(0, 2 * math.pi)
        r0 = random.uniform(24, 60)
        ln = random.uniform(6, 14)
        sx, sy = math.cos(a), math.sin(a)
        d = random.uniform(2.2, 4.8)
        col = random.choice([INK, INK, GOLD, AB])
        w = random.choice([.6, .8, 1.1])
        out += (f'<g transform="translate({cx} {cy})"><g>'
                f'<animateTransform attributeName="transform" type="scale" values="0.2;7" keyTimes="0;1" calcKeyTimes="0;1" dur="{d:.1f}s" begin="{-random.uniform(0, d):.1f}s" repeatCount="indefinite" calcMode="spline" keySplines=".5 0 .9 .6"/>'
                f'<line x1="{r0*sx:.1f}" y1="{r0*sy:.1f}" x2="{(r0+ln)*sx:.1f}" y2="{(r0+ln)*sy:.1f}" stroke="{col}" stroke-width="{w+.3:.1f}" stroke-linecap="round" vector-effect="non-scaling-stroke" opacity="0">'
                f'<animate attributeName="opacity" values="0;0;.95;.95;0" keyTimes="0;.15;.4;.85;1" dur="{d:.1f}s" begin="{-random.uniform(0, d):.1f}s" repeatCount="indefinite"/></line></g></g>')
    return out + '</g>'


def glitch_name(cx, y, text, size, width, front, N=48):
    """RGB-split name that tears sideways in two short bursts per 12 s loop."""
    dur = 12
    kt = [0, .25, .254, .259, .265, .271, .5, .70, .704, .709, .715, .72, 1]
    o = [(0, 0), (14, -1), (-12, 2), (9, 0)]
    seq = [o[0], o[0], o[1], o[2], o[3], o[0], o[0], o[0], o[2], o[1], o[3], o[0], o[0]]
    ktx = ";".join(f"{k:g}" for k in kt)
    at = f'text-anchor="middle" textLength="{width}" lengthAdjust="spacingAndGlyphs" font-family="{DISP}" font-size="{size}"'
    out = ""
    for fill, op, base, mul in ((AB, .35, 4, 1), (RED, .45, -4, -1)):
        vals = ";".join(f"{n1(base + dx*mul)} {n1(dy*mul)}" for dx, dy in seq)
        out += (f'<text x="{cx}" y="{y}" {at} fill="{fill}" opacity="{op}"><animateTransform attributeName="transform" type="translate" values="{vals}" '
                f'keyTimes="{ktx}" dur="{dur}s" repeatCount="indefinite"/>{E(text)}</text>')
    out += f'<text x="{cx}" y="{y}" {at} fill="{front}">{E(text)}</text>'
    gy = y - size * .62
    ys = ";".join(n1(v) for v in (gy, gy, gy + 6, gy + 26, gy - 4, gy, gy, gy, gy + 30, gy + 4, gy + 18, gy, gy))
    sh = ";".join(f"{n1(v)} 0" for v in (0, 0, 26, -22, 14, 0, 0, 0, -30, 18, -8, 0, 0))
    cid = J.uid("gsl")
    out += (f'<clipPath id="{cid}"><rect x="0" width="1000" height="11" y="{n1(gy)}"><animate attributeName="y" values="{ys}" keyTimes="{ktx}" dur="{dur}s" repeatCount="indefinite"/></rect></clipPath>'
            f'<g clip-path="url(#{cid})"><text x="{cx}" y="{y}" {at} fill="{GOLD}"><animateTransform attributeName="transform" type="translate" values="{sh}" keyTimes="{ktx}" dur="{dur}s" repeatCount="indefinite"/>{E(text)}</text></g>')
    return out


# =============================================================== 2. identity scan -> ACCESS GRANTED
def scan():
    W, H, D = 1000, 360, 10
    b = CORE_DEFS + f'<rect width="{W}" height="{H}" rx="10" fill="url(#glow)"/>'
    b += t(40, 34, "J.A.R.V.I.S  ·  IDENTITY SCAN", 11, GOLD, ls=4) + t(960, 34, "BIOMETRIC CHANNEL 01", 11, DIM, anchor="end", ls=3)
    cx, cy = 200, 196
    ring = lambda col: (f'<animate attributeName="stroke" values="{col};{col};{GREEN};{GREEN};{col}" keyTimes="0;.69;.72;.94;1" dur="{D}s" repeatCount="indefinite"/>')
    # outer rotating rings (turn green on grant)
    r1 = "".join(f'<path d="M{128*math.cos(rad(a)):.1f} {128*math.sin(rad(a)):.1f} A128 128 0 0 1 {128*math.cos(rad(a+50)):.1f} {128*math.sin(rad(a+50)):.1f}" fill="none" stroke="{RED}" stroke-width="3">{ring(RED)}</path>' for a in (0, 120, 240))
    r2 = "".join(f'<path d="M{116*math.cos(rad(a)):.1f} {116*math.sin(rad(a)):.1f} A116 116 0 0 0 {116*math.cos(rad(a-30)):.1f} {116*math.sin(rad(a-30)):.1f}" fill="none" stroke="{GOLD}" stroke-width="2"/>' for a in (60, 180, 300))
    b += f'<g transform="translate({cx} {cy})">' + J.spin(r1, 9) + J.spin(r2, 6, True) + '</g>'
    # fingerprint: nested arcs clipped to the ring
    fp = ""
    for k in range(1, 15):
        rx, ry = 6 * k + 4, 7.2 * k + 4
        gap = 36 + (k * 23) % 60
        fp += (f'<ellipse cx="0" cy="{-2 + (k % 3)}" rx="{rx}" ry="{ry}" fill="none" stroke="{GOLD}" stroke-width="1.6" stroke-opacity="{.85 - k*.03:.2f}" '
               f'stroke-dasharray="{rx*2.4:.0f} {gap}" stroke-dashoffset="{k*13}" stroke-linecap="round"/>')
    b += f'<clipPath id="fpc"><circle cx="{cx}" cy="{cy}" r="102"/></clipPath>'
    b += f'<circle cx="{cx}" cy="{cy}" r="104" fill="{PANEL}" fill-opacity=".8" stroke="{LINE}" stroke-width="2"/>'
    b += f'<g clip-path="url(#fpc)"><g transform="translate({cx} {cy})">{fp}</g>'
    b += f'<rect x="{cx-110}" y="{cy-118}" width="220" height="26" fill="{GOLD}" opacity=".35"><animate attributeName="y" values="{cy-118};{cy+92};{cy-118}" keyTimes="0;.5;1" dur="3.3s" repeatCount="indefinite"/></rect>'
    b += f'<rect x="{cx-110}" y="{cy-94}" width="220" height="2" fill="{INK}"><animate attributeName="y" values="{cy-94};{cy+116};{cy-94}" keyTimes="0;.5;1" dur="3.3s" repeatCount="indefinite"/></rect></g>'
    b += t(cx, 346, "PLACE FINGER · SCANNING", 10, GOLD, anchor="middle", ls=3)
    # readouts
    rx0 = 400
    b += t(rx0, 84, "SUBJECT PROFILE", 11, RED, ls=5)
    rows = [("SUBJECT", "DEVENDRA RATHOD"), ("DEGREE", "B.E. AI & DATA SCIENCE · SPPU"), ("CORE SKILLS", "PYTHON · SQL · POWER BI · FLASK"), ("RECORD", "4 ROLES · 3 PROJECTS · 6 CREDENTIALS")]
    for i, (k, v) in enumerate(rows):
        y = 118 + i * 34; a = .9 + i * .8
        b += (f'<g opacity="0">{win(D, a, 9.6)}<rect x="{rx0-12}" y="{y-16}" width="3" height="24" fill="{GOLD}"/>' + t(rx0, y, k, 10, DIM, ls=4)
              + t(rx0 + 130, y, v, 15, INK, ls=1) + '</g>')
    # match bar + percent
    by = 268
    b += t(rx0, by - 10, "IDENTITY MATCH", 10, DIM, ls=4)
    b += f'<rect x="{rx0}" y="{by}" width="520" height="12" rx="6" fill="{PANEL}" stroke="{LINE}"/>'
    b += (f'<rect x="{rx0}" y="{by}" width="0" height="12" rx="6" fill="{GOLD}"><animate attributeName="width" values="0;0;520;520;0" keyTimes="0;.12;.68;.96;1" dur="{D}s" repeatCount="indefinite"/>'
          f'<animate attributeName="fill" values="{GOLD};{GOLD};{GREEN};{GREEN}" keyTimes="0;.66;.7;1" dur="{D}s" repeatCount="indefinite"/></rect>')
    steps = [("0%", 0, 1.2), ("25%", 1.2, 2.5), ("50%", 2.5, 4.0), ("75%", 4.0, 5.4), ("99%", 5.4, 6.7), ("100%", 6.7, 9.6)]
    for lab, a, e in steps:
        b += f'<g opacity="0">{win(D, a, e)}' + t(960, by - 10, lab, 13, INK, DISP, "end", ls=2) + '</g>'
    # verdict stamp
    b += (f'<g opacity="0"><rect x="{rx0}" y="{by+34}" width="560" height="44" rx="4" fill="{GREEN}" fill-opacity=".1" stroke="{GREEN}" stroke-width="2"/>'
          f'<animate attributeName="opacity" calcMode="discrete" values="0;1;.35;1;.35;1;0" keyTimes="0;{7.1/D:.3f};{7.4/D:.3f};{7.6/D:.3f};{7.8/D:.3f};{8.0/D:.3f};{9.6/D:.3f}" dur="{D}s" repeatCount="indefinite"/>'
          + t(rx0 + 280, by + 66, "ACCESS GRANTED", 34, GREEN, DISP, "middle", ls=8) + '</g>')
    b += brackets(8, 8, W - 16, H - 16, GOLD, 24, 2) + f'<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="10" fill="none" stroke="{LINE}"/>'
    svg("scan.svg", W, H, b, "Identity scan of Devendra Rathod: B.E. AI and Data Science, core skills Python, SQL, Power BI and Flask, four roles, three projects, six credentials. Match reaches 100 percent and the panel reads ACCESS GRANTED")


# =============================================================== 3. Ask JARVIS terminal
QA = [("who is devendra?", "who", ["AI & Data Science graduate (B.E., PVG College of Engineering,", "SPPU, 2026). Builds with Python and SQL, ships small full-stack", "tools and designs dashboards people can actually read."]),
      ("what has he built?", "built", ["GramSathi: e-governance on MySQL with AI-sorted complaints.", "Motorola Sales Dashboard: interactive Power BI, KPIs + slicers.", "Spendwise: Flask + SQLite expense tracker, tested, in Docker."]),
      ("any work experience?", "experience", ["Four roles: Data Analysis Intern (Talent Battle), Software", "Engineer Intern (XMEGA), Python Programming Intern (Oasis", "Infobyte) and JioFiber Associate at Quess Corp Limited."]),
      ("is he available?", "hire", ["Yes. Open to entry-level Python, SQL, data and AI roles.", "Shall I open a channel, sir? LinkedIn and email are below,", "and the CV button sends the full résumé."])]


def ask():
    W, H, WIN = 1000, 400, 8
    D = WIN * len(QA)
    b = CORE_DEFS + f'<rect width="{W}" height="{H}" rx="10" fill="url(#glow)"/>'
    b += t(40, 34, "ASK  J.A.R.V.I.S", 11, GOLD, ls=5) + t(960, 34, "SCRIPTED Q&A  ·  4 TOPICS  ·  LOOPING", 10, DIM, anchor="end", ls=3)
    b += f'<rect x="40" y="52" width="650" height="276" rx="6" fill="{BG}" fill-opacity=".78" stroke="{LINE}"/>'
    b += f'<rect x="40" y="52" width="650" height="30" rx="6" fill="{PANEL2}" stroke="{LINE}"/>' + "".join(f'<circle cx="{58+i*18}" cy="67" r="4.5" fill="{c}"/>' for i, c in enumerate((RED, GOLD, GREEN)))
    b += t(365, 71, "jarvis@devs901 : ~", 10, MUTE, anchor="middle", ls=2)
    # input line (prompt is static, question is typed)
    b += t(62, 112, "ask ▸", 14, RED, weight="bold")
    b += f'<rect x="{62+6*14*CW+8}" y="99" width="8" height="15" fill="{GOLD}"><animate attributeName="opacity" values="1;0;1" dur="1s" repeatCount="indefinite"/></rect>'
    for i, (q, key, ans) in enumerate(QA):
        w0 = i * WIN
        b += typed(62 + 7 * 14 * CW + 6, 112, q, 14, GOLD, w0 + .4, w0 + WIN - .3, D, speed=.07)
        qt = w0 + .4 + len(q) * .07 + .5
        b += f'<g opacity="0">{win(D, qt, w0 + WIN - .3)}' + t(62, 156, "JARVIS ▸", 12, GREEN, weight="bold") + '</g>'
        for j, ln in enumerate(ans):
            b += typed(62, 184 + j * 28, ln, 12.5, INK, qt + .2 + j * 1.25, w0 + WIN - .3, D, speed=.022)
    # topic chips + active highlight
    b += t(724, 70, "TOPICS", 10, RED, ls=5)
    for i, (q, key, ans) in enumerate(QA):
        y = 90 + i * 58
        b += f'<rect x="724" y="{y}" width="236" height="44" rx="4" fill="none" stroke="{LINE}"/>' + t(742, y + 27, key.upper(), 13, DIM, ls=4)
        b += (f'<g opacity="0">{win(D, i*WIN, (i+1)*WIN - .2)}<rect x="724" y="{y}" width="236" height="44" rx="4" fill="{GOLD}" fill-opacity=".12" stroke="{GOLD}" stroke-width="1.5"/>'
              + t(742, y + 27, key.upper(), 13, GOLD, ls=4) + f'<circle cx="942" cy="{y+22}" r="4" fill="{GREEN}">{pulse("opacity", "1", ".2", 1)}</circle></g>')
    # voice waveform
    wy = 364; wv = []
    for f in range(20):
        pts = []
        for k in range(81):
            x = 40 + k * 11.5
            a = 17 * math.sin(k / 80 * math.pi) * math.sin(k * .8 + f / 20 * 4 * math.pi) * (.55 + .45 * math.sin(k * .23 + f / 20 * 2 * math.pi))
            pts.append(f"{x:.1f},{n1(wy + a)}")
        wv.append(" ".join(pts))
    b += f'<polyline points="{wv[0]}" fill="none" stroke="{GOLD}" stroke-width="1.5" stroke-linejoin="round">{anim("points", wv + [wv[0]], 2.2)}</polyline>'
    b += t(960, 392, "VOICE  ·  JARVIS  ·  SPEAKING", 9, MUTE, anchor="end", ls=3)
    b += brackets(8, 8, W - 16, H - 16, GOLD, 24, 2) + f'<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="10" fill="none" stroke="{LINE}"/>'
    svg("ask.svg", W, H, b, "Ask JARVIS terminal, a looping scripted Q&A: who is Devendra, what has he built, any work experience, is he available. He is open to entry-level Python, SQL, data and AI roles")


# =============================================================== 4. rotating 3D resume hologram
def _sheet_front():
    s = f'<rect x="-150" y="-200" width="300" height="400" rx="6" fill="{PANEL2}" fill-opacity=".94" stroke="{GOLD}" stroke-width="2"/>'
    s += f'<rect x="-150" y="-200" width="300" height="52" rx="6" fill="{GOLD}" fill-opacity=".12"/>'
    s += t(-134, -170, "DEVENDRA RATHOD", 22, INK, DISP, ls=2) + t(-134, -153, "AI & DATA SCIENCE  ·  PYTHON  ·  SQL", 8.5, GOLD, ls=1.5)
    def sec(y, title, lines):
        o = t(-134, y, title, 8, RED, ls=3) + f'<line x1="-134" y1="{y+4}" x2="134" y2="{y+4}" stroke="{LINE}"/>'
        for i, ln in enumerate(lines): o += t(-134, y + 18 + i * 14, ln, 8.6, INK)
        return o
    s += sec(-120, "EDUCATION", ["B.E. AI & Data Science · PVG COE, SPPU", "2022 - 2026"])
    s += sec(-62, "EXPERIENCE", ["JioFiber Associate · Quess Corp", "Python Programming Intern · Oasis Infobyte", "Software Engineer Intern · XMEGA", "Data Analysis Intern · Talent Battle"])
    s += sec(30, "PROJECTS", ["GramSathi · MySQL + AI complaints", "Motorola Sales Dashboard · Power BI", "Spendwise · Flask, SQLite, Docker, CI"])
    s += sec(98, "SKILLS", ["Python  SQL  MySQL  Power BI  Flask  Git", "Docker  pytest  Excel  REST API  JavaScript"])
    s += sec(152, "CREDENTIALS", ["6 verified · TCS iON NQT · 126 h training"])
    s += (f'<clipPath id="shc"><rect x="-150" y="-200" width="300" height="400" rx="6"/></clipPath><g clip-path="url(#shc)">'
          f'<rect x="-160" y="-200" width="320" height="30" fill="{GOLD}" opacity=".22"><animate attributeName="y" values="-200;190;-200" keyTimes="0;.5;1" dur="4s" repeatCount="indefinite"/></rect>'
          f'<rect x="-160" y="-200" width="320" height="2" fill="{INK}" opacity=".8"><animate attributeName="y" values="-174;216;-174" keyTimes="0;.5;1" dur="4s" repeatCount="indefinite"/></rect></g>')
    return s + brackets(-144, -194, 288, 388, GOLD, 16, 1.5, .9)


def _sheet_back():
    s = f'<rect x="-150" y="-200" width="300" height="400" rx="6" fill="{PANEL}" fill-opacity=".94" stroke="{GOLD}" stroke-width="2"/>'
    s += "".join(f'<circle r="{r}" fill="none" stroke="{GOLD}" stroke-opacity="{.7 - r/400:.2f}" stroke-width="{2 if r%40==0 else 1}" stroke-dasharray="{r/3:.0f} 6"/>' for r in range(30, 130, 20))
    s += f'<circle r="16" fill="{GOLD}" opacity=".85"/><circle r="7" fill="{INK}"/>'
    s += t(0, 150, "CONFIDENTIAL  ·  CV 2026", 10, GOLD, anchor="middle", ls=5) + t(0, 172, "D. RATHOD", 22, INK, DISP, "middle", ls=6)
    return s + brackets(-144, -194, 288, 388, GOLD, 16, 1.5, .9)


def resume():
    W, H, N, T = 1000, 540, 72, 16
    cx, cy = 700, 250
    b = CORE_DEFS + HZ_DEF() + f'<rect width="{W}" height="{H}" rx="10" fill="url(#glow)"/>' + J.stars(W, H, 50, seed=31, maxy=300) + J.floor(W, H, 410)
    # left copy
    b += t(44, 70, "RÉSUMÉ  ·  HOLOGRAM", 11, GOLD, ls=5)
    for i, (k, v) in enumerate((("TARGET", "Entry-level Python, SQL, data and AI roles"), ("CORE", "Python · SQL · MySQL · Power BI · Flask"), ("RECORD", "4 roles · 3 projects · 6 credentials"), ("FORMAT", "PDF · Devendra_Rathod_CV.pdf"))):
        y = 120 + i * 62
        b += f'<rect x="44" y="{y-16}" width="3" height="44" fill="{RED}"/>' + t(60, y, k, 10, DIM, ls=4) + t(60, y + 24, v, 15, INK)
    b += t(44, 400, "▸  FULL 360° VIEW  ·  SCAN IN PROGRESS", 11, GREEN, ls=2) + f'<circle cx="34" cy="396" r="3.5" fill="{GREEN}">{pulse("opacity", "1", ".2", 1.2)}</circle>'
    # holo base: rings + beam
    for k, (rx, ry, d, rev) in enumerate(((190, 34, 14, False), (150, 27, 9, True), (110, 20, 6, False))):
        dash = 8 + k * 6
        b += (f'<ellipse cx="{cx}" cy="470" rx="{rx}" ry="{ry}" fill="none" stroke="{GOLD}" stroke-opacity="{.7 - k*.15:.2f}" stroke-width="2" stroke-dasharray="{dash} {dash}">'
              f'<animate attributeName="stroke-dashoffset" from="0" to="{-dash*2 if not rev else dash*2}" dur="{d/4:.1f}s" repeatCount="indefinite"/></ellipse>')
    b += (f'<defs><linearGradient id="bm" x1="0" y1="1" x2="0" y2="0"><stop offset="0" stop-color="{GOLD}" stop-opacity=".38"/><stop offset="1" stop-color="{GOLD}" stop-opacity="0"/></linearGradient></defs>'
          f'<polygon points="{cx-150},470 {cx+150},470 {cx+120},120 {cx-120},120" fill="url(#bm)"/>')
    # rotating sheet: offset half a step so no frame is exactly edge-on
    yaw = [2 * math.pi * (i + .5) / N for i in range(N + 1)]
    ex = [1] * (N + 1)
    cs = [math.cos(y) for y in yaw]
    # front visible while cos>0
    kt, fv, bv = [], [], []
    for i in range(N + 1):
        kt.append(f"{i/N:.4f}"); fv.append("1" if cs[i] > 0 else "0"); bv.append("0" if cs[i] > 0 else "1")
    face = lambda vals: f'<animate attributeName="opacity" calcMode="discrete" values="{";".join(vals)}" keyTimes="{";".join(kt)}" dur="{T}s" repeatCount="indefinite"/>'
    pitch = rad(10)
    back = f'<g transform="scale(-1 1)">{_sheet_back()}</g>'
    b += f'<g opacity="1">{face(fv)}{J.layer(_sheet_front(), 0, cx, cy, yaw, pitch, ex, T)}</g>'
    b += f'<g opacity="0">{face(bv)}{J.layer(back, 0, cx, cy, yaw, pitch, ex, T)}</g>'
    # outline plates give the sheet thickness
    plate = f'<rect x="-150" y="-200" width="300" height="400" rx="6" fill="none" stroke="{GOLD}" stroke-opacity=".28" stroke-width="1.5"/>'
    b += J.layer(plate, 14, cx, cy, yaw, pitch, ex, T) + J.layer(plate, -14, cx, cy, yaw, pitch, ex, T)
    b += f'<rect width="{W}" height="{H}" rx="10" fill="url(#vig)"/>' + brackets(8, 8, W - 16, H - 16, GOLD, 24, 2)
    svg("resume.svg", W, H, b, "A fully rotating 3D hologram of Devendra Rathod's résumé: education, four roles, three projects, skills and six credentials")


def cvbutton():
    b = (f'<polygon points="12,1 299,1 299,42 287,53 1,53 1,12" fill="{PANEL}" stroke="{GREEN}" stroke-width="1.8"/>'
         f'<polygon points="12,1 299,1 299,42 287,53 1,53 1,12" fill="{GREEN}" opacity="0"><animate attributeName="opacity" values="0;.14;0" dur="2.4s" repeatCount="indefinite"/></polygon>'
         f'<path d="M34 14 v18 m-8 -8 l8 8 l8 -8 M24 40 h20" fill="none" stroke="{GREEN}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round">'
         f'<animateTransform attributeName="transform" type="translate" values="0 -2;0 3;0 -2" dur="1.6s" repeatCount="indefinite"/></path>'
         + t(176, 36, "DOWNLOAD CV", 22, INK, DISP, "middle", ls=5))
    svg("btn-cv.svg", 300, 54, b, "Download CV", bg=False)


# =============================================================== 5. live GitHub activity feed
KIND = {"PushEvent": ("PUSH", GOLD), "CreateEvent": ("NEW", GREEN), "WatchEvent": ("STAR", GOLD), "ForkEvent": ("FORK", AB), "PullRequestEvent": ("PR", RED),
        "IssuesEvent": ("ISSUE", RED), "IssueCommentEvent": ("NOTE", DIM), "DeleteEvent": ("DEL", DIM), "ReleaseEvent": ("TAG", GREEN), "PublicEvent": ("OPEN", GREEN)}


def feed(items=None, login="devs901", more=0):
    """items: list of (kind_tag, tag_colour_key, text, 'time ago'); None draws the 'waiting for first sync' state."""
    W = 1000
    H = 70 + 42 * min(len(items or [0]), 7) + 24
    b = CORE_DEFS + f'<rect width="{W}" height="{H}" rx="10" fill="url(#glow)"/>'
    b += t(40, 36, f"LIVE ACTIVITY FEED  ·  @{login.upper()}", 11, GOLD, ls=4)
    b += t(960, 36, "SYNCED EVERY 6 HOURS" if items else "WAITING FOR FIRST SYNC", 10, GREEN if items else DIM, anchor="end", ls=3)
    b += f'<circle cx="{W-250 if items else W-282}" cy="32" r="4" fill="{GREEN if items else DIM}">{pulse("opacity", "1", ".2", 1.2)}</circle>'
    b += f'<line x1="40" y1="50" x2="960" y2="50" stroke="{LINE}"/><rect x="40" y="49" width="120" height="2" fill="{GOLD}"><animate attributeName="x" values="40;840;40" dur="8s" repeatCount="indefinite"/></rect>'
    rows = items or [("···", DIM, "Run the “Update GitHub stats” workflow once (see SETUP.md) and your real activity appears here.", "")]
    rows = rows[:7]
    for i, (tag, col, text, ago) in enumerate(rows):
        y = 70 + i * 42
        b += f'<rect x="40" y="{y}" width="920" height="34" rx="4" fill="{PANEL}" fill-opacity=".7" stroke="{LINE}"/>'
        b += f'<rect x="40" y="{y}" width="3" height="34" fill="{col}"/>' + t(62, y + 22, tag, 11, col, ls=3, weight="bold")
        b += t(138, y + 22, text, 13, INK) + (t(944, y + 22, ago, 11, DIM, anchor="end", ls=1) if ago else "")
    if items:
        b += (f'<rect x="40" y="70" width="920" height="34" rx="4" fill="{GOLD}" opacity="0"><animate attributeName="y" values="70;{70+42*(len(rows)-1)};70" keyTimes="0;.5;1" dur="{max(4, len(rows)*1.4):.0f}s" repeatCount="indefinite"/>'
              f'<animate attributeName="opacity" values=".08;.08" dur="1s" repeatCount="indefinite"/></rect>')
    b += brackets(8, 8, W - 16, H - 16, GOLD, 24, 2) + f'<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="10" fill="none" stroke="{LINE}"/>'
    svg("feed.svg", W, H, b, f"Live GitHub activity feed for {login}: the latest public events such as pushes, new repositories and stars")


def ago(iso):
    import datetime
    d = datetime.datetime.now(datetime.timezone.utc) - datetime.datetime.fromisoformat(iso.replace("Z", "+00:00"))
    s = max(0, int(d.total_seconds()))
    return f"{s//60}m ago" if s < 3600 else f"{s//3600}h ago" if s < 86400 else f"{s//86400}d ago"


def events_to_items(events, login):
    """Turns GitHub public events into feed rows (newest first), merging repeated pushes to one repo."""
    out = []
    for e in events:
        tag, col = KIND.get(e["type"], (None, None))
        if not tag: continue
        repo = e["repo"]["name"].split("/")[-1]
        p = e.get("payload", {})
        if e["type"] == "PushEvent":
            n = p.get("distinct_size", p.get("size")) or len(p.get("commits", [])) or 1
            msg = (p.get("commits") or [{}])[-1].get("message", "").split("\n")[0]
            text = f"pushed {n} commit{'s' if n != 1 else ''} to {repo}" + (f": {msg}" if msg else "")
        elif e["type"] == "CreateEvent": text = f"created {p.get('ref_type', 'repository')} {p.get('ref') or repo}" + ("" if p.get("ref_type") != "branch" else f" in {repo}")
        elif e["type"] == "WatchEvent": text = f"starred {e['repo']['name']}"
        elif e["type"] == "ForkEvent": text = f"forked {e['repo']['name']}"
        elif e["type"] == "PullRequestEvent": text = f"{p.get('action', 'updated')} pull request in {repo}"
        elif e["type"] == "IssuesEvent": text = f"{p.get('action', 'updated')} an issue in {repo}"
        elif e["type"] == "IssueCommentEvent": text = f"commented in {repo}"
        elif e["type"] == "ReleaseEvent": text = f"released {repo}"
        else: text = f"{e['type'].replace('Event', '').lower()} in {repo}"
        if len(text) > 82: text = text[:79] + "..."
        if out and out[-1][2] == text: continue
        out.append((tag, col, text, ago(e["created_at"])))
    return out
