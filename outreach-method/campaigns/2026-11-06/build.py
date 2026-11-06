"""Builds leads.json for the 2026-11-06 campaign. Drafts live here so they're reviewable in one place."""
import json, pathlib

SIG = "Sachi\nKairo · kairobookings.com"
OPT = 'Not for you? Just reply "no thanks" and I won\'t email again.'
PS = "P.S. No monthly fee or commission, it's a one-off. And if it's not right within 14 days you get every cent back."
DEMO = ("I make Kairo, a booking system for hair and beauty. Rather than pitch it, I'll just build you "
        "a demo booking page with your own services and times, so you can click through it like a client would.")
ASK = "Want me to put it together?"


def booking(greet, obs, extra=None, ps=PS, demo=DEMO):
    parts = [greet, obs, demo + (" " + extra if extra else ""), ASK, SIG, ps, OPT]
    return "\n\n".join(parts)


def website(greet, obs, offer):
    return "\n\n".join([greet, obs, offer, "Want me to send it through?", SIG, OPT])


L = []
add = lambda **k: L.append(k)

# ---------- BOOKING ----------
add(business="Blondies Of Melbourne", email="blondiesmelbourne@gmail.com", city="Melbourne VIC", offer="booking",
    evidence="IG @blondieshair bio: 'No DM's, please email' to book; 21K followers, 2,553 posts; posted Oct 2026",
    subject="your email bookings",
    body=booking("Hi Blondies crew,",
        "Saw the bio: no DMs, email only for bookings. With 21K people following your colour work, that inbox must never stop. "
        "Every \"what have you got next week?\" turns into three or four emails before anyone's actually in the book.",
        ps="P.S. No monthly fee or commission, it's a one-off. It also keeps patch tests on each client's card, handy with this much bleach work."))

add(business="Hair by Seliina", email="hairbyseliinaa@gmail.com", city="Sydney NSW (travelling)", offer="booking",
    evidence="IG @hairbyseliina bio: bridal/events/formals, travelling across Sydney, 'Book via DM or Email'; posted 30 Sep 2026",
    subject="formal season bookings",
    body=booking("Hi Seliina,",
        "Saw you travel all over Sydney for bridal, events and formals, and it all gets booked through DMs or email. "
        "Formal and wedding season is a rough time to be answering \"are you free on the 28th?\" between clients.",
        extra="Clients would see your free dates and lock them in with a deposit."))

add(business="Luxe Glow Beauty", email="luxeglowbeauty11@gmail.com", city="Sydney NSW", offer="booking",
    evidence="IG posts: event hair/upstyles, 'DM or Luxeglowbeauty11@gmail.com to secure your appointment'; posted Oct 2026",
    subject="event season bookings",
    body=booking("Hi there,",
        "Loved the sleek ponies and upstyles on your page. I noticed every appointment gets secured over DM or email. "
        "With formals, Christmas parties and weddings all landing on the same Saturdays, that's a lot of back and forth for one inbox."))

add(business="Mermaid Braids Gold Coast", email="mermaidbraids.gc@gmail.com", city="Gold Coast QLD", offer="booking",
    evidence="IG reels: 'Book now: DM or email mermaidbraids.gc@gmail.com'; posted 7 Oct 2026",
    subject="school holiday braids",
    body=booking("Hi there,",
        "Saw your braids get booked through DMs and email. With the summer holidays coming up on the Gold Coast, "
        "you're about to get a lot of mums asking \"have you got anything Saturday?\"",
        extra="Parents could pick the style and a time and book it themselves, even at 10pm."))

add(business="Paulina Linford Hair & Makeup", email="paulinalinford@gmail.com", city="Perth WA", offer="booking",
    evidence="IG post 'SAPPHIRE BALL GIRLS... For booking please contact me via DM or email'; posted Oct/Nov 2026",
    subject="ball season bookings",
    body=booking("Hi Paulina,",
        "Saw your Sapphire Ball post. Ball season in Perth must mean a lot of girls messaging you for the same Saturday afternoon, "
        "all through DMs and email.",
        extra="Hair, makeup and combos, only the times you can actually do, and a deposit to hold the spot."))

add(business="Nadia Hair Professionals", email="nadia.hair26@gmail.com", city="Seaton SA", offer="booking",
    evidence="IG/FB reels: 'Call us right now at 08 8345 4251 to book'; posted Oct 2026",
    subject="bookings while you're mid-colour",
    body=booking("Hi Nadia,",
        "Saw your reels asking people to call the salon to book. The catch is, when you're halfway through a foil the phone has to wait, "
        "and some of those callers just try the next salon.",
        extra="People could book themselves at 9pm when they actually think of it."))

add(business="Braedon Richelle / Inka Fina", email="braedonrichelletattoo@gmail.com", city="South Yarra VIC + Sydney", offer="booking",
    evidence="IG reel: 'Limited bookings in South Yarra (Melbourne) and Sydney... DM or email to book'; posted Nov 2026",
    subject="south yarra and sydney bookings",
    body=booking("Hi Braedon,",
        "Saw you're running limited bookings across South Yarra and Sydney, all through DMs and email. "
        "Keeping two cities' availability straight by hand is a lot.",
        extra="It also keeps consent forms and patch tests on each client's card, which matters for cosmetic tattoo."))

add(business="Studio13 Lismore", email="studio13lismore@gmail.com", city="Lismore NSW", offer="booking",
    evidence="IG reel 'beauty prep checklist': 'DM, call or email to book'; posted Oct 2026",
    subject="dm, call or email",
    body=booking("Hi Studio13 team,",
        "Saw your beauty prep checklist post. It ends with \"DM, call or email to book\". "
        "That's three inboxes to keep an eye on while you're in the middle of a client."))

add(business="The Mane Stylist (Nicola)", email="the.mobilemanestylist@gmail.com", city="QLD/NSW (mobile + in salon)", offer="booking",
    evidence="IG posts: 'DM or Email now for further inquiries on mobile or in salon hair services'; posted 2026",
    subject="mobile and salon bookings",
    body=booking("Hi Nicola,",
        "Saw you do both mobile and in-salon hair, and enquiries come through DM or email. "
        "Formal season must mean plenty of \"can you come to us on the 20th?\" messages to sort through."))

add(business="Glam by Yashvi", email="contact.glambyyashvi@gmail.com", city="Australia (mobile 0412)", offer="booking",
    evidence="IG reel: 'For makeup bookings and bridal related enquiries, email ... or text 0412 507 146'; posted Jul 2026",
    subject="bridal enquiries",
    body=booking("Hi Yashvi,",
        "Saw that makeup and bridal bookings come through email or text. "
        "Bridal ones especially tend to take ten messages before a date is actually locked in.",
        extra="Real availability, and a deposit to hold the date."))

add(business="Dollhouse Studio", email="contactdollhouse.studio@gmail.com", city="Sydney NSW", offer="booking",
    evidence="IG reels: 'Sydney | Book now via DM or email'; flash special 2 braids w/ colour $45; posted 2026",
    subject="flash special bookings",
    body=booking("Hi Dollhouse team,",
        "Saw your flash specials, like the two braids with colour for two days only. "
        "Specials like that must flood the DMs, and someone has to answer every one.",
        extra="It has a waitlist too, so when a time frees up the people waiting get a text straight away."))

add(business="Jess Carolina MUA", email="byjesscarolina@gmail.com", city="Adelaide SA", offer="booking",
    evidence="IG reel: 'For event makeup or Bridal bookings are open... Dm or email to book your date'; posted Jul 2026",
    subject="booking your dates",
    body=booking("Hi Jess,",
        "Saw bridal and event bookings are open and dates go through DM or email. "
        "Every \"is the 14th of March free?\" is another thread to keep track of.",
        extra="Clients see which dates are free and hold one with a deposit."))

add(business="A Beauty (Ava-Maria)", email="avamaria.abeauty@gmail.com", city="Sydney Hills NSW", offer="booking",
    evidence="IG @a.beauty___ bio: qualified lash artist, lashes + brow waxing, hills based, 'dm OR email to book'",
    subject="lash infill bookings",
    body=booking("Hi Ava-Maria,",
        "Saw your bio: lashes and brows in the hills, booked by DM or email. "
        "With infills every two or three weeks, that's the same clients messaging you over and over to find a time.",
        extra="It sends their reminder before each appointment, and they can rebook themselves."))

add(business="Nails by Laurissa", email="nailsbylaurissa@gmail.com", city="Earlwood NSW", offer="booking",
    evidence="IG @nailsbylaurissa: nail artist + educator, private 1:1 training, Earlwood; Oct 2026 post on rising press-on orders, 'DM or email'",
    subject="appointments, training and press-ons",
    body=booking("Hi Laurissa,",
        "Saw your post about press-on orders picking up. Between appointments, 1:1 training and custom press-ons, "
        "that's three kinds of booking all landing in your DMs and email.",
        extra="Appointments and training sessions could book themselves, which leaves the DMs for press-on chats."))

add(business="Hair I Am", email="hairiamkew@gmail.com", city="Eltham VIC (mobile)", offer="booking",
    evidence="hairiamkew.wixsite.com: mobile hairdresser, 'Please call, drop an email or send a message' to book; travel fee listed",
    subject="booking while you're on the road",
    body=booking("Hi there,",
        "Saw on your site that clients book Hair I Am by calling or emailing. "
        "As a mobile hairdresser you're probably driving or mid-cut when most of those calls come in."))

# ---------- WEBSITE ----------
add(business="Hair By Yuki", email="hairbyyuuki@gmail.com", city="St Leonards NSW", offer="website",
    evidence="IG @hairbyyuuki: moved to 488 Pacific Hwy St Leonards (inside Salon Lane), 1.6K followers, Nov/Dec bookings open; "
             "wixsite still lists 1/355 Crown St Surry Hills",
    subject="your website address",
    body=website("Hi Yuki,",
        "Your Instagram says you're at 488 Pacific Hwy in St Leonards now, but your website still shows Crown St, Surry Hills. "
        "Anyone who Googles you could end up at the old address.",
        "I build websites for hairdressers. Happy to mock up a new homepage for you for free, with the new address, "
        "your low-maintenance colour work and an easy way to book. If you don't like it, you've lost nothing."))

add(business="Liv and Lash Co.", email="livandlashco@gmail.com", city="Moana SA", offer="website",
    evidence="IG @livandlashco active (posts this week); only web presence is livandlashco.setmore.com booking page",
    subject="your lash lift combos",
    body=website("Hi Liv,",
        "Your lash lift and brow lamination combos on Instagram are lovely. But the link people get sent to is your Setmore page, "
        "which looks like everyone else's and doesn't show any of that work.",
        "I build websites for beauty businesses. Happy to mock up a homepage for you for free: your best before-and-afters, "
        "Moana and Port Noarlunga front and centre, and your Setmore booking kept exactly as it is. If you don't like it, you've lost nothing."))

add(business="Lashly Beauty (Anna)", email="lashlybeauty.hello@gmail.com", city="Armstrong Creek VIC", offer="website",
    evidence="IG @lashly.beauty 3,125 followers, 641 posts; site is lashlybeauty.square.site (services/book/feedback/hours, no gallery)",
    subject="641 posts of lash work",
    body=website("Hi Anna,",
        "You've posted 641 lots of lash and brow work on Instagram, but your Square page, which is where people land to book, "
        "doesn't show any of it.",
        "I build websites for beauty businesses. Happy to mock up a homepage for you for free: your best sets, the Korean facials "
        "and cosmetic tattoo, and your Square booking button left exactly as it is. If you don't like it, you've lost nothing."))

add(business="Safezone Scalp Treatment Centre", email="safezonemelbourne@gmail.com", city="Burwood VIC", offer="website",
    evidence="Site is sites.google.com/view/safezone-melbourne (Google Sites), 2 pages; email published in search listing",
    subject="your google sites page",
    body=website("Hi there,",
        "Found Safezone's website on a sites.google.com address. For a scalp clinic, where people are trusting you with something "
        "like hair loss, a proper site on its own domain with before-and-afters and reviews goes a long way.",
        "I build websites for hair and beauty businesses. Happy to mock up a homepage for you for free, with your treatments, "
        "prices and an easy way to book. If you don't like it, you've lost nothing."))

add(business="Taya Bree Hair Artistry", email="tayabreehairartistry@gmail.com", city="Jandakot WA", offer="website",
    evidence="tayabreehairartist.wixsite.com: free Wix address, no prices shown, Timely booking already set up",
    subject="your wix site",
    body=website("Hi Taya,",
        "Your site is still on the free wixsite.com address and doesn't show any prices. "
        "Your Timely booking's already set up though, so the hard part's done.",
        "I build websites for hairdressers. Happy to mock up a homepage for you for free, on your own domain, with your colour "
        "and extension work, your prices and the Timely button. If you don't like it, you've lost nothing."))

out = pathlib.Path(__file__).with_name("leads.json")
out.write_text(json.dumps(L, indent=2, ensure_ascii=False))
print(len(L), "leads ->", out)
for l in L:
    print(f"{len(l['body'].split()):>4}w  {l['offer']:<8} {l['email']}")
