"""Tools the Campus Customs agent can call, plus the catalogue data access they share.

Everything the agent knows about products comes from here, so the shared read helpers
(`connect`, `product_from_row`, …) live in this file and `main.py` imports them for
its own product routes. That keeps one definition of "what a product looks like" for
both the website and the agent, and avoids an import cycle with main.py.
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

from models import (
    CategoryCount,
    CategorySummary,
    ProductCard,
    ProductDetails,
    SearchResults,
    SizeAvailability,
    SizeStock,
)

# --- paths -------------------------------------------------------------------
# Resolved relative to this file, not the process working directory, so the app
# behaves the same however uvicorn is launched.
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "campus_customs.db"
IMAGES_DIR = DATA_DIR / "products"

SIZE_ORDER = ["XS", "S", "M", "L", "XL", "XXL"]
MAX_RESULTS = 8  # cap on products handed back to the model in one tool call

# The catalogue has 22 raw garment_type strings for ~6 real categories. Map them to
# a canonical label for filtering while keeping the original for display.
GARMENT_CATEGORIES = [
    ("hood", "Hoodies"),
    ("quarter-zip", "Quarter-Zips"),
    ("jacket", "Jackets"),
    ("fleece", "Jackets"),
    ("long-sleeve", "Long Sleeves"),
    ("t-shirt", "T-Shirts"),
    ("crewneck", "Crewnecks"),
    ("crew-neck", "Crewnecks"),
    ("mockneck", "Crewnecks"),
    ("sweatshirt", "Crewnecks"),
]

# The words shoppers actually type, mapped onto the canonical categories above.
# "sweatshirt", "crew neck", and "pullover" all mean Crewnecks here; without this a
# search for "sweatshirt" misses 26 crewnecks whose garment_type never uses the word.
CATEGORY_SYNONYMS: dict[str, str] = {
    "hoodie": "Hoodies", "hoodies": "Hoodies", "hood": "Hoodies",
    "hooded": "Hoodies", "sweatshirt with a hood": "Hoodies",
    "crewneck": "Crewnecks", "crewnecks": "Crewnecks", "crew neck": "Crewnecks",
    "crew": "Crewnecks", "sweatshirt": "Crewnecks", "sweatshirts": "Crewnecks",
    "sweater": "Crewnecks", "mockneck": "Crewnecks", "pullover": "Crewnecks",
    "tshirt": "T-Shirts", "t-shirt": "T-Shirts", "t shirt": "T-Shirts",
    "tshirts": "T-Shirts", "t-shirts": "T-Shirts", "tee": "T-Shirts",
    "tees": "T-Shirts", "shirt": "T-Shirts", "shirts": "T-Shirts",
    "quarter zip": "Quarter-Zips", "quarter-zip": "Quarter-Zips",
    "quarterzip": "Quarter-Zips", "1/4 zip": "Quarter-Zips",
    "quarter zips": "Quarter-Zips", "half zip": "Quarter-Zips",
    "jacket": "Jackets", "jackets": "Jackets", "fleece": "Jackets",
    "bomber": "Jackets", "coat": "Jackets", "full zip": "Jackets",
    "long sleeve": "Long Sleeves", "long-sleeve": "Long Sleeves",
    "longsleeve": "Long Sleeves", "long sleeves": "Long Sleeves",
    "performance shirt": "Long Sleeves",
}

# Words that carry no signal in a catalogue where everything is Yale apparel.
SEARCH_STOPWORDS = {
    "a", "an", "and", "the", "of", "for", "with", "in", "on", "to", "me", "my",
    "do", "does", "you", "your", "have", "has", "any", "some", "show", "find",
    "looking", "look", "want", "need", "get", "something", "anything", "please",
    "what", "whats", "which", "there", "is", "are", "im", "i", "id", "like",
    "campus", "customs", "yale", "merch", "merchandise", "apparel", "item", "items",
    "product", "products", "size", "sizes", "under", "over", "buy", "shop",
}


def canonical_category(text: str | None) -> str:
    """Map whatever the shopper typed onto one of the six canonical categories.

    Accepts a category name ("Hoodies"), a synonym ("sweatshirt"), or a raw
    garment_type string. Returns "" when nothing matches.
    """
    raw = (text or "").strip().lower()
    if not raw:
        return ""
    for label in ("Hoodies", "Crewnecks", "T-Shirts", "Quarter-Zips", "Jackets", "Long Sleeves"):
        if raw == label.lower():
            return label
    if raw in CATEGORY_SYNONYMS:
        return CATEGORY_SYNONYMS[raw]
    # Longest phrases first, so "long sleeve" wins over "sleeve".
    for phrase in sorted(CATEGORY_SYNONYMS, key=len, reverse=True):
        if phrase in raw:
            return CATEGORY_SYNONYMS[phrase]
    guess = categorize(raw)
    return "" if guess == "Other" else guess


def split_query(query: str) -> tuple[str, list[str]]:
    """Pull a category out of free text and return it with the remaining keywords.

    "what hoodies do you have" -> ("Hoodies", []) rather than a literal search for
    the word "hoodies", which would miss every product whose garment_type says
    "pullover hoodie" but whose text never repeats the word.
    """
    raw = (query or "").strip().lower()
    if not raw:
        return "", []
    found = ""
    for phrase in sorted(CATEGORY_SYNONYMS, key=len, reverse=True):
        if phrase in raw:
            found = CATEGORY_SYNONYMS[phrase]
            raw = raw.replace(phrase, " ")
            break
    words = [
        w.strip(".,!?'\"")
        for w in raw.split()
        if w.strip(".,!?'\"") and w.strip(".,!?'\"") not in SEARCH_STOPWORDS
    ]
    return found, words


class DatabaseMissing(RuntimeError):
    """Raised when campus_customs.db is not on disk; it is not committed to git."""


def categorize(garment_type: str | None) -> str:
    raw = (garment_type or "").lower()
    for needle, label in GARMENT_CATEGORIES:
        if needle in raw:
            return label
    return "Other"


# --- data access -------------------------------------------------------------
def connect() -> sqlite3.Connection:
    if not DB_PATH.exists():
        raise DatabaseMissing(
            f"Database not found at {DB_PATH}. It is not committed to git — "
            "place campus_customs.db in the data/ folder."
        )
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    return con


def load_json_list(value: Any) -> list[str]:
    """colors and search_tags are JSON arrays stored as TEXT; unpack defensively."""
    if not value:
        return []
    if isinstance(value, list):
        return [str(v) for v in value]
    try:
        parsed = json.loads(value)
    except (json.JSONDecodeError, TypeError):
        # Fall back to a comma-separated reading rather than dropping the data.
        return [part.strip() for part in str(value).split(",") if part.strip()]
    if isinstance(parsed, list):
        return [str(v) for v in parsed]
    return [str(parsed)]


def short_description(description: str | None, limit: int = 120) -> str:
    text = (description or "").strip()
    if len(text) <= limit:
        return text
    return text[: text.rfind(" ", 0, limit)].rstrip(",;:") + "…"


def image_url(image_file_path: str | None) -> str | None:
    """catalogue.image_file_path is relative to data/, e.g. products/<id>.jpg."""
    if not image_file_path:
        return None
    return "/images/" + Path(image_file_path).name


def product_from_row(row: sqlite3.Row) -> dict[str, Any]:
    return {
        "product_id": row["product_id"],
        "name": row["name"],
        "garment_type": row["garment_type"],
        "category": categorize(row["garment_type"]),
        "description": row["description"],
        "short_description": short_description(row["description"]),
        "colors": load_json_list(row["colors"]),
        "search_tags": load_json_list(row["search_tags"]),
        "image_url": image_url(row["image_file_path"]),
        "price": row["price"],
    }


def stock_by_size(con: sqlite3.Connection, product_id: str) -> list[dict[str, Any]]:
    """Per-size stock in garment order, keeping sold-out sizes visible."""
    rows = con.execute(
        "SELECT size, quantity FROM inventory WHERE product_id = ?", (product_id,)
    ).fetchall()
    by_size = {r["size"]: r["quantity"] for r in rows}
    sizes = [
        {"size": s, "quantity": by_size[s], "in_stock": (by_size[s] or 0) > 0}
        for s in SIZE_ORDER
        if s in by_size
    ]
    sizes += [
        {"size": s, "quantity": q, "in_stock": (q or 0) > 0}
        for s, q in by_size.items()
        if s not in SIZE_ORDER
    ]
    return sizes


def to_card(row: sqlite3.Row, sizes: list[dict[str, Any]] | None = None) -> ProductCard:
    """Catalogue row -> the card shape the chat panel renders."""
    product = product_from_row(row)
    return ProductCard(
        product_id=product["product_id"],
        name=product["name"],
        price=product["price"],
        garment_type=product["garment_type"],
        category=product["category"],
        short_description=product["short_description"],
        colors=product["colors"],
        image_url=product["image_url"],
        sizes_in_stock=[s["size"] for s in (sizes or []) if s["in_stock"]],
    )


# --- agent tools -------------------------------------------------------------
# Each tool returns real catalogue rows. The agent is told to answer only from what
# these return, so a product can never be invented into a reply.


def all_stock() -> dict[str, list[dict[str, Any]]]:
    """Per-size stock for every product, in one query.

    Previously each candidate product cost its own SELECT against inventory; one
    pass over 612 rows replaces up to 102 round trips, which is what makes a broad
    search cheap enough to run on every chat turn.
    """
    con = connect()
    try:
        rows = con.execute(
            "SELECT product_id, size, quantity FROM inventory"
        ).fetchall()
    finally:
        con.close()

    order = {s: i for i, s in enumerate(SIZE_ORDER)}
    grouped: dict[str, list[dict[str, Any]]] = {}
    for r in rows:
        grouped.setdefault(r["product_id"], []).append(
            {"size": r["size"], "quantity": r["quantity"], "in_stock": (r["quantity"] or 0) > 0}
        )
    for sizes in grouped.values():
        sizes.sort(key=lambda s: order.get(s["size"], len(order)))
    return grouped


def find_products(
    query: str = "",
    category: str = "",
    color: str = "",
    min_price: float | None = None,
    max_price: float | None = None,
    in_stock_only: bool = False,
    size: str = "",
    exclude_product_id: str = "",
    sort: str = "name",
    limit: int | None = None,
) -> tuple[int, list[ProductCard]]:
    """The one catalogue search in the app.

    Both the agent's `search_products` tool and the website's /api/products route
    call this, so a chat query and a Products-page query apply exactly the same
    category consolidation and synonym handling. Returns (total matched, cards).
    """
    query_category, keywords = split_query(query)
    wanted_category = canonical_category(category) or query_category
    wanted_color = color.strip().lower()
    wanted_size = size.strip().upper()

    con = connect()
    try:
        rows = con.execute(
            "SELECT * FROM catalogue ORDER BY name COLLATE NOCASE"
        ).fetchall()
    finally:
        con.close()
    stock = all_stock()

    matched: list[tuple[dict[str, Any], sqlite3.Row, list[dict[str, Any]]]] = []
    for row in rows:
        product = product_from_row(row)
        if product["product_id"] == exclude_product_id:
            continue
        if wanted_category and product["category"] != wanted_category:
            continue
        if wanted_color and not any(wanted_color in c.lower() for c in product["colors"]):
            continue
        price = product["price"] or 0
        if min_price is not None and price < min_price:
            continue
        if max_price is not None and price > max_price:
            continue

        sizes = stock.get(product["product_id"], [])
        if in_stock_only and not any(s["in_stock"] for s in sizes):
            continue
        if wanted_size and not any(
            s["size"].upper() == wanted_size and s["in_stock"] for s in sizes
        ):
            continue

        if keywords:
            # Tags and the garment type are included, so "bulldog" finds products
            # tagged bulldog even when the name never says it.
            haystack = " ".join(
                [
                    product["name"] or "",
                    product["description"] or "",
                    " ".join(product["search_tags"]),
                    " ".join(product["colors"]),
                    product["garment_type"] or "",
                    product["category"],
                ]
            ).lower()
            if not all(word in haystack for word in keywords):
                continue

        matched.append((product, row, sizes))

    if sort == "price-asc":
        matched.sort(key=lambda m: (m[0]["price"] is None, m[0]["price"] or 0))
    elif sort == "price-desc":
        matched.sort(key=lambda m: (m[0]["price"] is None, -(m[0]["price"] or 0)))

    cards = [to_card(row, sizes) for _, row, sizes in matched[: limit or len(matched)]]
    return len(matched), cards


def search_products(
    query: str = "",
    category: str = "",
    color: str = "",
    max_price: float | None = None,
    min_price: float | None = None,
    in_stock_only: bool = False,
    size: str = "",
) -> SearchResults:
    """Search the Campus Customs catalogue.

    Understands the words shoppers actually use: "sweatshirt" finds crewnecks,
    "tee" finds T-shirts, "quarter zip" and "1/4 zip" both work. You can also pass a
    whole question as `query` ("what hoodies do you have?") and the category will be
    picked out of it.

    Args:
        query: Free text matched against name, description, search tags, colors, and
            garment type, e.g. "Harvard game", "bulldog", "sweatshirt".
        category: Hoodies, Crewnecks, T-Shirts, Quarter-Zips, Jackets, or Long
            Sleeves — or any common synonym. Leave empty for all categories.
        color: A color to filter on, e.g. "navy blue", "heather gray", "white".
        max_price: Only return products at or below this price in US dollars.
        min_price: Only return products at or above this price in US dollars.
        in_stock_only: When true, drop products that are sold out in every size.
        size: Only return products that have stock in this size, e.g. "XL".

    Returns:
        A SearchResults: how many products matched, and up to 8 of them with their
        real catalogue name, price, colors, and the sizes currently in stock. Only
        talk about products in this list.
    """
    total, cards = find_products(
        query=query,
        category=category,
        color=color,
        min_price=min_price,
        max_price=max_price,
        in_stock_only=in_stock_only,
        size=size,
        limit=MAX_RESULTS,
    )
    return SearchResults(count=total, returned=len(cards), products=cards)


def get_product_details(product_id: str) -> ProductDetails:
    """Look up one product by its catalogue id, with full description and per-size stock.

    Args:
        product_id: The catalogue slug, e.g. "basic-hoodie-big-yale". Use the
            product_id returned by search_products.

    Returns:
        A ProductDetails: the catalogue description, the exact price, the colors, and
        stock for every size including the ones at zero. `found` is false, with a
        reason in `error`, when no product has that id.
    """
    con = connect()
    try:
        row = con.execute(
            "SELECT * FROM catalogue WHERE product_id = ?", (product_id,)
        ).fetchone()
        if row is None:
            return ProductDetails(
                found=False, error=f"No product with id '{product_id}'."
            )
        sizes = stock_by_size(con, product_id)
    finally:
        con.close()

    product = product_from_row(row)
    size_stock = [
        SizeStock(size=s["size"], quantity=s["quantity"] or 0, in_stock=s["in_stock"])
        for s in sizes
    ]
    return ProductDetails(
        found=True,
        product_id=product["product_id"],
        name=product["name"],
        description=product["description"] or "",
        price=product["price"],
        garment_type=product["garment_type"],
        category=product["category"],
        colors=product["colors"],
        sizes=size_stock,
        # Split out explicitly so the agent does not have to reason about which
        # quantities are zero before telling a shopper what is sold out.
        sizes_in_stock=[s.size for s in size_stock if s.in_stock],
        sizes_sold_out=[s.size for s in size_stock if not s.in_stock],
        total_stock=sum(s.quantity for s in size_stock),
        in_stock=any(s.in_stock for s in size_stock),
        card=to_card(row, sizes),
    )


def check_size_availability(product_id: str, size: str) -> SizeAvailability:
    """Check whether one product is in stock in one size.

    Args:
        product_id: The catalogue slug, e.g. "basic-hoodie-big-yale".
        size: One of XS, S, M, L, XL, XXL.

    Returns:
        A SizeAvailability: whether that exact size is in stock and how many are left,
        plus the other sizes that do have stock. When `in_stock` is false, tell the
        shopper plainly that the size is sold out.
    """
    con = connect()
    try:
        row = con.execute(
            "SELECT name FROM catalogue WHERE product_id = ?", (product_id,)
        ).fetchone()
        if row is None:
            return SizeAvailability(
                found=False,
                product_id=product_id,
                size=size.strip().upper(),
                error=f"No product with id '{product_id}'.",
            )
        sizes = stock_by_size(con, product_id)
    finally:
        con.close()

    wanted = size.strip().upper()
    match = next((s for s in sizes if s["size"].upper() == wanted), None)
    offered = [s["size"] for s in sizes]
    if match is None:
        return SizeAvailability(
            found=False,
            product_id=product_id,
            product_name=row["name"],
            size=wanted,
            error=f"'{wanted}' is not a size this product comes in.",
            sizes_offered=offered,
            other_sizes_in_stock=[s["size"] for s in sizes if s["in_stock"]],
        )
    return SizeAvailability(
        found=True,
        product_id=product_id,
        product_name=row["name"],
        size=match["size"],
        in_stock=match["in_stock"],
        quantity=match["quantity"] or 0,
        sizes_offered=offered,
        other_sizes_in_stock=[
            s["size"] for s in sizes if s["in_stock"] and s["size"] != match["size"]
        ],
    )


def list_categories() -> CategorySummary:
    """List the product categories the shop carries, with how many items are in each.

    Returns:
        A CategorySummary: each category with its product count and cheapest price, so
        a shopper who has not said what they want can be oriented.
    """
    con = connect()
    try:
        rows = con.execute("SELECT * FROM catalogue").fetchall()
    finally:
        con.close()

    summary: dict[str, CategoryCount] = {}
    for row in rows:
        label = categorize(row["garment_type"])
        entry = summary.setdefault(label, CategoryCount(category=label, count=0))
        entry.count += 1
        price = row["price"]
        if price is not None and (entry.from_price is None or price < entry.from_price):
            entry.from_price = price

    return CategorySummary(
        categories=sorted(summary.values(), key=lambda c: -c.count)
    )


def find_alternatives_in_size(product_id: str, size: str) -> SearchResults:
    """Find similar items that ARE in stock in a size, when the asked-for one is not.

    Call this straight after `check_size_availability` comes back sold out, so the
    shopper gets a real alternative instead of a dead end.

    Args:
        product_id: The catalogue slug of the item that is sold out in their size.
        size: The size they want, e.g. "XL". Every product returned has stock in it.

    Returns:
        A SearchResults of same-category products with stock in that size, nearest
        in price first. Empty when nothing in that category has the size.
    """
    con = connect()
    try:
        row = con.execute(
            "SELECT * FROM catalogue WHERE product_id = ?", (product_id,)
        ).fetchone()
    finally:
        con.close()
    if row is None:
        return SearchResults(count=0, returned=0, products=[])

    source = product_from_row(row)
    total, cards = find_products(
        category=source["category"],
        size=size,
        in_stock_only=True,
        exclude_product_id=product_id,
    )
    # Nearest in price first: someone looking at a $68 hoodie wants another $68
    # hoodie, not the $98 one.
    base = source["price"] or 0
    cards.sort(key=lambda c: abs((c.price or 0) - base))
    cards = cards[:4]
    return SearchResults(count=total, returned=len(cards), products=cards)


AGENT_TOOLS = [
    search_products,
    get_product_details,
    check_size_availability,
    find_alternatives_in_size,
    list_categories,
]
