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

SRC = r"C:\Users\marya\.claude\projects\C--Users-marya-Downloads\96f79627-e0ee-4a3c-8285-e9d0c9c1aee4\tool-results\mcp-computer-use-blob-"
OUT = r"C:\Users\marya\Downloads\cavity_comsol"
SHOTS = os.path.join(OUT, "shots")
os.makedirs(SHOTS, exist_ok=True)


def S(i):
    return SRC + i + ".jpg"


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
    p = os.path.join(SHOTS, name + ".png")
    out.save(p)
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
c = canvas.Canvas(os.path.join(OUT, "COMSOL_Lid_Driven_Cavity_Guide.pdf"), pagesize=(W, H))
c.setTitle("COMSOL Multiphysics 4.3a - Lid-driven cavity (stream function - vorticity FDM) - student guide")
c.setAuthor("Claude")
page_no = [0]
NAVY = (0.09, 0.2, 0.42)
ACC = (0.86, 0.15, 0.15)


def footer():
    page_no[0] += 1
    c.setFont("UI", 8)
    c.setFillColorRGB(0.45, 0.45, 0.5)
    c.drawString(M, 20, "COMSOL 4.3a  |  Problem 6: lid-driven cavity, Re = 100  |  student guide")
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


import sys
import numpy as np
sys.path.insert(0, OUT)
from scipy.interpolate import CubicSpline
from p6_solver import GHIA_X, GHIA_Y, GHIA_U, GHIA_V, GHIA_PSI, velocities
NUM = json.load(open(os.path.join(OUT, "p6_numbers.json")))
CNUM = json.load(open(os.path.join(OUT, "p6_comsol_numbers.json")))
SELF = json.load(open(os.path.join(OUT, "p6_selfconv.json")))
N4 = json.load(open(os.path.join(OUT, "p6_n4.json")))
G = NUM["grid"]; CR = CNUM["res"]
FC = np.load(os.path.join(OUT, "p6_comsol_fields.npz"))
psi32 = np.load(os.path.join(OUT, "p6_psi_32.npy"))
u32, v32 = velocities(psi32, 32)
xs32 = np.linspace(0, 1, 33)
FDM_U = CubicSpline(xs32, u32[16])(GHIA_Y); FDM_V = CubicSpline(xs32, v32[:, 16])(GHIA_X)
COM_U = CubicSpline(xs32, FC["u32"][16])(GHIA_Y); COM_V = CubicSpline(xs32, FC["v32"][:, 16])(GHIA_X)


def sid(i):
    return S(i)


SDIM = sid("1793178665834-bsxtet"); SPHYS = sid("1793178691687-yvbef6"); SSTUDY = sid("1793178700655-qgrir3")
STREE = sid("1793178705442-13ob0n"); SGEOMMENU = sid("1793178710774-tv1q5j"); SSQUARE = sid("1793178735109-dra1dx")
SFLUID = sid("1793178773562-hrk7qs"); SWALL2 = sid("1793178799650-i896jv"); SSLIDE = sid("1793178826869-bxapq9")
SPOINTM = sid("1793178835192-32lv5n"); SPOINT = sid("1793178850146-g81dve"); SPARAM = sid("1793178895377-81adii")
SMESHM = sid("1793178902913-6zn1lj"); SDIST = sid("1793178924916-o7tddx"); SMESH = sid("1793178947161-nzx2bm")
SSOLVE1 = sid("1793178963556-4qeze8"); SWEAKWIZ = sid("1793179047792-41jt9w"); SWEAKEXPR = sid("1793179701244-rke76w")
SDIRI = sid("1793179119697-slsvvt"); SSOLVE2 = sid("1793179144141-99cfhr"); SCONTOUR = sid("1793179200293-2jj46z")
SVORT = sid("1793179264054-fh1otd"); SSWEEP = sid("1793179305487-1lptwq"); SSWDONE = sid("1793179350054-2ks7fw")
SEXPORT = sid("1793179400286-7p74vh")

STEPS = []


def step(title, sub, pre, imgs, items, note):
    STEPS.append(dict(title=title, sub=sub, pre=pre, imgs=imgs, items=items, note=note))


step("Start a 2D model", "Model Wizard 1 of 4",
     "Start COMSOL Multiphysics 4.3a. The Model Wizard opens (if not: File > New).",
     [dict(src=SDIM, crop=(0, 55, 570, 230), name="a", boxes=[(246, 147, 285, 164, 1), (524, 86, 542, 103, 2)])],
     [(1, "Select 2D: the cavity is very long in the third direction, so the flow is two-dimensional (Assumption 2)."),
      (2, "Click the Next arrow. Tip: if a later click on Next seems to do nothing, wait a second and look again - COMSOL answers slowly.")],
     "A 2D model needs only the square cross-section of the cavity. The third direction is infinitely long, so nothing changes along it.")

step("Add Laminar Flow", "Model Wizard 2 of 4",
     "The Navier-Stokes equations for a steady, incompressible, laminar flow are solved by the Laminar Flow interface.",
     [dict(src=SPHYS, crop=(0, 55, 570, 480), name="a",
           boxes=[(288, 243, 396, 259, 1), (245, 347, 262, 363, 2), (259, 390, 368, 407, 3), (524, 86, 542, 103, 4)])],
     [(1, "Open Fluid Flow > Single-Phase Flow and select Laminar Flow (spf)."),
      (2, "Click the blue + (Add Selected) button."),
      (3, "It appears under Selected physics."),
      (4, "Click Next.")],
     "COMSOL solves for the velocity (u, v) and the pressure p directly (a 'primitive variable' formulation). The problem statement solves for the stream function and the vorticity instead; both describe the same flow, so we can compare the two methods.")

step("Choose a stationary study", "Model Wizard 3 of 4",
     "Steady state: nothing changes with time (Assumption 1).",
     [dict(src=SSTUDY, crop=(0, 55, 570, 420), name="a", boxes=[(274, 149, 343, 166, 1), (541, 86, 559, 103, 2)])],
     [(1, "Select Stationary (under Preset Studies)."),
      (2, "Click Finish (the chequered-flag icon).")],
     "FDM reaches the steady state by iterating from rest (Gauss-Seidel). COMSOL's stationary study solves the nonlinear steady equations directly with Newton's method.")

step("Tour of the model tree", "Model Builder",
     "After Finish the Model Builder shows the model outline.",
     [dict(src=STREE, crop=(0, 55, 570, 320), name="a",
           boxes=[(47, 161, 122, 178, 1), (47, 194, 155, 211, 2), (60, 211, 162, 228, 3), (60, 227, 110, 244, 4), (47, 260, 100, 277, 5), (33, 277, 92, 294, 6)])],
     [(1, "Geometry 1: the square cavity."),
      (2, "Laminar Flow (spf): the equations."),
      (3, "Fluid Properties 1: density and viscosity (we enter rho = 1 and mu = 0.01)."),
      (4, "Wall 1: no-slip on all boundaries by default. We add a second wall node for the moving lid."),
      (5, "Mesh 1: the grid."),
      (6, "Study 1 with Step 1: Stationary.")],
     "Wall 1 already gives u = v = 0 on all four sides. We only have to change the lid, and fix the pressure level.")

step("Create the geometry: a unit square", "Geometry",
     "The cavity is the square 0 <= x, y <= 1 m.",
     [dict(src=SGEOMMENU, crop=(0, 95, 310, 420), name="a", boxes=[(47, 160, 122, 178, 1), (100, 282, 190, 300, 2)]),
      dict(src=SSQUARE, crop=(240, 95, 565, 420), name="b", boxes=[(252, 178, 552, 196, 3), (252, 252, 552, 292, 4)]),
      dict(src=SSQUARE, crop=(570, 95, 1389, 650), name="c", boxes=[(754, 123, 1237, 606, 5)])],
     [(1, "Right-click Geometry 1 (left-click it first if no menu appears)."),
      (2, "Choose Square."),
      (3, "Side length = 1 (m): the default."),
      (4, "Base: Corner, x = 0, y = 0: the default."),
      (5, "Click Build Selected (or F8). The square appears; its four edges are numbered 1 (left), 2 (right), 3 (top) and 4 (bottom) - we use boundary 3, the lid.")],
     "No typing is needed: the default square already has the size and position of the cavity. COMSOL numbers the corner points 1 (0,0), 2 (1,0), 3 (0,1), 4 (1,1).")

step("Enter the fluid properties", "Laminar Flow > Fluid Properties 1",
     "Re = U L rho / mu = 100 requires nu = mu / rho = 0.01 m^2/s. We choose rho = 1 kg/m^3 and mu = 0.01 Pa s.",
     [dict(src=SFLUID, crop=(240, 95, 565, 480), name="a", boxes=[(266, 365, 552, 383, 1), (266, 388, 508, 406, 2), (266, 432, 552, 450, 3), (266, 455, 508, 473, 4)])],
     [(1, "Click Fluid Properties 1, then set Density to User defined."),
      (2, "Type 1 (kg/m^3). (Click in the field, Ctrl+A, type, press Tab.)"),
      (3, "Set Dynamic viscosity to User defined."),
      (4, "Type 0.01 (Pa s).")],
     "Only the ratio matters for an incompressible flow with fixed velocity scale: Re = U L / nu = 1 x 1 / 0.01 = 100. We did not use a material from the library because the problem gives nu directly.")

step("Make the top boundary a moving lid", "Laminar Flow > Wall 2",
     "Right-click Laminar Flow > Wall to add a second wall node (Wall 2); it appears in the tree.",
     [dict(src=SWALL2, crop=(0, 95, 1389, 640), name="a", boxes=[(60, 294, 112, 311, 1), (535, 146, 552, 163, 2), (755, 115, 1237, 133, 3)]),
      dict(src=SSLIDE, crop=(240, 95, 565, 410), name="b", boxes=[(252, 146, 512, 236, 4), (252, 340, 552, 358, 5), (252, 382, 552, 402, 6)])],
     [(1, "Select Wall 2 in the tree."),
      (2, "Hover over the top edge in the graphics window until it turns red, click it, then press the + button next to the list: boundary 3 appears in the list."),
      (3, "The top edge (red/blue) is the lid."),
      (4, "The selection list shows boundary 3."),
      (5, "Boundary condition: Sliding wall (not Moving wall - that one is for deforming meshes)."),
      (6, "Velocity of the tangentially moving wall U_w = 1 m/s.")],
     "Wall 1 (no slip) still applies to the three other boundaries, because Wall 2 overrides it on boundary 3 only. We checked after solving that u = +1.000 at the middle of the lid: U_w = 1 moves the lid to the right.")

step("Fix the pressure level", "Laminar Flow > Pressure Point Constraint",
     "The cavity is closed, so the pressure is defined only up to a constant. The solver needs one point where p is fixed. Right-click Laminar Flow > Points > Pressure Point Constraint.",
     [dict(src=SPOINTM, crop=(0, 95, 700, 600), name="a", boxes=[(100, 531, 190, 549, 1), (350, 531, 530, 551, 2)]),
      dict(src=SPOINT, crop=(240, 95, 565, 360), name="b", boxes=[(252, 146, 512, 236, 3), (252, 313, 552, 331, 4)]),
      dict(src=SPOINT, crop=(570, 95, 1389, 650), name="c", boxes=[(744, 595, 766, 617, 5)])],
     [(1, "Right-click Laminar Flow (left-click it first) and open Points."),
      (2, "Choose Pressure Point Constraint."),
      (3, "Hover over the lower left corner until it turns red, click it, press +: point 1 is in the list."),
      (4, "p0 = 0 Pa."),
      (5, "The constrained corner (0, 0) is shown in blue.")],
     "Without this constraint the pressure matrix is singular and the solver stops. Any point and any value give the same velocity; only the pressure level changes.")

step("Define the number of elements as a parameter", "Global Definitions > Parameters",
     "A parameter lets us sweep the mesh from 4 x 4 to 128 x 128 (Task 7) without rebuilding the model.",
     [dict(src=SPARAM, crop=(0, 95, 565, 540), name="a", boxes=[(44, 125, 150, 143, 1), (252, 148, 552, 170, 2), (252, 418, 552, 515, 3)])],
     [(1, "Right-click Global Definitions > Parameters."),
      (2, "One row: nel = 32 (elements per side). Name nel, Expression 32, Description elements per side."),
      (3, "The fields below the table show the selected row.")],
     "We use the name nel (lower case): typing a capital N through the automation gave a lower-case n, and a one-letter name could collide with the COMSOL variable names. Any name works.")

step("Build the mapped mesh", "Mesh 1 > Mapped > Distribution",
     "The problem asks for a structured grid of square elements, like the FDM grid: a Mapped mesh with the same number of elements on every side.",
     [dict(src=SMESHM, crop=(0, 330, 560, 640), name="a", boxes=[(47, 343, 105, 360, 1), (90, 419, 230, 437, 2)]),
      dict(src=SDIST, crop=(0, 95, 565, 480), name="b", boxes=[(252, 127, 552, 145, 3), (252, 148, 512, 236, 4), (252, 290, 552, 308, 5), (252, 330, 552, 350, 6)])],
     [(1, "Right-click Mesh 1."),
      (2, "Choose Mapped. COMSOL creates a Size node and a Mapped 1 node."),
      (3, "Right-click Mapped 1 > Distribution; set Selection to All boundaries (boundaries 1-4 appear in the list)."),
      (4, "The list shows boundaries 1, 2, 3, 4."),
      (5, "Distribution properties: Fixed number of elements."),
      (6, "Number of elements: type nel (the parameter). Then click Build All (F8).")],
     "A mapped mesh is a regular grid of quadrilaterals with the same number of elements on opposite sides. With nel = 32, h = 1/32 = 0.03125 m and the nodes coincide with the FDM nodes - which lets us compare node by node later.")

step("The mesh", "Mesh 1",
     "After Build All the mesh is drawn in the graphics window and the Messages window reports the element count.",
     [dict(src=SMESH, crop=(570, 95, 1389, 760), name="a", boxes=[(754, 123, 1237, 606, 1), (570, 690, 1000, 720, 2)])],
     [(1, "32 x 32 square elements of size 0.03125 m."),
      (2, "Message: Complete mesh consists of 1024 elements.")],
     "1024 = 32 x 32, as required. COMSOL's default elements for Laminar Flow are linear (P1 for velocity and pressure, stabilised), so there are 33 x 33 = 1089 nodes per field: 3 fields x 1089 = 3267 unknowns (we will see this number in the Messages window).")

step("Solve and look at the velocity", "Study 1",
     "Select Study 1 and press F8 (Compute).",
     [dict(src=SSOLVE1, crop=(0, 60, 1389, 790), name="a", boxes=[(33, 477, 92, 494, 1), (570, 690, 900, 750, 2), (615, 125, 1275, 640, 3)])],
     [(1, "Study 1: press F8 (or the green = Compute button)."),
      (2, "Number of degrees of freedom solved for: 3267; solution time 2 s."),
      (3, "COMSOL's default plot: speed |u|. The flow is fast under the lid and slow in the core.")],
     "The maximum speed in the plot is 1.22 m/s, larger than the lid speed. It occurs at the nodes of the lid next to the two top corners, where the velocity jumps from 1 to 0 in one element: a numerical overshoot at the corner singularity. The interior flow is not affected.")

step("Add a Weak Form PDE to get the stream function", "Add Physics > Weak Form PDE",
     "COMSOL does not give the stream function of a laminar flow directly. We recover psi from the computed velocity by solving a small extra PDE. Right-click Model 1 > Add Physics, then open Mathematics > PDE Interfaces.",
     [dict(src=SWEAKWIZ, crop=(0, 55, 570, 700), name="a",
           boxes=[(275, 208, 420, 226, 1), (245, 347, 262, 364, 2), (259, 388, 375, 406, 3), (495, 495, 555, 512, 4), (495, 540, 555, 558, 5), (524, 86, 542, 103, 6)])],
     [(1, "Select Weak Form PDE (w)."),
      (2, "Click the + button."),
      (3, "It appears under Selected physics."),
      (4, "Field name: psi."),
      (5, "Dependent variables: replace u2 by psi (double-click the entry, Ctrl+A, type psi, Enter)."),
      (6, "Click Next, then Finish (no new study is needed: the existing Study 1 solves both physics).")],
     "Why a PDE? With u = d psi/dy and v = -d psi/dx, psi is determined by the velocity up to a constant. We fix the constant with psi = 0 on the walls and find psi from the velocity field in the weak sense on the same mesh.")

step("Write the weak equation and the wall condition", "Weak Form PDE 1 and Dirichlet Boundary Condition",
     "The stream function must satisfy psi_x = -v and psi_y = u. In the weak sense: the integral over the cavity of (psi_x + v) test(psi_x) + (psi_y - u) test(psi_y) is zero for every test function.",
     [dict(src=SWEAKEXPR, crop=(0, 95, 565, 380), name="a", boxes=[(60, 360, 165, 377, 1), (252, 322, 552, 346, 2)]),
      dict(src=SDIRI, crop=(0, 95, 565, 440), name="b", boxes=[(60, 410, 226, 427, 3), (252, 124, 552, 142, 4), (252, 343, 536, 361, 5)])],
     [(1, "Select Weak Form PDE 1."),
      (2, "weak expression: -(psix+v)*test(psix)-(psiy-u)*test(psiy). (COMSOL's sign convention: the expression is the residual; the default minus signs correspond to -grad(psi).grad(test).)"),
      (3, "Right-click Weak Form PDE (w) > Dirichlet Boundary Condition."),
      (4, "Selection: All boundaries."),
      (5, "Prescribed value of psi: r = 0 (the walls are streamlines, psi = 0).")],
     "psix, psiy are COMSOL's names for the derivatives of psi; u and v are the velocity components of Laminar Flow. The equation says that the gradient of psi is the rotated velocity (-v, u): the 'projection' of the velocity onto a stream function. For a divergence-free field it reproduces the true psi. Because v and u are linear on the mesh the recovered psi is accurate to the order of the velocity itself.")

step("Solve both physics", "Study 1",
     "The stationary study now solves Laminar Flow and the weak form PDE together.",
     [dict(src=SSOLVE2, crop=(0, 60, 1389, 790), name="a", boxes=[(570, 700, 900, 780, 1), (33, 477, 92, 494, 2)])],
     [(1, "7492 unknowns: 3267 (u, v, p) + 4225 (psi with quadratic elements, 65 x 65 points)."),
      (2, "Select Study 1 and press F8 again.")],
     "Newton's method converges for Re = 100 from the default zero start. The Weak Form PDE is linear in psi, so it needs no extra iterations.")

step("Plot the streamlines", "Results > 2D Plot Group > Contour",
     "The streamlines of a 2D flow are the contour lines of psi. Right-click Results > 2D Plot Group, then right-click the new group > Contour.",
     [dict(src=SCONTOUR, crop=(0, 60, 1389, 660), name="a", boxes=[(252, 205, 552, 224, 1), (322, 396, 552, 414, 2), (615, 125, 1275, 640, 3)])],
     [(1, "Expression: psi (unit 1)."),
      (2, "Total levels: 30. Click Plot (top left of the settings window)."),
      (3, "The streamlines: one big clockwise vortex. The colour bar shows psi down to -0.1015 at the vortex centre.")],
     "Streamlines are closed curves around the primary vortex; the spacing of the lines is proportional to the speed. The minimum psi is the strength of the vortex: the mass flow that circulates (per metre depth, with rho = 1).")

step("Plot the vorticity", "Results > 2D Plot Group > Surface",
     "Create another 2D Plot Group and right-click it > Surface.",
     [dict(src=SVORT, crop=(0, 95, 1389, 660), name="a", boxes=[(252, 210, 536, 228, 1), (252, 376, 532, 520, 2), (615, 125, 1275, 640, 3)])],
     [(1, "Expression: vx-uy (the vorticity v_x - u_y; COMSOL writes the derivatives as vx and uy)."),
      (2, "Range: tick Manual color range, Minimum -12, Maximum 6, and click Plot. (The corner values are far larger and would hide everything else.)"),
      (3, "Strongly negative vorticity under the lid, positive at the side walls: the fluid rotates clockwise.")],
     "The vorticity is about -7 at the middle of the lid (FDM 32 x 32: -6.99) and becomes very large at the two lid corners, where the velocity is discontinuous. These two corner values are singular: they grow without bound when the mesh is refined.")

step("Sweep the mesh (grid study)", "Study 1 > Parametric Sweep",
     "To repeat the calculation for 4, 8, 16, 32, 64 and 128 elements per side, add a parametric sweep. Right-click Study 1 > Parametric Sweep.",
     [dict(src=SSWEEP, crop=(0, 60, 565, 520), name="a", boxes=[(60, 493, 152, 511, 1), (252, 166, 552, 184, 2)])],
     [(1, "Parametric Sweep appears above Step 1."),
      (2, "Click the + button under the table. The row nel (elements per side) is filled in; set the parameter value list to  4 8 16 32 64 128  (separated by spaces) and press Enter.")],
     "The sweep rebuilds the mesh for each value of nel (the mesh depends on the parameter) and solves the whole model each time.")

step("Run the sweep", "Study 1",
     "Select Study 1 and press F8. Six solutions are computed.",
     [dict(src=SSWDONE, crop=(0, 60, 1389, 790), name="a", boxes=[(570, 690, 1100, 780, 1), (252, 155, 552, 172, 2)])],
     [(1, "Messages: degrees of freedom 156, 532, 1956, 7492, 29316 and 115972; total solution time 20 s."),
      (2, "Plots now show the last solution (nel = 128). Their data set has a Parameter value selector to choose another grid.")],
     "The number of unknowns grows four-fold with every halving of h: 156 -> 115972. The 128 x 128 grid has 129 x 129 = 16641 nodes per field.")

step("Export the fields for the comparison", "Results > Export > Data",
     "To compare with the FDM node by node we export psi, u, v and the vorticity at the mesh nodes. Right-click Results > Export > Data.",
     [dict(src=SEXPORT, crop=(0, 60, 565, 700), name="a",
           boxes=[(252, 127, 552, 145, 1), (252, 152, 552, 170, 2), (252, 210, 552, 352, 3), (357, 497, 484, 514, 4), (243, 78, 292, 95, 5)])],
     [(1, "Data set: Solution 2 (the parametric sweep)."),
      (2, "Parameter value (nel): choose the grid, e.g. 4."),
      (3, "Expressions: psi, u, v, vx-uy (type each in a new row of the table and press Enter)."),
      (4, "Filename, e.g. C:\\Users\\...\\cav_n4.txt (type the path into the field; Points to evaluate in: Take from data set = at the mesh nodes)."),
      (5, "Click Export. Repeat for 8, 16, 32, 64, 128 with new file names.")],
     "The files list x, y and the four quantities at the mesh nodes (25, 81, 289, 1089, 4225, 16641 rows). The accompanying Python script p6_comsol.py reads them. If you change the filename field, first clear it (Ctrl+A, Delete) and then type: typing over a selection can leave the field empty.")


# ---------------- helper drawing ----------------
def fig_at(path, x, y_top, w):
    im = Image.open(path)
    h = w * im.size[1] / im.size[0]
    c.drawImage(ImageReader(path), x, y_top - h, w, h)
    return y_top - h


def small_table(x, y, widths, rows, size=8.4, lead=13.6, hdr=True):
    tw = sum(widths)
    for k_, r in enumerate(rows):
        if k_ == 0 and hdr:
            c.setFillColorRGB(0.9, 0.93, 0.98)
            c.rect(x, y - lead + 3.5, tw, lead, fill=1, stroke=0)
        c.setFont("UIB" if (k_ == 0 and hdr) else "UI", size)
        c.setFillColorRGB(0.1, 0.1, 0.12)
        xx = x
        for w_, t in zip(widths, r):
            c.drawString(xx + 4, y - 7.5, t)
            xx += w_
        c.setStrokeColorRGB(0.82, 0.84, 0.9)
        c.line(x, y - lead + 3.5, x + tw, y - lead + 3.5)
        y -= lead
    return y


def cover():
    c.setFillColorRGB(*NAVY)
    c.rect(0, 0, W, H, fill=1, stroke=0)
    c.setFillColorRGB(1, 1, 1)
    c.setFont("UIB", 31)
    c.drawString(60, H - 140, "Lid-driven cavity flow, Re = 100")
    c.setFont("UI", 17)
    c.drawString(60, H - 178, "Finite differences (stream function - vorticity) and COMSOL Multiphysics 4.3a")
    y = H - 226
    g32 = G["32"]; cc = CR["32"]
    for t in ["Problem: steady 2D Navier-Stokes in a square cavity with a sliding lid, solved with the stream function - vorticity formulation and Gauss-Seidel iteration; verified against Ghia, Ghia & Shin (1982) (Introduction to CFD, Problem 6).",
              "Result: primary vortex psi_min = %.4f at (%.3f, %.3f) on the 32 x 32 FDM grid, %.4f on 128 x 128 (Ghia: -0.1034 at (0.617, 0.734)). COMSOL (Laminar Flow, mapped 32 x 32 mesh): %.4f at (%.3f, %.3f)." % (g32["psi_min"], g32["xc"], g32["yc"], G["128"]["psi_min"], cc["psi_min"], cc["xc"], cc["yc"]),
              "Includes: derivation of the stream function - vorticity equations and Thom's wall formula, the hand calculation of the first iterations on a 4 x 4 grid, 20 annotated COMSOL steps, grid study from 4 x 4 to 128 x 128, centre-line comparison with the benchmark, corner eddies."]:
        y = para(60, y, 400, t, size=12, lead=16.5, color=(0.82, 0.88, 1.0))
        y -= 8
    p = os.path.join(OUT, "p6_flow.png")
    im = Image.open(p)
    iw = 290
    ih = iw * im.size[1] / im.size[0]
    c.setFillColorRGB(1, 1, 1)
    c.roundRect(W - iw - 50 - 6, 110 - 6, iw + 12, ih + 12, 8, fill=1, stroke=0)
    c.drawImage(ImageReader(p), W - iw - 50, 110, iw, ih)
    c.setFillColorRGB(0.82, 0.88, 1.0)
    c.setFont("UI", 10)
    c.drawString(60, 70, "Model file: lid_cavity_comsol.mph  (nel = 32 solved, sweep 4 ... 128)")
    c.showPage()
    page_no[0] += 1


def problem_page():
    header("The problem and the physics", "Task 1")
    y = H - 75
    y = para(M, y, 380, "A square cavity of side L = 1 m is filled with an incompressible viscous fluid. The lid slides to the right with U = 1 m/s; the other three walls are at rest. Find the steady flow at Reynolds number Re = U L / nu = 100 (nu = 0.01 m^2/s) with the finite difference method in the stream function - vorticity formulation and compare with the benchmark of Ghia, Ghia and Shin (J. Comput. Phys. 48, 1982).", size=10.2, lead=13.7)
    y -= 4
    rows = [("Quantity", "Symbol", "Value"), ("side of the cavity", "L", "1 m"), ("lid speed (to the right)", "U", "1 m/s"), ("kinematic viscosity", "nu", "0.01 m^2/s"),
            ("Reynolds number", "Re", "100"), ("main grid", "N, h", "32 x 32, 0.03125 m"), ("grid study", "N", "4, 8, 16, 32, 64, 128"), ("hand calculation", "N, h", "4 x 4, 0.25 m")]
    y = table(M, y, [150, 80, 160], rows, size=9.4)
    y -= 8
    y = fig_at(os.path.join(OUT, "p6_domain.png"), M + 60, y, 235) - 6
    para(M, y, 390, "Assumptions: steady; 2D; incompressible Newtonian fluid with constant properties; no gravity or temperature effects.", size=9.6, lead=13, color=(0.25, 0.25, 0.3))
    rx = M + 420
    ry = H - 75
    ry = h2(rx, ry, "Governing equations")
    ry = eq_row(rx, ry + 4, r"$\dfrac{\partial u}{\partial x}+\dfrac{\partial v}{\partial y}=0,\qquad u\dfrac{\partial u}{\partial x}+v\dfrac{\partial u}{\partial y}=-\dfrac{1}{\rho}\dfrac{\partial p}{\partial x}+\nu\nabla^2u$", 11.5, maxw=360)
    ry = eq_row(rx, ry, r"$u\dfrac{\partial v}{\partial x}+v\dfrac{\partial v}{\partial y}=-\dfrac{1}{\rho}\dfrac{\partial p}{\partial y}+\nu\nabla^2v$", 11.5, maxw=360)
    ry = h2(rx, ry - 4, "Stream function and vorticity")
    ry = eq_row(rx, ry + 4, r"$u=\dfrac{\partial\psi}{\partial y},\quad v=-\dfrac{\partial\psi}{\partial x}\ \Rightarrow\ \dfrac{\partial u}{\partial x}+\dfrac{\partial v}{\partial y}=\dfrac{\partial^2\psi}{\partial x\partial y}-\dfrac{\partial^2\psi}{\partial y\partial x}=0$", 11, maxw=360)
    ry = para(rx, ry, 360, "Any psi gives a velocity field that satisfies continuity: the stream function satisfies continuity automatically. Define the vorticity omega = dv/dx - du/dy. Then", size=10, lead=13.4)
    ry = eq_row(rx, ry - 2, r"$\omega=\dfrac{\partial v}{\partial x}-\dfrac{\partial u}{\partial y}=-\nabla^2\psi\qquad\Rightarrow\qquad\nabla^2\psi=-\omega$", 12.5, maxw=360)
    ry = para(rx, ry, 360, "Take d/dx of the y-momentum equation minus d/dy of the x-momentum equation: the pressure terms cancel (d2p/dxdy is the same in both), the rest gives the vorticity transport equation, a convection-diffusion equation as in Problem 5:", size=10, lead=13.4)
    ry = eq_row(rx, ry - 2, r"$u\dfrac{\partial\omega}{\partial x}+v\dfrac{\partial\omega}{\partial y}=\nu\nabla^2\omega$", 13, maxw=360)
    ry = para(rx, ry, 360, "Boundary conditions. The walls are impermeable: no fluid crosses them, so the normal velocity is zero and psi does not change along a wall: psi is constant on each wall, and since the walls are connected psi has the same constant on all four. We choose psi = 0 on all four walls. (Tangential velocity u = psi_y = U on the lid and 0 on the others fixes psi_y, which becomes the wall vorticity condition on the next page.)", size=10, lead=13.4)
    footer()
    c.showPage()


def disc_page():
    header("Wall vorticity, grid and discretisation", "Tasks 2, 3 and 4")
    y = H - 75
    y = h2(M, y, "Thom's formula for the wall vorticity (Task 2)")
    y = para(M, y, 400, "Take the lid (y = L, grid line j = N) with psi_w = 0 on it. Taylor series from the wall into the fluid, step -h in y:", size=10, lead=13.4)
    y = eq_row(M, y - 2, r"$\psi_{N-1}=\psi_w-h\,\psi_y+\dfrac{h^2}{2}\psi_{yy}+O(h^3)$", 13, maxw=380)
    y = para(M, y, 400, "On the wall psi_y = u = U, and psi_xx = 0 because psi = 0 along it, so psi_yy = -omega - psi_xx = -omega_w. Solve for omega_w:", size=10, lead=13.4)
    y = eq_row(M, y - 2, r"$\omega_w=-\dfrac{2(\psi_{N-1}-\psi_w)}{h^2}-\dfrac{2U}{h}\quad\mathrm{(lid)}$", 13, maxw=380)
    y = eq_row(M, y, r"$\omega_w=-\dfrac{2(\psi_{1}-\psi_w)}{h^2}\quad\mathrm{(walls\ at\ rest,\ }\psi_y=0\mathrm{)}$", 13, maxw=380)
    y = para(M, y, 400, "The formula is only first-order accurate for omega (the Taylor series is cut after the psi_yy term), but the overall solution is still second order in psi, as the grid study shows. The extra -2U/h term is the vorticity put into the fluid by the moving lid. At the four corners the vorticity is not defined (the velocity is discontinuous); the five-point stencil never uses it, and for plots we take the mean of the two neighbours.", size=10, lead=13.4)
    y -= 6
    y = h2(M, y, "Grid and cell Reynolds number (Task 3)")
    rows = [("N", "4", "8", "16", "32", "64", "128"), ("h (m)", "0.25", "0.125", "0.0625", "0.03125", "0.0156", "0.0078"),
            ("Re_h = U h / nu", "25", "12.5", "6.25", "3.125", "1.56", "0.78")]
    y = table(M, y + 4, [110, 52, 52, 52, 60, 52, 52], rows, size=9.2)
    y -= 22
    y = para(M, y, 400, "In Problem 5 central differences for the convection term needed a cell Peclet number below 2. With the lid speed U as velocity scale Re_h = 3.1 > 2 on the 32 x 32 grid: only N >= 50 would satisfy the limit. But the speed in most of the cavity is much smaller than U (|u| and |v| stay below about 0.25 below y = 0.85), so the local cell Reynolds number is below 2 in most cells, and the central scheme still gives a bounded solution here, as the results show. Near the lid, in the thin layer of fast flow, the limit is violated and a refined grid is needed.", size=10, lead=13.4)
    rx = M + 430
    ry = H - 75
    ry = h2(rx, ry, "Discretisation (Task 4), interior nodes (i, j)")
    ry = para(rx, ry, 330, "Stream function (five-point formula as in Problem 3), from the Poisson equation psi_xx + psi_yy = -omega:", size=10, lead=13.4)
    ry = eq_row(rx, ry - 2, r"$\psi_{i,j}=\dfrac{1}{4}\left(\psi_{i+1,j}+\psi_{i-1,j}+\psi_{i,j+1}+\psi_{i,j-1}+h^2\omega_{i,j}\right)$", 11.5, maxw=330)
    ry = para(rx, ry, 330, "Velocities by central differences:", size=10, lead=13.4)
    ry = eq_row(rx, ry - 2, r"$u_{i,j}=\dfrac{\psi_{i,j+1}-\psi_{i,j-1}}{2h},\qquad v_{i,j}=-\dfrac{\psi_{i+1,j}-\psi_{i-1,j}}{2h}$", 11.5, maxw=330)
    ry = para(rx, ry, 330, "Vorticity transport with central differences (as in Problem 5, now in 2D):", size=10, lead=13.4)
    ry = eq_row(rx, ry - 2, r"$a_P\,\omega_{i,j}=a_E\omega_{i+1,j}+a_W\omega_{i-1,j}+a_N\omega_{i,j+1}+a_S\omega_{i,j-1}$", 11.5, maxw=330)
    ry = eq_row(rx, ry, r"$a_E=\dfrac{\nu}{h^2}-\dfrac{u}{2h},\ a_W=\dfrac{\nu}{h^2}+\dfrac{u}{2h},\ a_N=\dfrac{\nu}{h^2}-\dfrac{v}{2h},\ a_S=\dfrac{\nu}{h^2}+\dfrac{v}{2h},\ a_P=\dfrac{4\nu}{h^2}$", 10.5, maxw=330)
    ry = para(rx, ry, 330, "The coefficient a_E (or a_N) turns negative when |u| h / nu > 2: the same condition as Pe < 2 in Problem 5.", size=10, lead=13.4)
    ry -= 6
    ry = h2(rx, ry, "Solution procedure (Task 5)")
    steps = ["Start from rest: psi = omega = 0 everywhere.",
             "Wall vorticity from Thom's formula with the current psi.",
             "Sweep the interior with the vorticity equation (Gauss-Seidel: new values are used at once; u, v from the current psi).",
             "Sweep the interior with the stream-function equation using the new omega.",
             "Repeat from 2 until the largest change of omega and psi in a sweep is below 1e-8."]
    for k_, t in enumerate(steps, 1):
        badge(rx + 9, ry - 5, k_)
        ry = para(rx + 24, ry - 8, 306, t, size=10, lead=13) - 3
    footer()
    c.showPage()


def hand_page1():
    header("Hand calculation, first iterations on the 4 x 4 grid", "Task 8")
    y = H - 74
    y = para(M, y, 300, "h = 0.25 m, 9 interior nodes (i, j), i = 1..3 (x), j = 1..3 (y). Start from rest: psi = omega = 0. Sweep order: row by row from the bottom (j = 1) to the top, from left to right within a row.", size=10, lead=13.4)
    y -= 2
    fig_at(os.path.join(OUT, "p6_grid4.png"), M, y, 235)
    rx = M + 320
    ry = H - 74
    ry = h2(rx, ry, "Iteration 1")
    pts = ["1. Wall vorticity. The lid has psi = 0 and the grid line below has psi = 0, so omega(i,4) = -2U/h = -8 for i = 1..3. The other walls: omega = -2 psi1/h^2 = 0 (psi1 = 0).",
           "2. Vorticity sweep. With u = v = 0 all coefficients equal nu/h^2, so each omega is the average of its four neighbours. Rows j = 1 and 2 only see zeros (the row above is still 0 when they are computed), so they stay 0. Row j = 3 (top):  omega(1,3) = (0 + 0 - 8 + 0)/4 = -2;  omega(2,3) = (omega(1,3) + 0 - 8 + 0)/4 = (-2 - 8)/4 = -2.5;  omega(3,3) = (-2.5 + 0 - 8 + 0)/4 = -2.625.",
           "3. Stream-function sweep, psi(i,j) = (sum of 4 neighbours + h^2 omega)/4 with h^2 = 0.0625.  Rows 1, 2: psi = 0. Row 3:  psi(1,3) = 0.0625(-2)/4 = -0.03125;  psi(2,3) = (-0.03125 + 0.0625(-2.5))/4 = -0.046875;  psi(3,3) = (-0.046875 + 0.0625(-2.625))/4 = -0.052734.",
           "Largest change: |omega| 2.625 and |psi| 0.0527. The fluid has started to move only in the top row of nodes."]
    for t in pts:
        ry = para(rx, ry, 370, t, size=9.8, lead=13) - 5
    y2 = min(ry, y - 235) - 6
    rows = [("j \\ i", "0", "1", "2", "3", "4")]
    w1 = np.array(NUM["hand_it1_w"]); p1 = np.array(NUM["hand_it1_psi"])
    for j in range(4, -1, -1):
        rows.append(("omega, j=%d" % j,) + tuple("%.4f" % (w1[i, j] + 0.0) for i in range(5)))
    yL = small_table(M, y2, [88, 62, 62, 62, 62, 62], rows, size=9, lead=15)
    rows = [("j \\ i", "0", "1", "2", "3", "4")]
    for j in range(4, -1, -1):
        rows.append(("psi, j=%d" % j,) + tuple("%.6f" % p1[i, j] for i in range(5)))
    small_table(M + 420, y2, [66, 50, 62, 66, 66, 50], rows, size=9, lead=15)
    c.setFont("UII", 8.8); c.setFillColorRGB(0.3, 0.3, 0.35)
    c.drawString(M, yL - 8, "Corner values of omega (columns 0 and 4 in rows 0 and 4) are the mean of the two neighbouring wall values; they are not used by the stencil.")
    footer()
    c.showPage()


def hand_page2():
    header("Hand calculation: second iteration and the converged 4 x 4 solution", "Task 8")
    y = H - 74
    w2 = np.array(NUM["hand_it2_w"]); p2 = np.array(NUM["hand_it2_psi"])
    y = para(M, y, W - 2 * M, "Iteration 2. Step 1 again: the side walls now have vorticity (omega(0,3) = -2 psi(1,3)/h^2 = -32 x (-0.03125) = 1.0; omega(4,3) = -32 x (-0.052734) = 1.6875) and the lid  omega(i,4) = -32 psi(i,3) - 8 = -7, -6.5, -6.3125. Step 2 now uses the velocities from psi, e.g. at (1,3): u = (psi(1,4) - psi(1,2))/(2h) = (0 - 0)/0.5 = 0 and v = -(psi(2,3) - psi(0,3))/(2h) = -(-0.046875 - 0)/0.5 = +0.09375 (upwards at the left, as in a clockwise vortex), so a_E = nu/h^2 - u/(2h) = 0.16, a_W = 0.16, a_N = nu/h^2 - v/(2h) = 0.16 - 0.1875 = -0.0275, a_S = 0.3475, a_P = 4 nu/h^2 = 0.64. The convection term is already comparable to the diffusion: a_N is negative, because the cell Reynolds number for v is 0.09375 x 0.25/0.01 = 2.3 > 2. The new omega and psi then follow from the same arithmetic as in iteration 1 (tables below).", size=9.8, lead=13)
    y -= 6
    rows = [("j \\ i", "0", "1", "2", "3", "4")]
    for j in range(4, -1, -1):
        rows.append(("omega, j=%d" % j,) + tuple("%.4f" % (w2[i, j] + 0.0) for i in range(5)))
    yL = small_table(M, y, [88, 62, 62, 62, 62, 62], rows, size=9, lead=15)
    rows = [("j \\ i", "0", "1", "2", "3", "4")]
    for j in range(4, -1, -1):
        rows.append(("psi, j=%d" % j,) + tuple("%.6f" % p2[i, j] for i in range(5)))
    small_table(M + 420, y, [66, 50, 62, 66, 66, 50], rows, size=9, lead=15)
    y = yL - 14
    y = h2(M, y, "After %d iterations (largest change < 1e-8) - converged 4 x 4 solution" % N4["it4"])
    psi4 = np.array(N4["psi4"]); w4 = np.array(N4["w4"])
    rows = [("j \\ i", "0", "1", "2", "3", "4")]
    for j in range(4, -1, -1):
        rows.append(("omega, j=%d" % j,) + tuple("%.3f" % (w4[i, j] + 0.0) for i in range(5)))
    yL = small_table(M, y, [88, 62, 62, 62, 62, 62], rows, size=9, lead=15)
    rows = [("j \\ i", "0", "1", "2", "3", "4")]
    for j in range(4, -1, -1):
        rows.append(("psi, j=%d" % j,) + tuple("%.5f" % psi4[i, j] for i in range(5)))
    small_table(M + 420, y, [66, 50, 62, 66, 66, 50], rows, size=9, lead=15)
    y = yL - 12
    y = para(M, y, W - 2 * M, "The 4 x 4 grid is much too coarse: psi_min at a node is %.4f (the exact vortex strength is about -0.1035) and the vortex centre is not resolved. But the hand calculation shows the mechanism of the 'spin-up': the lid injects vorticity into the top row, diffusion and convection carry it into the cavity, and psi follows through the Poisson equation. Later iterations on a fine grid overshoot (psi_min = -0.1027 after 200 iterations on the 32 x 32 grid, against -0.1004 in the end) and then relax to the steady state (page on the spin-up)." % psi4.min(), size=10, lead=13.4)
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
    header("Results: streamlines, vorticity and the primary vortex", "Task 6")
    y = H - 72
    y = fig_at(os.path.join(OUT, "p6_flow.png"), M + 40, y, 640) - 8
    g32 = G["32"]; g128 = G["128"]; cc = CR["32"]; c128 = CR["128"]
    rows = [("", "psi_min (strength)", "centre x", "centre y", "|psi_min - Ghia|"),
            ("Ghia et al. 1982 (129 x 129)", "-0.103423", "0.6172", "0.7344", ""),
            ("FDM 32 x 32", "%.5f" % g32["psi_min"], "%.4f" % g32["xc"], "%.4f" % g32["yc"], "%.5f" % abs(g32["psi_min"] - GHIA_PSI)),
            ("FDM 128 x 128", "%.5f" % g128["psi_min"], "%.4f" % g128["xc"], "%.4f" % g128["yc"], "%.5f" % abs(g128["psi_min"] - GHIA_PSI)),
            ("FDM Richardson (from 32, 64, 128)", "%.5f" % NUM["richardson"], "", "", "%.5f" % abs(NUM["richardson"] - GHIA_PSI)),
            ("COMSOL 32 x 32 (Laminar Flow)", "%.5f" % cc["psi_min"], "%.4f" % cc["xc"], "%.4f" % cc["yc"], "%.5f" % abs(cc["psi_min"] - GHIA_PSI)),
            ("COMSOL 128 x 128", "%.5f" % c128["psi_min"], "%.4f" % c128["xc"], "%.4f" % c128["yc"], "%.5f" % abs(c128["psi_min"] - GHIA_PSI))]
    y = small_table(M, y, [250, 120, 90, 90, 120], rows, size=9, lead=15)
    y -= 6
    y = para(M, y, 700, "The centre (position and value of the extremum of psi) is found by fitting a parabola through the 3 x 3 nodes around the smallest node value. The sign is negative because the vortex is clockwise with u = dpsi/dy. The FDM vortex strength is 2.9 % too weak on 32 x 32 and within 0.1 % of Ghia on 128 x 128. COMSOL's 32 x 32 value happens to agree with Ghia within 1e-5, but this is partly luck: its error changes sign between grids (-0.109 at 4 x 4, -0.1034 at 16 x 16, -0.1035 at 128 x 128).", size=9.8, lead=13)
    footer()
    c.showPage()


def centre_page():
    header("Centre-line velocities against the Ghia et al. benchmark", "Task 7")
    y = H - 72
    y = fig_at(os.path.join(OUT, "p6_centrelines.png"), M + 20, y, 700) - 6
    g = G; r = CR
    rows = [("grid", "FDM max |u - Ghia|", "FDM max |v - Ghia|", "COMSOL max |u - Ghia|", "COMSOL max |v - Ghia|")]
    for n in ("8", "16", "32", "64", "128"):
        rows.append((n + " x " + n, "%.4f" % g[n]["max_err_u"], "%.4f" % g[n]["max_err_v"], "%.4f" % r[n]["max_err_u"], "%.4f" % r[n]["max_err_v"]))
    y = small_table(M, y, [90, 140, 140, 150, 150], rows, size=9, lead=14.5)
    y -= 6
    y = para(M, y, 720, "Errors are measured at the 17 stations of the Ghia tables (next page) after cubic-spline interpolation of the grid values. They fall by a factor of about 4 from 8 x 8 to 32 x 32 (FDM) and then stop falling: on 64 x 64 and 128 x 128 they stay near 0.004 - 0.009, i.e. 0.4 - 0.9 % of the lid speed. FDM and COMSOL are two independent discretisations (finite differences and finite elements with a different formulation) and they level off at the same value; an FDM run on 256 x 256 gives 0.0049 and 0.0090. The remaining difference is therefore most likely the discretisation error of the 129 x 129 benchmark itself rather than an error of our solvers. We have not been able to confirm this against another published reference.", size=9.6, lead=12.6)
    footer()
    c.showPage()


def table_page():
    header("Centre-line values at the benchmark stations", "Task 7")
    y = H - 72
    rows = [("y", "Ghia u", "FDM 32", "COMSOL 32", "FDM 128", "COMSOL 128")]
    s128 = np.linspace(0, 1, 129)
    p128 = np.load(os.path.join(OUT, "p6_psi_128.npy")); u128, v128 = velocities(p128, 128)
    FU128 = CubicSpline(s128, u128[64])(GHIA_Y); FV128 = CubicSpline(s128, v128[:, 64])(GHIA_X)
    CU128 = CubicSpline(s128, FC["u128"][64])(GHIA_Y); CV128 = CubicSpline(s128, FC["v128"][:, 64])(GHIA_X)
    for k_ in range(17):
        rows.append(("%.4f" % GHIA_Y[k_], "%.5f" % GHIA_U[k_], "%.5f" % FDM_U[k_], "%.5f" % COM_U[k_], "%.5f" % FU128[k_], "%.5f" % CU128[k_]))
    y0 = y
    y = small_table(M, y, [46, 62, 62, 66, 62, 70], rows, size=8.3, lead=14.2)
    rows = [("x", "Ghia v", "FDM 32", "COMSOL 32", "FDM 128", "COMSOL 128")]
    for k_ in range(17):
        rows.append(("%.4f" % GHIA_X[k_], "%.5f" % GHIA_V[k_], "%.5f" % FDM_V[k_], "%.5f" % COM_V[k_], "%.5f" % FV128[k_], "%.5f" % CV128[k_]))
    small_table(M + 395, y0, [46, 62, 62, 66, 62, 70], rows, size=8.3, lead=14.2)
    c.setFont("UII", 8.8); c.setFillColorRGB(0.3, 0.3, 0.35)
    c.drawString(M, y - 6, "u along the vertical centre line x = 0.5 (left) and v along the horizontal centre line y = 0.5 (right). Ghia values as published for Re = 100; FDM and COMSOL values from cubic-spline interpolation of the grid values.")
    c.drawString(M, y - 18, "Note: the Ghia tables were typed from the published paper; the course notebook with the tables was not available, so a transcription error cannot be excluded entirely.")
    footer()
    c.showPage()


def grid_page():
    header("Grid study: order of convergence", "Task 7")
    y = H - 72
    rows = [("N", "h (m)", "Re_h", "iterations", "FDM psi_min", "order*", "COMSOL psi_min", "FDM self-error**", "ratio", "COMSOL self-error**", "ratio")]
    ef, ec = SELF["ef"], SELF["ec"]
    Ns = [4, 8, 16, 32, 64, 128]
    for k_, n in enumerate(Ns):
        o = "" if k_ < 2 else "%.2f" % NUM["orders"][k_ - 2]
        e1 = "%.4f" % ef[k_] if k_ < 5 else "-"
        e2 = "%.4f" % ec[k_] if k_ < 5 else "-"
        rf = "" if k_ in (0, 5) else "%.2f" % (ef[k_ - 1] / ef[k_])
        rc = "" if k_ in (0, 5) else "%.2f" % (ec[k_ - 1] / ec[k_])
        rows.append((str(n), "%.4f" % (1 / n), "%.2f" % (1 / n / 0.01), str(G[str(n)]["it"]), "%.5f" % G[str(n)]["psi_min"], o, "%.5f" % CR[str(n)]["psi_min"], e1, rf, e2, rc))
    y = small_table(M, y, [34, 52, 44, 66, 82, 46, 90, 90, 40, 104, 40], rows, size=8.6, lead=15)
    y -= 4
    y = para(M, y, 740, "* observed order from three successive psi_min values: log2((psi_h - psi_2h)/(psi_h/2 - psi_h)).   ** max over the nodes of the 4 x 4 ... 64 x 64 grids of |psi_h - psi_(h = 1/128)| at the common nodes.   A second-order method shows a ratio 4 per halving of h; first order shows 2.", size=8.8, lead=11.8, color=(0.3, 0.3, 0.35))
    y = fig_at(os.path.join(OUT, "p6_convergence.png"), M, y - 2, 560) - 6
    para(M + 570, y + 140, 190, "FDM: the order measured from psi_min is 2.00 (16 -> 32 -> 64) and 2.04 (32 -> 64 -> 128), so the scheme is second order for the vortex strength. The self-error ratios rise towards 4 (4.07, 4.38) on the finer grids. COMSOL's first-order stabilised P1 elements show ratios near 2.8 (an order of about 1.5), limited by the corner singularities. The coarse grids are not in the asymptotic range: Re_h > 2 there and the first-order Thom formula dominates.", size=9, lead=11.8)
    footer()
    c.showPage()


def eddy_page():
    header("Corner eddies and the spin-up from rest", "Task 6 and Task 5")
    y = H - 72
    y = fig_at(os.path.join(OUT, "p6_corners.png"), M + 20, y, 560) - 4
    eb, el = NUM["eddy_br"], NUM["eddy_bl"]
    para(M + 600, y + 150, 175, "Yes, there are small corner eddies (counter-clockwise, psi > 0) in both bottom corners, but they are tiny: on 128 x 128 the bottom-right one has psi_max = %.2e at (%.3f, %.3f) and the bottom-left one %.1e at (%.3f, %.3f), about 1e-4 and 2e-5 of the main vortex. Ghia et al. list about 1.25e-5 and 1.75e-6 (quoted from the published table). COMSOL on the same grid gives 1.25e-5 for the bottom right. They are invisible in ordinary contour plots, which is why levels such as 1e-5, 1e-6 are needed." % (eb[0], eb[1], eb[2], el[0], el[1], el[2]), size=9, lead=11.8)
    y = fig_at(os.path.join(OUT, "p6_spinup.png"), M + 20, y - 6, 560) - 4
    para(M + 600, y + 120, 175, "From rest the iteration reaches psi_min = -0.1027 after 200 sweeps (more than the steady -0.1004), then settles: the Gauss-Seidel iteration is a pseudo-time march, and it overshoots as the real flow does when started impulsively. 1299 sweeps are needed for a change below 1e-8. On the finer grids the count grows roughly 4-fold per halving of h (41, 184, 335, 1299, 4882, 17910 iterations).", size=9, lead=11.8)
    footer()
    c.showPage()


def answers_page():
    header("Answers to the tasks", "Summary")
    y = H - 78
    g32 = G["32"]
    items = [("Task 1, physics.", "psi with u = psi_y, v = -psi_x satisfies continuity identically; omega = v_x - u_y gives psi_xx + psi_yy = -omega; cross-differentiating the momentum equations eliminates the pressure and gives u omega_x + v omega_y = nu (omega_xx + omega_yy). The walls are impermeable, so psi is constant along them (psi = 0 on all four)."),
             ("Task 2, Thom's formula.", "omega_w = -2 (psi_(1) - psi_w)/h^2 on walls at rest and omega_w = -2 (psi_(N-1) - psi_w)/h^2 - 2U/h on the lid, from the Taylor series of psi with psi_yy = -omega."),
             ("Task 3, grid.", "N = 32, h = 0.03125 m; Re_h = U h / nu = 3.125 on the 32 x 32 grid, above the limit 2 of Problem 5 if the lid speed is used. In the core the speed is far smaller than U, so the central scheme works, but the thin layer under the lid is only marginally resolved."),
             ("Task 4, discretisation.", "Five-point formula psi_ij = (sum of four neighbours + h^2 omega_ij)/4; central-difference vorticity equation a_P omega_P = sum a_nb omega_nb with a_E = nu/h^2 - u/(2h) etc.; u = (psi_(j+1) - psi_(j-1))/(2h), v = -(psi_(i+1) - psi_(i-1))/(2h)."),
             ("Task 5, solution.", "Gauss-Seidel loop: wall vorticity, vorticity sweep, stream function sweep, until the largest change is below 1e-8: %d iterations on 32 x 32. COMSOL solves the primitive-variable equations with Newton's method in 2 s." % g32["it"]),
             ("Task 6, results.", "One large clockwise vortex with centre (%.3f, %.3f) and psi_min = %.4f on 32 x 32; %.4f on 128 x 128; Ghia -0.1034 at (0.617, 0.734). Small counter-clockwise corner eddies exist in the two bottom corners (psi about 1e-5 and 2e-6)." % (g32["xc"], g32["yc"], g32["psi_min"], G["128"]["psi_min"])),
             ("Task 7, verification.", "psi_min converges with second order (2.0). The centre-line velocities agree with Ghia to within 0.9 % of U on 32 x 32 (FDM) and 0.4 - 0.5 % (u), 0.8 - 0.9 % (v) on the finest grids (FDM and COMSOL); the difference does not shrink below this, for both FDM and COMSOL."),
             ("Task 8, hand calculation.", "4 x 4: omega = -8 on the lid; after sweep 1 the top row has omega = -2, -2.5, -2.625 and psi = -0.03125, -0.046875, -0.052734; the converged 4 x 4 solution needs 41 iterations."),
             ("COMSOL.", "Laminar Flow on a mapped 32 x 32 mesh with a sliding lid, a point pressure constraint and an added weak form PDE for psi reproduces the FDM solution (max |psi difference| 0.0046 on 32 x 32, 0.0007 on 128 x 128) and the benchmark.")]
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
    tips = [("The right-click menu does not appear at once.", "COMSOL is slow to react: left-click the node, right-click, and wait two or three seconds."),
            ("Next in the Model Wizard seems to do nothing.", "Wait a second and look again; a second click can skip a page. If you skipped Add Physics, use the back arrow."),
            ("A selection list stays empty.", "Hover over the edge or point until it turns red, click, and press the + button above the list."),
            ("Typing in a field added to the old text, or a long path left a field empty.", "Click in the field, press Ctrl+A, then Delete, and type again. Press Tab to confirm."),
            ("The solver complains about a singular matrix.", "The pressure constraint is missing: add the Pressure Point Constraint (Step 8)."),
            ("The lid moves to the left.", "Change U_w to -1. We checked that U_w = 1 gives u = +1 at the lid for this geometry."),
            ("I cannot find the stream function.", "It is not a built-in variable of Laminar Flow 4.3a: add the Weak Form PDE with psi (Steps 13 and 14), or integrate u from the bottom wall."),
            ("The speed in the plot exceeds 1 m/s near the top corners.", "That is the corner singularity (the lid velocity jumps to 0 in one element). It is also present in the FDM vorticity."),
            ("The vorticity colour bar is dominated by two huge values.", "Set a manual colour range (-12 ... 6). The corner values are singular and grow when the mesh is refined."),
            ("Save your work.", "File > Save As, choose a folder you can write to. Compare with the supplied file lid_cavity_comsol.mph.")]
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
disc_page()
hand_page1()
hand_page2()
for i, st in enumerate(STEPS, 1):
    step_pages(i, st)
results_page()
centre_page()
table_page()
grid_page()
eddy_page()
answers_page()
tips_page()
c.save()
print("saved pages", page_no[0])
