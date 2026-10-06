"""Structured types for the Campus Customs chat agent.

Two groups of types live here:

1. **Tool return types** (`ProductDetails`, `SizeStock`, `SizeAvailability`,
   `SearchResults`, `CategorySummary`). Every lookup tool returns one of these rather
   than a loose dict, so each field the agent sees is named, typed, and described.
   The descriptions are what the model reads when deciding how to use a result, so
   they say explicitly that a quantity of zero means sold out.
2. **The chat output type** (`ChatReply` + `ProductCard`). The text the shopper reads
   plus the cards the website renders beside it. Keeping the cards structured — rather
   than asking the model to describe products in prose — means the UI shows real
   catalogue data (real names, prices, images) and the model cannot invent a product
   into the grid.
3. **Conversation context** (`ShopperContext`, `PageContext`, `ChatTurn`,
   `ChatHistoryItem`). Who is chatting and what they are looking at. `ShopperContext`
   is the agent's dependency object, so the agent is told about the shopper rather
   than having to ask.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class ProductCard(BaseModel):
    """One product, shaped for display in the chat panel."""

    product_id: str = Field(description="Catalogue slug, e.g. 'basic-hoodie-big-yale'.")
    name: str = Field(description="Product name exactly as it appears in the catalogue.")
    price: float | None = Field(default=None, description="Price in US dollars.")
    garment_type: str | None = Field(
        default=None, description="Raw garment type string from the catalogue."
    )
    category: str | None = Field(
        default=None,
        description="Normalized category: Hoodies, Crewnecks, T-Shirts, Quarter-Zips, Jackets, Long Sleeves.",
    )
    short_description: str = Field(
        default="", description="One-line description for the card."
    )
    colors: list[str] = Field(default_factory=list, description="Colors the item comes in.")
    image_url: str | None = Field(
        default=None, description="Path the frontend loads the photo from, e.g. '/images/<file>.jpg'."
    )
    sizes_in_stock: list[str] = Field(
        default_factory=list, description="Sizes with quantity greater than zero."
    )


# --- tool return types -------------------------------------------------------
class SizeStock(BaseModel):
    """Stock for one size of one product, straight from the inventory table."""

    size: str = Field(description="Size label: XS, S, M, L, XL, or XXL.")
    quantity: int = Field(
        description="Units of this size currently in stock. 0 means sold out in this size."
    )
    in_stock: bool = Field(
        description="True only when quantity is greater than 0. Never say a size is "
        "available when this is false."
    )


class ProductDetails(BaseModel):
    """Everything known about one product: description, price, and per-size stock."""

    found: bool = Field(description="False when no product has the requested id.")
    error: str = Field(
        default="", description="Why the lookup failed, when found is false."
    )
    product_id: str = Field(default="", description="Catalogue slug for this product.")
    name: str = Field(default="", description="Product name exactly as catalogued.")
    description: str = Field(
        default="",
        description="The full catalogue description — cut, color, and graphic. The only "
        "product description you may use; do not add details of your own.",
    )
    price: float | None = Field(
        default=None,
        description="Price in US dollars, exactly as stored. Never round, estimate, or invent it.",
    )
    garment_type: str | None = Field(default=None, description="Raw garment type string.")
    category: str | None = Field(
        default=None,
        description="Normalized category: Hoodies, Crewnecks, T-Shirts, Quarter-Zips, Jackets, Long Sleeves.",
    )
    colors: list[str] = Field(default_factory=list, description="Colors this item comes in.")
    sizes: list[SizeStock] = Field(
        default_factory=list,
        description="Every size this product is offered in, with its stock. Sold-out sizes "
        "are included with quantity 0 so you can say explicitly that they are unavailable.",
    )
    sizes_in_stock: list[str] = Field(
        default_factory=list, description="Just the sizes a shopper can actually buy right now."
    )
    sizes_sold_out: list[str] = Field(
        default_factory=list,
        description="Sizes offered but currently at 0. Name these when a shopper asks for one.",
    )
    total_stock: int = Field(
        default=0, description="Units across all sizes. 0 means the product is sold out entirely."
    )
    in_stock: bool = Field(
        default=False, description="True when at least one size has stock."
    )
    card: "ProductCard | None" = Field(
        default=None, description="The same product shaped for display in the chat panel."
    )


class SizeAvailability(BaseModel):
    """Answer to 'do you have this in <size>?' for one product and one size."""

    found: bool = Field(description="False when no product has the requested id.")
    error: str = Field(
        default="",
        description="Why the lookup failed — unknown product, or a size this product "
        "is not offered in.",
    )
    product_id: str = Field(default="", description="Catalogue slug for this product.")
    product_name: str = Field(default="", description="Product name, for use in the reply.")
    size: str = Field(default="", description="The size that was checked.")
    in_stock: bool = Field(
        default=False,
        description="True only when this exact size has stock. When false, tell the shopper "
        "plainly that this size is sold out.",
    )
    quantity: int = Field(
        default=0, description="Units left in this size. 0 means sold out in this size."
    )
    sizes_offered: list[str] = Field(
        default_factory=list, description="Every size this product comes in."
    )
    other_sizes_in_stock: list[str] = Field(
        default_factory=list,
        description="Other sizes that do have stock — offer these when the requested size is out.",
    )


class SearchResults(BaseModel):
    """Products matching a shopper's search."""

    count: int = Field(description="How many products matched before trimming to the cap.")
    returned: int = Field(description="How many are included below.")
    products: list["ProductCard"] = Field(
        default_factory=list,
        description="The matching products. Only mention products from this list; if it is "
        "empty, say nothing matched rather than suggesting something unverified.",
    )


class CategoryCount(BaseModel):
    """One product category and how much of it the shop carries."""

    category: str = Field(description="Category name, e.g. 'Hoodies'.")
    count: int = Field(description="Products in this category.")
    from_price: float | None = Field(
        default=None, description="Cheapest price in this category, in US dollars."
    )


class CategorySummary(BaseModel):
    """What the shop carries, for orienting a shopper who has not said what they want."""

    categories: list[CategoryCount] = Field(default_factory=list)


class ChatReply(BaseModel):
    """What the chat route returns to the website for one shopper message."""

    reply: str = Field(
        description=(
            "The assistant's message to the shopper. Friendly and concise — a couple of "
            "short sentences. Do not repeat every product in prose; the cards are shown "
            "alongside this text."
        )
    )
    products: list[ProductCard] = Field(
        default_factory=list,
        description=(
            "Products to show as cards beside the reply. Only products returned by a "
            "tool in this conversation. Empty when the message is not about specific items."
        ),
    )


# --- conversation context ----------------------------------------------------
class PageContext(BaseModel):
    """Where on the site the shopper is while they type.

    The widget sends this with every message. Its point is deixis: on a product page
    "do you have this in pink?" has to resolve to a specific catalogue id.
    """

    path: str = Field(default="", description="Route the shopper is on, e.g. '/products/basic-hoodie-big-yale'.")
    product_id: str = Field(
        default="",
        description="Catalogue id of the product being viewed, when the shopper is on a "
        "product page. This is what 'this', 'it', and 'this one' refer to.",
    )
    product_name: str = Field(
        default="", description="Name of that product, for use in the reply."
    )


class ShopperContext(BaseModel):
    """The agent's dependencies: who is chatting and what they are looking at.

    Guests are represented by this object with `signed_in` false and empty names —
    never by None — so the agent always has something well-formed to read.
    """

    signed_in: bool = Field(default=False, description="False for guests.")
    user_id: int | None = Field(default=None, description="Database id, when signed in.")
    first_name: str = Field(default="", description="Shopper's first name, for greeting them.")
    last_name: str = Field(default="")
    full_name: str = Field(default="")
    email: str = Field(default="", description="Account email. Never repeat it back unprompted.")
    page: PageContext = Field(default_factory=PageContext)


class ChatTurn(BaseModel):
    """One earlier message in the conversation."""

    role: str = Field(description="'user' or 'assistant'.")
    content: str


class ChatHistoryItem(ChatTurn):
    """A stored message, as replayed into the widget when a shopper returns."""

    id: int
    products: list[ProductCard] = Field(
        default_factory=list,
        description="Cards that were attached to this reply, rebuilt from products_json.",
    )
    created_at: str | None = None


class ChatRequest(BaseModel):
    """A message posted from the floating chat widget."""

    message: str = Field(min_length=1, max_length=2000)
    history: list["ChatTurn"] = Field(
        default_factory=list,
        description="Earlier turns in this conversation, oldest first, so the agent has context.",
    )
    page: PageContext = Field(
        default_factory=PageContext,
        description="Where the shopper is on the site as they send this message.",
    )


ProductDetails.model_rebuild()
ChatHistoryItem.model_rebuild()
SearchResults.model_rebuild()
ChatRequest.model_rebuild()
