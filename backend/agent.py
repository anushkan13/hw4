"""Campus Customs chat agent: PydanticAI over an OpenAI model routed through Portkey.

The agent is built once at import time and reused for every chat request:

    prompt   backend/prompts/prompt.md   (read from disk, not hard-coded)
    model    gpt-5.6-luna                (override with MODEL_NAME in the root .env)
    key      PORTKEY_API_KEY             (root .env, sent to api.portkey.ai)
    tools    backend/tools.py            (AGENT_TOOLS)
    deps     models.ShopperContext       (who is chatting, and what page they are on)
    output   models.ChatReply            (reply text + optional product cards)
    audit    output/audit_trail.json     (append-only record of every run's loop)

The static prompt file carries the rules. Who the shopper is and what they are
looking at change per request, so they are added by a dynamic system prompt built
from the deps rather than being pasted into the user message.
"""

from __future__ import annotations

import json
import os
import re
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

os.environ.setdefault("PYDANTIC_AI_NO_BANNER", "1")

from dotenv import load_dotenv
from openai import AsyncOpenAI
from pydantic_ai import Agent, CallToolsNode, ModelRequestNode, RunContext
from pydantic_ai.messages import TextPart, ThinkingPart, ToolCallPart, ToolReturnPart
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai.usage import UsageLimits

from models import ChatReply, ChatTurn, ShopperContext
from tools import AGENT_TOOLS

ROOT = Path(__file__).resolve().parent
PROMPT_PATH = ROOT / "prompts" / "prompt.md"

# Look for .env in the project folder first (what a fresh clone will have), then one
# level up (the course-wide .env this was developed against). The first file found
# wins; neither is committed.
for _candidate in (ROOT.parent / ".env", ROOT.parent.parent / ".env"):
    if _candidate.exists():
        load_dotenv(_candidate)
        break

# Default model, overridable with MODEL_NAME in .env.
# Alternatives if a harder step needs more capability: gpt-5.6-terra, gpt-5.6-sol, gpt-6-astra.
MODEL_NAME = os.getenv("MODEL_NAME") or "gpt-5.6-luna"

# A sold-out answer is a two-step flow: check_size_availability, then
# find_alternatives_in_size, then the reply — each tool result costs another model
# request. Four was too tight and tripped UsageLimitExceeded on that path, so the
# budget allows the two-step lookup plus slack for a retry.
MAX_MODEL_REQUESTS = 7
MAX_TOOL_CALLS = 6

# --- audit trail -------------------------------------------------------------
AUDIT_PATH = ROOT.parent / "output" / "audit_trail.json"
AUDIT_MAX_FIELD = 160  # characters kept per logged argument or result summary
_audit_lock = threading.Lock()  # the file is appended to from concurrent requests

# A shopper may paste something they should not into the chat. The assistant refuses
# to use it, but the audit trail must not quietly become the place it gets stored —
# so long digit runs are redacted before anything is written to disk.
_CARD_LIKE = re.compile(r"\b(?:\d[ -]?){12,18}\d\b")


def redact(text: str) -> str:
    """Strip card-like digit sequences out of anything headed for the audit file."""
    return _CARD_LIKE.sub("[redacted]", text)


def _short(value: Any, limit: int = AUDIT_MAX_FIELD) -> str:
    """One-line summary of a tool argument or result, trimmed to a readable length."""
    if value is None:
        return ""
    if hasattr(value, "model_dump"):
        value = value.model_dump()
    text = value if isinstance(value, str) else json.dumps(value, default=str)
    text = redact(" ".join(text.split()))
    return text if len(text) <= limit else text[: limit - 1] + "\u2026"


def summarize_result(value: Any) -> str:
    """Describe what a tool returned without dumping the whole payload.

    The point of the audit trail is to show what the agent did, not to duplicate the
    catalogue, so list-shaped results are reduced to counts and the first few names.
    """
    if hasattr(value, "model_dump"):
        value = value.model_dump()
    if isinstance(value, dict):
        if "products" in value:
            names = [p.get("name", "?") for p in value.get("products", [])][:3]
            tail = ", ".join(names) + ("\u2026" if value.get("returned", 0) > 3 else "")
            return f"{value.get('returned', len(value.get('products', [])))} of {value.get('count', '?')} products: {tail}"
        if "categories" in value:
            return f"{len(value['categories'])} categories"
        if value.get("found") is False:
            return f"not found: {_short(value.get('error', ''), 80)}"
        if "sizes_in_stock" in value:  # ProductDetails
            return (
                f"{value.get('name', '?')} ${value.get('price')} | in stock "
                f"{value.get('sizes_in_stock')} | sold out {value.get('sizes_sold_out')}"
            )
        if "in_stock" in value and "size" in value:  # SizeAvailability
            state = "in stock" if value.get("in_stock") else "SOLD OUT"
            return f"{value.get('product_name', '?')} {value.get('size')}: {state} (qty {value.get('quantity')})"
    return _short(value)


def append_audit(record: dict[str, Any]) -> None:
    """Append one run record to output/audit_trail.json.

    The file is a JSON array that is only ever *extended*: the closing bracket is
    overwritten in place with ",<record>]", so earlier runs are never rewritten and
    never wiped. The file stays valid JSON the whole time.
    """
    blob = json.dumps(record, indent=2, default=str)
    with _audit_lock:
        AUDIT_PATH.parent.mkdir(parents=True, exist_ok=True)
        if not AUDIT_PATH.exists() or AUDIT_PATH.stat().st_size == 0:
            AUDIT_PATH.write_text(f"[\n{blob}\n]\n")
            return
        with open(AUDIT_PATH, "r+", encoding="utf-8") as fh:
            fh.seek(0, os.SEEK_END)
            end = fh.tell()
            # Walk back past trailing whitespace to the array's closing bracket.
            pos = end - 1
            while pos >= 0:
                fh.seek(pos)
                char = fh.read(1)
                if char == "]":
                    break
                if not char.isspace():
                    pos = -1
                    break
                pos -= 1
            if pos < 0:
                # Not a JSON array any more (hand-edited or truncated); start a new
                # one rather than silently losing the new record.
                fh.seek(0, os.SEEK_END)
                fh.write(f"\n[\n{blob}\n]\n")
                return
            fh.seek(pos)
            fh.write(f",\n{blob}\n]\n")
            fh.truncate()


def make_client() -> AsyncOpenAI:
    key = os.getenv("PORTKEY_API_KEY")
    if not key:
        raise RuntimeError("PORTKEY_API_KEY is missing from the root .env file")
    return AsyncOpenAI(
        api_key=key,
        base_url="https://api.portkey.ai/v1",
        default_headers={"x-portkey-api-key": key},
    )


def load_prompt() -> str:
    if not PROMPT_PATH.exists():
        raise RuntimeError(f"System prompt not found at {PROMPT_PATH}")
    return PROMPT_PATH.read_text()


def describe_shopper(deps: ShopperContext) -> str:
    """The per-request half of the system prompt: who is chatting, and from where."""
    lines: list[str] = ["## Who you are talking to right now"]

    if deps.signed_in and deps.first_name:
        lines.append(
            f"- A signed-in customer: {deps.full_name or deps.first_name} ({deps.email})."
        )
        lines.append(
            f"- You may greet them by their first name, {deps.first_name}, once at the "
            "start of a conversation. Do not read their email address back to them, and "
            "do not mention their account unless they bring it up."
        )
    else:
        lines.append(
            "- A guest who is not signed in. You do not know their name, so do not guess "
            "it or ask for it; just help them shop. Never claim to know anything about them."
        )

    if deps.page.product_id:
        name = deps.page.product_name or deps.page.product_id
        lines.append(
            f"- They are looking at the product page for \"{name}\" "
            f"(product_id: {deps.page.product_id})."
        )
        lines.append(
            "- When they say \"this\", \"it\", \"this one\", or ask about colors, sizes, "
            "price, or stock without naming a product, they mean THAT product. Call a tool "
            f"with product_id \"{deps.page.product_id}\" and answer about it specifically."
        )
        lines.append(
            "- If they ask for a color or size that product does not come in, say so "
            "plainly — the tool result is the whole truth about it. Do not guess, do not "
            "imply it might exist, and do not substitute a different product without "
            "saying that is what you are doing."
        )
    elif deps.page.path:
        where = {
            "/": "the home page",
            "/products": "the full product grid",
            "/about": "the About Us page",
            "/login": "the log-in page",
            "/create-account": "the create-account page",
        }.get(deps.page.path, f"the page {deps.page.path}")
        lines.append(f"- They are on {where}, not a specific product page.")
        lines.append(
            "- Because no single product is on screen, ask which item they mean if they "
            "say \"this\" without naming one."
        )

    return "\n".join(lines)


def build_agent() -> Agent[ShopperContext, ChatReply]:
    model = OpenAIChatModel(MODEL_NAME, provider=OpenAIProvider(openai_client=make_client()))
    agent = Agent(
        model,
        deps_type=ShopperContext,
        system_prompt=load_prompt(),
        tools=AGENT_TOOLS,
        output_type=ChatReply,
        retries=2,
    )

    @agent.system_prompt
    def shopper_context(ctx: RunContext[ShopperContext]) -> str:
        return describe_shopper(ctx.deps)

    return agent


_agent: Agent[ShopperContext, ChatReply] | None = None


def get_agent() -> Agent[ShopperContext, ChatReply]:
    """Build the agent on first use, then reuse it.

    Built lazily so that importing this module (and therefore starting the server)
    does not fail when PORTKEY_API_KEY is missing — the products and auth routes
    should keep working even if the agent cannot be configured.
    """
    global _agent
    if _agent is None:
        _agent = build_agent()
    return _agent


def format_history(history: list[ChatTurn]) -> str:
    """Fold earlier turns into the prompt so follow-ups like 'the navy one' resolve.

    The widget sends its own transcript, so the server stays stateless.
    """
    if not history:
        return ""
    lines = [
        f"{'Shopper' if turn.role == 'user' else 'You'}: {turn.content}"
        for turn in history[-8:]  # keep the last few turns; older context is rarely needed
    ]
    return "Earlier in this conversation:\n" + "\n".join(lines) + "\n\n"


async def answer(
    message: str,
    history: list[ChatTurn] | None = None,
    deps: ShopperContext | None = None,
) -> ChatReply:
    """Run one turn of the shop assistant and return its structured reply.

    `deps` carries the shopper and their current page. Guests pass a default
    ShopperContext rather than None, so the agent always has a well-formed object.

    The run is driven with `agent.iter()` rather than `agent.run()` so each step of
    the loop can be recorded: every tool call with its arguments, a short summary of
    what came back, and why the run stopped. One record per turn is appended to
    output/audit_trail.json.
    """
    deps = deps or ShopperContext()
    prompt = f"{format_history(history or [])}Shopper: {message}"

    record: dict[str, Any] = {
        "run_id": uuid.uuid4().hex[:12],
        "started_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "model": MODEL_NAME,
        # Who, but not personal details: an id is enough to trace a run, and the
        # safety rules forbid spreading a shopper's name or email around.
        "shopper": {"signed_in": deps.signed_in, "user_id": deps.user_id},
        "page": {"path": deps.page.path, "product_id": deps.page.product_id},
        "message": _short(message, 200),
        "steps": [],
        "stop_reason": "",
    }

    pending: dict[str, dict[str, Any]] = {}  # tool calls waiting for their result
    output: ChatReply | None = None

    try:
        limits = UsageLimits(
            request_limit=MAX_MODEL_REQUESTS, tool_calls_limit=MAX_TOOL_CALLS
        )
        async with get_agent().iter(prompt, deps=deps, usage_limits=limits) as run:
            async for node in run:
                if isinstance(node, CallToolsNode):
                    # The model just replied. Its visible text is the only reasoning
                    # the API exposes, so it is recorded alongside the calls it made.
                    parts = node.model_response.parts
                    thoughts = " ".join(
                        part.content
                        for part in parts
                        if isinstance(part, (TextPart, ThinkingPart))
                        and isinstance(part.content, str)
                    ).strip()
                    for call in [p for p in parts if isinstance(p, ToolCallPart)]:
                        pending[call.tool_call_id] = {
                            "tool": call.tool_name,
                            "args": {k: _short(v, 80) for k, v in call.args_as_dict().items()},
                            "agent_thoughts": _short(thoughts, 200),
                        }
                elif isinstance(node, ModelRequestNode):
                    # Tool results arrive on the next request, so steps close here.
                    for part in node.request.parts:
                        if not isinstance(part, ToolReturnPart):
                            continue
                        call = pending.pop(part.tool_call_id, {})
                        record["steps"].append(
                            {
                                "step": len(record["steps"]) + 1,
                                "at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                                "tool": call.get("tool") or part.tool_name,
                                "args": call.get("args", {}),
                                "agent_thoughts": call.get("agent_thoughts", ""),
                                "result": summarize_result(part.content),
                            }
                        )
            output = run.result.output if run.result else None

        if output is None:
            raise RuntimeError("The agent finished without producing a reply.")
        record["stop_reason"] = "completed"
        record["reply"] = _short(output.reply, 300)
        record["products_returned"] = len(output.products)
        return output

    except Exception as exc:
        # Record the failure too — an audit trail that only logs successes is not one.
        record["stop_reason"] = f"error: {type(exc).__name__}"
        record["error"] = _short(str(exc), 200)
        raise
    finally:
        record["finished_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
        record["tool_calls"] = len(record["steps"])
        try:
            append_audit(record)
        except Exception as log_exc:  # noqa: BLE001 - logging must never break a reply
            print(f"[audit] could not append record: {type(log_exc).__name__}")
