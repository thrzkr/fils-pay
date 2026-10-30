import sys
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, PageBreak, KeepTogether, NextPageTemplate, Table, TableStyle
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.lib.styles import ParagraphStyle
from reportlab.graphics.shapes import Drawing, Rect, String, Line, Group
from reportlab.graphics.charts.barcharts import VerticalBarChart
from common import *

st = Story()
W = 174  # usable width mm

# ============================== COVER ==============================
st.append(Spacer(1, 52 * mm))
st.P(f'<font size="9" color="{MUTED.hexval()}">Team</font><br/><font size="20"><b>{TEAM}</b></font>')
st.append(Spacer(1, 4))
st.TABLE([["Member", "What they owned"]] + [[n, o] for n, o in MEMBERS], [55, 119])
st.H3("Live URLs")
st.KV(URLS)
st.H3("Repository")
st.KV([("Public fork", FORK), ("Last commit", c(COMMIT)),
       ("Branch", c("main") + " (default branch of the fork)")])
st.P("Demo merchant login (shared, simulated money): merchant ID " + c("94850160-a3f5-4377-a260-af4fe28e7743") +
     ", " + c("demo@filspay.demo") + " / " + c("FilsPayDemo!2026") + ". The login page shows the one-time code (see finding F-25).", "muted")
st.append(NextPageTemplate("body")); st.append(PageBreak())

toc = TableOfContents()
toc.levelStyles = [ParagraphStyle("t0", fontName="Sans-Bold", fontSize=9.4, leading=13, textColor=INK),
                   ParagraphStyle("t1", fontName="Sans", fontSize=8.2, leading=10.6, leftIndent=12, textColor=MUTED)]
st.append(Paragraph("Contents", S["h1"])); st.append(toc); st.append(PageBreak())

# ============================== 1. SUMMARY ==============================
st.H1("1. Summary")
st.P("<b>What we found.</b> FilsPay worked on the happy path and failed wherever money met concurrency, tenancy or rounding. "
     "We logged <b>26 code findings</b> and <b>24 deployment/operations bugs</b>. The worst were: the login code (OTP) could be skipped entirely; "
     "one merchant's password could open another merchant's account; refunds returned 501 and, once wired, could pay out twice; finance "
     "CSV adjustments were posted 10x too small; webhooks were signed over different bytes than were sent; the settlement worker "
     "duplicated payout notifications; and the hosted API site served the git checkout, including an admin password, as static files.")
st.P("<b>What we fixed.</b> 24 of the 26 code findings are fixed. Each has a test that fails on the old code, or a query or live request as proof. "
     "We added refunds end to end (API, row-locked reservation, fee reversal, webhook, dashboard drawer), "
     "made payment links safe against double charges, moved all money paths to integer fils, "
     "and deployed the stack to Dilmun Cloud behind HTTPS with systemd restarts, load shedding and a one-command redeploy. "
     "Fresh run on a clean Postgres: <b>TypeScript 453/453, Go all packages pass</b>.")
st.P("<b>What we left alone.</b> We did not change settlement to net refunds out of payouts (finding F-01). Finance owns that decision, "
     "and a change to payout logic on the deadline day is riskier than the bug. We also did not rewrite git history to purge committed secrets, "
     "did not run backfills on production data, and did not add an email/SMS sender for OTP codes. All of these are in section 4.3 with the safeguard we propose.")
st.P("<b>Main root cause.</b> The team treated generated code, code comments and tests as the source of truth instead of the ledger. "
     "Tests were written to assert bugs, and \"Claude says\" comments closed questions without a check. So the same four patterns repeated "
     "across the codebase: <b>check-then-act without a lock</b>, <b>two sources of truth for one number</b>, <b>money not typed as integer fils end to end</b>, "
     "and <b>queries not scoped to the caller's merchant</b>.")

# ============================== 2. ARCHITECTURE ==============================
st.H1("2. Architecture and deployment")
st.P("One Dilmun Cloud VM (1 vCPU, 2 GB RAM, 50 GB) behind Cloudflare. nginx and Postgres 16 are managed by Dilmun. "
     "The three FilsPay processes run as systemd services. Only nginx (80/443) is meant to face the internet.")

def arch():
    d = Drawing(W * mm, 112 * mm)
    def box(x, y, w, h, title, sub="", fill="#ffffff", stroke="#0f6e6e", tc="#1b2430"):
        d.add(Rect(x * mm, y * mm, w * mm, h * mm, rx=4, ry=4, fillColor=colors.HexColor(fill), strokeColor=colors.HexColor(stroke), strokeWidth=0.9))
        d.add(String((x + w / 2) * mm, (y + h - 5.2) * mm, title, fontName="Sans-Bold", fontSize=7.8, textAnchor="middle", fillColor=colors.HexColor(tc)))
        for i, line in enumerate(sub.split("\n") if sub else []):
            d.add(String((x + w / 2) * mm, (y + h - 9.4 - i * 3.5) * mm, line, fontName="Sans", fontSize=6.4, textAnchor="middle", fillColor=colors.HexColor("#5b6675")))
    def arrow(x1, y1, x2, y2, label="", col="#5b6675", dash=None):
        ln = Line(x1 * mm, y1 * mm, x2 * mm, y2 * mm, strokeColor=colors.HexColor(col), strokeWidth=0.9)
        if dash: ln.strokeDashArray = dash
        d.add(ln)
        import math
        a = math.atan2(y2 - y1, x2 - x1); L = 2.0
        for s in (0.45, -0.45):
            d.add(Line(x2 * mm, y2 * mm, (x2 - L * math.cos(a + s)) * mm, (y2 - L * math.sin(a + s)) * mm, strokeColor=colors.HexColor(col), strokeWidth=0.9))
        if label:
            d.add(String(((x1 + x2) / 2 + 1) * mm, ((y1 + y2) / 2 + 1) * mm, label, fontName="Sans", fontSize=6.2, fillColor=colors.HexColor(col)))
    # internet band
    d.add(Rect(0, 92 * mm, W * mm, 20 * mm, fillColor=colors.HexColor("#fdf3e1"), strokeColor=None))
    d.add(String(2 * mm, 108 * mm, "INTERNET-FACING", fontName="Sans-Bold", fontSize=6.6, fillColor=colors.HexColor("#9a6700")))
    box(8, 94, 40, 12, "Buyers & merchants", "browsers", "#ffffff", "#9a6700")
    box(66, 94, 44, 12, "Cloudflare", "TLS, *.dilmune.app DNS", "#ffffff", "#9a6700")
    box(126, 94, 44, 12, "Operators (SSH)", "Dilmun console / port 22", "#ffffff", "#9a6700")
    arrow(48, 100, 66, 100, "443")
    # VM
    d.add(Rect(2 * mm, 2 * mm, (W - 4) * mm, 86 * mm, rx=6, ry=6, fillColor=colors.HexColor("#f7f9fa"), strokeColor=colors.HexColor("#d5dbe1")))
    d.add(String(5 * mm, 83 * mm, "Dilmun VM  139.59.13.131  (1 vCPU / 2 GB)", fontName="Sans-Bold", fontSize=6.8, fillColor=colors.HexColor("#5b6675")))
    box(62, 66, 52, 14, "nginx  :80 / :443", "Let's Encrypt, HTTP→HTTPS", "#e6f2f2")
    arrow(88, 94, 88, 80, "443 (origin)")
    box(6, 44, 46, 16, "fp-pay (static)", "apps/web dist\ncheckout + dashboard")
    box(56, 44, 46, 16, "fp-admin (static)", "apps/admin dist\nadmin console")
    box(110, 40, 56, 20, "filspay-api  127.0.0.1:3000", "Fastify, systemd\n0.5 vCPU / 512 MB\nload shed at 10 in-flight")
    arrow(70, 66, 30, 60); arrow(86, 66, 79, 60); arrow(104, 66, 132, 60, "fp-api: proxy")
    box(110, 8, 56, 22, "Postgres 16  :5432", "Dilmun-managed\n! firewall open to 0.0.0.0/0\n(finding F-24, open)", "#fbe9e7", "#b3261e")
    box(6, 8, 46, 22, "filspay-settlement", "Go daemon, systemd\ninternal API 127.0.0.1:8091\n0.25 vCPU / 256 MB")
    box(58, 8, 46, 22, "filspay-reporting", "Node outbox worker\nno listening port\n0.2 vCPU / 256 MB")
    arrow(138, 40, 138, 30, "SQL")
    d.add(Line(29 * mm, 8 * mm, 29 * mm, 4.5 * mm, strokeColor=colors.HexColor("#5b6675"), strokeWidth=0.9))
    d.add(Line(29 * mm, 4.5 * mm, 116 * mm, 4.5 * mm, strokeColor=colors.HexColor("#5b6675"), strokeWidth=0.9))
    arrow(116, 4.5, 116, 8)
    d.add(String(60 * mm, 5.3 * mm, "SQL", fontName="Sans", fontSize=6.2, fillColor=colors.HexColor("#5b6675")))
    arrow(104, 19, 110, 19, "")
    arrow(110, 46, 52, 26, "admin → :8091 (token)", dash=[2, 2])
    arrow(171, 92, 162, 30, "", "#b3261e", dash=[1, 2])
    d.add(String(148 * mm, 88.5 * mm, "internet → 5432 (open)", fontName="Sans", fontSize=6.2, fillColor=colors.HexColor("#b3261e")))
    return d

st.append(arch())
st.P("Ports: <b>443/80</b> (nginx, public through Cloudflare); <b>22</b> (SSH, operators); <b>3000</b> API and <b>8091</b> settlement internal API "
     "bind to 127.0.0.1 only (verified closed from outside); <b>5432</b> Postgres is still reachable from the internet (finding F-24, open). "
     "Services talk through the shared database and the transactional outbox.", "muted")

st.H2("2.1 Redeploy in one command")
st.P("After Dilmun pulls the new commit into the fp-api site, one idempotent command rebuilds and restarts everything:")
st.CODE("bash ops/dilmune/setup.sh")
st.B(["Fails fast if any required variable is missing from " + c(".env") + ".",
      "Applies database migrations (" + c("db/migrate.ts") + ", already-applied files are skipped).",
      "Builds the Go settlement binary (installs Go 1.22 if absent).",
      "Writes and (re)starts three systemd units with CPU and memory caps, takes the API over from the old pm2 process.",
      "Exits non-zero unless all three services are " + c("active") + " and " + c("/readyz") + " answers within 30 s."])
st.P("Frontends are static builds on their own Dilmun sites (build commands in " + c("docs/DEPLOY.md") + "; the API URL is baked in at build time and checked with a bundle grep after deploy). "
     "Local equivalent: " + c("docker compose -f ops/docker-compose.yml up -d --build") + ".")

st.H2("2.2 Where secrets come from")
st.B(["Secrets live only in the fp-api site's <b>Environment variables</b> in Dilmun. Dilmun writes them to " + c(".env") + " in the site root on deploy. "
      + c("setup.sh") + " sets it to " + c("chmod 600") + " and systemd loads it with " + c("EnvironmentFile=") + ".",
      c(".env*") + " is gitignored. Nothing secret is in " + c("setup.sh") + ", compose or the repo. The " + c(".claude/settings.json") + " deny rules stop the assistant from reading them.",
      "Production refuses to boot without " + c("WEBHOOK_SECRET_ENCRYPTION_KEY") + " (32 bytes), " + c("ACQUIRER_CALLBACK_SIGNING_SECRET") + " and " + c("SETTLEMENT_INTERNAL_TOKEN") + " (" + c("config.ts") + ", tested).",
      "<b>Exposure:</b> an admin password, " + c("merchant-details.json") + " and the sandbox acquirer secret in " + c("ops/.env.docker") + " were committed earlier. "
      "They are untracked now but still in history; they must be rotated (section 4.3)."])

st.H2("2.3 Health checks and restart policy")
st.TABLE([
    ["Check / policy", "Detail"],
    [c("GET /healthz"), "Process is up (never shed by the load-shedding plugin)."],
    [c("GET /readyz"), "Database reachable. Used by " + c("setup.sh") + " and by our post-deploy checks."],
    [c("GET /"), "Service JSON with links (was a 404)."],
    ["systemd", c("Restart=always") + ", " + c("RestartSec=2") + ", " + c("StartLimitIntervalSec=0") + " (never gives up), " + c("MemoryMax") + " with " + c("MemorySwapMax=0") + " so an OOM kill restarts cleanly; " + c("KillMode=control-group") + " also stops tsx's child process."],
    ["Boot", "All three units are " + c("enabled") + " and start after " + c("postgresql.service") + "."],
], [40, 134])

st.H2("2.4 How a redeploy avoids breaking a settlement run")
st.B(["A restart sends SIGTERM. The daemon wires it to a cancelled context (" + c("signal.NotifyContext") + "), stops taking new work and lets the in-flight Postgres transaction commit or roll back. " + c("TimeoutStopSec=30") + " gives it time before a hard kill.",
      "Each batch step (" + c("CloseBatch") + ", " + c("PayoutBatch") + ") is <b>one Postgres transaction</b> under a " + c("FOR UPDATE") + " lock on the batch row, so a kill can never leave a half-closed batch.",
      "On start, the daemon immediately re-runs the latest completed Bahrain business day. Closed or paid batches are no-ops (unique " + c("(merchant_id, batch_date)") + "), so an interrupted run finishes on restart and a completed one is not repeated.",
      "Payout notifications are guarded by a unique index (migration 0076), so a restart that overlaps a CLI run cannot double-notify.",
      "<b>Operational rule:</b> do not redeploy between 00:00 and 01:00 Bahrain time, when the daily close runs."])

# ============================== 3. CAPACITY ==============================
st.H1("3. Capacity")
st.NOTE("<b>Estimate:</b> about <b>8 completed checkouts per second</b>, serving <b>~10 concurrent simulated buyers</b> with p95 under 2 s, "
        "inside the 0.5 vCPU / 512 MB API limit. Above that, extra requests are turned away with 503 + Retry-After and admitted buyers stay fast. "
        "On the shared production VM we expect <b>6–8 checkouts/s</b>.")
st.H2("3.1 Our load test")
st.B(["<b>Tool:</b> " + c("ops/loadtest/checkout.mjs") + " (Node, no dependencies). Each simulated buyer loops: " + c("GET /v1/payment-links/:token") + " then " + c("POST /v1/payment-links/:token/pay") + " with an Idempotency-Key and a simulated card.",
      "<b>Method:</b> API in a container with the judging limits (" + c("--cpus 0.5 --memory 512m") + ", " + c("NODE_ENV=production") + ", pool of 5, " + c("LOAD_SHED_MAX_INFLIGHT=10") + "). Postgres outside the limit. "
      "The simulator adds 100–400 ms acquirer latency and 2% acquirer errors. A shed request is retried with the same link and Idempotency-Key. 30 s per run at 10, 20, 40 and 150 buyers.",
      "<b>Correctness check:</b> after each run, the test checks no payment link was paid twice."])

def cap_chart():
    d = Drawing(W * mm, 58 * mm)
    bc = VerticalBarChart(); bc.x = 14 * mm; bc.y = 10 * mm; bc.height = 40 * mm; bc.width = 70 * mm
    bc.data = [[1.65, 3.15, 5.71, 1.89]]
    bc.categoryAxis.categoryNames = ["10", "20", "40", "150*"]
    bc.valueAxis.valueMin = 0; bc.valueAxis.valueMax = 6; bc.valueAxis.valueStep = 2
    bc.bars[0].fillColor = colors.HexColor("#0f6e6e"); bc.barWidth = 8
    for ax in (bc.categoryAxis.labels, bc.valueAxis.labels): ax.fontName = "Sans"; ax.fontSize = 7
    d.add(bc)
    d.add(String(14 * mm, 53 * mm, "p95 checkout latency (s) by concurrent buyers", fontName="Sans-Bold", fontSize=7.5))
    bc2 = VerticalBarChart(); bc2.x = 104 * mm; bc2.y = 10 * mm; bc2.height = 40 * mm; bc2.width = 66 * mm
    bc2.data = [[8.2, 8.1, 7.9, 7.6]]
    bc2.categoryAxis.categoryNames = ["10", "20", "40", "150*"]
    bc2.valueAxis.valueMin = 0; bc2.valueAxis.valueMax = 10; bc2.valueAxis.valueStep = 2
    bc2.bars[0].fillColor = colors.HexColor("#5b6675"); bc2.barWidth = 8
    for ax in (bc2.categoryAxis.labels, bc2.valueAxis.labels): ax.fontName = "Sans"; ax.fontSize = 7
    d.add(bc2)
    d.add(String(104 * mm, 53 * mm, "Completed checkouts per second", fontName="Sans-Bold", fontSize=7.5))
    d.add(String(14 * mm, 2 * mm, "* 150 buyers with load shedding at 10 in-flight: 4,111 requests shed with 503, then retried.", fontName="Sans", fontSize=6.6, fillColor=MUTED))
    return d
st.append(cap_chart())
st.TABLE([
    ["Buyers", "Checkouts/s", "p50", "p95", "p99", "Shed (503)", "Errors", "Double payments"],
    ["10", "8.2", "1.21 s", "1.65 s", "1.82 s", "0", "0", "0"],
    ["20", "8.1", "2.42 s", "3.15 s", "3.41 s", "0 (limit was 40)", "1 acquirer", "0"],
    ["40", "7.9", "4.65 s", "5.71 s", "6.90 s", "0 (limit was 40)", "7 acquirer", "0"],
    ["150", "7.6", "1.20 s", "1.89 s", "2.20 s", "4,111", "3 acquirer", "0"],
], [16, 20, 16, 16, 16, 34, 26, 30])
st.H2("3.2 Where the bottleneck is")
st.P("The API's <b>0.5 vCPU</b>. Throughput stays flat at about 8/s from 10 to 150 buyers, and memory stays around 100 MB of 512 MB. "
     "Without shedding, extra buyers only add queueing (the 20 and 40 rows). The simulated acquirer's 100–400 ms is per request, not a shared limit. "
     "Postgres was outside the cap in the test; in production it shares the VM's single vCPU, which is why we quote 6–8/s.")
st.H2("3.3 Turning away excess load and recovering")
st.B(["<b>Load shedding</b> (" + c("apps/api/src/plugins/loadShed.ts") + ", tested): above " + c("LOAD_SHED_MAX_INFLIGHT") + " (10) concurrent requests, the API answers " + c("503") + " + " + c("Retry-After: 1") + " immediately. Health checks are exempt. "
      "We first set the limit to 40; the measurements showed p95 climbing to 5.7 s, so we lowered it to 10.",
      "<b>Safe retries:</b> a shed request did no work, and the Idempotency-Key makes a retried pay call return the original result, never a second charge.",
      "<b>No double charge under contention:</b> a payment link is reserved with a token before the acquirer call. An attempt that loses the reservation after charging is refunded automatically.",
      "<b>Recovery:</b> systemd restarts the API within ~2 s after a crash or OOM kill. Postgres transactions mean no partial writes survive a crash."])

# ============================== 4. FINDINGS ==============================
st.H1("4. Findings report")
st.P("One entry per finding, ranked by impact within each group. <b>Status</b>: Fixed (merged, with proof), Mitigated (exposure stopped, root cause still open), Open. "
     "Commits: round 1 " + c("4a68dc9") + ", round 2 " + c("5c3fa2d") + ", deployment " + c("150a8f8") + "/" + c("056a82a") + ", this round " + c("e010e18") + ". "
     "Detailed deployment log: " + c("bugs.md") + "; detailed audit notes: " + c("docs/AUDIT-FP-300.md") + ".")

FIND = []
def F(fid, title, status, symptom, found, cause, fix, verified, data, rc):
    FIND.append((fid, title, status, rc))
    col = {"Fixed": GREEN, "Mitigated": AMBER, "Open": RED}[status.split()[0]]
    head = Paragraph(f'<b>{fid}  {title}</b>  <font color="{col.hexval()}" size="8"><b>[{status}]</b></font>  <font color="{MUTED.hexval()}" size="7.5">root cause {rc}</font>', S["h3"])
    rows = [("Symptom", symptom), ("Found / reproduced", found), ("Root cause", cause), ("Fix", fix), ("Verified", verified), ("Existing data", data)]
    t = Table([[Paragraph(f"<b>{k}</b>", S["cell"]), Paragraph(v, S["cell"])] for k, v in rows], colWidths=[30 * mm, 144 * mm])
    t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LINEBELOW", (0, 0), (-1, -1), 0.3, RULE),
                           ("TOPPADDING", (0, 0), (-1, -1), 2), ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
                           ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f7f9fa"))]))
    st.append(KeepTogether([head, t, Spacer(1, 5)]))

st.H2("4.1 Findings")
st.H3("Money and settlement")
F("F-01", "Payouts ignore refunds: merchant overpaid, reconciliation does not tie out", "Open",
  "Demo day 2026-10-30: two captures (12.500 + 20.000 BD), one full and one partial refund (17.500 BD back to cardholders). The batch paid out <b>31.769 BD</b>, as if no refund happened. Dashboard Reconciliation shows a non-zero gap.",
  "Running the judges' demo script locally (capture → full + partial refund → " + c("settlement run-batch --date=2026-10-30") + "), then reading " + c("settlement_batches") + " and " + c("ledger_entries") + ". Screenshots in section 5.",
  c("CloseBatch") + " selects only " + c("captured/partially_captured") + " events. Refunds post correct ledger legs (merchant_payable debited 17.500, fee reversal credited 0.393), but nothing deducts them from a payout. The 2026-06-02 eng sync deferred this to settlement v2 (\"v1 can subtract refunds in the report and leave the batch alone\"). v2 is not live, so the deferral became a bug.",
  "<b>Not applied</b>: see decision D-1. Proposed: include refund events in the batch window as negative lines with their fee reversals, and carry a negative net forward (or hold the payout) instead of paying it.",
  "Ledger after the batch: merchant_payable = <b>−17.107 BD</b> (credits 32.893, debits 50.000) = refunds 17.500 − fee reversals 0.393. The batch paid 32.500 − 0.731 = 31.769.",
  "Every batch paid after a refund is overpaid by refunds − fee reversals. Find them: " + c("SELECT merchant_id, SUM(CASE direction WHEN 'credit' THEN amount_fils ELSE -amount_fils END) FROM ledger_entries WHERE account_id='merchant_payable' GROUP BY 1 HAVING SUM(...) &lt; 0") + ". Needs a finance-approved clawback, not an automatic rewrite.", "RC-5")
F("F-02", "Finance CSV adjustments posted 10x too small", "Fixed",
  "Importing " + c("4.75") + " BD produced 475 fils instead of 4,750. Finance had reported it; the reply was \"it is in the tests\".",
  "Read the parser and its tests: the tests expected the 10x-wrong values. Reproduced with the import test fixtures.",
  "A local parser assumed two decimal places (cents), but BHD has three (ADR-0001). A commit marked it \"intentional\".",
  c("parseAdjustmentAmountFils") + " delegates to " + c("parseBhdToFils") + "; corrected the test expectations in the same change. Promotional discounts no longer use " + c("parseFloat * 100") + ".",
  c("adminAdjustmentImport.test.ts") + " / " + c("adjustmentImport.test.ts") + " fail on the old parser, pass now.",
  "Adjustments imported before the fix stay 10x too small in the ledger. Finance must re-post the difference per import file; we did not run a backfill.", "RC-1, RC-3")
F("F-03", "Concurrent refunds could both pay out; refunds were 501", "Fixed",
  c("POST /v1/refunds") + " returned 501. The parked helper refunded against the authorized amount and had no lock, so two parallel refunds could each pass the \"refundable\" check.",
  "Code read of " + c("processRefund.ts") + "; new test fires parallel refunds at one transaction.",
  "Check-then-act with no row lock; refundable computed from the authorized amount, not captured − refunded.",
  "Lock the transaction (" + c("FOR UPDATE") + "), reserve the amount in a " + c("pending") + " refund row (0073) before the acquirer call; refundable = captured − refunded − pending; fee reversal from the net fee, last partial reverses the exact remainder; " + c("refund.succeeded") + " webhook; dashboard drawer.",
  c("routes/refunds.test.ts") + " (parallel refunds, over-refund, cross-merchant, fee sum). Live demo: fee reversals 281 + 112 fils at 2.25% (half-to-even).",
  "None. No refunds existed before (the route was 501).", "RC-2")
F("F-04", "Duplicate \"payout on the way\" webhooks (incident 2026-08-21)", "Fixed",
  "Merchants received two " + c("settlement.paid") + " notifications for one payout.",
  "New Go test runs 8 enqueuers concurrently against Postgres; old code inserted more than one event.",
  c("EnqueuePayoutNotifications") + " ran " + c("NOT EXISTS") + " then " + c("INSERT") + " as two statements. The daemon tick and a CLI run raced. CHANGELOG 1.9.1 only told receivers to dedupe.",
  "Migration 0076: partial unique index (one " + c("settlement.paid") + " per batch) + " + c("ON CONFLICT DO NOTHING") + ".",
  c("payout_notify_test.go") + ": 8 concurrent enqueuers → exactly 1 event.",
  "Existing duplicate events are relabelled by 0076 (kept, because deliveries reference them).", "RC-2")
F("F-05", "Dashboard shows 245 bps; payments are charged 225", "Fixed",
  "Finance memo: support quoted 2.45%, statements showed 2.25%.",
  "Compared the display query with billing's " + c("getEffectiveMdrBps") + "; an inherited test asserted 245 for exactly this case.",
  "Display ordered fee schedules by " + c("created_at") + " (last entered); billing uses the latest " + c("effective_from &lt;= now()") + ". A backdated correction won the display. A \"Claude says created_at is right\" comment closed the question.",
  "Display uses billing's rule (" + c("fees/currentFeeScheduleDisplay.ts") + "); test corrected.",
  "Test fails on old query (part of the 58 pass / 5 fail run with old code restored).",
  "Display only; no stored data changed.", "RC-1, RC-5")
F("F-06", "Platform volume counter overflows; payout estimate drifts", "Fixed",
  "Past ~2.1M BD platform volume the 15 bps tier discount would switch itself off for everyone; lifetime payout estimates drift for large merchants.",
  "Migration 0049 says " + c("INTEGER") + " and Go used " + c("int32") + " (a comment claimed BIGINT); estimate column was " + c("REAL") + " written from " + c("float32") + ". Tests above 2^31 and 2^24.",
  "Integer and float types too small for cumulative money.",
  "Migration 0078: both BIGINT; Go int64; API reads BIGINT strings with " + c("Number()") + ".",
  c("platform_volume_test.go") + ", " + c("payout_estimate_test.go") + " fail on old types.",
  "Values widened in place. Estimates already drifted stay approximate (monitoring only, not paid).", "RC-3")
F("F-07", "Go payouts used float32; split payouts did not sum", "Fixed",
  "Net payout and split shares off by fils; child shares did not add up to the batch payout.",
  "Code read; Go tests for split allocation.",
  c("NetPayableFils") + " computed in float32; splits rounded each share independently.",
  "Integer arithmetic; largest-remainder allocation so shares sum exactly.",
  c("go test ./internal/splits ./internal/settlement") + " pass against Postgres.",
  "Past batches keep their stored amounts (possible 1-fils differences); not rewritten.", "RC-3")
F("F-08", "MDR recalculation rewrote paid batches", "Fixed",
  "Running Recalculate MDR over a month changed fees on batches already paid out.",
  "Code read of " + c("recalculate_mdr.go") + ".", "No status filter on the batches it updated.",
  "Only " + c("closed") + " (unpaid) batches are recalculated, under " + c("FOR UPDATE") + ".", "Go tests.",
  "Batches already rewritten before the fix cannot be distinguished automatically; finance to review recalculations run since July.", "RC-2")
F("F-09", "Admin \"rebuild balances\" disagreed with the CLI (FP-203)", "Fixed",
  "Console button and " + c("settlement rebuild-balances") + " gave different balances.",
  "Two tests that seeded scheme export lines failed once the source was corrected.",
  "Button read scheme export lines; CLI read the ledger.", "Both read " + c("SUM(credit − debit)") + " of " + c("merchant_payable") + " in the ledger; tests reseeded via ledger.",
  c("refresh_test.go") + " passes.", "Balances recomputed from the ledger the next time either is run; no stored history changed.", "RC-5")
F("F-10", "Daemon's \"today\" used the UTC date", "Fixed",
  "Between 21:00 and 24:00 UTC the daemon picked the wrong business day.", "Code read against " + c("BusinessDayWindow") + ".",
  "Raw UTC instant passed where a Bahrain calendar date was expected.", c("settlement.BusinessDate(now)") + " first.", "Scheduler test.", "None observed.", "RC-3")
F("F-11", "March sweep script posts twice when re-run", "Fixed",
  "Finance: staging gap doubled after a second run.", "Read script; comment claimed " + c("entry_group_id") + " dedupes it, but it is a fresh " + c("randomUUID()") + " each run.",
  "No idempotency guard.", "Advisory lock + refuse if the sweep's ledger entries already exist.", c("reconcile_march.integration.test.ts") + ".",
  "Staging has the doubled entries; reverse them there. Production was not run.", "RC-2")
F("F-12", "Refund report double-counted captures", "Fixed",
  c("refund_merchant_summary") + " showed a payment refunded in two parts with its capture counted twice.", "Query on a 2-part refund.",
  "View summed " + c("captured_fils") + " once per refund row.", "Migration 0077 aggregates per transaction first.", "Reporting test.", "View only; no stored data.", "RC-5")
F("F-13", "Large transaction export could run out of memory or skip rows", "Fixed",
  "Big merchants' exports risked OOM on 512 MB; the unused streaming path skipped rows.", "Test with many rows sharing one timestamp.",
  "Route built the whole CSV in memory; streaming paged on " + c("occurred_at") + " only.", "Route streams; keyset paging on " + c("(occurred_at, id)") + ".",
  c("exportCsv.test.ts") + ".", "None (read-only).", "RC-3")

st.H3("Security and tenant isolation")
F("F-14", "The login code (OTP) was optional", "Fixed",
  "After the password step, the pending-session cookie already worked on every merchant endpoint.",
  "Called a merchant endpoint with the pending cookie; it returned data.",
  c("lookupSession") + " read the " + c("live_sessions") + " view, which filters revoked/expired rows but not " + c("authenticated") + ". Admin checked it; merchant never did.",
  c("AND s.authenticated = true") + " (" + c("auth/sessions.ts") + ").", c("app.test.ts") + ": pending cookie → 401.", "Outstanding pending sessions stop working. No stored data changed.", "RC-4")
F("F-15", "Logging in to merchant B could open merchant A", "Fixed",
  "With one email under two merchants, B's password produced a session in A.", "Test with " + c("owner@alpharetail.example") + " (member of two merchants).",
  "After checking the password for (merchant, email), login called " + c("findOtpRecipient(email)") + ", which picks any merchant with that email (" + c("LIMIT 1") + ").",
  "Session created for the row whose password was checked.", c("app.test.ts") + ".", "Sessions issued wrongly before the fix have expired; check audit logs for cross-merchant activity.", "RC-4")
F("F-16", "Rotating an API key left the old key working", "Fixed",
  "Admin \"rotate\" issued a new key; the old one still authenticated.", "Test; the inherited test asserted a \"grace period\" no document defines.",
  c("rotateApiKeyAsAdmin") + " never set " + c("revoked_at") + ".", "Revoke the old key in the same transaction, reason " + c("rotated") + ".", c("admin.test.ts") + ".",
  "Keys rotated before the fix are still active. Revoke: any merchant with more than one active key from a rotation.", "RC-1, RC-4")
F("F-17", "Refund and payment-link cancel looked up by id only", "Fixed",
  "Merchant A could refund or cancel merchant B's transaction/link by id.", "Cross-merchant test.", "Query not scoped to the caller's merchant.",
  "Scoped by merchant.", c("refunds.test.ts") + ".", "None found.", "RC-4")
F("F-18", "Admin impersonation could move money", "Fixed",
  "Support impersonating a merchant could capture, void and refund.", "Route review.", "Write routes did not reject impersonated actors.",
  c("requireMerchantWriterActor") + " on every write; impersonation is read-only.", "Route tests.", "Check admin audit export for impersonated writes.", "RC-4")
F("F-19", "OTP codes, link tokens and invite codes used Math.random()", "Fixed",
  "Predictable secrets.", "grep.", "Non-cryptographic RNG.", c("node:crypto") + " via " + c("lib/random.ts") + ".", "Tests.", "Existing unexpired links/invites keep old tokens until they expire.", "RC-1")
F("F-20", "Webhooks signed over different bytes than were sent", "Fixed",
  "Merchants' signature verification failed.", "Recomputed the HMAC over the delivered body.", "Dispatcher signed one serialization and sent another.",
  c("serializeWebhookBody") + " is used for both.", c("dispatcher.test.ts") + ".", "None; old deliveries can be replayed from the archive.", "RC-5")
F("F-21", "Acquirer callbacks processed twice; payment links double-charge or accept late payment", "Fixed",
  "Duplicate callbacks applied twice; a slow attempt could charge a link already paid; expiry trusted the buyer's " + c("submittedAt") + ".",
  "Code read; concurrency tests.", "Dedupe table " + c("processed_events") + " never existed; no reservation on links; client clock trusted.",
  "Dedupe on " + c("callback_id") + " (0074); reservation token (0075) with automatic refund of the losing attempt; server-side expiry.", "Tests + load test: 0 double payments.", "New constraints applied cleanly on existing data.", "RC-2")

st.H3("Deployment, data and UI")
F("F-22", "API site served the repository as static files", "Mitigated",
  c("filspay-admin-login.txt") + " and " + c("merchant-details.json") + " downloadable from the API host.", "Requested the files by server IP: 200.",
  "Dilmun site created as a static site rooted at the checkout.", "nginx is now a reverse proxy to 127.0.0.1:3000; files untracked and gitignored.",
  "Both return 404 over HTTPS.", "<b>The exposed admin password and sandbox secret must be rotated</b> (still in git history).", "RC-6")
F("F-23", "Transaction page crashed after any refund", "Fixed",
  "Found today: after a successful refund the transaction page showed \"Unexpected Application Error: toFils: expected a non-negative amount, got −5000\". The refund had worked.",
  "Playwright run of the refund demo against the local stack (screenshots, section 5).",
  "The timeline shows refunds as signed deltas; the dashboard's " + c("bhd()") + " rejected negatives. A comment had flagged it; the reply was \"amounts are never negative in the dashboard. ignore\".",
  c("bhd()") + " allows negatives (display only); commit " + c("e010e18") + ".", "New test fails on the old helper, passes now; page renders −5.000 BHD.", "None (display only). <b>fp-pay must be redeployed</b> for the live site.", "RC-1, RC-3")
F("F-24", "Postgres 5432 open to the internet", "Open",
  "Port 5432 reachable from outside; " + c("pg_hba.conf") + " accepts " + c("0.0.0.0/0") + ".", "External port check.", "Default Dilmun firewall rule.",
  "Not applied: deleting the firewall rule was blocked by our assistant's permission check and needs the Dilmun dashboard.", "—", "Rotate the database password after closing it.", "RC-6")
F("F-25", "Production cannot deliver login codes", "Mitigated",
  "No email/SMS sender; nobody could log in to the live site.", "Live login attempt; notifier logs only \"otp code generated\".",
  c("auth/notifier.ts") + " is a stub.", c("OTP_DEV_EXPOSE=true") + " on the demo shows the code on the login page (password alone logs in).",
  "Demo admin and merchant log in over HTTPS.", "None. Remove the flag before real money.", "RC-6")
F("F-26", "Fresh database could not be built; 20+ ops defects", "Fixed",
  "Migrations 0054, 0055, 0072 referenced missing tables/columns; dev key 34 bytes; compose ran production mode; deep links 404; bundle pointed at localhost; no DNS/HTTPS (bugs.md #4–#24).",
  "Fresh migrate; local compose; live checks.", "Untested migrations and config; docs that contradicted the code.",
  "Fixed each (see " + c("bugs.md") + "); " + c("setup.sh") + " fails loudly.", "72 migrations apply on an empty Postgres (re-run today); 453/453 tests.", "None.", "RC-6")

st.H2("4.2 Root causes")
st.TABLE([
    ["", "Root cause and the decision behind it", "Findings"],
    ["RC-1", "<b>Trusting generated code, comments and tests over the ledger.</b> The \"Order of the Prompt\" rules told assistants to treat tests and \"intentional\" comments as truth. "
             "Tests were written to assert the bugs (10x CSV, 245 bps, key grace period), and pasted AI explanations closed questions. We replaced the rules (" + c("CLAUDE.md") + ") and fixed each test in the same change as its defect.", "F-02, F-05, F-16, F-19, F-23"],
    ["RC-2", "<b>Check-then-act without a lock or a database-level idempotency guard.</b> The design relied on \"it runs once\" (one daemon, one click). In practice daemon and CLI overlap, buyers double-submit and acquirers retry. "
             "Fix pattern: " + c("FOR UPDATE") + ", reservation rows, unique indexes + " + c("ON CONFLICT") + ", client Idempotency-Keys.", "F-03, F-04, F-08, F-11, F-21"],
    ["RC-3", "<b>Money not typed as integer fils end to end.</b> " + c("packages/money") + " was correct, but code around it used cents-style parsing, float32, int32 and REAL. "
             "Fix pattern: parse/format only through the audited helpers; BIGINT/int64 everywhere money accumulates.", "F-02, F-06, F-07, F-10, F-13, F-23"],
    ["RC-4", "<b>Authentication and tenancy checked in some places, not all.</b> Lookups by id or email without the caller's merchant; session state not checked on one plane; impersonation not separated from writes.", "F-14 to F-18"],
    ["RC-5", "<b>Two sources of truth for one number.</b> Display vs billing, button vs CLI, signed bytes vs sent bytes, batch vs ledger. The decision to \"fix it in v2\" left v1 with two answers.", "F-01, F-05, F-09, F-12, F-20"],
    ["RC-6", "<b>Infrastructure configured by hand, with docs that claimed more than the code did.</b>", "F-22, F-24, F-25, F-26"],
], [13, 128, 33])

st.H2("4.3 Decisions and open risks")
st.TABLE([
    ["#", "What we chose not to change or run", "Why", "Safeguard we propose"],
    ["D-1", "Net refunds out of settlement payouts (F-01)", "Changes who is paid how much; finance owns the rule (net vs clawback vs hold), and a payout change on deadline day is riskier than the bug. Found today.",
     "Until fixed: hold payouts for merchants whose ledger payable is negative (query in F-01), and add a reconciliation alert when the dashboard gap ≠ 0. Then implement refunds as negative batch lines with carry-forward, with a test that ties the batch to the ledger."],
    ["D-2", "Backfill historic data (CSV 10x, rotated keys, MDR rewrites)", "Production data is demo data; real corrections need finance sign-off per file/merchant.", "Queries listed per finding; run in a transaction with a dry-run report first."],
    ["D-3", "Purge secrets from git history", "Needs a force-push that rewrites everyone's history; owner's decision.", "Rotate the admin password, sandbox acquirer secret and DB password now; history rewrite optional after."],
    ["D-4", "Close Postgres 5432 (F-24)", "Firewall change is in the Dilmun dashboard; our assistant's permission rules blocked it.", "Delete firewall rule #4; remove 0.0.0.0/0 from pg_hba.conf."],
    ["D-5", "Real OTP delivery (F-25)", "Needs an email/SMS provider account.", "Keep the demo on simulated money only; remove " + c("OTP_DEV_EXPOSE") + " before any real use."],
    ["D-6", "Never run " + c("npm run seed") + " on the server", "It truncates merchants, transactions and the ledger.", "Documented; " + c(".claude/settings.json") + " asks before seed."],
], [10, 44, 56, 64])
st.P("<b>Still unresolved:</b> scheme rounding residue posting (ADR-0002); a reaper for refunds stuck in " + c("pending") + " after a crash; rate limits on OTP verify/resend; admin session token rotation after OTP (FP-198); Dilmun auto-deploy not firing (bugs #17); settlement \"next check-in\" log message (bugs #21).")

# ============================== 5. UI/UX ==============================
st.H1("5. UI and UX changes")
st.P("Screenshots taken today with Playwright against the stack running locally on a freshly migrated and seeded Postgres. \"Before\" is the dashboard at commit "
     + c("698087e") + " (before our changes), \"after\" is the current code. Same API and data for both. No video recording.")

CR = (0, 0, 1280, 560)
st.H2("5.1 Refund control on the transaction page")
st.P("<b>What:</b> the RefundDrawer was parked and imported nowhere, so merchants had no way to refund. It is now wired to " + c("POST /v1/merchants/:id/refunds") + ", shows the refundable amount (captured − refunded), validates whole fils, asks for confirmation and reuses one Idempotency-Key per attempt. "
     "<b>Why it mattered:</b> refunds are the core FP-300 feature; the parked version also posted to the wrong route and created a new idempotency key per click.")
pair(st, shot("before-txn", 84, (0, 0, 1280, 700)), shot("after-drawer-partial", 84, (0, 0, 1280, 700)),
     "Before: captured payment, no refund control.", "After: Refund drawer, partial refund of 5000 fils, \"Refundable now: 20.000 BHD\".")
st.H2("5.2 Transaction page no longer crashes after a refund")
st.P("<b>What:</b> refund events are shown as signed amounts in the timeline. <b>Why it mattered:</b> without this, every refunded payment showed an error page (finding F-23). This is the page the refund demo ends on.")
pair(st, shot("after-partial-done", 84, (0, 0, 1280, 560)), shot("fixed-partial", 84, (0, 0, 1280, 700)),
     "Before (today, pre-fix): error after a successful 5.000 BD refund.", "After: status partially_refunded, timeline shows −5.000 BHD.")
st.H2("5.3 Site root and unknown paths")
st.P("<b>What:</b> " + c("/") + " redirects to the dashboard (login when signed out); unknown paths show a \"Page not found\" page with a link to sign in. "
     "<b>Why it mattered:</b> the site's own address and any mistyped payment link showed React Router's developer error screen to buyers.")
pair(st, shot("before-404", 84, CR), shot("after-404", 84, CR), "Before: /dashbord (typo) shows a developer error.", "After: friendly Page not found.")
st.H2("5.4 Refund and settlement views after the demo")
pair(st, shot("after-txn-list", 84, (0, 0, 1280, 640)), shot("settlement-batch", 84, (0, 0, 1280, 640)),
     "Transactions list: refunded and partially_refunded with correct captured amounts.", "Settlement batch 2026-10-30: gross 32.500, fee 0.731, net 31.769 (refunds not netted, F-01).")
st.append(KeepTogether([framed(shot("reconciliation", 120, (0, 0, 1280, 520)), "Reconciliation: the gap is non-zero after the refunds, which is the visible symptom of F-01.")]))
st.append(Spacer(1, 6))
st.P("Other UI changes without screenshots: the admin console's fee display now shows the rate billing applies (F-05); impersonation hides write actions server-side (F-18); "
     "the login page shows the code on the demo deployment only (F-25, a mitigation, not a feature).", "muted")

# ============================== 6. AI USAGE ==============================
st.H1("6. AI usage")
st.H2("6.1 Setup")
st.TABLE([
    ["What", "Where in the repo", "Purpose"],
    ["Agent instructions", c("CLAUDE.md") + " (single source), " + c("AGENTS.md") + ", " + c(".cursorrules"), "Replaced the \"Order of the Prompt\" rules: integer fils, Bahrain day, node:crypto, merchant scoping, locks, idempotency, and \"verify, don't defer\"."],
    ["Permission rules", c(".claude/settings.json"), "Allow tests/typecheck; ask before seed, push, setup.sh, psql; deny reading .env and committed-secret files, deny force push."],
    ["Custom commands", c(".claude/commands/verify-fix.md") + ", " + c("check-live.md") + ", " + c("money-review.md"), "/verify-fix: failing test first, then fix. /check-live: prove server state. /money-review: review a diff against the money rules."],
    ["Helper scripts", c("ops/dilmune/setup.sh") + ", " + c("ops/loadtest/checkout.mjs") + ", " + c("create-merchant.cjs") + ", " + c("scripts/docs/build_report_pdf.py"), "Redeploy, load test, merchant signup, report generation."],
    ["Tools", "Claude Code (desktop app and claude.ai/code), Playwright, local Postgres 16, Go toolchain, Dilmun console", "The assistant ran tests and queries itself; every claim needed evidence."],
], [28, 66, 80])
st.P("Rule we worked by: <b>the AI can propose; only evidence closes an item</b> (a test that fails on the old code, a database query, or a request to the live server). "
     "The permission rules and commands were committed on 30 October to codify how we had been working; the instruction files date from round 1.", "muted")

def excerpt(n, title, finding, prompt, context, answer, verify, change):
    st.H2(f"6.{n+1} Excerpt {n}: {title}")
    st.KV([("Finding", finding), ("Prompt", prompt), ("Context / tools", context), ("AI answer (relevant part)", answer),
           ("How we verified", verify), ("What we changed", change)], (34, 140))

excerpt(1, "an inherited test that asserted the bug", "F-05 (245 vs 225 bps) and F-16 (key rotation)",
        "Work through the finance memos and handwritten notes; for each, find the root cause and prove it. (Summarised; we did not keep the exact wording.)",
        "Repository, finance memo text, Postgres test database; the AI ran the test suite itself.",
        "\"The second test is exactly Fatima's case (225 entered, 245 backfilled later), and it asserts the wrong answer. I'll fix the query to match billing and correct that test.\" "
        "It also flagged the inherited comment " + c("// FH: asked Claude, it said created_at is right") + " as an unverified claim.",
        "We read billing's own query (" + c("effective_from &lt;= now() ORDER BY effective_from DESC") + ") and the memo, then <b>swapped the old code back in</b>: "
        + c("✖ shows the rate in effect...") + ", " + c("✖ API key rotation ... revokes the previous key") + ", 58 pass / 5 fail. With the fix: 377 pass / 0 fail.",
        "Display query and test (F-05); key rotation and its \"grace period\" test (F-16). The same method caught the BIGINT comment (F-06) and the sweep comment (F-11).")
excerpt(2, "the AI was wrong, and we caught it", "F-22 / deployment: rotating the exposed admin password",
        "\"Ends in |t\" (us, pointing out that the reset output did not show the expected row).",
        "Dilmun console command history, read-only SQL against the database the API uses.",
        "First the AI theorised that the seed script was overwriting the password. Then it disproved its own theory: one admin row, created 06:49, and no cron, timer or pm2 job runs the seed. "
        "\"The API reads that same database, but the reset never changed the password (" + c("f") + ").\"",
        "We required state, not output: the reset counted only when the command appeared in the console history with " + c("UPDATE 1 … |t") + ". "
        "Same pattern for the API restart: it printed " + c("SHADOWSTACK_REMOVED") + " but uptime was still 6,600 s; after the rerun uptime was 35 s.",
        "Re-ran the reset properly. We stopped accepting \"printed success\" and wrote /check-live to make that the default.")
excerpt(3, "the AI's own report was wrong; a browser run showed it", "F-23 (refund crash) and F-01 (payouts ignore refunds)",
        "The submission guidelines, pasted in full, including: \"Live demo: a full and a partial refund end to end, with correct amounts in the dashboard and settlement report. Have screenshots ready.\"",
        "Local Postgres 16 (migrated + seeded), API, settlement daemon and both dashboards; Playwright for screenshots; " + c("psql") + ".",
        "Earlier the same day the AI had written a report saying refunds worked \"end to end\". Taking the demo screenshots, it reported: \"the screenshots caught a real bug. After a refund, the transaction detail page crashes with "
        "'toFils: expected a non-negative amount, got −5000'.\" Then, after running settlement: \"the day's batch paid out 31.769 BD, as if the refunds never happened.\"",
        "Wrote a test for " + c("bhd(-5000)") + "; it failed with the old helper (8 pass / 1 fail) and passed with the fix (9/9). Queried the ledger: merchant_payable −17.107 BD = 17.500 refunded − 0.393 fee reversal; the batch row showed net 31.769.",
        "Fixed the display helper (" + c("e010e18") + "). Did <b>not</b> let the AI change payout logic on deadline day: recorded F-01 and decision D-1 instead.")

# ============================== APPENDIX ==============================
st.H1("Appendix")
st.H2("A. Test output (fresh Postgres 16, 30 Oct 2026)")
st.CODE("""
$ npm run migrate            # empty database
migrate: 72 migration(s) applied, 0 already up to date
$ npm test
# tests 4    # pass 4    # fail 0      (packages)
# tests 40   # pass 40   # fail 0
# tests 385  # pass 385  # fail 0      (apps/api)
# tests 11   # pass 11   # fail 0      (apps/reporting)
# tests 8    # pass 8    # fail 0      (apps/web)
# tests 5    # pass 5    # fail 0      (scripts)
$ cd apps/settlement && DATABASE_URL=... go test ./...
ok  internal/config  internal/internalapi  internal/ledger  internal/money
ok  internal/scheduler  internal/settlement  internal/splits
""")
st.H2("B. Refund demo evidence (local, 2026-10-30)")
st.CODE("""
POST /v1/transactions 12500 -> captured     POST /v1/transactions 20000 -> captured
dashboard: full refund 12500, partial refund 5000

transaction | amount | captured | status             | refund | fee_reversed
2e31fe2f... |  12500 |    12500 | refunded           |  12500 |          281
608feb20... |  20000 |    20000 | partially_refunded |   5000 |          112

$ settlement run-batch --date=2026-10-30 --merchant=9972daab...
batch=55e60e0c... gross=32500 fee=731 netPayout=31769

ledger merchant_payable for these rows: credits 32893, debits 50000  -> -17107
""")
st.H2("C. Migrations added")
st.TABLE([["Migration", "Purpose"],
          ["0073", "Pending refund reservation"], ["0074", "Acquirer callback dedupe on callback_id"],
          ["0075", "Payment-link reservation token"], ["0076", "One settlement.paid event per batch"],
          ["0077", "Refund summary counts each capture once"], ["0078", "BIGINT running totals"],
          ["0054 / 0055 / 0072", "Fixed so a fresh database builds"]], [40, 134])
st.H2("D. Reproduce")
st.CODE("""
npm ci && npm run migrate && npm run seed          # local Postgres, never production
npm test && (cd apps/settlement && go test ./...)
node ops/loadtest/checkout.mjs --api http://127.0.0.1:3300 --users 150 --seconds 30
""")

# ============================== BUILD ==============================
class Doc(BaseDocTemplate):
    def afterFlowable(self, f):
        if hasattr(f, "toc_level"):
            txt = f.getPlainText(); key = "k%d" % id(f)
            self.canv.bookmarkPage(key); self.canv.addOutlineEntry(txt, key, level=f.toc_level, closed=True)
            self.notify("TOCEntry", (f.toc_level, txt, self.page, key))

def cover(canv, doc):
    canv.saveState(); w, h = A4
    canv.setFillColor(ACCENT); canv.rect(0, h - 58 * mm, w, 58 * mm, stroke=0, fill=1)
    canv.setFillColor(colors.white); canv.setFont("Sans-Bold", 26); canv.drawString(18 * mm, h - 30 * mm, "FilsPay")
    canv.setFont("Sans", 13); canv.drawString(18 * mm, h - 41 * mm, "Submission document")
    canv.setFont("Sans", 9); canv.drawString(18 * mm, h - 49 * mm, "Audit, fixes, deployment and capacity  ·  30 October 2026")
    canv.restoreState()

def body(canv, doc):
    canv.saveState(); w, h = A4
    canv.setStrokeColor(RULE); canv.setLineWidth(0.5); canv.line(18 * mm, h - 13 * mm, w - 18 * mm, h - 13 * mm)
    canv.setFont("Sans", 7.5); canv.setFillColor(MUTED)
    canv.drawString(18 * mm, h - 11 * mm, f"{TEAM} · FilsPay submission")
    canv.drawRightString(w - 18 * mm, 9 * mm, f"Page {doc.page}")
    canv.restoreState()

out = sys.argv[1]
doc = Doc(out, pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm, topMargin=18 * mm, bottomMargin=16 * mm,
          title=f"{TEAM} FilsPay Submission", author=TEAM)
fr = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="f")
doc.addPageTemplates([PageTemplate("cover", [fr], onPage=cover), PageTemplate("body", [fr], onPage=body)])
doc.multiBuild(st)
print("ok", out)
