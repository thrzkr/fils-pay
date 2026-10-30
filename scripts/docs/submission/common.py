"""Shared styles and helpers for the FilsPay submission PDFs."""
import os, subprocess
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph, Spacer, Table, TableStyle, Preformatted, Image, KeepTogether
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import registerFontFamily

F = "/usr/share/fonts/truetype/dejavu/"
pdfmetrics.registerFont(TTFont("Sans", F + "DejaVuSans.ttf"))
pdfmetrics.registerFont(TTFont("Sans-Bold", F + "DejaVuSans-Bold.ttf"))
pdfmetrics.registerFont(TTFont("Mono", F + "DejaVuSansMono.ttf"))
registerFontFamily("Sans", normal="Sans", bold="Sans-Bold", italic="Sans", boldItalic="Sans-Bold")

# ---- Team details: edit these, then rebuild --------------------------------
TEAM = os.environ.get("FP_TEAM", "TeamName")
MEMBERS = [  # (name, what they owned)
    ("Member 1", "Owner: ..."),
    ("Member 2", "Owner: ..."),
    ("Member 3", "Owner: ..."),
]
FORK = "https://github.com/thrzkr/fils-pay"
URLS = [
    ("Checkout", "https://fp-pay-tzakir.dilmune.app/pay/&lt;token&gt;"),
    ("Merchant dashboard", "https://fp-pay-tzakir.dilmune.app/dashboard/login"),
    ("Admin console", "https://fp-admin-tzakir.dilmune.app/login"),
    ("Public API", "https://fp-api-tzakir.dilmune.app  (health: /healthz, /readyz; API: /v1)"),
]
REPO = "/home/user/fils-pay"
COMMIT = os.environ.get("FP_COMMIT") or subprocess.check_output(["git", "-C", REPO, "rev-parse", "HEAD"]).decode().strip()
SHOTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "shots")

INK = colors.HexColor("#1b2430"); MUTED = colors.HexColor("#5b6675"); ACCENT = colors.HexColor("#0f6e6e")
ACCENT_LIGHT = colors.HexColor("#e6f2f2"); RULE = colors.HexColor("#d5dbe1"); CODE_BG = colors.HexColor("#f4f6f8")
RED = colors.HexColor("#b3261e"); AMBER = colors.HexColor("#9a6700"); GREEN = colors.HexColor("#1a7f37")

base = dict(fontName="Sans", textColor=INK)
S = {
    "body": ParagraphStyle("body", fontSize=9.3, leading=13.2, spaceAfter=5, **base),
    "small": ParagraphStyle("small", fontSize=8, leading=11, **base),
    "muted": ParagraphStyle("muted", fontSize=8, leading=11, fontName="Sans", textColor=MUTED, spaceAfter=6),
    "cell": ParagraphStyle("cell", fontSize=7.9, leading=10.6, **base),
    "cellb": ParagraphStyle("cellb", fontSize=7.9, leading=10.6, fontName="Sans-Bold", textColor=colors.white),
    "h1": ParagraphStyle("h1", fontName="Sans-Bold", fontSize=17, leading=22, textColor=ACCENT, spaceBefore=2, spaceAfter=8, keepWithNext=1),
    "h2": ParagraphStyle("h2", fontName="Sans-Bold", fontSize=12, leading=16, textColor=INK, spaceBefore=10, spaceAfter=4, keepWithNext=1),
    "h3": ParagraphStyle("h3", fontName="Sans-Bold", fontSize=9.8, leading=13, textColor=ACCENT, spaceBefore=7, spaceAfter=2, keepWithNext=1),
    "bullet": ParagraphStyle("bullet", fontSize=9.3, leading=12.8, leftIndent=13, bulletIndent=3, spaceAfter=2.5, **base),
    "code": ParagraphStyle("code", fontName="Mono", fontSize=7.4, leading=9.8, textColor=INK, backColor=CODE_BG,
                           borderPadding=(4, 5, 4, 5), leftIndent=5, rightIndent=5, spaceBefore=3, spaceAfter=8),
    "note": ParagraphStyle("note", fontSize=8.8, leading=12.5, backColor=ACCENT_LIGHT, borderPadding=(5, 7, 5, 7),
                           leftIndent=7, rightIndent=7, spaceBefore=4, spaceAfter=9, **base),
    "warn": ParagraphStyle("warn", fontSize=8.8, leading=12.5, backColor=colors.HexColor("#fdf3e1"), borderPadding=(5, 7, 5, 7),
                           leftIndent=7, rightIndent=7, spaceBefore=4, spaceAfter=9, **base),
    "quote": ParagraphStyle("quote", fontSize=8.6, leading=12, leftIndent=10, borderPadding=(0, 0, 0, 6),
                            textColor=colors.HexColor("#33404f"), fontName="Sans", spaceAfter=5),
}


def c(t):
    return f'<font name="Mono" size="8">{t}</font>'


class Story(list):
    def P(self, t, s="body"): self.append(Paragraph(t, S[s]))
    def H1(self, t):
        p = Paragraph(t, S["h1"]); p.toc_level = 0; self.append(p)
    def H2(self, t):
        p = Paragraph(t, S["h2"]); p.toc_level = 1; self.append(p)
    def H3(self, t): self.append(Paragraph(t, S["h3"]))
    def B(self, items):
        for i in items: self.append(Paragraph(i, S["bullet"], bulletText="•"))
        self.append(Spacer(1, 2))
    def N(self, items):
        for n, i in enumerate(items, 1): self.append(Paragraph(i, S["bullet"], bulletText=f"{n}."))
        self.append(Spacer(1, 2))
    def CODE(self, t): self.append(Preformatted(t.strip("\n"), S["code"]))
    def NOTE(self, t): self.append(Paragraph(t, S["note"]))
    def WARN(self, t): self.append(Paragraph(t, S["warn"]))
    def Q(self, t): self.append(Paragraph(t, S["quote"]))

    def TABLE(self, rows, widths, head=True, status_col=None, font=None):
        data = []
        for r_i, r in enumerate(rows):
            row = []
            for c_i, v in enumerate(r):
                if not isinstance(v, str):
                    row.append(v); continue
                st = S["cellb"] if (head and r_i == 0) else S["cell"]
                if status_col is not None and c_i == status_col and r_i > 0:
                    col = {"Fixed": GREEN, "Mitigated": AMBER, "Open": RED, "Found": RED}.get(v.split(" ")[0], INK)
                    v = f'<font color="{col.hexval()}"><b>{v}</b></font>'
                row.append(Paragraph(v, st))
            data.append(row)
        t = Table(data, colWidths=[w * mm for w in widths], repeatRows=1 if head else 0)
        ts = [("VALIGN", (0, 0), (-1, -1), "TOP"), ("LINEBELOW", (0, 0), (-1, -1), 0.4, RULE),
              ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
              ("LEFTPADDING", (0, 0), (-1, -1), 4), ("RIGHTPADDING", (0, 0), (-1, -1), 4)]
        if head:
            ts.append(("BACKGROUND", (0, 0), (-1, 0), ACCENT))
            for i in range(2, len(data), 2): ts.append(("BACKGROUND", (0, i), (-1, i), colors.HexColor("#f7f9fa")))
        t.setStyle(TableStyle(ts))
        self.append(t); self.append(Spacer(1, 7))

    def KV(self, rows, widths=(38, 136)):
        self.TABLE([[f"<b>{k}</b>", v] for k, v in rows], list(widths), head=False)


def shot(name, width_mm, crop=None):
    """Screenshot as an Image flowable, optionally cropped (x0, y0, x1, y1 in px)."""
    from PIL import Image as PImage
    src = os.path.join(SHOTS, name + ".png")
    out = os.path.join(SHOTS, f"c-{name}-{'x'.join(map(str, crop)) if crop else 'full'}.png")
    if not os.path.exists(out):
        im = PImage.open(src).convert("RGB")
        if crop: im = im.crop(crop)
        im.save(out)
    from PIL import Image as PImage2
    w, h = PImage2.open(out).size
    img = Image(out, width=width_mm * mm, height=width_mm * mm * h / w)
    return img


def framed(flow, caption):
    t = Table([[flow], [Paragraph(caption, S["muted"])]])
    t.setStyle(TableStyle([("BOX", (0, 0), (0, 0), 0.5, RULE), ("LEFTPADDING", (0, 0), (-1, -1), 0),
                           ("RIGHTPADDING", (0, 0), (-1, -1), 0), ("TOPPADDING", (0, 0), (-1, -1), 2),
                           ("BOTTOMPADDING", (0, 0), (-1, -1), 1)]))
    return t


def pair(story, left, right, lcap, rcap, w=84):
    t = Table([[framed(left, lcap), framed(right, rcap)]], colWidths=[(w + 3) * mm, (w + 3) * mm])
    t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 0)]))
    story.append(KeepTogether([t, Spacer(1, 8)]))
