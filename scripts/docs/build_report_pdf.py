from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer,
                                Table, TableStyle, PageBreak, Preformatted, KeepTogether, NextPageTemplate)
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import sys

F = "/usr/share/fonts/truetype/dejavu/"
pdfmetrics.registerFont(TTFont("Sans", F + "DejaVuSans.ttf"))
pdfmetrics.registerFont(TTFont("Sans-Bold", F + "DejaVuSans-Bold.ttf"))
pdfmetrics.registerFont(TTFont("Sans-Oblique", F + "DejaVuSans.ttf"))
pdfmetrics.registerFont(TTFont("Mono", F + "DejaVuSansMono.ttf"))
from reportlab.pdfbase.pdfmetrics import registerFontFamily
registerFontFamily("Sans", normal="Sans", bold="Sans-Bold", italic="Sans-Oblique", boldItalic="Sans-Bold")

INK = colors.HexColor("#1b2430")
MUTED = colors.HexColor("#5b6675")
ACCENT = colors.HexColor("#0f6e6e")
ACCENT_LIGHT = colors.HexColor("#e6f2f2")
RULE = colors.HexColor("#d5dbe1")
CODE_BG = colors.HexColor("#f4f6f8")
RED = colors.HexColor("#b3261e")
AMBER = colors.HexColor("#9a6700")
GREEN = colors.HexColor("#1a7f37")

base = dict(fontName="Sans", textColor=INK)
S = {
    "body": ParagraphStyle("body", fontSize=9.6, leading=14, spaceAfter=6, **base),
    "small": ParagraphStyle("small", fontSize=8.2, leading=11.5, **base),
    "cell": ParagraphStyle("cell", fontSize=8.2, leading=11, **base),
    "cellb": ParagraphStyle("cellb", fontSize=8.2, leading=11, fontName="Sans-Bold", textColor=colors.white),
    "h1": ParagraphStyle("h1", fontName="Sans-Bold", fontSize=18, leading=23, textColor=ACCENT, spaceBefore=4, spaceAfter=10),
    "h2": ParagraphStyle("h2", fontName="Sans-Bold", fontSize=12.5, leading=17, textColor=INK, spaceBefore=12, spaceAfter=5, keepWithNext=1),
    "h3": ParagraphStyle("h3", fontName="Sans-Bold", fontSize=10.2, leading=14, textColor=ACCENT, spaceBefore=8, spaceAfter=3, keepWithNext=1),
    "bullet": ParagraphStyle("bullet", fontSize=9.6, leading=13.5, leftIndent=14, bulletIndent=3, spaceAfter=3, **base),
    "code": ParagraphStyle("code", fontName="Mono", fontSize=7.8, leading=10.4, textColor=INK, backColor=CODE_BG,
                           borderPadding=(5, 6, 5, 6), leftIndent=6, rightIndent=6, spaceBefore=4, spaceAfter=9),
    "note": ParagraphStyle("note", fontSize=9, leading=13, backColor=ACCENT_LIGHT, borderPadding=(6, 8, 6, 8),
                           leftIndent=8, rightIndent=8, spaceBefore=4, spaceAfter=10, **base),
    "warn": ParagraphStyle("warn", fontSize=9, leading=13, backColor=colors.HexColor("#fdf3e1"), borderPadding=(6, 8, 6, 8),
                           leftIndent=8, rightIndent=8, spaceBefore=4, spaceAfter=10, **base),
}

story = []
def P(t, s="body"): story.append(Paragraph(t, S[s]))
def H1(t):
    p = Paragraph(t, S["h1"]); p.toc_level = 0; story.append(p)
def H2(t):
    p = Paragraph(t, S["h2"]); p.toc_level = 1; story.append(p)
def H3(t): story.append(Paragraph(t, S["h3"]))
def B(items):
    for i in items: story.append(Paragraph(i, S["bullet"], bulletText="•"))
    story.append(Spacer(1, 3))
def N(items):
    for n, i in enumerate(items, 1): story.append(Paragraph(i, S["bullet"], bulletText=f"{n}."))
    story.append(Spacer(1, 3))
def CODE(t): story.append(Preformatted(t.strip("\n"), S["code"]))
def NOTE(t): story.append(Paragraph(t, S["note"]))
def WARN(t): story.append(Paragraph(t, S["warn"]))
def c(t): return f'<font name="Mono" size="8.4">{t}</font>'

def TABLE(rows, widths, head=True, status_col=None):
    data = []
    for r_i, r in enumerate(rows):
        row = []
        for c_i, v in enumerate(r):
            st = S["cellb"] if (head and r_i == 0) else S["cell"]
            if status_col is not None and c_i == status_col and r_i > 0:
                col = {"Fixed": GREEN, "Mitigated": AMBER, "Open": RED}.get(v.split(" ")[0], INK)
                v = f'<font color="{col.hexval()}"><b>{v}</b></font>'
            row.append(Paragraph(v, st))
        data.append(row)
    t = Table(data, colWidths=[w * mm for w in widths], repeatRows=1 if head else 0)
    ts = [("VALIGN", (0, 0), (-1, -1), "TOP"),
          ("LINEBELOW", (0, 0), (-1, -1), 0.4, RULE),
          ("TOPPADDING", (0, 0), (-1, -1), 3.5), ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5),
          ("LEFTPADDING", (0, 0), (-1, -1), 4), ("RIGHTPADDING", (0, 0), (-1, -1), 4)]
    if head:
        ts += [("BACKGROUND", (0, 0), (-1, 0), ACCENT)]
        for i in range(2, len(data), 2): ts.append(("BACKGROUND", (0, i), (-1, i), colors.HexColor("#f7f9fa")))
    t.setStyle(TableStyle(ts))
    story.append(t); story.append(Spacer(1, 8))

# ---------------- Cover ----------------
def cover_page(canv, doc):
    canv.saveState()
    w, h = A4
    canv.setFillColor(ACCENT); canv.rect(0, h - 95 * mm, w, 95 * mm, stroke=0, fill=1)
    canv.setFillColor(colors.white)
    canv.setFont("Sans-Bold", 32); canv.drawString(20 * mm, h - 45 * mm, "FilsPay")
    canv.setFont("Sans", 15); canv.drawString(20 * mm, h - 57 * mm, "Fixes, features and field guide")
    canv.setFont("Sans", 10.5)
    canv.drawString(20 * mm, h - 70 * mm, "Everything changed during the FP-300 audit and the Dilmun Cloud deployment,")
    canv.drawString(20 * mm, h - 76 * mm, "how to use the platform, and how to set it all up (including Claude Code).")
    canv.setFillColor(MUTED); canv.setFont("Sans", 9)
    canv.drawString(20 * mm, 22 * mm, "Repository: thrzkr/fils-pay  ·  Branch: claude/dazzling-gates-5vyg5n  ·  Compiled 30 October 2026")
    canv.drawString(20 * mm, 16 * mm, "Sources: git history, bugs.md, docs/AUDIT-FP-300.md, docs/CAPACITY.md, docs/DEPLOY.md, docs/AI-USAGE.md")
    canv.restoreState()

def body_page(canv, doc):
    canv.saveState()
    w, h = A4
    canv.setStrokeColor(RULE); canv.setLineWidth(0.5)
    canv.line(18 * mm, h - 14 * mm, w - 18 * mm, h - 14 * mm)
    canv.setFont("Sans", 7.8); canv.setFillColor(MUTED)
    canv.drawString(18 * mm, h - 12 * mm, "FilsPay — fixes, features and field guide")
    canv.drawRightString(w - 18 * mm, 10 * mm, f"Page {doc.page}")
    canv.restoreState()

story.append(Spacer(1, 105 * mm))
# At-a-glance box on cover
glance = [
    ["What", "Result"],
    ["Code defects fixed (FP-300 audit, two rounds)", "30+ across money, refunds, security, webhooks, settlement and reports"],
    ["Deployment / ops bugs logged", "24 — 19 fixed, 2 mitigated, 3 open (one is a platform bug)"],
    ["New features", "Refunds end to end, safe payment links, load shedding, streaming export, setup script, load test, root & 404 pages"],
    ["Tests", "TypeScript suite 453 / 453 on real Postgres; Go settlement tests pass"],
    ["Live demo", "fp-pay-tzakir.dilmune.app · fp-admin-tzakir.dilmune.app · fp-api-tzakir.dilmune.app (HTTPS)"],
]
TABLE(glance, [62, 112])
story.append(NextPageTemplate("body"))
story.append(PageBreak())

# ---------------- TOC ----------------
toc = TableOfContents()
toc.levelStyles = [
    ParagraphStyle("t0", fontName="Sans-Bold", fontSize=9.6, leading=13.5, leftIndent=0, textColor=INK),
    ParagraphStyle("t1", fontName="Sans", fontSize=8.4, leading=11, leftIndent=12, textColor=MUTED),
]
story.append(Paragraph("Contents", S["h1"]))
story.append(toc)
story.append(PageBreak())

# ---------------- 1. Introduction ----------------
H1("1. Introduction")
P("<b>FilsPay</b> is a payment platform for merchants in Bahrain. A merchant signs up, passes KYC, and can then take card "
  "payments through an API or through hosted <i>payment links</i> that buyers open in a browser. FilsPay authorizes and "
  "captures those payments with an acquirer (simulated in this project), keeps a double-entry ledger, settles money to the "
  "merchant every business day, sends signed webhooks, and gives finance and support an internal admin console.")
P("The project arrived with a lot of hidden damage. Earlier contributors had followed an \"Order of the Prompt\" rule set that "
  "told AI assistants to trust generated code, never question tests, and treat odd behaviour as intentional. The result: "
  "money parsed ten times too small, refunds that returned 501, a second login factor that could be skipped, webhooks "
  "signed over different bytes than were sent, and tests written to assert the bugs.")
P("This document covers the work done to fix that, in three rounds:")
B(["<b>Round 1 — FP-300 audit.</b> Implemented refunds, made payment links safe, and fixed money, concurrency and security defects "
   "across the API and the Go settlement service.",
   "<b>Round 2 — open items closed.</b> OTP bypass, cross-merchant login, API key rotation, duplicate payout webhooks, fee display, "
   "overflowing counters, the March sweep script and large exports. Every fix has a test that fails on the old code.",
   "<b>Round 3 — run it for real.</b> Local Docker stack, Dilmun Cloud deployment with HTTPS, systemd services, load shedding, "
   "capacity measurement, and a 24-item bug log for everything that broke along the way."])
P("Read it in order the first time. After that, section 7 (real-life use) and section 8 (setup) are the parts you will come back to.")

H2("1.1 How the system fits together")
TABLE([
    ["Part", "Tech", "Job"],
    [c("apps/api"), "Node 22, Fastify, TypeScript", "Merchant, checkout, admin and partner API. Auth, payments, refunds, payment links, webhooks."],
    [c("apps/web"), "React + Vite", "Merchant dashboard and the buyer-facing checkout page (/pay/:token)."],
    [c("apps/admin"), "React + Vite", "Internal console for support, finance and super admins."],
    [c("apps/settlement"), "Go 1.22", "Daily settlement daemon and CLI: batches, payouts, splits, MDR, balance rebuild."],
    [c("apps/reporting"), "Node worker", "Reads the transactional outbox and builds reporting tables."],
    [c("packages/money"), "TypeScript", "Audited integer-fils helpers: parse, format, rates, allocation."],
    [c("db/migrations"), "PostgreSQL 16", "Schema, 78 migrations (0073–0078 added in this work)."],
    [c("ops/"), "Docker Compose, bash", "Local stack, Dilmun VM setup script, load test."],
], [30, 40, 104])
P("All services share one PostgreSQL database and talk to each other through a <b>transactional outbox</b>: a service writes "
  "its change and an event row in the same transaction, and consumers (webhooks, reporting) read the events afterwards.")

H2("1.2 Ground rules that every change follows")
B(["<b>Money is integer fils.</b> 1 BD = 1,000 fils (not cents). Parse text with " + c("parseBhdToFils") + ", format with " + c("formatBhd") + "; never " + c("parseFloat") + ", " + c("toFixed(2)") + " or " + c("* 100") + ".",
   "<b>Business day is Asia/Bahrain</b> (UTC+3, no daylight saving), including the settlement daemon's idea of \"today\".",
   "<b>Randomness for secrets</b> (OTP codes, link tokens, invite codes, keys) comes from " + c("node:crypto") + ", never " + c("Math.random()") + ".",
   "<b>Lock before read-then-write on money</b> (" + c("SELECT … FOR UPDATE") + " or an atomic conditional UPDATE), and every money-moving call takes a client " + c("Idempotency-Key") + ".",
   "<b>Scope every query by the caller's merchant.</b> Admin impersonation is read-only.",
   "<b>Verify, don't defer.</b> A failing test, a doc, or a comment that says \"intentional\" or \"Claude says\" is a claim to check."])

# ---------------- 2. Cases solved ----------------
H1("2. Cases solved so far")
P("These are the tickets, incidents and memos that came with the repository, and how each one ended. \"Solved\" means a fix "
  "is merged and covered by a test or a check against the live server.")
TABLE([
    ["Case", "Symptom reported", "Root cause", "Outcome"],
    ["<b>FP-212 / FP-300 / FP-209</b> Refunds", "POST /v1/refunds returned 501; dashboard had no refund button.", "Helper existed but was never wired; it also refunded against the authorized (not captured) amount and had a race.", "Solved — refunds live, race-free, merchant-scoped."],
    ["<b>FP-187 / FP-198</b> Payment links", "Late payments accepted; possible double charge.", "Expiry trusted buyer-supplied " + c("submittedAt") + "; finalize/release not tied to the attempt holding the link.", "Solved — server-side expiry, reservation token, automatic refund of a losing attempt."],
    ["<b>FP-240</b> Webhooks & callbacks", "Merchants' signature checks failed; callbacks processed twice.", "Dispatcher signed one serialization and sent another; dedupe table " + c("processed_events") + " never existed.", "Solved — signs exact bytes; callbacks deduped on " + c("callback_id") + "."],
    ["<b>FP-203</b> Balance rebuild", "Admin \"rebuild balances\" gave a different number from the CLI.", "Button read scheme-export lines; CLI read the ledger.", "Solved — both read the ledger."],
    ["<b>Incident 2026-08-21</b>", "Two \"payout on the way\" webhooks for one payout.", "Check-then-insert with no lock; daemon and CLI raced. 1.9.1 only told receivers to dedupe.", "Solved — unique index + " + c("ON CONFLICT DO NOTHING") + " (migration 0076)."],
    ["<b>Finance memo:</b> 245 vs 225 bps", "Dashboard showed 245 bps; payments charged 225.", "Display ordered fee schedules by " + c("created_at") + "; billing by " + c("effective_from") + ". A test asserted 245.", "Solved — display uses billing's rule; test corrected."],
    ["<b>Finance memo:</b> CSV import", "Adjustments imported 10x too small (4.75 BD → 475 fils).", "Two-decimal parser default; tests expected the wrong values (\"it is in the tests\").", "Solved — " + c("parseBhdToFils") + "; tests fixed."],
    ["<b>Finance memo:</b> March sweep", "Re-running the sweep doubled the gap on staging.", c("entry_group_id") + " was a fresh UUID each run, so nothing deduped.", "Solved — advisory lock + refuse if already posted."],
    ["<b>Finance memo:</b> volume tier", "Platform discount could switch itself off; payout estimate drifted.", c("int32") + " counter wrapped past ~2.1M BD; estimate stored as " + c("float32") + "/REAL.", "Solved — BIGINT / int64 (migration 0078)."],
    ["<b>\"Is OTP still safe?\"</b>", "Login second factor suspected weak.", "Pending session cookie (password only) worked on every merchant endpoint.", "Solved — sessions require " + c("authenticated = true") + "."],
    ["<b>Cross-merchant login</b>", "Logging in to merchant B could open merchant A.", "Session created for <i>any</i> user with that email, not the row whose password was checked.", "Solved — session tied to the checked row."],
    ["<b>Handwritten note:</b> key rotation", "Old API key still worked after rotation.", c("revoked_at") + " never set; a test asserted a \"grace period\" no doc defines.", "Solved — old key revoked with reason " + c("rotated") + "."],
    ["<b>\"Really large export?\"</b>", "Big exports risked running out of memory or dropping rows.", "Built the whole CSV in memory; the unused streaming version skipped rows that shared a timestamp.", "Solved — streams with keyset paging on (occurred_at, id)."],
    ["<b>Refund report</b>", "Captured totals too high for partly refunded payments.", "Summary view summed capture once per refund row.", "Solved — migration 0077 aggregates per transaction."],
], [30, 40, 56, 48])
NOTE("<b>Not part of this work:</b> the git history also contains a puzzle storyline (the \"Yousif\" commits, three encrypted "
     "\"transmissions\", a \"dead man's switch\"). It is not a defect in the product, it was not attempted here, and nothing in this "
     "document depends on it.")

# ---------------- 3. New features ----------------
H1("3. New features")
H2("3.1 Refunds, end to end")
P("Merchants can now refund a captured payment, fully or in parts, from the API or the dashboard.")
B([c("POST /v1/refunds") + " (API key or session) and " + c("POST /v1/merchants/:id/refunds") + " (dashboard) share one code path.",
   "Refundable amount = <b>captured − already refunded − pending</b>. You can never refund more than was captured.",
   "The transaction row is locked and the amount is reserved in a <b>pending</b> refund row (migration 0073) <i>before</i> calling the acquirer, so two simultaneous refunds cannot both pay out.",
   "Fee reversal uses the net fee kept after any negotiated discount; the final partial refund reverses the exact remainder so fees net to zero.",
   "Status becomes " + c("refunded") + " only when every captured fil has gone back.",
   "A " + c("refund.succeeded") + " webhook is sent to the merchant; the dashboard <b>RefundDrawer</b> is back on the transaction page and transactions now carry " + c("refundedFils") + "."])
H2("3.2 Safe hosted payment links")
B(["Expiry is decided by the server clock only.",
   "Each payment attempt gets a <b>reservation token</b> (migration 0075). Only the attempt that holds the link can finalize or release it.",
   "If a slow attempt loses its reservation after the card was already charged, it is <b>refunded automatically</b> instead of answering \"paid\".",
   "Cancel is scoped to the caller's merchant."])
H2("3.3 Load shedding and self-healing")
P("New Fastify plugin " + c("apps/api/src/plugins/loadShed.ts") + ". When more than " + c("LOAD_SHED_MAX_INFLIGHT") + " requests (default 10) "
  "are in flight, extra requests get " + c("503") + " with " + c("Retry-After: 1") + ". Health checks are never shed. Under systemd the API restarts "
  "within ~2 s after a crash or out-of-memory kill.")
H2("3.4 Measured capacity")
TABLE([
    ["Buyers", "Checkouts/s", "p95 latency", "Shed (503)", "Duplicate payments"],
    ["10", "8.2", "1.65 s", "0", "0"],
    ["20", "8.1", "3.15 s", "0", "0"],
    ["40", "7.9", "5.71 s", "0", "0"],
    ["150 (shedding at 10)", "7.6", "1.89 s", "4,111", "0"],
], [42, 30, 30, 30, 42])
P("Measured at 0.5 vCPU / 512 MB with the simulated acquirer. The honest production range is <b>6–8 checkouts per second</b>. "
  "Beyond that, extra buyers are asked to retry instead of slowing everyone down. Load test: " + c("ops/loadtest/checkout.mjs") + ".")
H2("3.5 Other additions")
TABLE([
    ["Feature", "What it gives you"],
    ["Streaming CSV export", c("GET /v1/transactions/export") + " streams rows with keyset paging; safe for very large merchants."],
    [c("ops/dilmune/setup.sh"), "One command on the server: checks env vars, runs migrations, builds Go settlement, starts 3 systemd services with CPU/memory caps, fails loudly if anything is down."],
    ["Docker images", c("ops/Dockerfile.node") + " (api, reporting, migrate, seed) and " + c("ops/Dockerfile.go") + " (settlement, distroless)."],
    [c("CORS_ALLOWED_ORIGINS"), "Deployed frontends on other hosts can call the API."],
    ["API root " + c("GET /"), "Returns service name, status and links to health, readiness and the API instead of a 404."],
    ["Dashboard root and 404 page", c("/") + " redirects to the dashboard (or login); unknown paths show \"Page not found\"."],
    [c("create-merchant.cjs"), "Helper to sign up a merchant on the hosted API (" + c("--dry-run") + " validates input)."],
    ["Config tests", c("apps/api/src/config.test.ts") + " guards the dev webhook key length and production requirements."],
    ["New migrations", "0073 pending refunds · 0074 callback dedupe · 0075 link reservation token · 0076 one payout event per batch · 0077 refund summary fix · 0078 BIGINT running totals."],
    [c("CLAUDE.md") + " / " + c("AGENTS.md"), "New AI conventions replacing \"Order of the Prompt\"; one source for Claude, Cursor and Copilot."],
], [48, 126])

# ---------------- 4. Bugs fixed in code ----------------
H1("4. Bugs fixed in the code")
P("Grouped by area. The commit that carries most of round 1 is " + c("4a68dc9") + "; round 2 is " + c("5c3fa2d") + ". "
  "Each round-2 fix has a test that fails when the old code is swapped back in.")
H2("4.1 Money")
TABLE([
    ["Bug", "Impact", "Fix"],
    ["Adjustment CSV read 4.75 BD as 475 fils", "Every finance adjustment 10x too small", "Use " + c("parseBhdToFils") + "; corrected tests that encoded the bug"],
    ["Promotional discounts used " + c("parseFloat * 100"), "Cents maths on a fils currency", "Integer fils helpers"],
    ["Go " + c("NetPayableFils") + " used float32", "Rounding errors on payouts", "Integer arithmetic"],
    ["Split payouts did not sum to the batch", "Fils lost or invented between child merchants", "Largest-remainder allocation"],
    ["MDR recalculation rewrote paid batches", "History of paid money changed", "Skips paid batches"],
    ["Daemon \"today\" from UTC date", "Wrong business day near midnight", "Derived from Bahrain calendar date"],
    ["Platform volume counter int32 / INTEGER", "Wraps negative past ~2.1M BD; discount turns off for all", "BIGINT / int64 (0078)"],
    ["Lifetime payout estimate REAL / float32", "Drifts past ~16,777 BD", "BIGINT / int64 (0078)"],
    ["Fee display vs billing (245 vs 225 bps)", "Support quotes the wrong fee", "Display uses " + c("effective_from") + " like billing"],
    ["March sweep not re-runnable", "Second run posts residue again", "Advisory lock + existence check"],
    ["Refund summary double-counted captures", "Reports overstate captured money", "Migration 0077"],
], [56, 58, 60])
H2("4.2 Security")
TABLE([
    ["Bug", "Impact", "Fix"],
    ["OTP step optional on merchant plane", "Stolen password = full login", c("lookupSession") + " requires " + c("authenticated = true")],
    ["Login could land in another merchant", "Tenant isolation broken", "Session created for the row whose password was checked"],
    ["API key rotation left old key active", "Rotating a leaked key did nothing", "Old key revoked in the same transaction"],
    ["OTP, link tokens, invite codes from " + c("Math.random()"), "Predictable secrets", c("node:crypto") + " via " + c("lib/random.ts")],
    ["Admin impersonation could capture, void, refund", "Support staff moving merchant money", "Impersonation is read-only"],
    ["Refund / cancel looked up by id only", "Merchant A could refund merchant B's payment", "Scoped by caller's merchant"],
    ["Secrets committed to git", "Admin password and sandbox secret public", "Untracked + gitignored (rotation still required)"],
], [56, 52, 66])
H2("4.3 Concurrency, webhooks and data")
TABLE([
    ["Bug", "Impact", "Fix"],
    ["Concurrent refunds both paid out", "Double refunds", "Row lock + pending reservation (0073)"],
    ["Payment link double charge / late pay", "Buyer charged twice or after expiry", "Reservation token, server expiry, auto-refund (0075)"],
    ["Webhook signed bytes ≠ sent bytes", "Every merchant's signature check failed", c("serializeWebhookBody") + " used for both"],
    ["Acquirer callbacks not deduplicated", "Same callback applied twice", "Dedupe on " + c("callback_id") + " (0074)"],
    ["Duplicate " + c("settlement.paid") + " events", "Two payout webhooks per payout", "Partial unique index (0076)"],
    ["Export built in memory / skipped rows", "OOM or silently missing rows", "Streaming + keyset paging"],
    ["Admin rebuild read wrong source (FP-203)", "Button and CLI disagree", "Both read the ledger"],
], [56, 52, 66])
H2("4.4 Migrations and tests")
B(["Migrations 0054, 0055 and 0072 referenced tables or columns that do not exist, so a fresh database could not be built. Fixed.",
   "A webhook back-off test asserted an exact delay against randomly jittered code (flaky). It now fixes the jitter.",
   "An archive-replay test wrote empty outbox payloads that crashed the reporting consumer on a shared database (bug #11). Fixed.",
   "Tests that encoded defects (CSV 10x, 245 bps, key \"grace period\", balance seeding from scheme lines) were corrected in the same change as the code."])

# ---------------- 5. Deployment bug log ----------------
H1("5. Deployment and operations bug log")
P("Found while running the stack locally and deploying it to Dilmun Cloud on 30 October 2026. Full details are in " + c("bugs.md") + ".")
TABLE([
    ["#", "Bug", "Sev.", "Status"],
    ["1", "API site served the repo as static files (admin password downloadable)", "Critical", "Mitigated"],
    ["2", "Admin password and sandbox secret committed to git", "Critical", "Mitigated"],
    ["3", "Postgres port 5432 open to the internet", "High", "Open"],
    ["4", c("*.dilmune.app") + " DNS records never created", "High", "Fixed"],
    ["5", "No HTTPS (nothing on port 443)", "High", "Fixed"],
    ["6", "API, settlement and reporting not running", "High", "Fixed"],
    ["7", c("DATABASE_URL") + " held a placeholder password", "High", "Fixed"],
    ["8", "Overlapping API deploys corrupted " + c("node_modules"), "High", "Fixed"],
    ["9", "Frontend deep links (" + c("/pay/:token") + ") returned 404", "High", "Fixed"],
    ["10", "Checkout bundle called " + c("http://localhost:3000"), "High", "Fixed"],
    ["11", "Reporting tests failed on a shared test database", "Medium", "Fixed"],
    ["12", "Local compose: settlement exited at boot (no token)", "Medium", "Fixed"],
    ["13", "Root helper scripts crashed (" + c("require") + " in an ESM repo)", "Medium", "Fixed"],
    ["14", "Helper scripts pointed at old hostnames", "Low", "Fixed"],
    ["15", c("setup.sh") + " skipped migrations and reported success on failure", "Medium", "Fixed"],
    ["16", "Docs and comments contradicted the code (8 claims)", "Medium", "Fixed"],
    ["17", "Dilmun auto-deploy does not fire on push", "Medium", "Open"],
    ["18", "Dilmun reports sites active / SSL on when they are not", "Low", "Open (platform)"],
    ["19", "Dev webhook key was 34 bytes, so the API couldn't boot in dev", "Medium", "Fixed"],
    ["20", "Local compose ran every Node service in production mode", "Medium", "Fixed"],
    ["21", "Settlement logs \"next check-in ~tomorrow\" but re-runs every minute", "Low", "Open"],
    ["22", "Production cannot deliver login codes (no email/SMS)", "High", "Mitigated"],
    ["23", "fp-pay " + c("/") + " and unknown paths showed a router error", "Medium", "Fixed"],
    ["24", "API root " + c("/") + " returned \"Route GET:/ not found\"", "Low", "Fixed"],
], [9, 115, 20, 30], status_col=3)

H2("5.1 Still open — what to do next")
TABLE([
    ["Item", "Why it matters", "Next step"],
    ["#3 Postgres open to internet", "Database reachable from anywhere", "Delete firewall rule #4 in the Dilmun dashboard; remove " + c("0.0.0.0/0") + " from pg_hba.conf"],
    ["#2 Secrets in git history", "Old admin password and sandbox secret are public", "Rotate both; optionally rewrite history (owner decision)"],
    ["#22 OTP delivery", c("OTP_DEV_EXPOSE=true") + " shows the code on the login page, so password alone logs in", "Add an email/SMS sender, then remove " + c("OTP_DEV_EXPOSE")],
    ["#17 Auto-deploy", "Pushes don't deploy", "Check the Dilmun GitHub app / webhook; deploy manually until then"],
    ["#21 Settlement log", "Log contradicts behaviour", "Decide whether the per-minute re-run is intended; fix log or loop"],
    ["Scheme residue (ADR-0002)", "Statements always a few fils over", "Post residue inside CloseBatch"],
    ["Stale pending refunds", "A crash between reserve and settle leaves money reserved", "Add a reaper job"],
    ["OTP rate limit / admin session rotation", "Brute force; session fixation (FP-198)", "Rate-limit verify/resend; rotate token after OTP"],
], [42, 62, 70])

# ---------------- 6. How AI was used ----------------
H1("6. How the work was verified")
P("Claude Code did much of the investigation and coding. The rule for every AI claim was: <b>the AI can propose, only evidence "
  "closes an item.</b> Evidence means a test that fails on the old code and passes on the new, a query against the real database, "
  "or a request to the live server.")
B(["Inherited \"Claude says\" comments were treated as claims. Three of them were wrong (fee ordering, BIGINT column, sweep dedupe).",
   "Old code was swapped back in to prove the new tests catch it: 58 pass / 5 fail on old code → 377 / 0 on fixed code (round 2).",
   "\"It printed success\" was not accepted for server work. Database rows, process uptime and command history were checked instead.",
   "The round-1 Go fixes were only counted as done once they compiled and passed " + c("go test") + " against Postgres.",
   "Final state: TypeScript suite <b>453 / 453</b> on a fresh Postgres; Go settlement packages pass."])
P("Details and transcript excerpts: " + c("docs/AI-USAGE.md") + ".")

# ---------------- 7. Real-life use ----------------
H1("7. Using FilsPay in a real business")
P("This section walks through the platform from a merchant's, a developer's and an operator's point of view. "
  "Amounts are always integer fils: " + c("12500") + " means 12.500 BD.")
H2("7.1 As a merchant (dashboard)")
N(["<b>Sign up and pass KYC.</b> Payments are refused with " + c("merchant_not_approved") + " until an admin approves your KYC documents.",
   "<b>Log in</b> at " + c("/dashboard/login") + " with merchant ID, email and password, then the 6-digit code. The merchant ID is needed because one email can belong to several merchants.",
   "<b>Create an API key</b> for your website or app, and a <b>webhook endpoint</b> to receive events.",
   "<b>Create a payment link</b> (amount, reference, description, expiry) and send it to the buyer by WhatsApp, SMS or email. The buyer opens " + c("/pay/&lt;token&gt;") + " and pays by card.",
   "<b>Watch transactions</b>: authorized, captured, refunded. Open one to see details and refund it with the <b>Refund</b> drawer (full or partial).",
   "<b>Export</b> transactions to CSV for your accountant; large exports stream, so they are safe.",
   "<b>Receive payouts</b>: settlement runs per Bahrain business day; you get a " + c("settlement.paid") + " webhook once per payout."])
H2("7.2 As a developer (API integration)")
P("Server-to-server calls use your API key as a Bearer token. Always send a unique " + c("Idempotency-Key") + " per logical operation "
  "and reuse it when you retry, so a network timeout never causes a double charge.")
CODE("""
API=https://fp-api-tzakir.dilmune.app        # or http://localhost:3000
KEY=fp_test_...                               # your API key

# 1. Authorize a card payment of 12.500 BD
curl -s $API/v1/transactions \\
  -H "authorization: Bearer $KEY" -H "content-type: application/json" \\
  -H "idempotency-key: order-1042-auth" \\
  -d '{"amountFils":12500,"card":{"pan":"4242424242424242",
       "expiryMonth":12,"expiryYear":2030,"cvv":"123"}}'

# 2. Capture it when you ship the goods
curl -s -X POST $API/v1/transactions/<id>/capture \\
  -H "authorization: Bearer $KEY" -H "idempotency-key: order-1042-capture"

# 3. Refund part of it (2.000 BD)
curl -s $API/v1/refunds \\
  -H "authorization: Bearer $KEY" -H "content-type: application/json" \\
  -H "idempotency-key: order-1042-refund-1" \\
  -d '{"transactionId":"<id>","amountFils":2000,"reason":"damaged item"}'
""")
P("Other useful routes: " + c("POST /v1/transactions/:id/void") + " (cancel an uncaptured authorization), "
  + c("POST /v1/merchants/:merchantId/payment-links") + " (body: " + c("amountFils") + ", " + c("expiresAt") + ", optional "
  + c("reference") + ", " + c("description") + "), " + c("GET /v1/transactions/export") + ".")
H3("Handling 503 under load")
P("If the API is busy it answers " + c("503") + " with " + c("Retry-After: 1") + ". Wait one second and retry <b>with the same Idempotency-Key</b>. "
  "The request was not processed, so retrying is safe.")
H3("Verifying webhooks")
P("Each delivery carries " + c("Webhook-Signature: t=&lt;unix&gt;,v1=&lt;hex&gt;") + " and a stable delivery id. Compute "
  "HMAC-SHA256 with your endpoint secret over " + c("&lt;t&gt;.&lt;raw body bytes&gt;") + " and compare in constant time. "
  "Use the <b>raw</b> request body, not re-serialized JSON. Reject old timestamps (for example older than 5 minutes) and dedupe on the delivery id.")
CODE("""
import crypto from "node:crypto";
function verify(rawBody, header, secret) {
  const { t, v1 } = Object.fromEntries(header.split(",").map(p => p.split("=")));
  if (Math.abs(Date.now() / 1000 - Number(t)) > 300) return false;
  const mac = crypto.createHmac("sha256", secret).update(`${t}.${rawBody}`).digest("hex");
  return crypto.timingSafeEqual(Buffer.from(mac), Buffer.from(v1));
}
""")
H2("7.3 As an operator (admin console)")
B(["<b>Support</b> can look up merchants and transactions and impersonate a merchant to see what they see. Impersonation cannot capture, void or refund.",
   "<b>Finance</b> imports adjustment sheets (BD amounts are now parsed correctly), reviews fee schedules (shown as billing applies them) and checks settlement.",
   "<b>Super admins</b> approve KYC, manage admin users and rotate merchant API keys. Rotation immediately revokes the old key.",
   "Rebuild balances from the console or " + c("settlement rebuild-balances") + "; both read the ledger and agree."])
H2("7.4 Before handling real money")
WARN("The live demo uses a <b>simulated acquirer</b> and shows login codes on screen. It must not take real card payments until these are done.")
N(["Connect a real acquirer and complete PCI DSS scope review. Raw card numbers should go to a PCI-compliant tokenizer, not your own servers.",
   "Add real OTP delivery (email or SMS) and remove " + c("OTP_DEV_EXPOSE") + ".",
   "Close Postgres to the internet (bug #3) and rotate every secret that was ever committed (bug #2).",
   "Generate fresh " + c("WEBHOOK_SECRET_ENCRYPTION_KEY") + ", " + c("ACQUIRER_CALLBACK_SIGNING_SECRET") + " and " + c("SETTLEMENT_INTERNAL_TOKEN") + " per environment.",
   "Finish scheme residue posting, the pending-refund reaper and OTP rate limiting (section 5.1).",
   "Set up backups for Postgres, log retention and alerts on " + c("/readyz") + ".",
   "Get finance sign-off on settlement output for a full test month."])
story.append(PageBreak())

# ---------------- 8. Setup ----------------
H1("8. Setting everything up")
H2("8.1 Prerequisites")
TABLE([
    ["Tool", "Version", "Used for"],
    ["Node.js + npm", "22", "API, frontends, reporting, tests"],
    ["Go", "1.22+", "Settlement daemon and CLI"],
    ["Docker Desktop", "recent", "Local Postgres and backend services"],
    ["Git", "any", "Getting the code"],
    ["PostgreSQL", "16", "Only if you run without Docker"],
], [40, 25, 109])
H2("8.2 Get the code")
CODE("""
git clone https://github.com/thrzkr/fils-pay.git
cd fils-pay
npm ci
""")
H2("8.3 Run the backend locally (Docker)")
CODE("""
docker compose -f ops/docker-compose.yml up -d postgres
docker compose -f ops/docker-compose.yml run --rm migrate
docker compose -f ops/docker-compose.yml run --rm seed
docker compose -f ops/docker-compose.yml up -d --build api settlement reporting
""")
P("Postgres is on " + c("localhost:5432") + ", the API on " + c("localhost:3000") + ". The seed prints a test API key. Check it:")
CODE("""
curl http://localhost:3000/healthz     # {"status":"ok",...}
curl http://localhost:3000/readyz      # {"status":"ready"}
""")
P("Stop with " + c("docker compose -f ops/docker-compose.yml down") + " (add " + c("-v") + " to wipe the database). "
  "Re-running " + c("seed") + " resets everything; never run it against a shared or production database.")
H2("8.4 Run the frontends")
CODE("""
npm run dev --workspace @filspay/web      # http://localhost:5173  (dashboard + checkout)
npm run dev --workspace @filspay/admin    # http://localhost:5174  (admin console)
""")
H2("8.5 Log in locally")
P("In development the API returns the one-time code and the login page shows it.")
TABLE([
    ["Where", "Login", "Password"],
    ["Admin  localhost:5174/login", c("support@filspay.test") + ", " + c("finance@filspay.test") + ", " + c("superadmin@filspay.test"), c("FilsPayAdminSeed!2026")],
    ["Dashboard  localhost:5173/dashboard/login", c("owner@alpharetail.example") + " (and others in README) + merchant ID", c("FilsPaySeed!2026")],
], [44, 82, 48])
P("Merchant IDs change on every seed. List them with:")
CODE("""
docker compose -f ops/docker-compose.yml exec postgres psql -U filspay -d filspay -c \\
  "select m.id, m.display_name, u.email from merchant_users u join merchants m on m.id = u.merchant_id"
""")
P("<b>Live demo:</b> " + c("fp-pay-tzakir.dilmune.app/dashboard/login") + ", merchant ID " + c("94850160-a3f5-4377-a260-af4fe28e7743") + ", "
  "email " + c("demo@filspay.demo") + ", password " + c("FilsPayDemo!2026") + " (shared, simulated money only). Other live accounts have private passwords held by the repository owner.")
H2("8.6 Run without Docker")
CODE("""
export DATABASE_URL="postgres://USER:PASSWORD@localhost:5432/filspay"
npm run migrate
npm run dev --workspace @filspay/api
""")
H2("8.7 Run the tests")
CODE("""
npm run typecheck
DATABASE_URL=postgres://.../filspay_test npm run migrate
DATABASE_URL=postgres://.../filspay_test npm test      # use a disposable database
cd apps/settlement && go test -short ./...
""")
H2("8.8 Deploy to production (Dilmun Cloud)")
TABLE([
    ["Site", "Build command", "Serves"],
    ["fp-pay", c("VITE_API_BASE_URL=https://fp-api-…  npm run build --workspace @filspay/web"), c("apps/web/dist") + " (static)"],
    ["fp-admin", c("VITE_ADMIN_API_BASE_URL=… VITE_WEB_BASE_URL=… npm run build --workspace @filspay/admin"), c("apps/admin/dist") + " (static)"],
    ["fp-api", "none (checkout only)", "nginx reverse proxy → 127.0.0.1:3000"],
], [22, 102, 50])
N(["Install command on all three sites: " + c("npm ci --include=dev") + ". Frontend nginx must use " + c("try_files $uri $uri/ /index.html") + ".",
   "Set the API environment: " + c("NODE_ENV=production") + ", " + c("DATABASE_URL") + ", " + c("WEBHOOK_SECRET_ENCRYPTION_KEY") + " (" + c("openssl rand -base64 32") + "), "
   + c("ACQUIRER_CALLBACK_SIGNING_SECRET") + ", " + c("SETTLEMENT_INTERNAL_TOKEN") + ", " + c("SETTLEMENT_INTERNAL_URL=http://127.0.0.1:8091") + ", "
   + c("CORS_ALLOWED_ORIGINS") + ", " + c("CHECKOUT_BASE_URL") + ", " + c("TZ=Asia/Bahrain") + ", " + c("KYC_UPLOAD_DIR") + ", optional " + c("LOAD_SHED_MAX_INFLIGHT") + ".",
   "Deploy fp-api, then from its site root run " + c("bash ops/dilmune/setup.sh") + ". It must end with " + c("setup: OK") + ".",
   "Deploy fp-pay and fp-admin <b>one at a time</b> (overlapping deploys corrupt node_modules), then confirm the bundle points at the live API (command in " + c("docs/DEPLOY.md") + ").",
   "Check " + c("/healthz") + " and " + c("/readyz") + ", log in, capture a test payment and refund it.",
   "Never run " + c("npm run seed") + " on the server: it truncates merchants, transactions and the ledger."])
story.append(PageBreak())

# ---------------- 9. Claude Code ----------------
H1("9. Setting up Claude Code (the AI assistant)")
P("Claude Code is Anthropic's coding assistant. It reads the repository, runs commands and tests, edits files and makes commits. "
  "This project was worked on with it from the desktop app and from the web. Pick one of the options below.")
H2("9.1 Option A — in the browser (no install)")
N(["Go to " + c("claude.ai/code") + " and sign in with a Claude Pro, Max, Team or Enterprise account.",
   "Connect GitHub when asked and install the Claude GitHub App on " + c("thrzkr/fils-pay") + ".",
   "Pick the repository and start a session. It runs in a cloud sandbox with its own copy of the code and pushes work to a branch.",
   "Optional: in the environment settings, allow network access and add a setup script (for example " + c("npm ci") + ") so tests can run."])
H2("9.2 Option B — on your computer (terminal, desktop app or IDE)")
CODE("""
# macOS / Linux / WSL
curl -fsSL https://claude.ai/install.sh | bash

# Windows PowerShell
irm https://claude.ai/install.ps1 | iex

# or, with Node.js 18+ installed
npm install -g @anthropic-ai/claude-code
""")
P("Then open the project and start it:")
CODE("""
cd fils-pay
claude          # first run opens the browser to log in
""")
P("The Claude desktop app (macOS / Windows) and the VS Code and JetBrains extensions use the same account and the same project rules.")
H2("9.3 Project rules Claude follows automatically")
P("When Claude Code opens this repository it loads " + c("CLAUDE.md") + " (other tools read " + c("AGENTS.md") + ", which points to it). "
  "Those rules encode everything in section 1.2: integer fils, Bahrain business day, crypto randomness, merchant scoping, "
  "locking and idempotency, and \"verify, don't defer\". Change them there, in one place, if the conventions change.")
H2("9.4 Working with Claude effectively")
B(["<b>Give it the evidence.</b> Paste the error, the failing test name or the finance memo. \"Refunds over 10 BD fail with 409\" beats \"refunds are broken\".",
   "<b>Ask for a failing test first</b>, then the fix. That is the rule this whole project followed.",
   "<b>Make it prove server work.</b> Ask it to check database rows, " + c("/readyz") + " or process uptime, not just a printed \"OK\".",
   "<b>Keep a database for tests.</b> Give it a disposable " + c("DATABASE_URL") + " so " + c("npm test") + " can run without touching real data.",
   "<b>Review the diff before merging.</b> " + c("/code-review") + " and " + c("/security-review") + " in Claude Code help, but a person approves money and security changes.",
   "<b>Never paste production secrets</b> into a chat or commit them; put them in the server's environment settings."])
H3("Example prompts")
CODE("""
"Run the test suite against $DATABASE_URL and fix any failures. For each one,
 tell me whether the test or the code was wrong and why."

"Add an email sender for OTP codes (bug #22) behind an OTP_EMAIL_* config,
 with a test, then tell me exactly what to change on the fp-api site."

"Write a reaper for refunds stuck in 'pending' for more than 15 minutes.
 Lock rows, be idempotent, add a test, and explain the failure cases."
""")

# ---------------- Appendix ----------------
H1("Appendix — glossary")
TABLE([
    ["Term", "Meaning"],
    ["Fils", "1/1000 of a Bahraini dinar. All money in the system is stored as whole fils."],
    ["Authorize / capture / void", "Reserve money on the card / actually take it / release the reservation."],
    ["Basis points (bps)", "1/100 of a percent. 225 bps = 2.25%."],
    ["MDR", "Merchant discount rate: the fee FilsPay charges per payment."],
    ["Settlement batch", "All of a merchant's captured money for one Bahrain business day, paid out together."],
    ["Outbox", "Event table written in the same transaction as the change; webhooks and reporting read from it."],
    ["Idempotency-Key", "Client-chosen id that makes a retried request return the original result instead of repeating it."],
    ["Load shedding", "Refusing extra work with 503 so admitted requests stay fast."],
    ["Scheme residue", "Fils lost when card schemes round amounts to two decimals; still to be posted automatically."],
    ["OTP", "One-time 6-digit login code, the second login factor."],
], [40, 134])

# ---------------- build ----------------
class Doc(BaseDocTemplate):
    def afterFlowable(self, f):
        if hasattr(f, "toc_level"):
            txt = f.getPlainText()
            key = "k%d" % id(f)
            self.canv.bookmarkPage(key)
            self.canv.addOutlineEntry(txt, key, level=f.toc_level, closed=False)
            self.notify("TOCEntry", (f.toc_level, txt, self.page, key))

out = sys.argv[1]
doc = Doc(out, pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm, topMargin=20 * mm, bottomMargin=18 * mm,
          title="FilsPay — fixes, features and field guide", author="FilsPay team with Claude Code",
          subject="FP-300 audit, deployment bug log, usage and setup guide")
fr = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="f")
doc.addPageTemplates([PageTemplate("cover", [fr], onPage=cover_page), PageTemplate("body", [fr], onPage=body_page)])
doc.multiBuild(story)
print("ok", out)
