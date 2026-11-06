"""Campaign 2 (6 Nov 2026, afternoon). Same rules as campaign 1; see .claude/skills/email-outreach/SKILL.md."""
import json, pathlib

SIG = "Sachi\nKairo · kairobookings.com"
OPT = 'Not for you? Just reply "no thanks" and I won\'t email again.'
PS = "P.S. No monthly fee or commission, it's a one-off. And if it's not right within 14 days you get every cent back."
DEMO = ("I make Kairo, a booking system for hair and beauty. Rather than pitch it, I'll just build you "
        "a demo booking page with your own services and times, so you can click through it like a client would.")


def booking(greet, obs, extra=None):
    return "\n\n".join([greet, obs, DEMO + (" " + extra if extra else ""), "Want me to put it together?", SIG, PS, OPT])


def website(greet, obs, specifics, trade="beauty businesses"):
    offer = (f"I build websites for {trade}. Happy to mock up a homepage for you for free, {specifics}. "
             "If you don't like it, you've lost nothing.")
    return "\n\n".join([greet, obs, offer, "Want me to send it through?", SIG, OPT])


SQUARE = ("It takes bookings fine, but it's not much to win over someone who's never heard of you.")
KEEP_SQ = "with your best work, your prices and your Square booking button kept exactly as it is"
L = []
add = lambda **k: L.append(k)

# ---------- BOOKING ----------
add(business="Magic Touch Barber Shop", email="magictouchbarbers@gmail.com", city="Neutral Bay NSW", offer="booking",
    evidence="magictouchbarbers.wixsite.com: 'Contact via email or phone to schedule an appointment'; Neutral Bay NSW 2089",
    subject="bookings by phone",
    body=booking("Hi there,",
        "Saw on your site that bookings at Magic Touch are by email or phone. When you've got someone in the chair the phone "
        "has to wait, and the bloke who wanted a 5:30 cut just tries the next shop.",
        "Clients could pick their barber and time themselves, even after you've closed."))

add(business="Moda Hair Melbourne", email="modahairmelbourne@gmail.com", city="Melbourne VIC", offer="booking",
    evidence="IG post (Jun 2026): bridal hair, 'Secure your date... Enquire via DM or email us at modahairmelbourne@gmail.com'",
    subject="securing wedding dates",
    body=booking("Hi there,",
        "Saw your bridal post: \"secure your date, enquire via DM or email\". Wedding enquiries are the ones that take "
        "ten messages before a date is actually held.",
        "Brides would see your free dates and hold one with a deposit."))

add(business="Katie MacNally MUA", email="katiemacnallymua@gmail.com", city="Iluka, Perth WA", offer="booking",
    evidence="IG reel 2026: 'Email to book your next glam with me katiemacnallymua@gmail.com'; site lists Iluka, Perth WA",
    subject="email bookings",
    body=booking("Hi Katie,",
        "Saw your posts say to email to book your next glam. Every booking by email is a few rounds of "
        "\"what time suits?\" before it's actually in the diary.",
        "A deposit holds the spot, so no more no-shows on a Saturday morning."))

add(business="MINK Beauty Bar", email="info.minkbeautybar@gmail.com", city="Ellenbrook WA", offer="booking",
    evidence="beautopiabar.wixsite.com: MINK Beauty Bar, 39 Mornington Pkwy Ellenbrook; 'book services via Instagram or by phone'",
    subject="instagram and phone bookings",
    body=booking("Hi there,",
        "Saw on your site that MINK bookings go through Instagram or a phone call. That's a lot of messages to keep on top of "
        "while you're in the middle of a feathertouch brow."))

add(business="Makeup by Neha", email="makeupbyneha2022@gmail.com", city="Canberra ACT", offer="booking",
    evidence="IG reels 2026 (#canberramua): '2026 bookings now open, Dm or email me to book'",
    subject="2026 bookings",
    body=booking("Hi Neha,",
        "Saw your 2026 bookings are open and it's DM or email to book. Formal and wedding season means a lot of the same "
        "\"is Saturday the 14th free?\" messages.",
        "Clients see your free dates and hold one with a deposit."))

# ---------- WEBSITE ----------
add(business="Smoky Barbershop", email="smokybarbershop@gmail.com", city="Bowen Hills QLD", offer="website",
    evidence="Site smokybarbershop.wixsite.com/my-site-2 (free Wix address); owner Sahand; IG @smoky_barbershop posted 21 Sep 2026",
    subject="your wix address",
    body=website("Hi Sahand,",
        "Your Bowen Hills shop's website is still on a free Wix address, smokybarbershop.wixsite.com/my-site-2. "
        "That's a hard one for anyone to remember or type in.",
        "on your own domain, with your fades front and centre and your online booking kept as it is",
        trade="barbers and beauty businesses"))

add(business="Lunas Nails Palace", email="lunasnailspalace@gmail.com", city="Walkerville SA", offer="website",
    evidence="envieadl.wixsite.com: page content is Lunas Nails Palace, but site/tab title is still 'Envie Nails & Beauty'; Fresha booking",
    subject="your old name on the site",
    body=website("Hi there,",
        "Your website is all Lunas Nails Palace now, but the title still says \"Envie Nails & Beauty\". "
        "That old name is usually what Google shows when someone searches for you.",
        "with the right name everywhere, your nail work and your Fresha booking button kept as it is"))

add(business="Glorious Brows & Beauty", email="lovepreetkaur1414@gmail.com", city="Torrensville SA", offer="website",
    evidence="glorious-brows-beauty.square.site: two different phone numbers shown (0416 780 744 and 0452 073 302); owner Lovepreet",
    subject="two phone numbers",
    body=website("Hi Lovepreet,",
        "Noticed your Square page shows two different phone numbers, 0416 780 744 and 0452 073 302. "
        "A new client won't know which one to call.",
        KEEP_SQ.replace("your prices", "one clear contact number")))

add(business="Lashes by Mira", email="lashesbymira82@gmail.com", city="Bertram WA", offer="website",
    evidence="mjearnshaw82.wixsite.com/lashesbymira-1: free Wix address, home salon Bertram WA, no prices shown",
    subject="your lash site",
    body=website("Hi Mira,",
        "Your Bertram lash site is still on the free wixsite.com address and doesn't show any prices, "
        "which is usually the first thing a new client looks for.",
        "on your own domain, with your sets, your prices and your Book Now button",
        trade="lash techs and beauty businesses"))

add(business="Futaba Eyelash Extensions", email="futaba.eyelash@gmail.com", city="Hobart TAS", offer="website",
    evidence="futabaeyelash.wixsite.com/exts: free Wix address, Hobart CBD, online booking, no prices shown",
    subject="your hobart lash site",
    body=website("Hi there,",
        "Your site is still on the free wixsite.com address and doesn't show prices for your classic, hybrid or volume sets. "
        "That's usually the first thing a new client in Hobart looks for.",
        "on your own domain, with your sets, your prices and your booking button",
        trade="lash techs and beauty businesses"))

add(business="Nikki's Nails", email="sanaoliver168@gmail.com", city="Mount Pleasant WA", offer="website",
    evidence="nikkisnailsperth168.square.site: Square booking page is the only site; owner Nikki; Mount Pleasant WA",
    subject="your mount pleasant page",
    body=website("Hi Nikki,",
        "Your website is your Square booking page. " + SQUARE,
        KEEP_SQ))

add(business="G & Co Studio", email="gandcostudiox@gmail.com", city="Gunbower VIC", offer="website",
    evidence="g-co-studio.square.site: Square page is the site, no prices shown; owner Georgia; Gunbower VIC 3566",
    subject="your square page",
    body=website("Hi Georgia,",
        "Your G & Co Studio site is the Square booking page, and it doesn't show any prices. "
        "It does the booking part, but it's not much to win over someone who's never heard of you.",
        KEEP_SQ))

add(business="Green Goddess Nails and Beauty", email="greengoddessnailsbeauty@gmail.com", city="Blackwood SA", offer="website",
    evidence="greengoddessnailsandbeauty.square.site: Square booking page is the only site; Blackwood SA",
    subject="your blackwood page",
    body=website("Hi there,",
        "Your website is your Square booking page. " + SQUARE,
        KEEP_SQ))

add(business="Aphrodite Beauty Artistry", email="aphroditebeautyartistry@gmail.com", city="Mount Barker SA", offer="website",
    evidence="aphrodite-beauty-artistry.square.site: Square booking page is the only site; Mount Barker SA",
    subject="your mount barker page",
    body=website("Hi there,",
        "Your website is your Square booking page. " + SQUARE,
        KEEP_SQ))

add(business="NailsbyLin", email="nailsbylin.au@gmail.com", city="Campsie NSW", offer="website",
    evidence="nailsbylin.square.site: home-based nail salon Campsie; prices shown are deposits only",
    subject="your nail prices",
    body=website("Hi Lin,",
        "Your Square page only shows the deposit for each service, not what a set actually costs. "
        "New clients usually want the real price before they'll book.",
        "with your sets, your full prices and your Square booking button kept exactly as it is"))

add(business="Crystal's Lash & Brow Art", email="crystalrmackay@gmail.com", city="West End QLD", offer="website",
    evidence="crystalrmackay.wixsite.com/lash: free Wix address with Wix ad banner, West End Brisbane, no prices shown",
    subject="your brow site",
    body=website("Hi Crystal,",
        "Your site is still on the free wixsite.com address, with the Wix banner across the top, and it doesn't show prices "
        "for your microblading or lashes.",
        "on your own domain, with your brows and lashes, your prices and an easy way to book"))

add(business="HxHair Salon", email="hxhairsalon@gmail.com", city="Point Cook VIC", offer="website",
    evidence="hxhairau.wixsite.com/home: free Wix address; Sanctuary Lakes SC, Point Cook; big hair + nails service list",
    subject="your wix address",
    body=website("Hi there,",
        "Your Point Cook salon's site is still on the free wixsite.com address. With hair and nails both on the menu, "
        "that's a lot of services sitting on a page that's hard to find.",
        "on your own domain, with your hair and nail work split out clearly and an easy way to book",
        trade="hair and beauty salons"))

add(business="Woodside Hair & Beauty", email="woodsidehairandbeauty@gmail.com", city="Woodside SA", offer="website",
    evidence="woodside-hair-beauty.square.site: Square booking page is the only site; Woodside SA 5244",
    subject="your woodside page",
    body=website("Hi there,",
        "Your website is your Square booking page. " + SQUARE,
        KEEP_SQ, trade="hair and beauty salons"))

add(business="The Bloom Beauty Bar", email="bloombeautybarkta@gmail.com", city="Australia", offer="website",
    evidence="the-bloom-beauty-bar-au.square.site: Square page; 'message me on Facebook/Instagram' for times not shown",
    subject="messaging for a time",
    body=website("Hi there,",
        "Your website is the Square booking page, and it asks people to message you on Facebook or Instagram if they can't "
        "see a time they want. " + SQUARE,
        KEEP_SQ))

add(business="No Loose Ends Hair", email="nolooseendshairstyling@gmail.com", city="South Melbourne VIC", offer="website",
    evidence="nolooseendshairsty.wixsite.com/website: free Wix address, 287 Clarendon St South Melbourne, no prices shown",
    subject="your clarendon st site",
    body=website("Hi there,",
        "Your South Melbourne salon's site is still on a free wixsite.com address and doesn't show any prices, "
        "which is usually the first thing a new client looks for.",
        "on your own domain, with your colour and wedding work, your prices and an easy way to book",
        trade="hair salons"))

out = pathlib.Path(__file__).with_name("leads.json")
out.write_text(json.dumps(L, indent=2, ensure_ascii=False))
print(len(L), "leads")
for l in L:
    print(f"{len(l['body'].split()):>4}w  {l['offer']:<8} {l['email']}")
