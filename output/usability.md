# Campus Customs — Usability Upgrades

Four improvements to the shop: two on the storefront, two in the agent backend.
Each entry records what was added, why it helps a Campus Customs shopper or the
business, and how it was verified.

---

## 1. Chat starter chips (frontend)

**What was added.** Three tappable suggested questions sit inside the chat panel
whenever the conversation is empty — "What hoodies do you have?", "Show me items
under $50", and "What t-shirts are in stock in the XL size?". Tapping one sends it
to the agent as a normal message, exactly as if the shopper had typed it. The chips
disappear once the conversation starts and come back only on an empty transcript, so
they never get in the way of a returning shopper's saved history.

*Where:* `frontend/src/components/ChatPanel.tsx` (`STARTER_CHIPS`, `send()`),
styles in `src/index.css`.

**Why it helps the shopper.** An empty text box does not advertise what it can do. A
shopper who has never used a shop chatbot usually assumes it is a help desk for
orders and shipping, and either ignores it or asks something it cannot answer. The
chips show, in the shopper's own language, that this assistant searches the actual
catalogue — by category, by budget, and by size in stock. They are also the fastest
possible path to a result: one tap instead of a sentence of typing, which matters
most on a phone.

**Why it helps the business.** The three chips were chosen to exercise three
different tools, so whichever one a shopper taps, they immediately see the feature
that makes the assistant worth using: real product cards they can click through to a
product page. That turns an ignored widget into the top of a browsing funnel.

**Verified.** All three chips render on an empty conversation. Tapping the XL chip
sent "What t-shirts are in stock in the XL size?" as a shopper message, the chips
disappeared, and the agent returned 8 T-shirt cards — every one of which really has
XL in stock.

---

## 2. Price sorting and price filtering on the Products page (frontend)

**What was added.** A second toolbar row under the existing search box and category
chips, in the same chip language so it reads as one control set:

- **Price bands in $10 increments** — `$30–40`, `$40–50`, … `$90–100`, plus "Any".
  The bands are generated from the catalogue's own price range, so there is never an
  empty bucket and the top end is never cut off.
- **A sort control** — A–Z (the existing default), Price: low to high, and Price:
  high to low.

Both compose with the search box and the category chips: Hoodies + $60–70 + price
low to high all apply together. The backend also accepts `min_price`, `max_price`,
and `sort` on `/api/products`, so the same filtering is available to any other
client.

*Where:* `frontend/src/pages/Products.tsx` (`priceBands`, `SORTS`), `backend/main.py`
(`list_products`).

**Why it helps the shopper.** 102 products in a single A–Z grid is a wall. Budget is
the most common first constraint in apparel — a student shopping for themselves and
a parent buying a gift are looking at very different parts of the same catalogue —
and before this there was no way to express it. $10 bands are narrow enough to be
meaningful across a $32–$98 range without producing a long list of options.

**Why it helps the business.** Sorting high-to-low surfaces the $88–$98 jackets and
premium quarter-zips that are invisible at the bottom of an alphabetical grid, and
low-to-high gives price-sensitive shoppers a reason to stay rather than bounce.
Either way fewer shoppers leave because they could not find their price point.

**Verified.** Bands render as `$30–40` through `$90–100`. Selecting `$60–70` narrows
102 pieces to 23, every one priced in that band. Price low-to-high orders all 102
products with zero inversions ($32 first); high-to-low likewise ($98 first, $32
last). Filters and sort compose correctly.

---

## 3. Sold-out size suggestions (backend / agent)

**What was added.** A fifth tool, `find_alternatives_in_size(product_id, size)`. It
returns same-category products that genuinely have stock in the size the shopper
asked for, excludes the item that was sold out, and sorts by closeness in price so a
$72 quarter-zip is offered against another $72 quarter-zip rather than a $98 jacket.
The prompt now carries a rule — "never end on a sold-out answer" — telling the agent
to call this immediately after any sold-out result and to present the alternatives as
clearly different items.

*Where:* `backend/tools.py` (`find_alternatives_in_size`),
`backend/prompts/prompt.md` (How to answer, rule 6).

**Why it helps the shopper.** "Sorry, that's sold out" is a dead end, and the shopper
has to start their search over. Now the honest answer and a usable next step arrive
together, and because the alternatives come back as product cards they are one click
from the detail page.

**Why it helps the business.** 145 of 612 size rows are currently at zero, so
sold-out answers are common — nearly a quarter of size questions could end in a lost
sale. Recovering even some of those is real revenue, and the shopper gets a better
experience than a bare apology. Crucially this is *not* a bait-and-switch: the
original answer stays honest and explicit about being sold out, and the suggestions
are named as different items.

**Verified.** Asked "Do you have this in XL?" on the Benjamin Franklin 1/4 Zip, whose
XL is genuinely at zero:

> "The XL is sold out right now for the Benjamin Franklin 1 4 Zip. It is available in
> XS, S, M, L, and XXL. These are different quarter-zips with XL in stock:"
> — followed by Berkeley, Branford, and Morse 1/4 Zips, all $72, all with XL in stock.

Checks confirm every suggested alternative really has the requested size, and the
sold-out item is never suggested back to the shopper.

---

## 4. Smarter product search (backend / agent)

**What was added.** The messy `garment_type` column flagged in the original database
review is now actioned in one place that both the chat and the Products page use.

- **One search engine.** `tools.find_products()` is the only catalogue search in the
  app. The agent's `search_products` tool and the website's `/api/products` route
  both call it, so a chat query and a grid query return the same items — the Products
  page no longer carries its own near-duplicate filtering logic.
- **Garment types consolidated.** The 22 raw strings (including case-only duplicates
  like `short-sleeve t-shirt` vs `short-sleeve T-shirt`, and five different ways to
  write "hoodie") collapse into six canonical categories via the existing
  `categorize()` mapping — the same one behind the filter chips. All 102 products map
  cleanly; nothing falls into "Other".
- **Synonyms shoppers actually type.** `CATEGORY_SYNONYMS` maps "sweatshirt",
  "sweater", "crew neck", "pullover" → Crewnecks; "tee", "tees", "shirt" → T-Shirts;
  "1/4 zip", "half zip" → Quarter-Zips; "fleece", "bomber", "coat" → Jackets.
- **Whole questions work.** `split_query()` pulls the category out of free text and
  drops filler words, so "what hoodies do you have?" is treated as a Hoodies search
  rather than a literal hunt for the word "hoodies".
- **Tags and garment type are searched** alongside name and description, so "bulldog"
  finds the products tagged bulldog even when their names never say it.

*Where:* `backend/tools.py` (`CATEGORY_SYNONYMS`, `canonical_category`,
`split_query`, `find_products`, `all_stock`), `backend/main.py` (`list_products`).

**Why it helps the shopper.** Before this, searching "sweatshirt" returned only the
handful of products with that exact word in their text; the 26 crewnecks whose
`garment_type` says "crewneck sweatshirt" but whose names never repeat it were
invisible. Now "sweatshirt" returns all 29 crewnecks. A shopper gets the complete,
correct set without having to guess the shop's internal vocabulary — and gets the
same answer whether they ask the chat or type in the search box.

**Why it helps the business — cheaper and faster.** The old search issued one
`inventory` query per candidate product: **103 SQL round trips** for a broad search.
`all_stock()` now fetches the whole stock table in a single pass, bringing that to
**2 round trips**, and a broad search runs in about **5 ms**. Because the category is
resolved before the keyword scan, a query like "what hoodies do you have?" filters
102 products down to 27 before any text matching happens. Fewer wasted queries per
chat turn means the assistant stays cheap to run as traffic grows, and consolidating
two search implementations into one means a future fix lands in both places at once.

**Verified.** "sweatshirt" → 29 crewnecks; "tee" and "t-shirt" return identical
counts; "1/4 zip" and "quarter zip" return identical counts; "what hoodies do you
have?" returns exactly the same 27 products as an explicit Hoodies filter; all 102
products categorize without falling into "Other"; the six categories sum to 102; and
`/api/products?q=sweatshirt` returns the same 29 the agent's tool does, confirming
the two share one engine.

---

## Checks

`check_tools.py` at the HW 4 root covers all four upgrades (sections K and L for the
backend pair; the frontend pair was verified in the browser as described above).

```bash
.venv/bin/python check_tools.py
```

**53 of 53 checks pass.**
