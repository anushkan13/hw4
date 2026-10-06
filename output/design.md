# Campus Customs — Design Pass

Goal: make the site feel like a real storefront with a point of view — **heritage
varsity**. Yale navy and white, warmed with gold and cream, a friendly bulldog as
the shop's character, and motion that rewards poking at things.

---

## Typography

**What changed.** A three-font system replacing Georgia-for-everything:

| Role | Font | Where |
|---|---|---|
| Display | **Alfa Slab One** | Logo, hero headline, About drop cap |
| Headings | **Playfair Display** | Page titles, product names, section heads |
| Body | **Inter** | Everything else |

**Why it helps.** The slab is the varsity banner voice — it does the "this is a real
college shop" work in the first second, before anyone reads a word. Playfair gives
product names a considered, boutique feel instead of a database-row feel. Inter is
boring on purpose: prices, sizes, and stock counts have to be read accurately at
11–14px, and prices use tabular figures so columns of `$68.00` line up.

---

## Color

**What changed.** The palette went from two flat colors to a layered one: four navies
(`#00356b` through `#001f3f`) for depth, **warm gold** (`#c8a04a`, lifting to
`#e9c877` on dark) as the accent, and **cream** (`#faf6ee`) replacing white as the
page ground. Shadows are tinted navy rather than grey.

**Why it helps.** Flat navy-on-white reads as a template. Gold is the single cheapest
signal of "established" in collegiate branding, and cream takes the clinical edge off
white so the product photos feel warmer. The navy-tinted shadows matter more than
they sound: grey shadows on a cream page look like dirt, navy ones look like depth.

A **3px gold rule** repeats under the nav, under the hero headline, across the chat
header, and above the footer — one detail tying four unrelated surfaces together.

---

## Handsome Dan, the bulldog mascot

**What changed.** An original bulldog drawn from scratch as inline SVG
(`components/Bulldog.tsx`) — rounded head, folded ears, brow wrinkles in gold, wide
muzzle, off-centre grin, one tooth, gold collar. Not traced from or modelled on any
real university's mascot. He appears as:

- the **nav logo mark** (and tips his head on hover),
- the **hero brand figure**, floating in a dashed gold ring labelled "Handsome Dan",
- the **chat launcher**, the **chat header avatar**, and a small avatar **beside every
  message the assistant sends**,
- the **footer mark** and the **browser favicon**.

The agent's system prompt names him too, so asking the chat "what's your name?"
answers "I'm Handsome Dan, the Campus Customs shop dog" rather than "I'm the
shopping assistant".

He is built to work on any surface: the body is `currentColor`, so he is navy on
cream and white on navy, and the face carries its own navy outlines so the eyes and
muzzle never disappear into the body.

**Why it helps.** The assistant was a generic speech bubble. Giving it a face and a
name turns "a chatbot" into "Handsome Dan" — a name any Yale shopper recognises
instantly — which people are far more willing to talk to, and the chat is where this
shop's best feature lives. Repeating one character
across logo, hero, chat, and footer also does brand work no amount of color alone
can: the shop becomes recognisable.

---

## Home hero

**What changed.** Navy gradient with a gold glow top-right, an angled **varsity
pinstripe** overlay (the kind printed inside a letterman jacket), the headline in
Alfa Slab with a gold swash beneath it, Handsome Dan floating in a dashed ring on the right,
and a gold **"Shop the Collection →"** button whose arrow slides on hover.

**Why it helps.** The old hero was a navy box with text. This one has a focal point,
a brand figure, and one obvious thing to click. The CTA is the only gold-filled
button on the page, so the eye lands on the route into the shop rather than on the
secondary "About Us".

---

## Product presentation

**What changed.**

- **Uniform image framing.** The catalogue photos are genuinely inconsistent — I
  sampled all 102: **28 are shot on white, 43 on black, 31 on grey or a set**. Since
  the backgrounds can't be fixed without re-shooting, uniformity comes from identical
  *framing* instead: every photo now sits in the same square, cream-matted, rounded
  tile with the same hairline inner ring. (I first tried `mix-blend-mode: multiply` to
  drop white backgrounds into the mat — it worked for the 28 white-background shots
  and turned the other 74 into black blocks, so I dropped it.)
- **Hover:** card lifts 6px into a deeper shadow, border turns gold, a gold rule wipes
  across the top edge, and the photo zooms 7% inside its frame.
- **Category as a gold pill**, product name in Playfair, price in bold tabular navy.
- **Detail page:** larger framed image with **gold corner brackets**, a 30px price, and
  the description set off behind a gold left rule. Size boxes lift on hover; sold-out
  ones stay dashed and muted.

**Why it helps.** A grid where every tile is a different shape and tone looks like a
spreadsheet; one where every tile matches looks like a catalogue, and shoppers scan
it faster. The hover lift makes the grid feel responsive to touch, which encourages
the browsing that leads to a product page. The corner brackets on the detail page are
a small thing that makes a $68 hoodie feel like a considered purchase.

---

## Motion

**What changed.** A shared easing curve and three reusable keyframes (`rise`, `fade`,
`pop`) applied as: page content fading in, product cards and pillars rising in with
staggered delays, cards and size boxes lifting on hover, chips and buttons shifting
on hover with the CTA arrow sliding, chat messages and product cards popping in, a
gold three-dot typing indicator, a shimmer on loading skeletons, Handsome Dan floating in
the hero, and a gold halo pulsing around the chat launcher.

**Everything is wrapped in `prefers-reduced-motion`,** which drops all animation to
near-zero duration while keeping the design intact.

**Why it helps.** Motion is feedback: a card that lifts confirms it is clickable, a
typing indicator says the assistant heard you, a shimmer says data is coming rather
than broken. The halo on the launcher is the one piece of motion that's there to
attract rather than confirm — it pulses every 2.6 seconds, enough to be noticed and
not enough to nag. Respecting reduced-motion keeps all of this from being an
accessibility problem for anyone who gets motion sick.

---

## Chat feel

**What changed.** Handsome Dan's avatar in the header (titled "Handsome Dan / Campus Customs
shopping assistant") and beside every reply; navy-gradient bubbles for the shopper
and white bordered bubbles for Handsome Dan, each popping in; a gold typing indicator; the
starter chips restyled as gold-outlined pills that slide right on hover and stagger
in; a gold-tinted "Viewing:" context strip; product cards that slide and gold-border
on hover. The greeting is now in his voice: *"Hi, I'm Handsome Dan — the Campus Customs
bulldog."*

**Why it helps.** The chat is the differentiating feature of this shop, so it should
look like a first-class part of the storefront rather than a bolted-on widget. The
avatar beside every reply is what makes a thread feel like a conversation with
someone.

---

## Footer

**What changed.** A navy-gradient footer under a gold rule: Handsome Dan's mark beside the
wordmark and the brand line *"Bulldog pride, wherever you are."*, and a New Haven
block — *"Made for New Haven / Two blocks off the Green, under the elms. / Shipping
Yale blue to every corner of the world."* with the city's coordinates
(41.3163° N · 72.9223° W) in letterspaced caps. A thin legal row sits below.

**Why it helps.** A one-line copyright footer says "unfinished". The place detail is
what makes the shop feel like it belongs to somewhere real, which is the whole
proposition for alumni buying from across the country — and it closes the page on the
same brand note the nav opens it with.

---

## Verified

Fonts load live (Alfa Slab One, Playfair Display, Inter all confirmed `loaded`, not
fallbacks). No console errors. Production build clean. All 53 backend checks still
pass, so nothing in the redesign disturbed the catalogue, auth, chat, or memory
behaviour.

**One note on process:** partway through, a bad find-and-replace corrupted
`src/index.css` (an empty match ballooned it to 141 MB). I rewrote the stylesheet
from scratch as the design system above rather than patching the old one — the file
is now ~32 KB and organised by section.
