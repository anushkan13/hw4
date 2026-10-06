# Campus Customs

An AI shopping assistant for a Yale apparel storefront, built for **AI Foundations for
Managers, HW 4**.

A React + Vite + TypeScript front end, a FastAPI backend, and a PydanticAI agent
("Handsome Dan") that answers questions about products, prices, and stock by reading a
real SQLite catalogue — never by guessing.

| | |
|---|---|
| **Frontend** | React 19, Vite, TypeScript, React Router |
| **Backend** | FastAPI + Uvicorn, SQLite |
| **Agent** | PydanticAI, `gpt-5.6-luna` routed through Portkey |
| **Catalogue** | 102 products, 612 size/stock rows |

### What it does

- Browse 102 products with search, category chips, $10 price bands, and price sorting.
- Ask the chat assistant about products, prices, sizes, and stock. It answers only from
  the database, says plainly when something is sold out, and suggests similar items that
  *do* have the size you asked for.
- Matching products come back as structured data and render as clickable cards in the
  chat; clicking one opens that product's detail page while the chat stays open.
- Create an account and log in. Signed-in shoppers get their chat history saved and
  replayed, cards included, scoped so nobody can see anyone else's.
- Every agent run appends a record of its tool loop to `output/audit_trail.json`.

---

## Prerequisites

- **Python 3.11+**
- **Node.js 20+** and npm
- A **Portkey API key**
- The **data pack** — `campus_customs.db` and the product images. These are not in the
  repository (see [Data pack](#data-pack) below).

---

## Setup

### 1. Clone

```bash
git clone https://github.com/anushkan13/hw4.git
cd hw4
```

### 2. Add the data pack

The database and product photos are deliberately **not committed**. Drop them in so the
folder looks like this:

```
hw4/
  data/
    campus_customs.db
    products/
      2025-yale-vs-harvard-t-shirt.jpg
      ...
```

The backend resolves these paths relative to its own location, so nothing needs
configuring — but it will return a clear `503` if `data/campus_customs.db` is missing.

### 3. Create your `.env`

```bash
cp .env.example .env
```

Then open `.env` and set `PORTKEY_API_KEY` to your own key. Everything else has a
working default. `.env` is gitignored.

### 4. Install backend dependencies

From the `hw4` folder:

```bash
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 5. Install frontend dependencies

```bash
npm --prefix frontend install
```

---

## Running the app

Two terminals, both from the `hw4` folder.

**Terminal 1 — backend** (note: run it *from inside* `backend/`):

```bash
cd backend
uvicorn main:app --reload --reload-include "*.md" --port 8000
```

> `--reload-include "*.md"` is worth keeping: Uvicorn only watches `.py` files by
> default, so without it an edit to `prompts/prompt.md` silently has no effect until a
> manual restart. Plain `uvicorn main:app --reload --port 8000` also works.

**Terminal 2 — frontend:**

```bash
npm --prefix frontend run dev
```

Then open **http://localhost:5173**.

The frontend talks to the backend through a Vite proxy on `/api` and `/images`, so no
host is hard-coded and there are no CORS steps. Check the backend on its own at
<http://localhost:8000/api/health> — it reports whether the database, the images, and
the API key were found.

### Logging in

The seeded test account is `test@campuscustoms.yale.edu` / `password`, or create a new
account from the **Create Account** page.

---

## Project layout

```
hw4/
  AI_prompts.md          every prompt used to build this, by problem
  requirements.txt       backend Python dependencies
  .env.example           environment variables, placeholders only
  check_tools.py         73-check verification suite (backend must be running)
  README.md
  backend/
    main.py              FastAPI app: products, auth, chat routes
    agent.py             agent setup, run loop, audit trail
    tools.py             the agent's five tools + shared catalogue search
    models.py            Pydantic types: tool returns, chat output, context
    auth.py              password hashing and session tokens
    prompts/prompt.md    the agent's system prompt, including safety rules
  frontend/              Vite React TypeScript app
  output/
    harness.md           full system write-up
    design.md            the design pass
    usability.md         the four usability upgrades
    app_check.html       screenshot report of the running app
    app_check_images/
    audit_trail.json     append-only log of agent runs
  data/                  the data pack goes here (not committed)
```

Start with [`output/harness.md`](output/harness.md) — it documents the database, auth,
the agent, the tools, the safety rules, and every spec that matters, with values pulled
from the code.

---

## Verifying it works

With the backend running:

```bash
.venv/bin/python check_tools.py
```

73 checks covering tool accuracy against the database, sold-out handling, the product
card contract, chat history persistence and isolation, guest behaviour, page context,
all seven safety rules, and the audit trail.

For a visual check, open [`output/app_check.html`](output/app_check.html) in a browser —
three annotated screenshots from the running app.

---

## Data pack

`data/campus_customs.db` and `data/products/` are intentionally kept out of version
control, along with `.env` and `backend/.session_secret`. The repository contains code
and documentation only — no secrets, no database, no product photography.
