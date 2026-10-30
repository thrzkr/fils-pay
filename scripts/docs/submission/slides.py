import sys
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, PageBreak, Table, TableStyle, Preformatted
from reportlab.lib.styles import ParagraphStyle
from common import *

PW, PH = 338.67 * mm, 190.5 * mm
M = 16 * mm
CW = (PW - 2 * M) / mm  # content width in mm

T = {
    "kicker": ParagraphStyle("k", fontName="Sans-Bold", fontSize=10, leading=13, textColor=ACCENT),
    "title": ParagraphStyle("t", fontName="Sans-Bold", fontSize=24, leading=29, textColor=INK, spaceAfter=10),
    "big": ParagraphStyle("b", fontName="Sans-Bold", fontSize=19, leading=26, textColor=INK, spaceAfter=10),
    "body": ParagraphStyle("bo", fontName="Sans", fontSize=12.5, leading=17.5, textColor=INK, spaceAfter=6),
    "small": ParagraphStyle("s", fontName="Sans", fontSize=10, leading=13.5, textColor=INK, spaceAfter=4),
    "muted": ParagraphStyle("m", fontName="Sans", fontSize=9, leading=12, textColor=MUTED),
    "cell": ParagraphStyle("c", fontName="Sans", fontSize=10, leading=13.2, textColor=INK),
    "cellb": ParagraphStyle("cb", fontName="Sans-Bold", fontSize=10, leading=13.2, textColor=colors.white),
    "num": ParagraphStyle("n", fontName="Sans-Bold", fontSize=26, leading=30, textColor=ACCENT),
    "code": ParagraphStyle("code", fontName="Mono", fontSize=8.6, leading=11.4, textColor=INK, backColor=CODE_BG,
                           borderPadding=(5, 6, 5, 6), leftIndent=6, rightIndent=6, spaceBefore=3, spaceAfter=8),
}
cc = lambda t: f'<font name="Mono">{t}</font>'
st = []
def P(t, s="body"): st.append(Paragraph(t, T[s]))
def head(k, t): P(k, "kicker"); P(t, "title")
def tbl(rows, widths, head=True, fs=None):
    data = [[Paragraph(v, T["cellb"] if head and i == 0 else T["cell"]) if isinstance(v, str) else v for v in r] for i, r in enumerate(rows)]
    t = Table(data, colWidths=[w * mm for w in widths], repeatRows=1 if head else 0)
    ts = [("VALIGN", (0, 0), (-1, -1), "TOP"), ("LINEBELOW", (0, 0), (-1, -1), 0.4, RULE),
          ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4)]
    if head: ts.append(("BACKGROUND", (0, 0), (-1, 0), ACCENT))
    t.setStyle(TableStyle(ts)); st.append(t); st.append(Spacer(1, 6))
def grid(cells, widths):
    t = Table([cells], colWidths=[w * mm for w in widths])
    t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 8)]))
    st.append(t)
def cap_img(name, w, crop, caption):
    t = Table([[shot(name, w, crop)], [Paragraph(caption, T["muted"])]])
    t.setStyle(TableStyle([("BOX", (0, 0), (0, 0), 0.5, RULE), ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0)]))
    return t
def nb(): st.append(PageBreak())

# 1 Team
st.append(Spacer(1, 30 * mm))
P("FilsPay", "kicker")
P(f'<font size="40">{TEAM}</font>', "title"); st.append(Spacer(1, 12))
tbl([["Member", "Owned"]] + [[n, o] for n, o in MEMBERS], [90, 180])
P("Live: fp-pay-tzakir.dilmune.app · fp-admin-tzakir.dilmune.app · fp-api-tzakir.dilmune.app &nbsp;&nbsp; Code: " + FORK.replace("https://", ""), "muted")
nb()

# 2 Root cause
head("2 · Root cause", "We trusted generated code, comments and tests instead of the ledger.")
P("Tests were written to assert the bugs and \"Claude says\" comments closed questions without a check. So four patterns repeated everywhere:", "body")
tbl([["Pattern", "Symptoms it explains"],
     ["<b>Check-then-act, no lock</b>", "Refunds could pay out twice · duplicate payout webhooks · payment links double-charge · sweep posts twice"],
     ["<b>Two sources of truth</b>", "Dashboard 245 bps vs billing 225 · rebuild button ≠ CLI · webhook signed ≠ sent · <b>payout ≠ ledger after refunds</b>"],
     ["<b>Money not integer fils end to end</b>", "CSV adjustments 10x too small · float32 payouts · int32 volume counter wraps at 2.1M BD"],
     ["<b>Auth / tenancy checked in some places only</b>", "OTP optional · login lands in another merchant · refund another merchant's payment · impersonation can move money"]],
    [90, CW - 90])
nb()

# 3 Key findings
head("3 · Key findings, ranked by impact", "Top four")
rows = [["#", "Finding", "Evidence", "Status"],
        ["1", "<b>The login code was optional.</b> The password-step cookie already worked on every merchant endpoint.", "Pending cookie → merchant API returned data; test now gets 401.", "Fixed"],
        ["2", "<b>One merchant's password opened another merchant.</b> Session created for any user with that email.", "Shared-email login test (owner@alpharetail is in 2 merchants).", "Fixed"],
        ["3", "<b>Payouts ignore refunds.</b> Merchant paid for money already returned to cardholders.", "Demo day: batch paid 31.769 BD; ledger payable −17.107 BD; reconciliation gap ≠ 0.", "Open (finance)"],
        ["4", "<b>Finance CSV adjustments 10x too small.</b> 4.75 BD posted as 475 fils; tests expected it.", "Import test fails on old parser, passes on parseBhdToFils.", "Fixed"]]
tbl([[r[0], r[1], r[2], (f'<font color="{(GREEN if r[3]=="Fixed" else RED).hexval()}"><b>{r[3]}</b></font>' if i else r[3])] for i, r in enumerate(rows)], [10, 120, 130, CW - 260])
P("Also fixed: concurrent refunds double-paying, duplicate payout webhooks (incident 08-21), webhook signatures, API key rotation, int32/float32 money, and a dashboard crash after every refund (found this week).", "small")
nb()

# 4 Fixes and proof
head("4 · Fixes and proof", "Every fix has a test that fails on the old code, or a query / live request")
tbl([["Fix", "Proof"],
     ["Sessions require authenticated = true; session tied to the checked (merchant, email)", cc("app.test.ts") + ": pending cookie 401; cross-merchant login rejected"],
     ["Refunds: FOR UPDATE + pending reservation (0073), captured − refunded − pending, fee reversal", cc("refunds.test.ts") + " parallel refunds; demo fee reversals 281 + 112 fils"],
     ["One settlement.paid per batch (0076, ON CONFLICT)", cc("payout_notify_test.go") + ": 8 concurrent enqueuers → 1 event"],
     ["Fee display uses billing's effective_from rule", "Old code restored: 58 pass / 5 fail → fixed: 377 / 0"],
     ["BIGINT/int64 running totals (0078); integer Go payouts; largest-remainder splits", "Go tests above 2^31 and 2^24"],
     ["Webhooks sign the bytes they send; callbacks deduped (0074); link reservation (0075)", "Load test: 0 double payments at 150 buyers"],
     ["Dashboard bhd() accepts signed amounts (refund events)", "bhd(−5000): 8 pass / 1 fail before, 9/9 after"],
     ["API site → reverse proxy; HTTPS; systemd; setup.sh fails loudly", "Secret files 404; /healthz /readyz 200; ports 3000/8091 closed"]],
    [150, CW - 150])
st.append(Preformatted("Fresh Postgres 16, 30 Oct:  72 migrations apply · npm test 453/453 · go test ./... all packages ok", T["code"]))
nb()

# 5 Live demo
head("5 · Live demo: full and partial refund", "12.500 BD refunded in full · 20.000 BD refunded 5.000")
grid([cap_img("after-drawer-partial", 100, (0, 0, 1280, 700), "Refund drawer: 5000 fils, refundable 20.000"),
      cap_img("fixed-partial", 100, (0, 0, 1280, 700), "partially_refunded · timeline −5.000 BHD"),
      cap_img("fixed-full", 100, (0, 0, 1280, 700), "refunded · timeline −12.500 BHD")], [104, 104, 104])
st.append(Spacer(1, 4))
P("Fee reversed: 281 + 112 fils (2.25%, half-to-even). Settlement batch for the day: gross 32.500, fee 0.731, <b>net 31.769</b>: the refunds are in the ledger but not netted from the payout (finding 3, open).", "small")
nb()

head("5 · Live demo: settlement report", "Backup screenshots if the live demo fails")
grid([cap_img("settlement-batch", 150, (0, 0, 1280, 640), "Settlement batch 2026-10-30: both transactions, refunded / partially_refunded"),
      cap_img("reconciliation", 150, (0, 0, 1280, 560), "Reconciliation: gap ≠ 0 shows payouts don't net refunds")], [156, 156])
nb()

# 6 Under load
head("6 · Under load", "Estimate ~8 checkouts/s, ~10 concurrent buyers at p95 < 2 s; measured")
tbl([["Buyers", "Checkouts/s", "p95", "Shed (503)", "Double payments"],
     ["10", "8.2", "1.65 s", "0", "0"], ["20", "8.1", "3.15 s", "0", "0"], ["40", "7.9", "5.71 s", "0", "0"],
     ["150 (shed at 10)", "7.6", "1.89 s", "4,111", "0"]], [60, 45, 40, 45, 50])
grid([Paragraph("<b>Architecture.</b> Cloudflare → nginx 443 → static fp-pay / fp-admin, API on 127.0.0.1:3000 (systemd, 0.5 vCPU / 512 MB), Go settlement (127.0.0.1:8091), reporting worker, Postgres 16. Redeploy: " + cc("bash ops/dilmune/setup.sh") + ".", T["small"]),
      Paragraph("<b>Bottleneck:</b> the API's 0.5 vCPU (throughput flat, memory ~100 MB). <b>Overload:</b> over 10 in-flight → 503 + Retry-After; retries are safe with the same Idempotency-Key; systemd restarts in ~2 s. We tried 40 first: p95 hit 5.7 s, so we cut it to 10.", T["small"])], [150, 156])
nb()

# 7 AI
head("7 · How we used AI", "Claude Code + CLAUDE.md rules + permission rules + /verify-fix, /check-live, /money-review")
P("<b>Rule:</b> the AI proposes; only a failing-then-passing test, a query or a live request closes an item.", "body")
P("<b>When it was wrong:</b> we asked it to rotate the leaked admin password. It reported success and blamed the seed script when the login still failed. "
  "We asked for state, not output: a read-only query showed the password unchanged (" + cc("|f") + "), and the console history showed the reset had never run. "
  "It disproved its own seed theory (one admin row, no cron/timer/pm2). We only accepted " + cc("UPDATE 1 … |t") + ".", "body")
P("<b>And this week:</b> its own report said refunds worked \"end to end\". Driving the real dashboard with Playwright showed the page crashed after every refund, and that payouts ignore refunds.", "body")
nb()

# 8 Decisions
head("8 · Decisions and open risks", "What we chose not to change, and why")
tbl([["Decision / risk", "Why", "Safeguard"],
     ["Payouts don't net refunds (not changed)", "Finance owns net vs clawback vs hold; payout change on deadline day is riskier", "Hold payouts where ledger payable &lt; 0; alert on reconciliation gap ≠ 0"],
     ["No backfills (CSV 10x, rotated keys, MDR rewrites)", "Needs finance sign-off per file / merchant", "Queries per finding, dry-run first"],
     ["Secrets still in git history", "History rewrite = force push, owner's call", "Rotate admin, acquirer sandbox and DB passwords now"],
     ["Postgres 5432 open", "Dilmun dashboard change", "Delete firewall rule #4; drop 0.0.0.0/0"],
     ["Login code shown on screen (demo)", "No email/SMS sender yet", "Simulated money only; remove OTP_DEV_EXPOSE before real use"]],
    [85, 110, CW - 195])
P("Still open: scheme residue posting (ADR-0002) · reaper for stuck pending refunds · OTP rate limits · Dilmun auto-deploy.", "small")
nb()

# Appendix
head("Appendix", "Evidence")
st.append(Preformatted("""$ npm test            (fresh Postgres 16)
# pass 4 · 40 · 385 · 11 · 8 · 5  = 453, fail 0
$ go test ./...       ok config internalapi ledger money scheduler settlement splits

transaction | amount | captured | status             | refund | fee_reversed
2e31fe2f... |  12500 |    12500 | refunded           |  12500 |          281
608feb20... |  20000 |    20000 | partially_refunded |   5000 |          112
$ settlement run-batch --date=2026-10-30   gross=32500 fee=731 netPayout=31769
ledger merchant_payable: credits 32893, debits 50000 -> -17107""", T["code"]))
P("Full findings (26), root causes, decisions and screenshots: " + TEAM + "_FilsPay_Submission.pdf · " + cc("bugs.md") + " · " + cc("docs/AUDIT-FP-300.md") + ".", "small")

def bg(canv, doc):
    canv.saveState()
    canv.setFillColor(ACCENT); canv.rect(0, PH - 4 * mm, PW, 4 * mm, stroke=0, fill=1)
    canv.setFont("Sans", 8); canv.setFillColor(MUTED)
    canv.drawString(M, 7 * mm, f"{TEAM} · FilsPay"); canv.drawRightString(PW - M, 7 * mm, str(doc.page))
    canv.restoreState()

out = sys.argv[1]
doc = BaseDocTemplate(out, pagesize=(PW, PH), leftMargin=M, rightMargin=M, topMargin=13 * mm, bottomMargin=13 * mm, title=f"{TEAM} FilsPay Slides", author=TEAM)
doc.addPageTemplates([PageTemplate("s", [Frame(M, 13 * mm, PW - 2 * M, PH - 26 * mm, id="f")], onPage=bg)])
doc.build(st)
print("ok", out)
