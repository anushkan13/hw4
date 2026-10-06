"""Campus Customs backend.

FastAPI over data/campus_customs.db. Serves the product catalogue, per-product
detail with size/stock, the product images, account signup/login, and the chat route
the floating widget talks to.

Run from this folder:

    uvicorn main:app --reload --port 8000

Catalogue reads live in tools.py, shared with the agent, so there is one definition
of a product for both the website and the chat. Password hashing and session tokens
live here alongside the routes that use them.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import secrets
import sqlite3
import time
from pathlib import Path
from typing import Any

from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, EmailStr, Field

import agent as chat_agent
from models import ChatHistoryItem, ChatReply, ChatRequest, PageContext, ProductCard, ShopperContext
from tools import (
    DB_PATH,
    IMAGES_DIR,
    DatabaseMissing,
    connect as _connect,
    find_products,
    product_from_row,
    stock_by_size,
)

app = FastAPI(title="Campus Customs API", version="0.2.0")

# The Vite dev server runs on a different origin than uvicorn, so the browser needs
# CORS permission to call this API during development.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:4173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if IMAGES_DIR.exists():
    app.mount("/images", StaticFiles(directory=IMAGES_DIR), name="images")


def connect() -> sqlite3.Connection:
    """tools.connect, with the missing-database case turned into a 503 response."""
    try:
        return _connect()
    except DatabaseMissing as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@app.get("/api/health")
def health() -> dict[str, Any]:
    return {
        "status": "ok",
        "database_present": DB_PATH.exists(),
        "images_present": IMAGES_DIR.exists(),
        "agent_model": chat_agent.MODEL_NAME,
        "agent_configured": bool(os.environ.get("PORTKEY_API_KEY")),
    }


# --- catalogue ---------------------------------------------------------------
@app.get("/api/products")
def list_products(
    category: str | None = None,
    q: str | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    sort: str = "name",
) -> dict[str, Any]:
    """Catalogue listing for the Products grid.

    Runs through tools.find_products — the same search the agent's tool uses — so the
    grid and the chat apply identical category consolidation and synonyms. Searching
    "sweatshirt" here finds the same 29 crewnecks the agent would find.
    """
    total, cards = find_products(
        query=q or "",
        category=(category or ""),
        min_price=min_price,
        max_price=max_price,
        sort=sort,
    )
    products = [c.model_dump() for c in cards]
    categories = sorted({c.category for c in cards if c.category})
    return {"count": total, "categories": categories, "products": products}


@app.get("/api/products/{product_id}")
def get_product(product_id: str) -> dict[str, Any]:
    """Single product detail, including per-size stock from the inventory table."""
    con = connect()
    try:
        row = con.execute(
            "SELECT * FROM catalogue WHERE product_id = ?", (product_id,)
        ).fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail=f"No product '{product_id}'")
        sizes = stock_by_size(con, product_id)
    finally:
        con.close()

    product = product_from_row(row)
    product["sizes"] = sizes
    product["total_stock"] = sum((s["quantity"] or 0) for s in sizes)
    product["in_stock"] = product["total_stock"] > 0
    return product


# --- passwords and session tokens --------------------------------------------
# The three seeded users were created with PBKDF2-HMAC-SHA256 and stored as
#
#     pbkdf2_sha256$<salt>$<hex digest>
#
# with 120,000 iterations and the salt used as raw UTF-8 bytes. New accounts are
# written in exactly that format with the same parameters, so the seeded users keep
# working and every row in the table verifies through one code path.
#
# Plain passwords exist only as a local variable inside hash_password() and
# verify_password(). They are never stored, never returned by a route, and never
# logged.
ALGORITHM = "pbkdf2_sha256"
ITERATIONS = 120_000
SALT_BYTES = 8  # 8 bytes -> 16 hex chars, matching the seeded users' salts


def hash_password(password: str) -> str:
    """Return a storable `pbkdf2_sha256$salt$digest` string for a plain password."""
    salt = secrets.token_hex(SALT_BYTES)
    digest = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt.encode("utf-8"), ITERATIONS
    )
    return f"{ALGORITHM}${salt}${digest.hex()}"


def verify_password(password: str, stored: str | None) -> bool:
    """Check a plain password against a stored hash, in constant time."""
    if not stored:
        return False
    try:
        algorithm, salt, expected = stored.split("$")
    except ValueError:
        return False
    if algorithm != ALGORITHM:
        return False
    digest = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt.encode("utf-8"), ITERATIONS
    )
    # compare_digest avoids leaking how much of the hash matched via timing.
    return hmac.compare_digest(digest.hex(), expected)


# Stateless HMAC-signed session tokens: "<user_id>.<expiry>.<signature>". Nothing about the
# password is in the token, and a tampered id or expiry fails the signature check.
TOKEN_TTL_SECONDS = 14 * 24 * 60 * 60  # 14 days
_SECRET_FILE = Path(__file__).resolve().parent / ".session_secret"


def _load_secret() -> bytes:
    """Secret for signing tokens, from the environment or a local gitignored file.

    Persisting it means a backend restart does not log everyone out, which matters
    during development.
    """
    from_env = os.environ.get("CAMPUS_CUSTOMS_SECRET")
    if from_env:
        return from_env.encode("utf-8")
    if _SECRET_FILE.exists():
        return _SECRET_FILE.read_text().strip().encode("utf-8")
    generated = secrets.token_hex(32)
    _SECRET_FILE.write_text(generated)
    _SECRET_FILE.chmod(0o600)
    return generated.encode("utf-8")


_SECRET = _load_secret()


def _sign(payload: str) -> str:
    mac = hmac.new(_SECRET, payload.encode("utf-8"), hashlib.sha256).digest()
    return base64.urlsafe_b64encode(mac).decode("ascii").rstrip("=")


def create_token(user_id: int, ttl: int = TOKEN_TTL_SECONDS) -> str:
    payload = f"{user_id}.{int(time.time()) + ttl}"
    return f"{payload}.{_sign(payload)}"


def read_token(token: str | None) -> int | None:
    """Return the user id for a valid, unexpired token, else None."""
    if not token:
        return None
    try:
        user_id, expiry, signature = token.split(".")
    except ValueError:
        return None
    if not hmac.compare_digest(_sign(f"{user_id}.{expiry}"), signature):
        return None
    try:
        if int(expiry) < time.time():
            return None
        return int(user_id)
    except ValueError:
        return None


# --- auth routes -------------------------------------------------------------
MIN_PASSWORD_LENGTH = 8


class SignupRequest(BaseModel):
    first_name: str = Field(min_length=1, max_length=80)
    last_name: str = Field(min_length=1, max_length=80)
    email: EmailStr
    password: str = Field(min_length=MIN_PASSWORD_LENGTH, max_length=200)
    confirm_password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


def public_user(row: sqlite3.Row) -> dict[str, Any]:
    """Shape of a user as the frontend sees it. password_hash is never included."""
    first = row["first_name"] or (row["name"] or "").split(" ")[0]
    last = row["last_name"] or " ".join((row["name"] or "").split(" ")[1:])
    return {
        "id": row["id"],
        "first_name": first,
        "last_name": last,
        "name": row["name"] or f"{first} {last}".strip(),
        "email": row["email"],
        "created_at": row["created_at"],
    }


def current_user(authorization: str | None = Header(default=None)) -> dict[str, Any]:
    """Resolve the bearer token on a request into a user row, or 401."""
    token = None
    if authorization and authorization.lower().startswith("bearer "):
        token = authorization.split(" ", 1)[1].strip()
    user_id = read_token(token)
    if user_id is None:
        raise HTTPException(status_code=401, detail="Not signed in.")
    con = connect()
    try:
        row = con.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    finally:
        con.close()
    if row is None:
        raise HTTPException(status_code=401, detail="Account no longer exists.")
    return public_user(row)


@app.post("/api/auth/signup", status_code=201)
def signup(payload: SignupRequest) -> dict[str, Any]:
    if payload.password != payload.confirm_password:
        raise HTTPException(status_code=400, detail="The passwords do not match.")

    first = payload.first_name.strip()
    last = payload.last_name.strip()
    email = payload.email.strip().lower()

    con = connect()
    try:
        taken = con.execute(
            "SELECT 1 FROM users WHERE lower(email) = ?", (email,)
        ).fetchone()
        if taken:
            raise HTTPException(
                status_code=409, detail="An account with that email already exists."
            )
        # Fill every column the seeded rows use, including the legacy `name`, so new
        # accounts are indistinguishable from the originals.
        cursor = con.execute(
            """INSERT INTO users (name, email, password_hash, created_at,
                                  first_name, last_name)
               VALUES (?, ?, ?, datetime('now'), ?, ?)""",
            (f"{first} {last}".strip(), email, hash_password(payload.password),
             first, last),
        )
        con.commit()
        row = con.execute(
            "SELECT * FROM users WHERE id = ?", (cursor.lastrowid,)
        ).fetchone()
    finally:
        con.close()

    user = public_user(row)
    return {"user": user, "token": create_token(user["id"])}


@app.post("/api/auth/login")
def login(payload: LoginRequest) -> dict[str, Any]:
    con = connect()
    try:
        row = con.execute(
            "SELECT * FROM users WHERE lower(email) = ?",
            (payload.email.strip().lower(),),
        ).fetchone()
    finally:
        con.close()

    # One message for both "no such email" and "wrong password" so the endpoint does
    # not reveal which addresses have accounts.
    if row is None or not verify_password(payload.password, row["password_hash"]):
        raise HTTPException(status_code=401, detail="Incorrect email or password.")

    user = public_user(row)
    return {"user": user, "token": create_token(user["id"])}


@app.get("/api/auth/me")
def me(user: dict[str, Any] = Depends(current_user)) -> dict[str, Any]:
    """Used on page load to restore a session from a stored token."""
    return {"user": user}


@app.post("/api/auth/logout")
def logout() -> dict[str, str]:
    """Tokens are stateless, so logging out is the client discarding its token."""
    return {"status": "signed out"}


# --- chat --------------------------------------------------------------------
# The shopper only ever sees our own wording here. Provider errors can contain the
# model name and other internal details, so they are logged shape-only and replaced
# with a neutral message rather than being passed through.
CONTENT_FILTER_REPLY = (
    "Sorry — I can't help with that one. I'm here for Campus Customs shopping, so "
    "ask me about hoodies, tees, sizes, colors, or prices and I'll find you something."
)
UNAVAILABLE_REPLY = (
    "Sorry, I'm having trouble reaching the shop assistant right now. Please try "
    "again in a moment, or browse the full collection on the Products page."
)
HISTORY_LIMIT = 50  # messages replayed into the widget when a shopper returns


def optional_user(authorization: str | None = Header(default=None)) -> dict[str, Any] | None:
    """Like current_user, but returns None for guests instead of raising 401.

    The chat is open to everyone; being signed in only adds persistence and context.
    """
    try:
        return current_user(authorization)
    except HTTPException:
        return None


def resolve_page(page: PageContext) -> PageContext:
    """Fill in the product name for a product page, from the database.

    The widget only knows the slug in the URL. Looking the name up here means the
    agent is told what the shopper is actually looking at, and an unknown or made-up
    slug in the request is dropped rather than passed through to the model.
    """
    if not page.product_id:
        return page
    con = connect()
    try:
        row = con.execute(
            "SELECT name FROM catalogue WHERE product_id = ?", (page.product_id,)
        ).fetchone()
    finally:
        con.close()
    if row is None:
        return PageContext(path=page.path)
    return PageContext(path=page.path, product_id=page.product_id, product_name=row["name"])


def build_shopper_context(
    user: dict[str, Any] | None, page: PageContext
) -> ShopperContext:
    """What the agent is told about who it is talking to.

    Only these fields are passed: id, names, and email. Nothing about the password,
    the session token, or any other account internals is ever put in the deps.
    """
    if user is None:
        return ShopperContext(page=resolve_page(page))
    return ShopperContext(
        signed_in=True,
        user_id=user["id"],
        first_name=user["first_name"],
        last_name=user["last_name"],
        full_name=user["name"],
        email=user["email"],
        page=resolve_page(page),
    )


def save_message(
    user_id: int, role: str, content: str, products: list[ProductCard] | None = None
) -> None:
    """Append one turn to chat_messages for a signed-in shopper.

    Cards are stored in products_json so a replayed reply can show them again.
    """
    con = connect()
    try:
        con.execute(
            """INSERT INTO chat_messages (user_id, role, content, products_json, created_at)
               VALUES (?, ?, ?, ?, datetime('now'))""",
            (
                user_id,
                role,
                content,
                json.dumps([p.model_dump() for p in products]) if products else None,
            ),
        )
        con.commit()
    finally:
        con.close()


@app.get("/api/chat/history")
def chat_history(user: dict[str, Any] = Depends(current_user)) -> dict[str, Any]:
    """This shopper's own saved conversation, oldest first.

    Scoped by the user id from the bearer token, never by anything the client sends,
    so one shopper cannot read another's history. Guests get a 401 from current_user
    and simply start with an empty widget.
    """
    con = connect()
    try:
        rows = con.execute(
            """SELECT id, role, content, products_json, created_at
               FROM chat_messages WHERE user_id = ?
               ORDER BY id DESC LIMIT ?""",
            (user["id"], HISTORY_LIMIT),
        ).fetchall()
    finally:
        con.close()

    messages: list[ChatHistoryItem] = []
    for row in reversed(rows):  # newest N, back into chronological order
        products: list[ProductCard] = []
        if row["products_json"]:
            try:
                products = [ProductCard.model_validate(p) for p in json.loads(row["products_json"])]
            except (json.JSONDecodeError, TypeError, ValueError):
                # An old or malformed payload should not break the whole history.
                products = []
        messages.append(
            ChatHistoryItem(
                id=row["id"],
                role=row["role"],
                content=row["content"] or "",
                products=products,
                created_at=row["created_at"],
            )
        )
    return {"messages": messages}


@app.delete("/api/chat/history", status_code=204)
def clear_chat_history(user: dict[str, Any] = Depends(current_user)) -> None:
    """Let a shopper clear their own transcript. Scoped to their user id."""
    con = connect()
    try:
        con.execute("DELETE FROM chat_messages WHERE user_id = ?", (user["id"],))
        con.commit()
    finally:
        con.close()


@app.post("/api/chat")
async def chat(
    payload: ChatRequest,
    user: dict[str, Any] | None = Depends(optional_user),
) -> ChatReply:
    """One turn of the shop assistant, for the floating chat widget.

    Signed-in shoppers get their turns saved to chat_messages; guests can chat but
    nothing is persisted. Either way the agent receives a ShopperContext describing
    who is chatting and which page they are on.
    """
    deps = build_shopper_context(user, payload.page)

    try:
        reply = await chat_agent.answer(payload.message, payload.history, deps)
    except DatabaseMissing:
        raise HTTPException(
            status_code=503, detail="The product catalogue is unavailable right now."
        ) from None
    except Exception as exc:  # noqa: BLE001 - the widget always needs something to show
        text = str(exc)
        # The provider's safety filter rejects some messages outright. That is a
        # refusal, not an outage, so answer in the assistant's own voice.
        if "content_filter" in text or "content management policy" in text:
            reply = ChatReply(reply=CONTENT_FILTER_REPLY, products=[])
        elif "PORTKEY_API_KEY" in text:
            raise HTTPException(
                status_code=503,
                detail="The shopping assistant is not configured on this server.",
            ) from None
        else:
            print(f"[chat] agent call failed: {type(exc).__name__}")
            reply = ChatReply(reply=UNAVAILABLE_REPLY, products=[])

    if user is not None:
        # Persist after the turn completes, so a failed run does not leave a
        # question in the transcript with no answer beside it.
        save_message(user["id"], "user", payload.message)
        save_message(user["id"], "assistant", reply.reply, reply.products)

    return reply
