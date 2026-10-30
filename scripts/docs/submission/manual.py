import sys, os
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, PageBreak, Table, TableStyle,
                                KeepTogether, NextPageTemplate, Image)
from reportlab.platypus.tableofcontents import TableOfContents
import common
from common import Story, S, c, INK, MUTED, ACCENT, RULE, GREEN, RED, AMBER

common.SHOTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mshots")
from common import shot

MERCHANT_SITE = os.environ.get("FP_MERCHANT_SITE", "fp-merchants-tzakir.dilmune.app")
ADMIN_SITE = "fp-admin-tzakir.dilmune.app"

# friendlier, larger type for this guide
S["body"].fontSize = 10.2; S["body"].leading = 14.6
S["bullet"].fontSize = 10.2; S["bullet"].leading = 14.2
S["h1"].fontSize = 20; S["h1"].leading = 25
STEP = ParagraphStyle("step", fontName="Sans", fontSize=10.2, leading=14.4, textColor=INK)
STEPN = ParagraphStyle("stepn", fontName="Sans-Bold", fontSize=13, leading=16, textColor=colors.white, alignment=1)

st = Story()
from reportlab.platypus import CondPageBreak
_h1 = st.H1
def _H1(t):
    st.append(CondPageBreak(70 * mm)); _h1(t)
st.H1 = _H1

def box(kind, text):
    colr = {"TIP": ("#e6f2f2", ACCENT), "WATCH OUT": ("#fbe9e7", RED), "REMEMBER": ("#fdf3e1", AMBER), "TECH STUFF": ("#eef0f3", MUTED)}[kind]
    t = Table([[Paragraph(f'<font color="{colr[1].hexval()}"><b>{kind}</b></font><br/>{text}', S["body"])]], colWidths=[174 * mm])
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), colors.HexColor(colr[0])), ("LINEBEFORE", (0, 0), (0, -1), 3, colr[1]),
                           ("LEFTPADDING", (0, 0), (-1, -1), 9), ("RIGHTPADDING", (0, 0), (-1, -1), 9),
                           ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 4)]))
    st.append(KeepTogether([t, Spacer(1, 8)]))

def steps(items):
    rows = []
    for i, t in enumerate(items, 1):
        rows.append([Paragraph(str(i), STEPN), Paragraph(t, STEP)])
    tb = Table(rows, colWidths=[9 * mm, 165 * mm])
    ts = [("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (1, 0), (1, -1), 8), ("BOTTOMPADDING", (0, 0), (-1, -1), 5)]
    for i in range(len(rows)):
        ts.append(("BACKGROUND", (0, i), (0, i), ACCENT))
    tb.setStyle(TableStyle(ts)); st.append(tb); st.append(Spacer(1, 8))

def pic(name, crop, caption, w=150):
    img = shot(name, w, crop)
    t = Table([[img], [Paragraph(caption, S["muted"])]], colWidths=[w * mm])
    t.setStyle(TableStyle([("BOX", (0, 0), (0, 0), 0.6, RULE), ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                           ("ALIGN", (0, 0), (-1, -1), "CENTER")]))
    outer = Table([[t]], colWidths=[174 * mm]); outer.setStyle(TableStyle([("ALIGN", (0, 0), (-1, -1), "CENTER")]))
    st.append(KeepTogether([outer, Spacer(1, 8)]))

def two(a, b, ca, cb, crop_a, crop_b):
    def cell(n, cr, cap):
        t = Table([[shot(n, 84, cr)], [Paragraph(cap, S["muted"])]], colWidths=[84 * mm])
        t.setStyle(TableStyle([("BOX", (0, 0), (0, 0), 0.6, RULE), ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0)]))
        return t
    t = Table([[cell(a, crop_a, ca), cell(b, crop_b, cb)]], colWidths=[87 * mm, 87 * mm])
    t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 0)]))
    st.append(KeepTogether([t, Spacer(1, 8)]))

FORM = (330, 0, 950, 640)   # centred login/checkout forms
TOP = (0, 0, 1280, 620)

# =============================== COVER ===============================
st.append(Spacer(1, 120 * mm))
st.P(f'<font size="11" color="{MUTED.hexval()}">For shop owners, their staff, and the FilsPay team. No technical knowledge needed.</font>')
st.append(Spacer(1, 6))
st.TABLE([["You are…", "Read these chapters"],
          ["A shop owner or manager", "1, 2, 3, 4, 5, 6, 7, 8, 9, 12, 13"],
          ["Shop staff answering customer questions", "1, 2, 3, 4, 5, 6, 9, 12"],
          ["A buyer who received a payment link", "Chapter 6 only"],
          ["Your shop's web developer", "10 (and the tech boxes)"],
          ["FilsPay operations staff", "11, 12, 13"]], [80, 94])
st.append(NextPageTemplate("body")); st.append(PageBreak())

toc = TableOfContents()
toc.levelStyles = [ParagraphStyle("t0", fontName="Sans-Bold", fontSize=10, leading=15, textColor=INK),
                   ParagraphStyle("t1", fontName="Sans", fontSize=8.6, leading=11.5, leftIndent=14, textColor=MUTED)]
st.append(Paragraph("What's inside", S["h1"])); st.append(toc); st.append(PageBreak())

# =============================== 1 ===============================
st.H1("1. FilsPay in one minute")
st.P("FilsPay lets your shop <b>take card payments</b> and <b>see your money</b> in one place. You can:")
st.B(["send a customer a <b>payment link</b> (by WhatsApp, SMS or email) and they pay by card on their phone,",
      "see every payment, who paid and how much,",
      "<b>give money back</b> (a refund), in full or in part,",
      "see when FilsPay pays the money into your account (a <b>payout</b>)."])
st.H2("The three websites")
st.TABLE([["Website", "Who uses it", "What for"],
          [f"<b>fp-merchants</b><br/>{c(MERCHANT_SITE)}", "You and your staff", "Your shop's dashboard: payments, links, refunds, payouts."],
          [f"<b>Checkout page</b><br/>{c(MERCHANT_SITE + '/pay/…')}", "Your customers", "The page a customer opens from your payment link to pay."],
          [f"<b>fp-admin</b><br/>{c(ADMIN_SITE)}", "FilsPay staff only", "Approving shops, settlement and support tools."]], [60, 40, 74])
box("REMEMBER", "This version of FilsPay uses a <b>practice card system</b>. No real money moves and no real card is charged. "
    "Use it to learn and to test, not to sell to real customers yet.")

# =============================== 2 ===============================
st.H1("2. Five words you need to know")
st.TABLE([["Word", "What it means in plain English"],
          ["<b>Fils</b>", "Bahrain's smallest coin. <b>1 dinar (BD) = 1,000 fils.</b> Some FilsPay boxes ask for the amount in fils."],
          ["<b>Payment link</b>", "A web address you send to a customer. They open it and pay by card."],
          ["<b>Captured</b>", "The money has been taken from the customer's card. The sale is done."],
          ["<b>Refund</b>", "Giving money back to the customer's card. <b>Full</b> = all of it. <b>Partial</b> = some of it."],
          ["<b>Payout</b> (settlement)", "FilsPay adds up a day's sales, takes its fee, and pays you the rest."]], [38, 136])
st.H2("Turning dinars into fils (the only maths you need)")
st.P("Multiply dinars by 1,000. Or: take away the dot and make sure there are three numbers after where the dot was.")
st.TABLE([["You want to charge", "Type this many fils"],
          ["0.500 BD (half a dinar)", c("500")], ["1 BD", c("1000")], ["7.500 BD", c("7500")],
          ["12.250 BD", c("12250")], ["100 BD", c("100000")]], [87, 87])
box("WATCH OUT", "Typing <b>75</b> instead of <b>7500</b> charges <b>0.075 BD</b> (seventy-five fils), not 7.500 BD. Always check the BD amount FilsPay shows you before you press the button.")

# =============================== 3 ===============================
st.H1("3. Signing in")
st.H2("What you need")
st.B(["Your <b>Merchant ID</b>: a long code like " + c("9972daab-2c86-459f-9d78-3fe1be4e3280") + ". FilsPay gives it to you when your shop is set up. Keep it in your phone's notes.",
      "Your <b>email</b> and <b>password</b>.",
      "Access to the <b>one-time code</b> FilsPay sends you each time you sign in (a 6-digit number)."])
box("TIP", "Why the Merchant ID? One person can work for two shops with the same email. The ID tells FilsPay which shop you mean.")
st.H2("Step by step")
steps([f"Open <b>{MERCHANT_SITE}</b> in your browser. It takes you to the sign-in page.",
       "Type your <b>Merchant ID</b>, <b>Email</b> and <b>Password</b>, then press <b>Continue</b>.",
       "Type the <b>6-digit one-time code</b> into the box and press <b>Verify</b>.",
       "You are in. You land on the <b>Transactions</b> page."])
two("m-login-filled", "m-otp-filled", "Step 2: Merchant ID, email, password.", "Step 3: the one-time code.", FORM, FORM)
box("REMEMBER", "On the demo website the code appears on the screen (\"Development code\"). On a real system it will arrive by email or SMS instead. Never tell anyone your code, not even FilsPay staff.")
st.P("<b>Code didn't work?</b> Codes expire after a few minutes. Press <b>Resend code</b>, or <b>Start over</b>.")

# =============================== 4 ===============================
st.H1("4. A quick tour of your dashboard")
pic("m-transactions", (0, 0, 1280, 420), "The menu across the top. Your email, your role and your shop name are on the right.", 170)
st.TABLE([["Menu item", "What you'll find there"],
          ["<b>Transactions</b>", "Every payment. Click one to see its details or refund it."],
          ["<b>Payment links</b>", "Create links to send to customers, and see which ones were paid."],
          ["<b>Webhooks</b>", "For your web developer only (chapter 10). Owners and finance staff can open it."],
          ["<b>Settlement</b>", "Your payouts: how much FilsPay paid you, and for which day."],
          ["<b>Reconciliation</b>", "A check that every fils is accounted for. Mainly for your accountant."],
          ["<b>Overview</b>", "Summary charts: sales per day and your best-selling links."],
          ["<b>Log out</b>", "Always log out on a shared computer."]], [40, 134])

# =============================== 5 ===============================
st.H1("5. Seeing your payments")
st.P("Click <b>Transactions</b>. The newest payments are at the top.")
st.B(["<b>Status</b> tick boxes: show only some kinds of payment (for example, only refunded ones).",
      "<b>From / To</b>: pick dates.", "<b>Search</b>: type a reference (like an invoice number) to find one payment.",
      "Click the <b>date</b> on any row to open that payment."])
st.H2("What the statuses mean")
st.TABLE([["Status", "In plain English", "Do you have the money?"],
          ["authorized", "The card was approved, but the money isn't taken yet.", "Not yet"],
          ["captured", "Money taken. Sale complete.", "Yes"],
          ["partially_captured", "Only part of the approved amount was taken.", "The part taken"],
          ["voided", "Cancelled before the money was taken.", "No"],
          ["partially_refunded", "Some money was given back.", "The rest"],
          ["refunded", "All money was given back.", "No"],
          ["chargeback", "The customer's bank took the money back (a dispute).", "No; contact FilsPay"]], [38, 100, 36])

# =============================== 6 ===============================
st.H1("6. Getting paid with a payment link")
st.P("This is the easiest way to get paid without a card machine or a website.")
st.H2("Make a link")
steps(["Click <b>Payment links</b>, then <b>New payment link</b>.",
       "<b>Amount in fils</b>: for 7.500 BD type " + c("7500") + " (see chapter 2).",
       "<b>Reference</b> (optional): your invoice or order number, so you can find it later. Example: " + c("INV-1042") + ".",
       "<b>Description</b> (optional): what the customer is paying for. They will see it. Example: \"2 x Karak tea gift box\".",
       "<b>Expires at</b>: the last date and time the customer can pay.",
       "Press <b>Create payment link</b>."])
two("m-link-new", "m-link-detail", "Filling in a new link.", "The finished link. Press Copy link.", (0, 0, 900, 640), (0, 0, 1000, 640))
st.H2("Send it")
steps(["On the link's page, press <b>Copy link</b> next to <b>Checkout link</b>.",
       "Paste it into WhatsApp, SMS or email to your customer.",
       "When they pay, the link's status changes to <b>paid</b> and the payment appears under <b>Transactions</b>."])
st.TABLE([["Link status", "Meaning"],
          ["active", "Waiting for the customer to pay."], ["reserved", "The customer is paying right now. Wait a moment."],
          ["paid", "Done. You can't use this link again."], ["expired", "Time ran out. Make a new link."],
          ["canceled", "You cancelled it (button <b>Cancel payment link</b>)."]], [40, 134])
box("TIP", "One link = one payment. Need to charge three customers? Make three links.")
st.H2("What your customer sees")
st.P("Your customer opens the link on their phone or computer. They see your shop name, the amount and your description, type their card details and press <b>Pay</b>.")
two("b-checkout-filled", "b-checkout-done", "The customer fills in their card.", "Payment successful. They can screenshot this as a receipt.", FORM, FORM)
st.P("If something is wrong they see a clear message instead: <b>Link expired</b>, <b>Already paid</b>, <b>Payment link not found</b> (they mistyped it) or <b>card declined</b> (they can try another card).")
box("TECH STUFF", "Practice cards on the demo: any card number works, for example " + c("4242 4242 4242 4242") + ", any future date, any 3-digit CVV. "
    "Numbers ending " + c("0002") + " or " + c("0119") + " are always declined, so you can see what a decline looks like.")

# =============================== 7 ===============================
st.H1("7. Giving money back (refunds)")
box("WATCH OUT", "A refund <b>cannot be undone</b>. The money goes back to the customer's card. Check the amount twice.")
st.P("Only the shop's <b>owner</b> and <b>finance</b> users see the Refund button. Support staff can look but not refund.")
st.H2("Full refund (give everything back)")
steps(["Click <b>Transactions</b> and open the payment.",
       "Press <b>Refund</b>.",
       "Leave the amount box <b>empty</b>. Empty means \"refund everything that's left\".",
       "Press <b>Refund</b>, then <b>OK</b> on the \"Are you sure?\" question."])
st.H2("Partial refund (give some back)")
steps(["Open the payment and press <b>Refund</b>.",
       "Type the amount <b>in fils</b>. To give back 5.000 BD, type " + c("5000") + ". FilsPay shows <b>Refundable now</b>: the most you can give back.",
       "Press <b>Refund</b>, then <b>OK</b>."])
two("after-drawer-partial", "fixed-partial", "Typing 5000 fils (5.000 BD). Refundable now: 20.000 BD.",
    "Done: status partially_refunded, and −5.000 BHD in the timeline.", (0, 0, 1280, 700), (0, 0, 1280, 700))
st.P("You can do several partial refunds on one payment until the whole amount is back. FilsPay will never let you refund more than the customer paid, even if two people press the button at the same time.")
box("TIP", "FilsPay also gives back the matching part of its fee. Refund a whole 12.500 BD payment and the fee FilsPay charged on it comes back to you too.")

# =============================== 8 ===============================
st.H1("8. Your payouts (when you get your money)")
st.P("Every day, shortly after midnight Bahrain time, FilsPay adds up the previous day's captured payments, takes its fee, and pays you the rest. Each day's payout is called a <b>batch</b>.")
pic("m-settlement", (0, 0, 1280, 420), "Settlement: one row per day. Click a date to see which payments it includes.", 170)
st.TABLE([["Column", "Meaning"],
          ["Gross", "Total captured that day."], ["Fee", "FilsPay's fee."], ["Net payout", "What you receive: Gross − Fee."],
          ["Status", "<b>open</b> (day not finished), <b>closed</b> (added up, not paid yet), <b>paid</b> (sent to you)."]], [40, 134])
box("WATCH OUT", "<b>Known issue in this version:</b> payouts do not yet subtract refunds. If you refund a customer, that day's payout is still based on the full sale, "
    "so the <b>Reconciliation</b> page will show a difference (a \"gap\"). FilsPay's finance team settles this separately. If you see a gap after refunds, this is why. Tell FilsPay if you're unsure.")

# =============================== 9 ===============================
st.H1("9. Who can do what (roles)")
st.TABLE([["Role", "Can look", "Can make links", "Can refund", "Webhooks"],
          ["<b>Owner</b>", "Yes", "Yes", "Yes", "Yes"],
          ["<b>Finance</b>", "Yes", "Yes", "Yes", "Yes"],
          ["<b>Support</b>", "Yes", "No", "No", "No"]], [34, 35, 35, 35, 35])
st.P("Give your staff the smallest role they need. Someone who only answers customer questions should be <b>Support</b>.")

# =============================== 10 ===============================
st.H1("10. For your web developer")
st.P("Skip this chapter if you only use payment links. If your shop has its own website or app, your developer connects it to FilsPay.")
st.B(["<b>API key</b>: a password for computers. FilsPay gives one to your shop. Keep it secret, like a bank PIN.",
      "<b>Webhooks</b> (menu item): FilsPay sends your website a message when something happens, for example \"payment captured\" or \"refund succeeded\". Your developer adds the website address under <b>New endpoint</b>.",
      "Full technical details are in the FilsPay technical guide (" + c("docs/FilsPay-Report.pdf") + ", section 7.2)."])
box("TECH STUFF", "Every money request must send an " + c("Idempotency-Key") + " header. If the internet drops and your system sends the same request again with the same key, FilsPay will not charge twice. "
    "If FilsPay is very busy it answers " + c("503") + ": wait one second and try again with the <b>same</b> key.")

# =============================== 11 ===============================
st.H1("11. For FilsPay staff: the admin console")
st.P(f"Open <b>{ADMIN_SITE}</b>, sign in with your FilsPay email and password, then the one-time code. It works the same way as chapter 3, without a Merchant ID.")
pic("a-merchants", (0, 0, 1280, 470), "Merchants: every shop, its status, KYC (identity check) and fee rate.", 170)
st.TABLE([["Menu item", "What it's for", "Who"],
          ["<b>Merchants</b>", "Find a shop, check its profile, KYC and fee, approve or review it.", "All staff"],
          ["<b>Credits</b>", "Give a shop a credit. Needs a second person to approve.", "Finance"],
          ["<b>Settlement ops</b>", "Re-run a day's payout, rebuild balances. Every action is logged.", "Finance, super admin"],
          ["<b>Import adjustments</b>", "Upload finance's CSV sheet of corrections (amounts in BD).", "Finance"],
          ["<b>Webhook replay</b>", "Re-send a webhook a shop says it didn't receive.", "Support"]], [38, 110, 26])
box("WATCH OUT", "Settlement ops and adjustments move real money in a live system. Re-running a day that is already paid is safe (nothing happens twice), but <b>check the date and the shop</b> before you press Run.")
box("REMEMBER", "\"View as merchant\" (impersonation) is <b>read-only</b>. You can see what the shop sees, but you can't refund or capture for them.")

# =============================== 12 ===============================
st.H1("12. Something's wrong? Try this")
st.TABLE([["Problem", "What to do"],
          ["Sign-in says the details are wrong", "Check the Merchant ID (copy and paste it), the email and the password. Capital letters matter."],
          ["The one-time code doesn't work", "It may have expired. Press <b>Resend code</b>, or <b>Start over</b>."],
          ["I see \"Page not found\"", "The address was mistyped. Click <b>Merchant sign-in</b>, or check the link you were sent."],
          ["Customer says the link says \"expired\"", "Make a new link with a later <b>Expires at</b> time."],
          ["Customer says \"Already paid\"", "Good news: they paid. Check <b>Transactions</b>."],
          ["Customer's card was declined", "They should try another card or call their bank. Nothing was charged."],
          ["There is no Refund button", "You are signed in as <b>Support</b>, or the payment isn't captured, or it's already fully refunded."],
          ["Refund says the amount is too big", "You can refund at most the <b>Refundable now</b> amount. Some was already refunded."],
          ["Charged the wrong amount", "Refund it (chapter 7) and send a new link with the right amount."],
          ["Payout is less (or more) than expected", "Open the day under <b>Settlement</b> to see which payments it includes. See the refund note in chapter 8."],
          ["Website shows \"Service unavailable\" or is slow", "FilsPay is busy. Wait a few seconds and try again; nothing is charged twice."]], [62, 112])

# =============================== 13 ===============================
st.H1("13. Ten safety rules")
st.N(["Never share your password or one-time code. FilsPay will never ask for them.",
      "Never send card numbers by WhatsApp or email. Send a payment link instead.",
      "Log out on shared computers.",
      "Give staff the smallest role they need (chapter 9).",
      "Check the BD amount before creating a link or a refund.",
      "Refunds can't be undone. Check twice.",
      "Keep your API key secret. If it leaks, ask FilsPay to rotate it; the old key stops working at once.",
      "Use the reference box for invoice numbers, so every payment can be matched.",
      "Check the Settlement page each week against your bank statement.",
      "If something looks wrong with money, stop and contact FilsPay before trying to fix it."])

# =============================== CHEAT SHEET ===============================
st.H1("Cheat sheet")
st.TABLE([["I want to…", "Do this"],
          ["Sign in", f"{MERCHANT_SITE} → Merchant ID + email + password → Continue → code → Verify"],
          ["Get paid", "Payment links → New payment link → amount in fils → Create → Copy link → send"],
          ["Find a payment", "Transactions → Search (reference) or From/To dates"],
          ["Refund everything", "Transactions → open payment → Refund → leave empty → Refund → OK"],
          ["Refund part", "Transactions → open payment → Refund → type fils → Refund → OK"],
          ["See my payouts", "Settlement → click a date"],
          ["Convert BD to fils", "× 1,000 (7.500 BD = 7500 fils)"]], [44, 130])

# =============================== BUILD ===============================
class Doc(BaseDocTemplate):
    def afterFlowable(self, f):
        if hasattr(f, "toc_level") and f.toc_level == 0:
            txt = f.getPlainText(); key = "k%d" % id(f)
            self.canv.bookmarkPage(key); self.canv.addOutlineEntry(txt, key, level=0)
            self.notify("TOCEntry", (0, txt, self.page, key))

def cover(canv, doc):
    canv.saveState(); w, h = A4
    canv.setFillColor(ACCENT); canv.rect(0, h - 110 * mm, w, 110 * mm, stroke=0, fill=1)
    canv.setFillColor(colors.HexColor("#f2c14e")); canv.rect(0, h - 113 * mm, w, 3 * mm, stroke=0, fill=1)
    canv.setFillColor(colors.white)
    canv.setFont("Sans", 13); canv.drawString(20 * mm, h - 38 * mm, "FilsPay")
    canv.setFont("Sans-Bold", 38); canv.drawString(20 * mm, h - 58 * mm, "Made Easy")
    canv.setFont("Sans", 14); canv.drawString(20 * mm, h - 72 * mm, "The plain-English guide to taking payments,")
    canv.drawString(20 * mm, h - 80 * mm, "sending payment links and giving refunds")
    canv.setFont("Sans", 10); canv.drawString(20 * mm, h - 98 * mm, f"Merchant site: {MERCHANT_SITE}")
    canv.setFillColor(MUTED); canv.setFont("Sans", 8)
    canv.drawString(20 * mm, 14 * mm, "User manual · October 2026 · Screens shown are from the practice (demo) system.")
    canv.restoreState()

def body(canv, doc):
    canv.saveState(); w, h = A4
    canv.setStrokeColor(RULE); canv.line(18 * mm, h - 13 * mm, w - 18 * mm, h - 13 * mm)
    canv.setFont("Sans", 7.5); canv.setFillColor(MUTED)
    canv.drawString(18 * mm, h - 11 * mm, "FilsPay Made Easy · user manual")
    canv.drawRightString(w - 18 * mm, 9 * mm, f"Page {doc.page}")
    canv.restoreState()

out = sys.argv[1]
doc = Doc(out, pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm, topMargin=18 * mm, bottomMargin=16 * mm,
          title="FilsPay Made Easy: User Manual", author="FilsPay")
fr = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="f")
doc.addPageTemplates([PageTemplate("cover", [fr], onPage=cover), PageTemplate("body", [fr], onPage=body)])
doc.multiBuild(st)
print("ok", out)
