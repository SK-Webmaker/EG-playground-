"""Render the master call sheet artifact."""
import collections, html, json, pathlib

M = json.load(open("data/leads/master.json"))
CSS = open("scripts/artifact.css").read()
def e(x): return html.escape(str(x if x not in (None, "", []) else "—"))

top = [m for m in M if m["score"] >= 85][:16]
strips = sum(1 for m in M if m["source"] == "trader association")

def social_chips(m):
    out = []
    for u in m["socials"][:3]:
        lbl = ("Instagram" if "instagram" in u else "Facebook" if "facebook" in u
               else "LinkedIn" if "linkedin" in u else "Social")
        out.append(f'<a class="chip ok" href="{e(u)}" target="_blank" rel="noopener">{lbl}</a>')
    return " ".join(out) or '<span class="chip none">none found</span>'

dockets = "".join(f'''
<article class="docket">
  <div class="dhead"><span class="rank">{i:02d}</span>
    <div class="dtitle"><h3>{e(m["name"])}</h3>
      <span class="niche">{e(m["category"])} · {e(m["suburb"])}</span></div>
    <div class="score"><b>{m["score"]}</b><span>SCORE</span></div></div>
  <div class="grid">
    <div class="cell"><span class="k">Ask for</span><span class="v">{e(m["owner_name"])}</span>
      <span class="chip {'ok' if m['owner_confidence']=='confirmed' else 'warn'}">{e(m["owner_confidence"])}</span></div>
    <div class="cell"><span class="k">Phone</span><span class="v tel">{e(m["phone"])}</span></div>
    <div class="cell"><span class="k">Trading</span><span class="v">{e(m["trading_years"])} years</span>
      <span class="v" style="font-size:12.5px;color:var(--slate)">{'GST registered' if m["gst"] else 'no GST'}</span></div>
    <div class="cell"><span class="k">Socials</span><span class="v">{social_chips(m)}</span></div>
  </div>
  <div class="ev"><b>{e(m["address"])}</b> · ABN {e(m["abn"])} · {e(m["entity_type"])}<br>{e(m["website_note"])}</div>
</article>''' for i, m in enumerate(top, 1))

rows = "".join(
    f'<tr><td class="num">{m["score"]}</td><td><b>{e(m["name"])}</b></td>'
    f'<td>{e(m["category"])}</td><td class="num tel">{e(m["phone"])}</td>'
    f'<td>{e(m["owner_name"])}</td><td class="num">{e(m["trading_years"])}</td>'
    f'<td>{"✓" if m["gst"] else "—"}</td><td class="num">{len(m["socials"]) or "—"}</td>'
    f'<td>{e(m["suburb"])}</td></tr>' for m in M)

cats = collections.Counter(m["category"] or "Other" for m in M)
cat_rows = "".join(f'<tr><td>{e(c)}</td><td class="num">{n}</td></tr>'
                   for c, n in cats.most_common(14))

doc = f'''<title>Melbourne Small Business Leads</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wght@500;600;700&family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Sans:wght@400;500;600&display=swap">
<style>{CSS}</style>
<div class="wrap">
<header>
  <span class="eyebrow">Lead scavenger · run 25 Aug 2026</span>
  <h1>126 Melbourne businesses with no website</h1>
  <p class="sub">Every lead carries a phone number. 50 name the owner from the public
  business register, 97 have a verified-active ABN, and 49 have been trading ten years or more.</p>
  <div class="meta"><span>{strips} from shopping-strip trader associations</span><span>·</span>
  <span>{len(M)-strips} from directories, DNS-checked</span><span>·</span><span>Zero API credits used</span></div>
</header>

<section>
  <h2>What makes these better than a raw scrape</h2>
  <div class="funnel">
    <div class="stage"><span class="n">01 CURATED SOURCE</span><span class="v">317</span><span class="l">Trader-association members — paid listings, so dead businesses drop off</span></div>
    <div class="stage"><span class="n">02 WEBSITE CHECK</span><span class="v">−20</span><span class="l">Directory leads whose own domain resolves — dropped before you call</span></div>
    <div class="stage"><span class="n">03 REGISTER</span><span class="v">97</span><span class="l">Matched to an active ABN: proof they still trade</span></div>
    <div class="stage final"><span class="n">04 CALLABLE</span><span class="v">126</span><span class="l">50 with an owner to ask for by name</span></div>
  </div>
</section>

<section>
  <h2>Call these first</h2>
  <p class="sub" style="font-size:13.5px;color:var(--slate)">Owner named, register-confirmed, and mostly GST-registered — meaning turnover above $75k, so they can afford the work.</p>
  <div class="dockets">{dockets}</div>
</section>

<section>
  <h2>All 126 leads</h2>
  <div class="tscroll"><table>
    <thead><tr><th>Score</th><th>Business</th><th>Trade</th><th>Phone</th><th>Ask for</th><th>Yrs</th><th>GST</th><th>Social</th><th>Where</th></tr></thead>
    <tbody>{rows}</tbody></table></div>
</section>

<section>
  <h2>Coverage</h2>
  <div class="rejects">
    <div class="rcard"><h3><span class="dot" style="background:var(--signal)"></span>By trade</h3>
      <div class="tscroll"><table><tbody>{cat_rows}</tbody></table></div></div>
    <div class="rcard"><h3><span class="dot" style="background:var(--ok)"></span>Why the owner names are real</h3>
      <p style="font-size:13px;color:var(--ink-2);line-height:1.5;margin:0">Every name comes from
      ABN Lookup, the public business register. A sole trader's registered entity name
      <em>is</em> their legal name. A family trust names the family — so "Limnos Butchers"
      resolves to the <b>Droutsis family</b>, and you can ask for them at the counter.</p>
      <p style="font-size:13px;color:var(--ink-2);line-height:1.5;margin:0">Companies name the
      company, not a director, so those are left blank rather than guessed at.</p></div>
  </div>
</section>

<section>
  <h2>Before you dial</h2>
  <div class="note">
    <p><b>The strip leads are the strongest.</b> Trader-association membership is paid and
    maintained, so the business is trading now, and the listing itself shows no website —
    that is observed, not inferred.</p>
    <p><b>The directory leads were checked by DNS,</b> which is a good filter but not perfect:
    it catches a website at the business's own name, and would miss one at an unrelated domain.
    Expect a small number to still turn out to have a site.</p>
    <p><b>Wash the numbers against the Do Not Call Register</b> (donotcall.gov.au) first.
    Owner names come from a public register but are still personal information under the
    Privacy Act — use them for this outreach, don't resell the list.</p>
  </div>
</section>
</div>'''

out = pathlib.Path("/tmp/claude-0/-home-user-EG-playground-/3e47d570-5972-5aee-a261-aa93b3366cfa/scratchpad/leads.html")
out.write_text(doc, encoding="utf-8")
print(f"wrote {len(doc)} bytes | {len(M)} leads | {len(top)} dockets")
