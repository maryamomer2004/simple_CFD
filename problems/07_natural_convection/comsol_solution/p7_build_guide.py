import os, io, json
from PIL import Image, ImageDraw, ImageFont
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.utils import ImageReader, simpleSplit
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

SRC = None
OUT = os.path.dirname(os.path.abspath(__file__))
SHOTS = os.path.join(OUT, "annotated")
os.makedirs(SHOTS, exist_ok=True)


def S(i):
    return os.path.join(OUT, "shots", "s_" + i + ".jpg")


FD = r"C:\Windows\Fonts"
pdfmetrics.registerFont(TTFont("UI", os.path.join(FD, "segoeui.ttf")))
pdfmetrics.registerFont(TTFont("UIB", os.path.join(FD, "segoeuib.ttf")))
pdfmetrics.registerFont(TTFont("UII", os.path.join(FD, "segoeuii.ttf")))
pdfmetrics.registerFont(TTFont("MONO", os.path.join(FD, "consola.ttf")))
BADGE_FONT = ImageFont.truetype(os.path.join(FD, "segoeuib.ttf"), 30)
RED = (220, 38, 38)
K = 2


def annotate(src, crop, boxes, name):
    im = Image.open(src).convert("RGB")
    if im.size[0] < 1000:
        im = im.resize((1389, 868), Image.LANCZOS)
    x0, y0, x1, y1 = crop
    im = im.crop(crop).resize(((x1 - x0) * K, (y1 - y0) * K), Image.LANCZOS)
    ov = Image.new("RGBA", im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    for b in boxes:
        bx0, by0, bx1, by1, n = b[:5]
        pos = b[5] if len(b) > 5 else "tl"
        r = [(bx0 - x0) * K, (by0 - y0) * K, (bx1 - x0) * K, (by1 - y0) * K]
        d.rounded_rectangle(r, radius=8, outline=RED + (255,), width=5, fill=RED + (28,))
        R = 20
        if pos == "tl":
            cx, cy = r[0] - 4, r[1] - 4
        elif pos == "tr":
            cx, cy = r[2] + 4, r[1] - 4
        elif pos == "l":
            cx, cy = r[0] - R - 6, (r[1] + r[3]) / 2
        else:
            cx, cy = r[2] + R + 6, (r[1] + r[3]) / 2
        cx = max(R + 2, min(im.size[0] - R - 2, cx))
        cy = max(R + 2, min(im.size[1] - R - 2, cy))
        d.ellipse([cx - R, cy - R, cx + R, cy + R], fill=RED + (255,), outline=(255, 255, 255, 255), width=3)
        t = str(n)
        tw = d.textlength(t, font=BADGE_FONT)
        d.text((cx - tw / 2, cy - 20), t, font=BADGE_FONT, fill=(255, 255, 255, 255))
    out = Image.alpha_composite(im.convert("RGBA"), ov).convert("RGB")
    p = os.path.join(SHOTS, name + ".jpg")
    out.save(p, quality=88)
    return p


def eq_img(latex, fs=16):
    fig = plt.figure(figsize=(0.1, 0.1), dpi=300)
    fig.text(0, 0, latex, fontsize=fs, color="#111827")
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=300, bbox_inches="tight", pad_inches=0.04, transparent=True)
    plt.close(fig)
    return buf.getvalue()


W, H = landscape(A4)
M = 36
c = canvas.Canvas(os.path.join(OUT, "COMSOL_Natural_Convection_Guide.pdf"), pagesize=(W, H))
c.setTitle("COMSOL Multiphysics 4.3a - Natural convection in a heated square cavity - student guide")
c.setAuthor("Claude")
page_no = [0]
NAVY = (0.09, 0.2, 0.42)
ACC = (0.86, 0.15, 0.15)


def footer():
    page_no[0] += 1
    c.setFont("UI", 8)
    c.setFillColorRGB(0.45, 0.45, 0.5)
    c.drawString(M, 20, "COMSOL 4.3a  |  Problem 7: natural convection in a heated cavity, Ra = 1e3 and 1e4  |  student guide")
    c.drawRightString(W - M, 20, "Page %d" % page_no[0])


def header(txt, sub=None):
    c.setFillColorRGB(*NAVY)
    c.rect(0, H - 52, W, 52, fill=1, stroke=0)
    c.setFillColorRGB(1, 1, 1)
    c.setFont("UIB", 19)
    c.drawString(M, H - 34, txt)
    if sub:
        c.setFont("UI", 10)
        c.drawRightString(W - M, H - 33, sub)


def para(x, y, w, text, font="UI", size=10.5, lead=14, color=(0.1, 0.1, 0.12)):
    c.setFont(font, size)
    c.setFillColorRGB(*color)
    lines = []
    for chunk in text.split("\n"):
        lines += simpleSplit(chunk, font, size, w) or [""]
    for ln in lines:
        c.drawString(x, y, ln)
        y -= lead
    return y


def h2(x, y, txt):
    c.setFont("UIB", 12)
    c.setFillColorRGB(*NAVY)
    c.drawString(x, y, txt)
    return y - 16


def badge(x, y, n, r=8.5):
    c.setFillColorRGB(*ACC)
    c.circle(x, y, r, fill=1, stroke=0)
    c.setFillColorRGB(1, 1, 1)
    c.setFont("UIB", 10.5)
    c.drawCentredString(x, y - 3.8, str(n))


def item_height(text, w):
    lines = 0
    for chunk in text.split("\n"):
        lines += len(simpleSplit(chunk, "UI", 10.2, w)) or 1
    return lines * 13 + 6


def draw_items(items, x, y, w, ncols=2):
    colw = (w - 18) / ncols if ncols > 1 else w
    cols = [[] for _ in range(ncols)]
    heights = [item_height(t, colw - 24) for _, t in items]
    total = sum(heights)
    acc = 0
    ci = 0
    for (n, t), h in zip(items, heights):
        if ci < ncols - 1 and acc + h / 2 > total / ncols * (ci + 1):
            ci += 1
        cols[ci].append((n, t, h))
        acc += h
    ymin = y
    for ci, col in enumerate(cols):
        cx = x + ci * (colw + 18)
        cy = y
        for n, t, h in col:
            badge(cx + 9, cy - 5, n)
            para(cx + 24, cy - 8, colw - 24, t, size=10.2, lead=13)
            cy -= h
        ymin = min(ymin, cy)
    return ymin


def note_height(text):
    return len(simpleSplit(text, "UI", 10, W - 2 * M - 24)) * 13 + 30


def note_box(text, y_top, title="Why?"):
    w = W - 2 * M
    lines = simpleSplit(text, "UI", 10, w - 24)
    h = len(lines) * 13 + 30
    c.setFillColorRGB(1.0, 0.97, 0.85)
    c.setStrokeColorRGB(0.93, 0.78, 0.3)
    c.roundRect(M, y_top - h, w, h, 6, fill=1, stroke=1)
    c.setFillColorRGB(0.45, 0.3, 0.0)
    c.setFont("UIB", 10)
    c.drawString(M + 12, y_top - 15, title)
    c.setFont("UI", 10)
    c.setFillColorRGB(0.2, 0.15, 0.05)
    yy = y_top - 29
    for ln in lines:
        c.drawString(M + 12, yy, ln)
        yy -= 13
    return y_top - h


def draw_row(paths, top, maxh=262, maxw=W - 2 * M, gap=12):
    ims = [Image.open(p) for p in paths]
    maxpx = max(i.size[1] for i in ims)
    sump = sum(i.size[0] for i in ims)
    s = min(maxh / maxpx, (maxw - gap * (len(ims) - 1)) / sump)
    tw = sum(i.size[0] * s for i in ims) + gap * (len(ims) - 1)
    x = M + (maxw - tw) / 2
    bottom = top
    for p, i in zip(paths, ims):
        w, h = i.size[0] * s, i.size[1] * s
        c.setStrokeColorRGB(0.7, 0.72, 0.78)
        c.setLineWidth(0.8)
        c.drawImage(ImageReader(p), x, top - h, w, h)
        c.rect(x, top - h, w, h, fill=0, stroke=1)
        bottom = min(bottom, top - h)
        x += w + gap
    return bottom


def table(x, y, widths, rows, hdr=True, size=10, bold_last=False):
    tw = sum(widths)
    for k_, r in enumerate(rows):
        if k_ == 0 and hdr:
            c.setFillColorRGB(0.9, 0.93, 0.98)
            c.rect(x, y - 17, tw, 20, fill=1, stroke=0)
        c.setFont("UIB" if (k_ == 0 and hdr) or (bold_last and k_ == len(rows) - 1) else "UI", size)
        c.setFillColorRGB(0.1, 0.1, 0.12)
        xx = x
        for w_, t in zip(widths, r):
            c.drawString(xx + 6, y - 12, t)
            xx += w_
        c.setStrokeColorRGB(0.8, 0.82, 0.88)
        c.line(x, y - 18, x + tw, y - 18)
        y -= 20
    return y


def mono(x, y, lines, size=9.6, lead=12.5):
    c.setFont("MONO", size)
    c.setFillColorRGB(0.1, 0.1, 0.15)
    for ln in lines:
        c.drawString(x, y, ln)
        y -= lead
    return y


def eq_row(x, y, tex, fs=15, maxw=380):
    img = eq_img(tex, fs)
    im = Image.open(io.BytesIO(img))
    sc = min(1.0, maxw / (im.size[0] * 72 / 300))
    w_, h_ = im.size[0] * 72 / 300 * sc, im.size[1] * 72 / 300 * sc
    c.drawImage(ImageReader(io.BytesIO(img)), x, y - h_, w_, h_)
    return y - h_ - 8


import numpy as np
R = json.load(open(os.path.join(OUT, "p7_comsol_numbers.json")))
CO, BE, FD_, RI = R["comsol"], R["bench"], R["fdm"], R["comsol_richardson"]
FR = R["fdm_richardson"]
FD_ = {ra: {n: tuple(d[k] for k in ("psi", "umax", "yu", "vmax", "xv", "nu")) for n, d in v.items()} for ra, v in FD_.items()}


def cv(n, ra, q):
    return CO["%d_%d" % (n, ra)][q]


SDIM = S("dimension"); SPHYS = S("wizard_physics"); SSTUDY = S("wizard_study"); SPAR = S("params")
SGEO = S("geometry"); SMAT = S("material"); SFLU = S("fluid_node"); SVF = S("volume_force")
STH = S("temp_hot"); STC = S("temp_cold"); SWALL = S("wall_noslip"); SIV = S("initial_values")
SPP = S("pressure_point"); SMESH = S("mesh"); SSW = S("sweep"); SSOL = S("solve")
SLI = S("lineint_hot"); SCUT = S("cutline_x"); SEXP = S("export_data"); SSTR = S("streamline_ra1e4")
ST3 = S("T_ra1e3"); ST4 = S("T_ra1e4")

STEPS = []


def step(title, sub, pre, imgs, items, note):
    STEPS.append(dict(title=title, sub=sub, pre=pre, imgs=imgs, items=items, note=note))


step("Start a 2D model", "Model Wizard 1 of 3",
     "Start COMSOL Multiphysics 4.3a. The Model Wizard opens (if not: File > New).",
     [dict(src=SDIM, crop=(0, 55, 570, 230), name="a", boxes=[(246, 147, 285, 164, 1), (524, 85, 541, 102, 2)])],
     [(1, "Select 2D: the cavity is long in the third direction, so the flow and the temperature are two-dimensional."),
      (2, "Click the Next arrow. COMSOL reacts slowly: if nothing seems to happen, wait a second before clicking again (a second click skips a page).")],
     "Only the square cross-section of the cavity is modelled. Assumption 1 of the problem (steady, two-dimensional, laminar) is what makes a 2D stationary model enough.")

step("Add the Non-Isothermal Flow interface", "Model Wizard 2 of 3",
     "Open Heat Transfer > Conjugate Heat Transfer. Laminar Flow (nitf) couples the Navier-Stokes equations and the energy equation in one interface.",
     [dict(src=SPHYS, crop=(0, 55, 570, 480), name="a",
           boxes=[(288, 292, 397, 310, 1), (245, 346, 262, 362, 2), (259, 390, 421, 407, 3), (509, 85, 526, 102, 4)])],
     [(1, "Select Heat Transfer > Conjugate Heat Transfer > Laminar Flow (nitf)."),
      (2, "Click the blue + (Add Selected) button."),
      (3, "Conjugate Heat Transfer (nitf) appears under Selected physics."),
      (4, "Click Next.")],
     "The FDM solves for the stream function, the vorticity and T. COMSOL solves for the velocity (u, v), the pressure p and T directly. The nitf interface passes the computed velocity to the energy equation and the temperature to the flow automatically, so flow and heat are coupled both ways, as in the problem. (Laminar Flow + Heat Transfer in Fluids as two separate interfaces also works, but then the velocity field must be linked by hand.)")

step("Choose a stationary study", "Model Wizard 3 of 3",
     "We want the steady state (Assumption 1).",
     [dict(src=SSTUDY, crop=(0, 55, 570, 420), name="a", boxes=[(274, 149, 343, 166, 1), (541, 85, 558, 102, 2)])],
     [(1, "Select Preset Studies > Stationary."),
      (2, "Click Finish (the chequered flag).")],
     "The FDM reaches the steady state with Gauss-Seidel sweeps from pure conduction (1450 and 3489 sweeps on 33 x 33 nodes). COMSOL solves the nonlinear steady equations directly with Newton's method in a handful of iterations.")

step("Define the parameters", "Global Definitions > Parameters",
     "Right-click Global Definitions > Parameters and type four rows (Name, Expression, Description).",
     [dict(src=SPAR, crop=(0, 95, 565, 520), name="a", boxes=[(47, 110, 122, 127, 1), (252, 143, 552, 160, 2), (252, 160, 552, 177, 3), (252, 177, 552, 194, 4), (252, 194, 552, 211, 5)])],
     [(1, "Parameters node under Global Definitions."),
      (2, "Ra = 1e3 (Rayleigh number; the sweep will add 1e4)."),
      (3, "Pr = 0.71 (Prandtl number of air)."),
      (4, "nel = 32 (elements per side of the mesh)."),
      (5, "T0 = 0.5[K] (reference temperature of the Boussinesq force).")],
     "Parameters let us change Ra and the mesh in a sweep without editing the model. Tip: if you type in the table and a letter goes missing, select the row and type into the Name / Expression / Description fields below the table instead. With the automation used to make this guide, capital letters sometimes arrived in lower case; check the names (Ra, Pr, T0) after typing.")

step("Geometry: the unit square", "Geometry 1 > Square",
     "Right-click Geometry 1 > Square. The default square is exactly the cavity: side 1 m, lower-left corner at (0, 0).",
     [dict(src=SGEO, crop=(0, 72, 565, 420), name="a", boxes=[(60, 194, 150, 210, 1), (252, 178, 540, 196, 2), (252, 229, 540, 292, 3), (336, 78, 393, 95, 4)]),
      dict(src=SGEO, crop=(570, 95, 1389, 650), name="b", boxes=[(754, 123, 1237, 606, 5)])],
     [(1, "Square 1 (sq1) appears under Geometry 1."),
      (2, "Side length 1 m (default)."),
      (3, "Base: Corner, x = 0, y = 0 (default)."),
      (4, "Click Build All."),
      (5, "The cavity. COMSOL numbers its edges 1 (left, hot), 2 (bottom), 3 (top) and 4 (right, cold).")],
     "We choose L = 1 m so that lengths in metres are already the dimensionless lengths x/L of the problem. Then, with the properties of the next steps, every COMSOL number is directly the dimensionless number of the FDM.")

step("A material with unit properties", "Materials > Material",
     "Right-click Materials > Material (a blank material). The table lists the properties the physics needs; fill in the Value column.",
     [dict(src=SMAT, crop=(0, 95, 565, 530), name="a", boxes=[(60, 227, 162, 244, 1), (362, 148, 552, 165, 2), (252, 361, 552, 413, 3)])],
     [(1, "Material 1 (mat1)."),
      (2, "Selection: All domains (the default)."),
      (3, "Thermal conductivity k = 1, density rho = 1, heat capacity Cp = 1 (double-click the Value cell, type 1, press Enter). The red stop signs turn into green ticks.")],
     "With rho = 1, Cp = 1 and k = 1 the thermal diffusivity is alpha = k/(rho Cp) = 1 m^2/s. Velocities are then measured in units of alpha/L = 1 m/s, exactly the velocity scale of the dimensionless equations. Temperatures in kelvin are the dimensionless T = (T_dim - T_c)/(T_h - T_c) when T_h = 1 K and T_c = 0 K.")

step("Fluid properties: viscosity = Pr", "Conjugate Heat Transfer > Fluid 1",
     "Select Fluid 1. Its Selection starts empty (Manual): choose All domains. Scroll down to Thermodynamics and Dynamic Viscosity.",
     [dict(src=SFLU, crop=(0, 95, 565, 400), name="a", boxes=[(60, 327, 112, 343, 1), (252, 95, 497, 185, 2)]), dict(src=SFLU, crop=(240, 480, 565, 805), name="b", boxes=[(252, 669, 540, 712, 3), (252, 763, 552, 803, 4)])],
     [(1, "Fluid 1 in the model tree."),
      (2, "Selection: All domains (domain 1 in the list)."),
      (3, "Ratio of specific heats: User defined, 1 (the material has no value for it)."),
      (4, "Dynamic viscosity: User defined, Pr (Pa s).")],
     "The momentum equation in dimensionless form has Pr in front of the viscous term. With rho = 1 the kinematic viscosity is nu = mu/rho = Pr = 0.71 m^2/s, and Pr = nu/alpha = 0.71 as required. Density, heat capacity and conductivity stay 'From material' (all equal to 1).")

step("The buoyancy force (Boussinesq)", "Conjugate Heat Transfer > Volume Force",
     "Right-click Conjugate Heat Transfer (nitf) > Laminar Flow > Volume Force. Selection: All domains.",
     [dict(src=SVF, crop=(0, 95, 565, 400), name="a", boxes=[(60, 360, 152, 377, 1), (300, 124, 552, 141, 2), (264, 352, 522, 372, 3)])],
     [(1, "Volume Force 1."),
      (2, "Selection: All domains."),
      (3, "F, y component: Ra*Pr*nitf.rho*(T-T0)*1[m/(s^2*K)]. The x component stays 0.")],
     "This is the force rho g beta (T - T0) of the Boussinesq approximation, written in the units of this model: in dimensionless form it is Ra Pr (T - T0) in the y direction. Taking the curl of the momentum equation turns it into the vorticity source Ra Pr dT/dx of the FDM. The factor 1[m/(s^2*K)] only makes the units N/m^3 (it avoids a unit warning); its value is 1. T0 = 0.5 K is the mean temperature. Any constant T0 gives the same velocity: the constant part of the force is balanced by a hydrostatic pressure.")

step("Hot and cold walls", "Conjugate Heat Transfer > Temperature 1 and 2",
     "Right-click nitf > Heat Transfer > Temperature (twice). Hover over an edge until it turns red, click it, then press the green + above the list.",
     [dict(src=STH, crop=(0, 95, 565, 420), name="a", boxes=[(60, 377, 148, 394, 1), (252, 146, 512, 236, 2), (270, 335, 540, 353, 3)]),
      dict(src=STC, crop=(0, 95, 565, 420), name="b", boxes=[(60, 393, 148, 410, 4), (252, 146, 512, 236, 5), (270, 335, 540, 353, 6)])],
     [(1, "Temperature 1."),
      (2, "Boundary 1 (left wall)."),
      (3, "T0 = 1[K]: the hot wall, T = 1."),
      (4, "Temperature 2."),
      (5, "Boundary 4 (right wall)."),
      (6, "T0 = 0[K]: the cold wall, T = 0.")],
     "The top and bottom walls keep the default Thermal Insulation 1 (dT/dn = 0): a node added later overrides the default only on its own boundaries. In the FDM the insulated walls need ghost nodes; in the finite element method the insulation is the 'natural' boundary condition: it is satisfied automatically when nothing else is prescribed.")

step("No slip on all walls (default)", "Conjugate Heat Transfer > Wall 1",
     "Click Wall 1 to check it. Nothing has to be changed.",
     [dict(src=SWALL, crop=(0, 95, 565, 420), name="a", boxes=[(60, 310, 112, 327, 1), (252, 146, 512, 236, 2), (252, 338, 552, 358, 3)])],
     [(1, "Wall 1 (created by the wizard)."),
      (2, "Applies to all four boundaries (greyed: it is a default node)."),
      (3, "Boundary condition: No slip: u = v = 0. (In the graphics window all four walls are highlighted.)")],
     "No slip u = v = 0 is the same condition as psi = 0 plus Thom's formula on the four walls of the FDM. COMSOL imposes it on the velocity directly.")

step("Start from pure conduction", "Conjugate Heat Transfer > Initial Values 1",
     "The default initial temperature is 293.15 K, far from our 0 ... 1 K. Use the conduction profile T = 1 - x instead (Task 4 of the problem).",
     [dict(src=SIV, crop=(0, 95, 565, 545), name="a", boxes=[(60, 343, 148, 360, 1), (293, 384, 520, 420, 2), (293, 514, 520, 533, 3)])],
     [(1, "Initial Values 1."),
      (2, "Velocity 0 (fluid at rest)."),
      (3, "Temperature: (1-x/1[m])*1[K].")],
     "Newton's method needs a starting guess; a guess close to the answer converges faster and more safely. Starting from 293 K the buoyancy force Ra Pr (T - T0) would be about 200 000 instead of order 1. The FDM also starts from pure conduction, so both methods begin at the same state.")

step("Fix the pressure level", "nitf > Points > Pressure Point Constraint",
     "The cavity is closed, so the pressure is known only up to a constant. Right-click nitf > Points > Pressure Point Constraint, and select the lower left corner.",
     [dict(src=SPP, crop=(0, 95, 565, 440), name="a", boxes=[(60, 410, 205, 427, 1), (252, 146, 512, 236, 2), (270, 313, 535, 331, 3)]),
      dict(src=SPP, crop=(570, 95, 1389, 650), name="b", boxes=[(744, 595, 764, 615, 4)])],
     [(1, "Pressure Point Constraint 1."),
      (2, "Point 1 in the list (hover until the corner turns red, click, press +)."),
      (3, "p0 = 0 Pa."),
      (4, "The constrained corner (0, 0), shown in blue.")],
     "Without this constraint the pressure is undetermined and the matrix is singular. The FDM does not need it: the stream function - vorticity formulation eliminates the pressure. The problem statement's data box asks for exactly this constraint.")

step("Mapped mesh, nel x nel", "Mesh 1 > Mapped > Distribution",
     "Right-click Mesh 1 > Mapped, then right-click Mapped 1 > Distribution. Selection: All boundaries; Number of elements: nel. Click Build All.",
     [dict(src=SMESH, crop=(0, 72, 565, 500), name="a", boxes=[(60, 460, 128, 477, 1), (75, 477, 158, 494, 2), (300, 127, 552, 145, 3), (252, 331, 552, 350, 4), (336, 78, 393, 95, 5)]),
      dict(src=SMESH, crop=(570, 95, 1389, 730), name="b", boxes=[(748, 117, 1243, 612, 6), (570, 705, 780, 721, 7)])],
     [(1, "Mapped 1."),
      (2, "Distribution 1."),
      (3, "Selection: All boundaries (1 - 4)."),
      (4, "Fixed number of elements: nel."),
      (5, "Build All."),
      (6, "32 x 32 square elements, h = 1/32."),
      (7, "Messages: Complete mesh consists of 1024 elements.")],
     "A mapped mesh of squares is the finite element version of the FDM grid: with nel = 32 its 33 x 33 nodes are exactly the FDM nodes of the main grid (N = 32, h = 1/32).")

step("Parametric sweep over the mesh and Ra", "Study 1 > Parametric Sweep",
     "Right-click Study 1 > Parametric Sweep. Sweep type: All combinations. Add two rows with the + button under the table.",
     [dict(src=SSW, crop=(0, 95, 565, 545), name="a", boxes=[(47, 510, 152, 527, 1), (312, 124, 552, 141, 2), (252, 166, 552, 184, 3), (252, 184, 552, 201, 4)])],
     [(1, "Parametric Sweep (above Step 1: Stationary)."),
      (2, "Sweep type: All combinations."),
      (3, "nel: 32 64 128 (pick the name from the drop-down list of the cell)."),
      (4, "Ra: 1e3 1e4.")],
     "All combinations gives 3 x 2 = 6 solutions. The first parameter (nel) is the outer loop, so for each mesh Ra = 1e3 is solved first and its solution is the starting guess for Ra = 1e4: a 'continuation' in Ra that helps Newton's method at the higher Rayleigh number.")

step("Compute", "Study 1",
     "Save first (File > Save As). Then select Study 1, right-click > Compute (or F8).",
     [dict(src=SSOL, crop=(0, 95, 1389, 795), name="a", boxes=[(33, 427, 92, 444, 1), (570, 702, 820, 787, 2), (735, 172, 1155, 590, 3), (1290, 127, 1345, 142, 4)])],
     [(1, "Study 1: Compute."),
      (2, "Degrees of freedom: 4356 (32 x 32), 16900 (64 x 64), 66564 (128 x 128), twice each. All six solved in 87 s."),
      (3, "Default plot: the speed for the last solution (nel = 128, Ra = 1e4)."),
      (4, "Largest speed 19.70: the fast upward stream along the hot wall.")],
     "4356 = 33 x 33 nodes x 4 fields (u, v, p, T): the default elements of this interface are linear (P1) for all four fields, with stabilisation for the flow. The speed plot shows the two fast boundary layers along the hot (rising) and cold (sinking) walls and the slow core.")

step("Average Nusselt number on the hot wall", "Derived Values > Integration > Line Integration",
     "Right-click Results > Derived Values > Integration > Line Integration. Choose Data set Solution 2 (the sweep), select boundary 1, type the integrand, click Evaluate.",
     [dict(src=SLI, crop=(0, 72, 565, 650), name="a", boxes=[(60, 626, 162, 643, 1), (369, 133, 552, 150, 2), (369, 162, 552, 214, 3), (252, 312, 512, 402, 4), (252, 454, 552, 472, 5), (245, 80, 322, 97, 6)]),
      dict(src=SLI, crop=(570, 655, 1000, 800), name="b", boxes=[(572, 693, 760, 797, 7)])],
     [(1, "Line Integration 1."),
      (2, "Data set: Solution 2."),
      (3, "Parameter selection: All (one row per solution)."),
      (4, "Boundary 1, the hot wall."),
      (5, "Expression: -Tx*1[m/K]. (Tx is COMSOL's name for dT/dx.)"),
      (6, "Evaluate."),
      (7, "The results table: one Nu value for each nel and Ra.")],
     "Nu_avg = integral over 0 <= y <= 1 of -dT/dx at x = 0, as in the problem (L = 1, so no division by the length is needed). Repeat with a second Line Integration on boundary 4 for the cold wall: in a steady state the heat entering at the hot wall must leave at the cold wall (energy balance). Export each table with the Export button of the Table window.")

step("Centre lines for psi, u_max and v_max", "Data Sets > Cut Line 2D",
     "Right-click Results > Data Sets > Cut Line 2D. Data set: Solution 2; Point 1 (0.5, 0), Point 2 (0.5, 1). Add a second cut line from (0, 0.5) to (1, 0.5).",
     [dict(src=SCUT, crop=(0, 95, 1389, 668), name="a", boxes=[(60, 643, 145, 660, 1), (296, 127, 552, 145, 2), (252, 220, 552, 262, 3), (985, 150, 1003, 610, 4)])],
     [(1, "Cut Line 2D 1."),
      (2, "Data set: Solution 2."),
      (3, "Point 1: x = 0.5, y = 0; Point 2: x = 0.5, y = 1."),
      (4, "The vertical centre line x = 0.5 (red).")],
     "COMSOL does not give the stream function directly. But u = dpsi/dy and psi = 0 on the bottom wall, so the stream function at the centre is psi(0.5, 0.5) = integral of u(0.5, y) dy from 0 to 0.5. On a mapped mesh u is linear between the nodes along x = 0.5, so the trapezoidal rule on the exported nodal values is exact for the finite element solution.")

step("Export the centre-line data", "Results > Export > Data",
     "Right-click Results > Export > Data. Data set Cut Line 2D 1; one file per solution (choose the Parameter value, change the file name, click Export).",
     [dict(src=SEXP, crop=(240, 72, 565, 530), name="a", boxes=[(334, 127, 552, 145, 2), (334, 152, 552, 170, 3), (252, 228, 552, 281, 4), (357, 496, 484, 514, 5), (243, 78, 292, 95, 6)]), dict(src=SEXP, crop=(0, 560, 240, 795), name="b", boxes=[(60, 760, 112, 776, 1)])],
     [(1, "Data 1 (export node)."),
      (2, "Data set: Cut Line 2D 1 (then 2D 2 for y = 0.5)."),
      (3, "Parameter value: one of the six (nel, Ra) pairs."),
      (4, "Expressions u, v, T (one per row; type T with Shift, see the tips page)."),
      (5, "Filename, e.g. ...\\cutx_1.txt ... cutx_6.txt and cuty_1.txt ... cuty_6.txt."),
      (6, "Export.")],
     "The files list x, y, u, v, T at the mesh nodes along the line (33, 65 or 129 rows). The supplied script p7_comsol.py reads them and computes |psi| at the centre, the largest u and v and their positions (a parabola through the three nodes around the largest node value), and Richardson extrapolation.")

step("Plot isotherms and streamlines", "Temperature (nitf) > Streamline",
     "Select the Temperature (nitf) plot group, choose nel = 32 and Ra. Right-click it > Streamline. Positioning: Start point controlled, Entry method: Coordinates.",
     [dict(src=SSTR, crop=(0, 95, 1389, 650), name="a", boxes=[(60, 776, 140, 793, 1), (252, 375, 552, 416, 2), (252, 423, 552, 467, 3), (715, 150, 1175, 610, 4)])],
     [(1, "Streamline 1 inside the Temperature plot group."),
      (2, "Start point controlled, Coordinates."),
      (3, "x: 0.5 0.5 0.5 0.5 0.5 0.5 0.5 0.5;  y: 0.56 0.62 0.68 0.74 0.8 0.86 0.92 0.97."),
      (4, "Closed streamlines over the temperature field (Ra = 1e4).")],
     "The flow is a closed circulation, so streamlines released from points on the vertical centre line close on themselves. In Surface 1 we changed the Color table to Rainbow (red = hot, blue = cold). The streamlines are the contour lines of psi; their spacing shows the speed.")

step("Compare the two Rayleigh numbers", "Temperature (nitf)",
     "Switch the Parameter value (Ra) of the plot group between 1000 and 10000 and click Plot.",
     [dict(src=ST3, crop=(570, 95, 1389, 650), name="a", boxes=[(735, 172, 1155, 590, 1)]),
      dict(src=ST4, crop=(570, 95, 1389, 650), name="b", boxes=[(735, 172, 1155, 590, 2)])],
     [(1, "Ra = 1000: the isotherms (colour bands) are almost vertical, as in pure conduction; the circulation is weak and nearly circular."),
      (2, "Ra = 10000: the isotherms are strongly tilted; thin hot and cold layers along the side walls and a stratified core (warm at the top, cold at the bottom). The vortex is flattened.")],
     "At Ra = 1e3 heat crosses the cavity mostly by conduction (Nu = 1.12, only 12 % more than conduction). At Ra = 1e4 the flow is about four times stronger (|psi| 5.07 against 1.17) and carries hot fluid up and over to the cold wall: the heat transfer more than doubles (Nu = 2.24).")


# ---------------- helpers ----------------
def fig_at(path, x, y_top, w):
    im = Image.open(path)
    h = w * im.size[1] / im.size[0]
    c.drawImage(ImageReader(path), x, y_top - h, w, h)
    return y_top - h


def small_table(x, y, widths, rows, size=8.8, lead=14.5, hdr=True, bold_rows=()):
    tw = sum(widths)
    for k_, r in enumerate(rows):
        if k_ == 0 and hdr:
            c.setFillColorRGB(0.9, 0.93, 0.98)
            c.rect(x, y - lead + 3.5, tw, lead, fill=1, stroke=0)
        c.setFont("UIB" if (k_ == 0 and hdr) or k_ in bold_rows else "UI", size)
        c.setFillColorRGB(0.1, 0.1, 0.12)
        xx = x
        for w_, t in zip(widths, r):
            c.drawString(xx + 4, y - 7.5, t)
            xx += w_
        c.setStrokeColorRGB(0.82, 0.84, 0.9)
        c.line(x, y - lead + 3.5, x + tw, y - lead + 3.5)
        y -= lead
    return y


def pct(a, b):
    return "%+.2f %%" % (100 * (a / b - 1))


def cover():
    c.setFillColorRGB(*NAVY)
    c.rect(0, 0, W, H, fill=1, stroke=0)
    c.setFillColorRGB(1, 1, 1)
    c.setFont("UIB", 30)
    c.drawString(60, H - 140, "Natural convection in a heated square cavity")
    c.setFont("UI", 17)
    c.drawString(60, H - 178, "Solved with COMSOL Multiphysics 4.3a and compared with the finite difference solution")
    y = H - 226
    for t in ["Problem 7 of Introduction to CFD: air (Pr = 0.71) in a square cavity with a hot left wall, a cold right wall and insulated top and bottom; steady buoyancy-driven flow for Ra = 1e3 and 1e4.",
              "COMSOL (Non-Isothermal Flow, mapped 32 x 32 mesh): |psi|_centre = %.3f and %.3f, average Nusselt number %.3f and %.3f. de Vahl Davis (1983): 1.174 and 5.071, Nu = 1.118 and 2.243. FDM notebook (33 x 33 nodes): 1.185 and 5.129, Nu = 1.118 and 2.268." % (cv(32, 1000, "psi_mid"), cv(32, 10000, "psi_mid"), cv(32, 1000, "nu_hot"), cv(32, 10000, "nu_hot")),
              "Inside: how the dimensionless problem becomes COMSOL inputs, 20 annotated COMSOL steps with 'Why?' notes, results, comparison with the FDM and the benchmark, grid study (32, 64, 128), troubleshooting. The hand calculation and the FDM itself are in the course's 02_solution.pdf and 03_fdm_solver.ipynb."]:
        y = para(60, y, 410, t, size=12, lead=16.5, color=(0.82, 0.88, 1.0))
        y -= 8
    p = annotate(ST4, (735, 140, 1345, 600), [], "cover_T4")
    im = Image.open(p)
    iw = 300
    ih = iw * im.size[1] / im.size[0]
    c.setFillColorRGB(1, 1, 1)
    c.roundRect(W - iw - 50 - 6, 120 - 6, iw + 12, ih + 12, 8, fill=1, stroke=0)
    c.drawImage(ImageReader(p), W - iw - 50, 120, iw, ih)
    c.setFillColorRGB(0.82, 0.88, 1.0)
    c.setFont("UI", 9.5)
    c.drawString(W - iw - 50, 100, "Ra = 1e4: temperature (colours) and streamlines, COMSOL 32 x 32")
    c.setFont("UI", 10)
    c.drawString(60, 70, "Model file: natural_convection_comsol.mph  (sweep nel = 32, 64, 128 and Ra = 1e3, 1e4, all solved)")
    c.showPage()
    page_no[0] += 1


def problem_page():
    header("The problem and how it becomes a COMSOL model", "Problem 7")
    y = H - 75
    y = para(M, y, 385, "A square cavity of side L is filled with air. The left wall is hot (T_h), the right wall cold (T_c), the top and bottom walls are insulated, and gravity points down. Buoyancy makes the air rise along the hot wall and sink along the cold wall. Find the steady flow, the temperature field and the average Nusselt number for Ra = 1e3 and 1e4 (Pr = 0.71) and compare with de Vahl Davis (1983).", size=10.2, lead=13.7)
    y -= 2
    y = fig_at(os.path.join(OUT, "p7_domain.png"), M + 45, y, 290) - 4
    y = h2(M, y, "Benchmark (de Vahl Davis 1983, Pr = 0.71)")
    rows = [("", "|psi| centre", "u_max on x = 0.5 (y)", "v_max on y = 0.5 (x)", "Nu avg"),
            ("Ra = 1e3", "1.174", "3.649 (0.813)", "3.697 (0.178)", "1.118"),
            ("Ra = 1e4", "5.071", "16.178 (0.823)", "19.617 (0.119)", "2.243")]
    small_table(M, y + 4, [62, 70, 110, 110, 50], rows, size=8.8)
    rx = M + 420
    ry = H - 75
    ry = h2(rx, ry, "Dimensionless equations (Boussinesq)")
    ry = eq_row(rx, ry + 4, r"$\nabla\cdot\mathbf{u}=0,\qquad (\mathbf{u}\cdot\nabla)\mathbf{u}=-\nabla p+Pr\,\nabla^2\mathbf{u}+Ra\,Pr\,(T-T_0)\,\mathbf{e}_y$", 11.5, maxw=355)
    ry = eq_row(rx, ry, r"$\mathbf{u}\cdot\nabla T=\nabla^2 T$", 12, maxw=355)
    ry = para(rx, ry, 355, "lengths in L, velocities in alpha/L, T = (T_dim - T_c)/(T_h - T_c). The FDM uses the curl of the momentum equation (stream function and vorticity); COMSOL solves these primitive-variable equations as they stand.", size=9.8, lead=13)
    ry -= 4
    ry = h2(rx, ry, "COMSOL's equations with unit properties")
    ry = eq_row(rx, ry + 4, r"$\rho(\mathbf{u}\cdot\nabla)\mathbf{u}=-\nabla p+\mu\nabla^2\mathbf{u}+\mathbf{F},\qquad \rho C_p\,\mathbf{u}\cdot\nabla T=k\nabla^2T$", 11.5, maxw=355)
    ry = para(rx, ry, 355, "become the dimensionless equations above when we choose:", size=9.8, lead=13)
    rows = [("COMSOL input", "value", "why"), ("L (square side)", "1 m", "x, y are x/L"), ("rho, Cp, k", "1, 1, 1", "alpha = k/(rho Cp) = 1"),
            ("mu (dynamic viscosity)", "Pr = 0.71 Pa s", "nu = mu/rho = Pr"), ("T_h, T_c", "1 K, 0 K", "T in K is dimensionless T"),
            ("F_y (volume force)", "Ra Pr rho (T - T0)", "buoyancy, T0 = 0.5 K"), ("pressure point", "p = 0 at (0, 0)", "closed cavity")]
    ry = small_table(rx, ry, [120, 105, 130], rows, size=8.8)
    ry -= 12
    para(rx, ry, 355, "Nusselt number: Nu(y) = -dT/dx on the hot wall, Nu_avg = integral over the wall (= 1 for pure conduction). Assumptions: steady, 2D, laminar, constant properties except the density in the buoyancy force, no radiation or viscous heating.", size=9.6, lead=12.8, color=(0.25, 0.25, 0.3))
    footer()
    c.showPage()


def step_pages(i, st):
    groups, cur, curw = [], [], 0
    for im in st["imgs"]:
        w = im["crop"][2] - im["crop"][0]
        if cur and curw + w > 1000:
            groups.append(cur)
            cur, curw = [], 0
        cur.append(im)
        curw += w
    groups.append(cur)
    for gi, grp in enumerate(groups):
        last = gi == len(groups) - 1
        header("Step %d - %s" % (i, st["title"]), st["sub"] + ("  (part %d of %d)" % (gi + 1, len(groups)) if len(groups) > 1 else ""))
        y = H - 66
        if gi == 0:
            y = para(M, y - 6, W - 2 * M, st["pre"], font="UII", size=10.5, lead=14, color=(0.25, 0.25, 0.3))
        else:
            y = y - 6
        nums = set()
        paths = []
        for im in grp:
            paths.append(annotate(im["src"], im["crop"], im["boxes"], "step%02d_%s%d" % (i, im["name"], gi)))
            nums.update(b[4] for b in im["boxes"])
        items = [it for it in st["items"] if it[0] in nums]
        colw = (W - 2 * M - 18) / 2 - 24
        ih = sum(item_height(t, colw if len(items) > 2 else W - 2 * M - 24) for _, t in items)
        ih = ih / 2 + 14 if len(items) > 2 else ih
        nh = note_height(st["note"]) + 10 if last else 0
        avail = (y - 4) - 46 - ih - nh - 14
        maxh = max(170, min(avail, 360))
        bottom = draw_row(paths, y - 4, maxh=maxh)
        y3 = draw_items(items, M, bottom - 14, W - 2 * M, ncols=2 if len(items) > 2 else 1)
        if last:
            note_box(st["note"], y3 - 6)
        footer()
        c.showPage()


def results_page():
    header("Results: COMSOL against the FDM notebook and the benchmark", "main grid: 33 x 33 nodes")
    y = H - 72
    rows = [("", "|psi| centre", "u_max (y)", "v_max (x)", "Nu hot wall", "Nu cold wall")]
    for ra in (1000, 10000):
        b, f = BE[str(ra)], FD_[str(ra)]["32"]
        rows.append(("Ra = %g  de Vahl Davis" % ra, "%.3f" % b["psi"], "%.3f (%.3f)" % (b["umax"], b["yu"]), "%.3f (%.3f)" % (b["vmax"], b["xv"]), "%.3f" % b["nu"], ""))
        rows.append(("      FDM 33 x 33 nodes", "%.4f" % f[0], "%.3f (%.3f)*" % (f[1], f[2]), "%.3f (%.3f)*" % (f[3], f[4]), "%.4f" % f[5], "%.4f" % f[5]))
        rows.append(("      COMSOL 32 x 32", "%.4f" % cv(32, ra, "psi_mid"), "%.3f (%.3f)" % (cv(32, ra, "umax"), cv(32, ra, "yu")), "%.3f (%.3f)" % (cv(32, ra, "vmax"), cv(32, ra, "xv")), "%.4f" % cv(32, ra, "nu_hot"), "%.4f" % cv(32, ra, "nu_cold")))
        rows.append(("      FDM vs benchmark", pct(f[0], b["psi"]), pct(f[1], b["umax"]), pct(f[3], b["vmax"]), pct(f[5], b["nu"]), ""))
        rows.append(("      COMSOL vs benchmark", pct(cv(32, ra, "psi_mid"), b["psi"]), pct(cv(32, ra, "umax"), b["umax"]), pct(cv(32, ra, "vmax"), b["vmax"]), pct(cv(32, ra, "nu_hot"), b["nu"]), ""))
    y = small_table(M, y, [175, 95, 115, 115, 95, 95], rows, size=9, lead=15.5, bold_rows=(1, 6))
    y -= 4
    y = para(M, y, W - 2 * M, "* FDM maxima are the largest node values printed by the notebook (no interpolation between nodes); COMSOL maxima use a parabola through the three nodes around the largest node value. The FDM hot- and cold-wall averages agree to all printed digits (notebook); so do COMSOL's (to 14 digits): energy is conserved and the problem is centro-symmetric.", size=8.8, lead=11.8, color=(0.3, 0.3, 0.35))
    y -= 6
    y = h2(M, y, "What agrees and what does not")
    pts = ["Agrees: both methods give the same flow pattern and the same physics: a single clockwise cell, Nu = 1.12 at Ra = 1e3 and about 2.24 at Ra = 1e4, hot and cold wall Nu equal (energy balance). Every COMSOL and FDM value is within 1.2 % of de Vahl Davis on the main grid.",
           "Agrees: on the finer grids both converge to the same numbers. |psi| centre: COMSOL 128 x 128 %.4f / %.4f, FDM Richardson %.4f / %.4f, benchmark 1.174 / 5.071 (Ra = 1e3 / 1e4)." % (cv(128, 1000, "psi_mid"), cv(128, 10000, "psi_mid"), FR["1000"]["psi"], FR["10000"]["psi"]),
           "Differs: on the same 33 x 33 nodes COMSOL is closer to the benchmark than the FDM for |psi| and for Nu at Ra = 1e4 (|psi|: %s against %s; Nu: %s against %s). On this grid the FDM overestimates |psi| and Nu by about 1 %%; COMSOL's Nu is slightly low (-0.1 and -0.4 %%) and its |psi| is within 0.3 %%. The two discretisations are different (finite differences for psi-omega-T with Thom's first-order wall vorticity, against stabilised linear finite elements for u, v, p, T), so their errors on a coarse grid differ in size and sign." % (pct(cv(32, 10000, "psi_mid"), 5.071), pct(FD_["10000"]["32"][0], 5.071), pct(cv(32, 10000, "nu_hot"), 2.243), pct(FD_["10000"]["32"][5], 2.243)),
           "Differs: at Ra = 1e3 the FDM Nu on 33 x 33 (1.1181) is closer to 1.118 than COMSOL's (1.1165, -0.14 %). COMSOL reaches 1.1177 on 128 x 128."]
    for t in pts:
        c.setFillColorRGB(*ACC); c.circle(M + 4, y - 4, 2.2, fill=1, stroke=0)
        y = para(M + 12, y - 8, W - 2 * M - 12, t, size=9.6, lead=12.8) - 4
    footer()
    c.showPage()


def profiles_page():
    header("Velocity along the centre lines", "COMSOL 32 x 32 and 128 x 128, with the de Vahl Davis maxima")
    y = H - 70
    y = fig_at(os.path.join(OUT, "p7_profiles.png"), M + 40, y, 690) - 6
    rows = [("", "u_max (y), 32", "u_max (y), 128", "v_max (x), 32", "v_max (x), 128", "benchmark u_max (y)", "benchmark v_max (x)")]
    for ra in (1000, 10000):
        b = BE[str(ra)]
        rows.append(("Ra = %g" % ra, "%.3f (%.3f)" % (cv(32, ra, "umax"), cv(32, ra, "yu")), "%.3f (%.3f)" % (cv(128, ra, "umax"), cv(128, ra, "yu")),
                     "%.3f (%.3f)" % (cv(32, ra, "vmax"), cv(32, ra, "xv")), "%.3f (%.3f)" % (cv(128, ra, "vmax"), cv(128, ra, "xv")),
                     "%.3f (%.3f)" % (b["umax"], b["yu"]), "%.3f (%.3f)" % (b["vmax"], b["xv"])))
    y = small_table(M, y, [70, 105, 110, 105, 110, 120, 120], rows, size=8.8)
    y -= 4
    para(M, y, W - 2 * M, "The 32 x 32 and 128 x 128 curves lie on top of each other at plotting scale. u(0.5, y) is positive in the upper half (flow from the hot to the cold wall along the top) and negative in the lower half; v(x, 0.5) is positive near the hot wall (rising) and negative near the cold wall. At Ra = 1e4 the vertical velocity peaks in thin layers next to the side walls (x = 0.12 and 0.88). On 128 x 128 the maxima agree with de Vahl Davis to 0.1 % and the positions to 0.002.", size=9.6, lead=12.8)
    footer()
    c.showPage()


def grid_page():
    header("Grid study: COMSOL 32 / 64 / 128 and the FDM notebook 8 ... 64", "Verification")
    y = H - 70
    y = fig_at(os.path.join(OUT, "p7_convergence.png"), M + 40, y, 640) - 6
    rows = [("", "COMSOL 32", "COMSOL 64", "COMSOL 128", "COMSOL Richardson", "order", "FDM 64", "FDM Richardson", "benchmark")]
    for ra in (1000, 10000):
        for q, qf, lab in (("psi_mid", "psi", "|psi|"), ("nu_hot", "nu", "Nu")):
            ri = RI[str(ra)][q]
            rows.append(("%s, Ra = %g" % (lab, ra), "%.4f" % cv(32, ra, q), "%.4f" % cv(64, ra, q), "%.4f" % cv(128, ra, q),
                         "%.4f" % ri["extrap"], "%.2f" % ri["order"], "%.4f" % FD_[str(ra)]["64"][0 if qf == "psi" else 5],
                         "%.4f" % FR[str(ra)][qf], "%.3f" % BE[str(ra)][qf]))
    y = small_table(M, y, [95, 72, 72, 76, 102, 46, 62, 92, 70], rows, size=8.8)
    y -= 4
    para(M, y, W - 2 * M, "Richardson: f = f_128 + (f_128 - f_64)/3; order = log2[(f_32 - f_64)/(f_64 - f_128)]. COMSOL converges with an observed order of about 2 for |psi| and Nu, like the FDM. The extrapolated values of the two methods agree with each other and with de Vahl Davis to 0.1 % (COMSOL Nu at Ra = 1e4: 2.2449; FDM: 2.2423; benchmark 2.243), so the grid-independent answer is known to about 0.1 % from these grids, not better. FDM grids: N = 8, 16, 32, 64 intervals (notebook); COMSOL: 32, 64, 128 elements.", size=9.4, lead=12.4)
    footer()
    c.showPage()


def answers_page():
    header("Summary: what was compared and what was verified", "Summary")
    y = H - 78
    items = [("Model.", "Non-Isothermal Flow (nitf) in COMSOL 4.3a with unit properties (L = rho = Cp = k = 1, mu = Pr), a Boussinesq volume force Ra Pr rho (T - 0.5), T = 1 / 0 on the left / right walls, insulated top and bottom, no slip, a pressure point, a mapped nel x nel mesh, and a sweep over nel = 32, 64, 128 and Ra = 1e3, 1e4. Linear elements for u, v, p and T (4356 unknowns on 32 x 32)."),
             ("Results (32 x 32).", "|psi| centre %.4f and %.4f; Nu %.4f and %.4f (Ra = 1e3 and 1e4). The flow is a single clockwise cell; at Ra = 1e4 thin boundary layers and a stratified core form." % (cv(32, 1000, "psi_mid"), cv(32, 10000, "psi_mid"), cv(32, 1000, "nu_hot"), cv(32, 10000, "nu_hot"))),
             ("Against de Vahl Davis.", "COMSOL is within 0.5 % on 32 x 32 for |psi|, u_max, v_max and Nu, and within 0.1 % on 128 x 128 (largest: v_max at Ra = 1e4, +0.09 %)."),
             ("Against the FDM notebook.", "Same fields and the same converged values (Richardson estimates agree to 0.1 %). On the same 33 x 33 nodes the FDM errors are larger (up to +1.1 % in |psi| and Nu at Ra = 1e4) and, for Nu, of the opposite sign to COMSOL's. At Ra = 1e3 the FDM Nu on 33 x 33 is the closer one."),
             ("Energy balance.", "Hot-wall and cold-wall Nu agree to 14 digits in COMSOL (and to the printed digits in the FDM)."),
             ("Verified.", "The COMSOL numbers above come from this model file (natural_convection_comsol.mph) and the exported tables; the comparison script p7_comsol.py reproduces them from the exports. The FDM numbers were read from the notebook outputs in the repository; we did not re-run the FDM."),
             ("Not verified.", "The local Nusselt number along the wall was not compared point by point with the FDM. Nu is computed from the gradient of the linear elements at the wall, which is only first-order accurate pointwise; the wall average still converges at about second order here. The guide was checked page by page on screen, not tested with students.")]
    for a, b in items:
        c.setFont("UIB", 10.6)
        c.setFillColorRGB(*NAVY)
        c.drawString(M, y, a)
        y = para(M + 14, y - 14, W - 2 * M - 14, b, size=10, lead=13)
        y -= 4
    footer()
    c.showPage()


def tips_page():
    header("Troubleshooting and tips", "Appendix")
    y = H - 85
    tips = [("The right-click menu does not appear.", "COMSOL is slow: left-click the node first, right-click, and wait two or three seconds."),
            ("A selection list stays empty, or the wrong edge was added.", "Hover over the edge or point until it turns red, click, then press the green + above the list. Wrong entry: select it in the list and press the minus button."),
            ("Fluid 1 or Volume Force does nothing.", "Their Selection starts as Manual with an empty list. Set Selection to All domains."),
            ("The material table shows red stop signs.", "A property needed by the physics has no value. Enter 1 for k, rho and Cp; set gamma = 1 and mu = Pr in Fluid 1."),
            ("Newton's method does not converge at Ra = 1e4.", "Check the initial temperature (1 - x, not 293.15 K), and solve Ra = 1e3 first (the sweep order nel, Ra does this), so that 1e4 starts from the 1e3 solution."),
            ("The flow turns the wrong way or there is no flow.", "Check the sign and the y component of the Volume Force (+Ra*Pr*rho*(T-T0) in y), and that the hot wall (T = 1) is on the left."),
            ("An expression with T gives seconds as unit.", "Lower-case t is time. Type a capital T (Shift+T); after typing, the Unit column must show K."),
            ("The export file is empty or was not written.", "Click the Filename field, Ctrl+A, Delete, type the full path, press Tab, then Export. Typing over a selected path can leave the field empty ('Empty filename')."),
            ("Exporting the sweep in one go.", "Export > Data takes one Parameter value at a time: repeat with each (nel, Ra) and a new file name. Derived Values (Line Integration) with Parameter selection All give all six values in one table."),
            ("Save your work.", "File > Save As into a folder you can write to; compare with the supplied natural_convection_comsol.mph.")]
    for a, b in tips:
        c.setFont("UIB", 10.6)
        c.setFillColorRGB(*NAVY)
        c.drawString(M, y, a)
        y = para(M + 14, y - 14, W - 2 * M - 14, b, size=10, lead=13)
        y -= 5
    footer()
    c.showPage()


cover()
problem_page()
for i, st in enumerate(STEPS, 1):
    step_pages(i, st)
results_page()
profiles_page()
grid_page()
answers_page()
tips_page()
c.save()
print("saved pages", page_no[0])
