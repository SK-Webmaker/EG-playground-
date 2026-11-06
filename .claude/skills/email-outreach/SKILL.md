---
name: email-outreach
description: Kairo's cold email outreach system for small beauty businesses (hair, nails, lashes, brows, barbers, MUAs). Use when asked to find businesses to email, validate emails, draft outreach, send a campaign, or run follow-ups for Kairo booking software or website builds.
---

# Email outreach (Kairo)

One job: get a solo beauty owner to **reply**. Not to buy. A reply means they read it, it trains Gmail that we're wanted, and it opens a conversation Sachi can close.

## Who we are (never promise beyond this)
- **Sender:** Sachi, Kairo. Gmail `kairobooking18@gmail.com` (Composio account `gmail_basoid-tun`, alias "business"). Site: kairobookings.com
- **Kairo booking:** $410 AUD once. No monthly fee, no commission. Own booking link, deposits via Stripe, reminders by email/SMS, waitlist, client cards, patch-test + consent records, iPhone app. Setup + client import done with them. **Full refund within 14 days.**
- **Websites:** we build sites for beauty businesses. No published price, so don't quote one. Offer a free homepage mockup instead.

## Pick booking or website (one offer per email, never both)
| What you see | Send |
|---|---|
| Books by DM, email, call or text. No booking link | **Booking** |
| Has a booking tool but the "website" is a free page (wixsite.com, sites.google.com, square.site, setmore, fresha-only) or is out of date (old address, stale info) | **Website** |
| Has both a real site and online booking | Skip |

## Lead rules (all must pass)
1. **Owner reachable:** solo or tiny team. Owner's first name is known where possible. Gmail/Outlook addresses on solo businesses usually go straight to the owner.
2. **Email is conspicuously published** by the business (bio, site, captions). Never guess or enrich private addresses. Skip anything that says "no unsolicited emails".
3. **Active:** a post within ~60 days (Instagram shortcode prefixes: `Df`=Nov 2026, `De`=Oct, `Dd`=Sep, `Dc`=Aug, `Db`=Jul). Dormant accounts are skipped.
4. **Deliverable:** Hunter `people/email-verify` (Firecrawl Alexandria, 10 credits) must return `status: valid`. Invalid = drop. accept_all/unknown = only if everything else is strong.
5. **Australia only** (Spam Act 2003 inferred-consent position, our market).

### Where to find them (Firecrawl search)
- `site:instagram.com "@gmail.com" "DM or email" <niche> <city>`: owners who book by email
- `site:wixsite.com` / `site:sites.google.com` / `site:square.site` + niche + city + "@gmail.com": weak sites
- Verify a site with a `json` scrape (location, how clients book, owner name, prices, problems).
- Instagram can't be scraped directly. Use search snippets for bio, follower count and post dates.

## What makes it convert (from the training videos + experience)
1. **Relevance beats volume.** Small, tight segments (<50) reply ~3x more than blasts. Every email opens with something only *they* could receive.
2. **Lead with an offer, not a meeting.** Give away the first step: a demo booking page built with their services, or a free homepage mockup. "Book a call" and free audits are not value.
3. **Reward every step.** The subject earns the open, line 1 rewards it (a real observation about them), and the P.S. (the most-read line after the subject) adds risk reversal or proof.
4. **Look like a real email.** Plain text, no images, no HTML, at most 1 link (the signature), no $ amounts or "sale/free!!!" in the subject. Under ~120 words. Mobile-short lines.
5. **Ask for a reply, not a click.** "Want me to put it together?" Replies lift inbox placement.
6. **Two touches only.** One email + one bump 3-5 days later, then stop. A non-responder later gets a *new angle*, not a third chaser.
7. **Easy opt-out.** Makes us look human and protects the inbox. Honour it forever.
8. **Timing:** Tue-Thu, 10am-12pm or 1-3pm in *their* timezone. Max ~25 cold sends/day from this Gmail, paced in small batches.
9. **Humans close.** I find, verify, draft and send. Sachi handles replies fast (call or reply same day). Speed to contact is the biggest conversion lever.

## Voice (don't sound like AI)
- Write like Sachi typing on a phone: short, warm, Australian, specific. Contractions. One idea per line.
- Banned: "I hope this finds you well", "I came across your", "game-changer", "elevate", "streamline", "take your business to the next level", "I'd love to hop on a call", em-dash chains, triple-adjective lists, exclamation spam.
- Never invent facts. Every observation must come from their page. If unsure, leave it out.

## Templates (fill, then rewrite line 1 by hand for every lead)

**Booking** (subject: lowercase, 2-5 words, about *their* thing, e.g. `your email bookings`)
```
Hi {first_name},

{observation from their page, e.g. "Saw bookings are email-only (no DMs) on your page."}
{their pain in one line, e.g. "Every 'what times have you got?' is 3 or 4 emails before anyone's actually in the book."}

I make Kairo, a booking system for salons. Rather than pitch it, I'll just build you a demo booking page with your own services and times, so you can click through it like a client would.

Want me to put it together?

Sachi
Kairo · kairobookings.com

P.S. No monthly fee or commission, it's a one-off. And if it's not right within 14 days you get every cent back.

Not for you? Just reply "no thanks" and I won't email again.
```

**Website**
```
Hi {first_name},

{specific site problem, e.g. "Your Instagram says you've moved to St Leonards, but your website still lists the Surry Hills address."}
{consequence in one line}

I build websites for hairdressers and beauty businesses. Happy to mock up a new homepage for you for free: {2-3 specifics, e.g. "new address, your colour work, a proper Book button"}. If you don't like it, you've lost nothing.

Want me to send it through?

Sachi
Kairo · kairobookings.com

Not for you? Just reply "no thanks" and I won't email again.
```

**Bump (day 3-5, same thread, only if no reply)**
```
Hi {first_name}, just floating this back up in case it got buried. Happy to put the {demo page / mockup} together either way, it takes me about 20 minutes.

Sachi
```

## Run it
1. Find candidates → verify site/activity → Hunter verify → write `outreach-method/campaigns/<date>/leads.json` (business, email, city, offer, evidence, source URL, subject, body).
2. Re-read every draft against the voice rules and the facts in the evidence column.
3. Send with Composio `GMAIL_SEND_EMAIL` (`account: gmail_basoid-tun`, `is_html: false`, `include_signature: false`), 4-5 per call. Log message/thread ids to `sent.json`.
4. Bump day: `GMAIL_FETCH_EMAILS` for replies first (`from:<lead>`). Replied → hand to Sachi. "no thanks"/unsubscribe → add to `outreach-method/suppression.txt`. Silent → send the bump as a reply in-thread (`GMAIL_REPLY_TO_THREAD`).
5. Never email anyone in `suppression.txt`. Never email the same business twice in one campaign.

## Compliance (Spam Act 2003 / Privacy Act)
Only conspicuously published business addresses, relevant to their business, no "no unsolicited email" notice. Every email identifies Sachi + Kairo + site and has a working reply opt-out, honoured within 5 business days (we do it immediately). See `COMPLIANCE.md`.
