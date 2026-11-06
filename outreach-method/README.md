# Outreach Method

Kairo's outreach: Instagram DMs + cold email to owner-operated beauty businesses.
The method itself lives in `.claude/skills/email-outreach/SKILL.md`.

- `instagram/`: `leads.csv` (30) + `leads-2.csv` (20 more) DM leads, and the recommended @kairo profile mockup
- `campaigns/2026-11-06/`: first email campaign
  - `build.py`: every draft in one reviewable place (`python3 build.py` regenerates `leads.json`)
  - `leads.json`: 20 leads with offer, evidence, subject and body
  - `sent.json`: Gmail thread ids, follow-up date, reply status
- `suppression.txt`: anyone who opts out. Never email them again.

## Campaign 1 (Fri 6 Nov 2026)
20 sent, 0 bounces. 15 booking offers, 5 website offers. Every address passed a Hunter SMTP check;
2 failed and were dropped (Merci Nail Campsie, Sharps Barber Crows Nest).
Bump to non-responders scheduled for Wed 11 Nov, 10:30am Melbourne.

## Campaign 2 (Fri 6 Nov 2026, afternoon)
20 sent, 0 bounces, in `campaigns/2026-11-06b/`. 5 booking, 15 website (free Square/Wix pages).
New cities: Hobart, Canberra, Perth, Brisbane, Adelaide Hills. All 24 candidates passed Hunter; 4 dropped on fit
(shared hub, already has own domain, no location, inactive since early 2025). Gilded Nail Designs dropped: closed July 2025.
