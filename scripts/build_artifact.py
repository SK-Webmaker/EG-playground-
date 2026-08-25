"""Generate the small-business call-sheet artifact from the exported leads."""
import html, json, pathlib, collections

d = json.load(open("data/leads/smallbiz-full.json"))
qual, rej = d["qualified"], d["rejected"]
clear = [r for r in qual if r["website_status"] == "clear"]
unver = [r for r in qual if r["website_status"] != "clear"]

CSS = open("scripts/artifact.css").read()

def esc(x): return html.escape(str(x or "—"))

rows = []
for r in sorted(qual, key=lambda r: (-r["score"], r["category"])):
    badge = ('<span class="chip ok">verified</span>' if r["website_status"] == "clear"
             else '<span class="chip none">unverified</span>')
    rows.append(
        f'<tr><td class="num">{r["score"]}</td><td><b>{esc(r["name"])}</b></td>'
        f'<td>{esc(r["category"])}</td><td class="num tel">{esc(r["phone"])}</td>'
        f'<td>{esc(r["suburb"])}</td><td>{esc(r["address"])}</td><td>{badge}</td></tr>')

dockets = []
for i, r in enumerate(sorted(clear, key=lambda r: -r["score"]), 1):
    dockets.append(f'''
    <article class="docket">
      <div class="dhead"><span class="rank">{i:02d}</span>
        <div class="dtitle"><h3>{esc(r["name"])}</h3>
          <span class="niche">{esc(r["category"])} · {esc(r["suburb"])}</span></div>
        <div class="score"><b>{r["score"]}</b><span>SCORE</span></div></div>
      <div class="grid">
        <div class="cell"><span class="k">Phone</span><span class="v tel">{esc(r["phone_raw"])}</span></div>
        <div class="cell"><span class="k">Address</span><span class="v">{esc(r["address"])}</span></div>
        <div class="cell"><span class="k">Website</span><span class="chip ok">None found</span></div>
      </div>
      <div class="ev"><b>Evidence:</b> {esc(r["website_note"])}</div>
    </article>''')

cats = collections.Counter(r["category"] for r in qual)
cat_rows = "".join(f'<tr><td>{esc(c)}</td><td class="num">{n}</td></tr>'
                   for c, n in cats.most_common())

reasons = collections.Counter(x.split('_x')[0] for r in rej for x in r["reasons"])
rej_rows = "".join(f'<tr><td>{esc(k.replace("_"," "))}</td><td class="num">{v}</td></tr>'
                   for k, v in reasons.most_common())

doc = f'''<title>Melbourne Small Business Leads</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wght@500;600;700&family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Sans:wght@400;500;600&display=swap">
<style>{CSS}</style>
<div class="wrap">
<header>
  <span class="eyebrow">Lead scavenger · run 25 Aug 2026</span>
  <h1>100 Melbourne small businesses with no website</h1>
  <p class="sub">Local operators across 12 trades and 12 suburbs, filtered clear of franchises,
  directory spam and multi-listing resellers. Every one has a phone number you can dial today.</p>
  <div class="meta"><span>Source: Hotfrog · 130 listings harvested</span><span>·</span>
  <span>9 spot-verified as having no website</span></div>
</header>

<section>
  <h2>How 130 listings became 100 leads</h2>
  <div class="funnel">
    <div class="stage"><span class="n">01 HARVEST</span><span class="v">130</span><span class="l">Listings across 12 trades × 12 Melbourne suburbs</span></div>
    <div class="stage"><span class="n">02 DE-DUPE</span><span class="v">−10</span><span class="l">Same operator listed repeatedly</span></div>
    <div class="stage"><span class="n">03 DE-SPAM</span><span class="v">−20</span><span class="l">Franchises, offshore support spam, resold numbers, SEO shells</span></div>
    <div class="stage final"><span class="n">04 CALLABLE</span><span class="v">100</span><span class="l">Real local businesses with a working number</span></div>
  </div>
</section>

<section>
  <h2>Verified — no website found</h2>
  <p class="sub" style="font-size:13.5px;color:var(--slate)">These nine were individually checked against a live web search. Start here.</p>
  <div class="dockets">{"".join(dockets)}</div>
</section>

<section>
  <h2>All 100 leads</h2>
  <p class="sub" style="font-size:13.5px;color:var(--slate)">Ranked by call quality: direct mobile, real street premises, owner-named business, specific trading name.</p>
  <div class="tscroll">
    <table>
      <thead><tr><th>Score</th><th>Business</th><th>Trade</th><th>Phone</th><th>Suburb</th><th>Address</th><th>Website</th></tr></thead>
      <tbody>{"".join(rows)}</tbody>
    </table>
  </div>
</section>

<section>
  <h2>Coverage &amp; what got cut</h2>
  <div class="rejects">
    <div class="rcard"><h3><span class="dot" style="background:var(--signal)"></span>Leads by trade</h3>
      <div class="tscroll"><table><tbody>{cat_rows}</tbody></table></div></div>
    <div class="rcard"><h3><span class="dot" style="background:var(--dead)"></span>Rejected (30)</h3>
      <div class="tscroll"><table><tbody>{rej_rows}</tbody></table></div>
      <p style="font-size:12.5px;color:var(--slate);margin:0">Includes one operator running four fake
      suburb listings on a single number, five offshore "Canon printer support" listings, and a
      competitor already selling websites to hairdressers.</p></div>
  </div>
</section>

<section>
  <h2>Before you dial</h2>
  <div class="note">
    <p><b>91 of these are unverified for website status.</b> Hotfrog hides the website field on search
    pages, so absence there is a candidate signal, not proof. On the sample I checked, roughly
    <b>6 in 7 genuinely had no website</b> — expect to lose about one in seven on the call.
    Run <span class="mono">python -m scavenger.cli</span> to verify the rest in bulk.</p>
    <p><b>Wash the numbers against the Do Not Call Register</b> (donotcall.gov.au) before cold-calling.
    Penalties under the Do Not Call Register Act 2006 are charged per call.</p>
    <p><b>Best opener for the social-only ones</b> — Maurice Albert Salon and Limnos Butchers both run
    active Instagram and Facebook but own nothing. They already believe in being online; they just
    never got a site. That is the shortest conversation on this list.</p>
  </div>
</section>
</div>'''

out = pathlib.Path("/tmp/claude-0/-home-user-EG-playground-/3e47d570-5972-5aee-a261-aa93b3366cfa/scratchpad/leads.html")
out.write_text(doc, encoding="utf-8")
print(f"wrote {out} ({len(doc)} bytes) | {len(qual)} leads, {len(clear)} verified")
