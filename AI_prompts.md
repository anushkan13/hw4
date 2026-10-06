# HW 4 — AI Prompts Log

This file records every prompt issued to the AI assistant (Claude Code) for HW 4,
organized by problem. Follow-up prompts are noted along with what was missing from
the initial prompt that made the follow-up necessary.

---

## Problem 1: Vibe Coder Prompts

### Prompt 1 (initial)

> Today, we will be working in the HW 4 folder. Navigate there, and create an AI_prompts.md. In this file, please input a section for every problem we go through, including the following for each:
>
> * The problem number and title
> * The prompts I type to you pertaining to each problem
>    * If I issue any follow-up prompts for any problem, add those too, noting one sentence regarding what was missing in my first prompt that required a follow-up to clarify, etc.
>
> This message pertains to Problem 1: Vibe Coder Prompts.
> Confirm every time I prompt you that the AI_prompts.md has been updated.
> Note that we will be using the PORTKEY_API_KEY and OpenAI models (gpt-5.6-luna, gpt-5.6-terra, gpt-5.6-sol, and gpt-6-astra). Default to gpt-5.6-luna, but keep the the smarter models as backup in case needed for harder vision steps. Always ask before ramping up models if you believe it to be necessary, and say why.

*Follow-ups: none yet.*

---

## Problem 2: Analyze the Database

### Prompt 1 (initial)

> Ok, Problem 2: Analyze the Database.
>
> I will provide this prompt in two parts. First, open and inspect the SQLite database at data/campus_customs.db. List every table, and for each table, list its columns with their types. Cover at the minimum catalogue, inventory, and users, showing a sample row of each.
> For the users table, do not print the entire password hashes; shorten, or mask them. Print all of the above to the screen here for now, so that I can see them. Do not write any files yet. Once this is done, I will follow up with the second prompt for this problem.

### Prompt 2 (follow-up — planned, not a clarification)

> Great - Part 2:
> Start the output/harness.md file - write the Database section for now, we will add to the file in other sections later on.
> For each of the four tables in the campus_customs.db file (catalogue, inventory, users, chat_messages), list its fields and add one short line per field nothing why the fields matter for the shop and/or the chatbot. Be concise and clear.
> Note further the aspects that will matter in future steps (ex: garment_type needs tidying/consolidating, any text lists that need unpacking, etc., account creation with hashed password management so that existing users can still interface with the website, etc.).
> The database file and product images are not committed to git.
> Leave output/harness.md such that more content can be added in later problems.

**Why a second prompt was needed:** None was missing — the two-part split was
intentional and announced up front. Prompt 1 deliberately scoped the work to
read-only inspection ("do not write any files yet") so the schema could be reviewed
before deciding what to document; Prompt 2 then supplied the write target, the
required per-field commentary, the forward-looking caveats, and the constraint that
the file stay open for later sections.

---

## Problem 3: Build the Campus Customs Website

### Prompt 1 (initial)

> Ok, Problem 3: Build the Campus Customs Website:
>
> Scaffold the Campus Customs storefront: a React + Vite +TypeScript front end, and a small FastAPI backend to feed it data.
>
> Appearance/vibe:
>
> * Campus Customs sells official Yale merch; keep the aesthetic aligned with white/Yale navy colors and a preppy, collegiate vibe that's clean and modern, emphasizing school spirit.
>
> Frontend:
>
> * Nav bar at the top of the page linking to:
>    * Home
>       * On this page, write the following:
>          * Headline: Yale Bulldog Pride
>          * Subheadline: Official Yale apparel and gear for students, alumni, and famillies.
>          * Introduction: Campus Customs brings Yale spirit to you with merchandise you can't wait to wear, from game-day hoodies, to every-day tees. Whether you're showing your school spirit from campus or from across the world, we help you show your pride.
>    * Products
>       * Get the products from the backend and show them as cards with the product image, name, price, and short description.
>          * Clicking on the card of each product should open that product's own page:
>             * Single product page: large image on the left side, the full product's details on the right side (description, price, available sizes with their stock when the data is there).
>       * There should also be a floating chat panel in the bottom-right corner on the overall Products page, and on single product pages. For now, just leave it as the chat interface, it does not talk to an agent yet - that will be set up to call on the backend at a later stage.
>    * About Us
>       * On this page, write the following:
>          * Campus Customs outfits the Yale community in the navy and white that Bulldogs are proud to wear. We center around the idea that Yale spirit wear should be easy to find, well-made, and welcome all those who wish to support Yale's legacy, wherever and whenever.
>          * Every piece of ours is built to last generations, upholding Yale's heritage and spirit for years to come.
>          * From New Haven to your corner of the world, we welcome you.
>    * Log In
>    * Create Account
>
> Backend (start simple in backend/main.py - this will later grow into the agent backend at a later stage):
>
> * A small, FastAPI app that reads campus_customs.db and serves the products from the catalogue table, and a product's detail including sizes/stock from the inventory table.
> * Serve the product images from data/products/ using the image paths in the catalogue (colors and tags need to be unpacked from text).
> * Frontend should read everything from this backend, ensuring that it can actually reach the backend in development.
>
> Set up a .gitignore such that data/campus_customs.db and data/products/ are never committed to git.

*Follow-ups: none yet.*

---

## Problem 3: Build the Campus Customs Website

### Prompt 1 (initial)

> Ok, Problem 3: Build the Campus Customs Website:
>
> Scaffold the Campus Customs storefront: a React + Vite +TypeScript front end, and a small FastAPI backend to feed it data.
>
> Appearance/vibe:
>
> * Campus Customs sells official Yale merch; keep the aesthetic aligned with white/Yale navy colors and a preppy, collegiate vibe that's clean and modern, emphasizing school spirit.
>
> Frontend:
>
> * Nav bar at the top of the page linking to:
>    * Home
>       * On this page, write the following:
>          * Headline: Yale Bulldog Pride
>          * Subheadline: Official Yale apparel and gear for students, alumni, and families.
>          * Introduction: Campus Customs brings Yale spirit to you with merchandise you can't wait to wear, from game-day hoodies, to every-day tees. Whether you're showing your school spirit from campus or from across the world, we help you show your pride.
>    * Products
>       * Get the products from the backend and show them as cards with the product image, name, price, and short description.
>          * Clicking on the card of each product should open that product's own page:
>             * Single product page: large image on the left side, the full product's details on the right side (description, price, available sizes with their stock when the data is there).
>    * There should also be a floating chat panel in the bottom-right corner on the on all pages of the overall site, as well. For now, just leave it as the chat interface, it does not talk to an agent yet - that will be set up to call on the backend at a later stage.
>    * About Us
>       * On this page, write the following:
>          * Campus Customs outfits the Yale community in the navy and white that Bulldogs are proud to wear. We center around the idea that Yale spirit wear should be easy to find, well-made, and welcome all those who wish to support Yale's legacy, wherever and whenever.
>          * Every piece of ours is built to last generations, upholding Yale's heritage and spirit for years to come.
>          * From New Haven to your corner of the world, we welcome you.
>    * Log In
>    * Create Account
>
> Backend (start simple in backend/main.py - this will later grow into the agent backend at a later stage):
>
> * A small, FastAPI app that reads campus_customs.db and serves the products from the catalogue table, and a product's detail including sizes/stock from the inventory table.
> * Serve the product images from data/products/ using the image paths in the catalogue (colors and tags need to be unpacked from text).
> * Frontend should read everything from this backend, ensuring that it can actually reach the backend in development.
>
> Set up a .gitignore such that data/campus_customs.db and data/products/ are never committed to git.

### Prompt 2 (follow-up — scope correction)

> Please only touch the output/harness.md when asked to do so - remove the added section for now.

**What the first prompt was missing:** Prompt 1 said nothing about `output/harness.md`
either way, and I inferred from Problem 2's "we will add to the file in other sections
later on" that the storefront should be documented there automatically — the follow-up
established that harness.md is only to be edited on explicit request.

---

## Problem 4: Create Account and Log In

### Prompt 1 (initial)

> Ok, Problem 4: Create Account and Log In:
>
> Build the create-account and login flow, connecting the Create Account and Log In pages from the frontend in the last problem to the backend.
>
> Create Account:
>
> * Contains the below fields:
>    * First Name
>    * Last Name
>    * Email
>    * Password
>    * Confirm Password
> * New accounts should be saved into the users table of the database.
> * Fill all the columns for existing users, including the older 'name' column (first + last), such that new accounts match original ones.
>
> Log In:
>
> * Email
> * Password
>    * Store passwords securely such that no one (human/AI) can read them (hashing, etc.). Never store or return the plain password, and never log it anywhere.
>    * Hash new passwords with the same method as is done for existing users.
> * After a user successfully logs in, keep them logged in, and show the user's name in the nav bar ('Hello, [first name]), and an option to log out.
>
> Test:
>
> * Test these functions in both of the below ways:
>    * Log in as the test user (test@campuscustoms.yale.edu // password).
>    * Create a new account, and log in to confirm it works
>
> Update output/harness.md denoting how authorization works - what fields are stored for a user, how they are stored, how passwords are protected, etc.

*Follow-ups: none.*

---

## Problem 5: PydanticAI Agent Backend

### Prompt 1 (initial)

> Ok, Problem 5: PydanticAI Agent Backend:
>
> Build the Campus Customs shop chatbot as a PydanticAI agent behind FastAPI, and wire it into the floating chat widget on the site. Keep the same four-file structure as was used in HW 3, all inside the backend/:
>
> * backend/prompts/prompt.md: the agent's system prompt (we will grow this more later).
>    * Here, also set the Campus Customs voice and basic safety:
>       * Voice: Friendly Campus Customs shopping assistant, welcoming and informative but speaks concisely deriving knowledge from the backend.
>       * Safety Basics: (will expand later) Only helps with Campus Customs shopping related questions, be honest, never invent information, politely decline harmful/off-topic rhetoric, never reveal internal/system details.
> * backend/agent.py: the agent setup and wiring.
> * backend/tools.py: tools the agent can call (we will grow this more later).
> * backend/models.py: the structured types.
>    * Here, set up the types for a chat reply: text reply, optional list of product cards so that the UI can show matching items on the page later.
>
> In backend/main.py (the file I run with Uvicorn), add a chat route such that a message that is sent from the website returns with a reply from the agent.
>
> Make the floating chat widget actually call the chat route and show the agent's reply.
>
> Update output/harness.md denoting how the frontend talks to the FastAPI and how the agent is loaded (prompt file, model).
>
> Make sure the backend runs from the backend/ folder with:
> uvicorn main:app --reload --port 8000
> Keep the existing products and auth routes working. Load the agent from the prompt file and my model, routed through my PORTKEY_API_KEY per my previous instructions.

*Follow-ups: none.*

---

## Problem 6: Tools: Product Info and Stock

### Prompt 1 (initial)

> Ok, Problem 6: Tools: Product Info and Stock:
>
> Since in previous steps, you built the agent with database lookup tools, please only refine rules, document them, etc. per the below specifications so that everything that is needed is covered. Do not rebuild things that already work.
>
> Ensure that the agent has tools that look up real information from campus_customs.db for:
>
> * A product description.
> * A product's price.
> * The number of items of a product in stock, by size, when a customer requests information about sizes.
>
> The agent should always derive information from the database, never invent a price or quantity, and if a size is out of stock, it should say so clearly and explicitly.
>
> Expand prompts/prompt.md such that the agent knows to call these tools whenever a customer asks about price, stock, product details, etc. and to reply on the tool results instead of guessing. Add/update the return types in models.py for the lookup results if missing anything.
>
> Update output/harness.md to list each of the tools, and list for the lookup result types which fields were included and why.
>
> Run a check to confirm all works correctly.

*Follow-ups: none.*

---

## Problem 7: Chat Search that Updates the Page

### Prompt 1 (initial)

> Ok, Problem 7: Chat Search that Updates the Page:
>
> Add the dynamic product cards feature: when a customer asks about a type of item (ex: "What hoodies do you have?"), the agent should search the catalogue and returns the matching products as structured data, and the website should show them on the chat page as product cards (image, name, price, short info).
>
> Treat the way that the agent returns product matches in its reply as a contract:
> The agent returns the structured matches, and the chat panel renders them as product cards.
>
> When a customer clicks on one of the cards in the chat, open that product's full single-item detail page (large image and full info) in the main area of the site, as in Problem 3. The chat panel can stay open; clicking a card should take the main page to that product's detail view. Reuse the existing detail page and routing so that the chat card behaves like a card on the Products page.
>
> Verify per the following:
> Ask the chat "What hoodies do you have?", confirm that the cards appear in the chat, click one, and confirm the full product detail opens in the main area.
>
> Update prompts/prompt.md such that the agent knows to return the matching products for these browsing-styled questions, and update output/harness.md to explain how search results reach the page: the agent returns structured matches, the chat route delivers them, the chat panel renders them as cards, clicking a card opens the product's detail page in the main area, etc.

*Follow-ups: none.*

---

## Problem 8: Customer Memory

### Prompt 1 (initial)

> Ok, Problem 8: Customer Memory:
>
> Add chat history persistence and give the agent context about who's chatting/what they're chatting about.
>
> Persist history for logged-in users:
>
> * Save each chat message, both the shopper's and the agent's, to the chat_messages table tied to the logged-in user. Store attached product cards too (in the appropriate table column), so past replies can show the cards again.
> * When a logged-in shopper returns and opens the chat, reload their saved history into the widget, including any product cards from previous conversations.
> * The shopped should only ever see their own history.
>
> Guests should still be able to chat, but history does not need to be saved.
>
> Tell the agent who it is talking to:
>
> * When a shopper is logged in, pass their name and email into the agent's context (agent deps, or equivalent) so that the agent knows who it is talking to. Guests have no user, but the agent should handle this gracefully.
>
> Pass page context as follows:
>
> * Send the agent the page the shopper is on, especially which product they are viewing.
>    * Ex: if someone is on a product page and asks "do you have this in pink?", the agent knows which item "this" is, and answers about that specific item from the database. If the answer is 'no' (there is no product in pink, for example), the agent should answer honestly rather than guessing. Put this page context into the agent's context with the user info.
>
> Update output/harness.md to denote how chat history is stored (the table, fields, etc.), what customer fields the agent sees, how the page context is passed to the agent, etc.
>
> Run checks.

*Follow-ups: none.*

---

## Problem 9: Usability Improvements

### Prompt 1 (initial)

> Ok, Problem 9: Usability Improvements:
>
> Improve the shop with 4 usability upgrades (2 frontend, 2 backend). Write output/usability.md as you build, with a short entry for each upgrade, denoting what was added and why it helps a Campus Customs shopper/the business. Ensure that all four successfully show up in the app.
>
> Frontend:
>
> 1. Chat starter chips: add a few tappable suggested questions in the chat panel (ex: "What hoodies do you have?", "Show me items under $50", "What t-shirts are in stock in the XL size?"), where tapping one sends it to the agent as a message. This shows shoppers initial examples of what types of questions the chatbot can answer.
> 2. Price sorting + price filtering on the Products page: let shoppers sort items by price (low to high/high to low), and provide an option to let shoppers filter by price ranges ($10 increments: $0-10, $10-20, etc.). Show this alongside the existing search box and category chips, such that it is consistent with the overall current look.
>
> Backend/Agent:
>
> 3. Sold-out size suggestions: when a shopper asks about a size that is out of stock, the agent should say that it is sold out (as already specified in previous problems), but additionally the agent should suggest similar items in the requested size that are still in stock, so that a helpful alternative is proposed instead of a dead-end.
> 4. Smarter product search (action the messy garment types that were flagged initially): The catalogue's garment types are inconsistent - same categories are spelled several ways. Reuse the consolidation of the types in Products filter chips in the agent's product search (don't duplicate) so that a chat query or search in the Products page returns the correct items completely, and finds synonyms/tags. This should overall make things run cheaper/faster.
>
> For each upgrade, add the corresponding entry to output/usability.md denoting the purpose/effect/helpful action for the customer or business.
>
> Run checks.

*Follow-ups: none.*

---

## Problem 10: Style the Website

### Prompt 1 (initial)

> Ok, Problem 10: Style the Website:
>
> Give the site a creative design pass so it feels like a real, polished Campus Customs storefront, to fulfil a "heritage varsity" aesthetic: Yale navy and white with a warm gold accent, a collegiate feel, and a friendly bulldog as the brand's mascot.
>
> Make these changes, and feel free to go further:
>
> Typography and color: pick a strong collegiate type pairing (a classic serif for headings, a clean look for body, and a bolder display font for the logo and hero). Build the palette out beyond flat navy and white with a warm gold or cream accent and some depth.
>
> Bulldog mascot: design an original, friendly bulldog motif (your own illustration or line icon, not a copy of any real university's logo or mascot) and use it as a recurring brand element: the chat assistant's avatar.  It should feel like the shop's little character.
>
> Home hero: give the home page a bold hero with the headline, a confident navy design with the mascot or a subtle pattern, and a clear call-to-action button into the shop.
>
> Product presentation: elevate the product cards. Give them a consistent image backdrop so the grid looks uniform (the catalogue photos have mixed backgrounds right now), and add a nice hover effect (a card lift and a gentle image zoom). Keep the category tag and price clear, and make the detail page feel premium too.
>
> Motion: add tasteful micro-interactions, like cards lifting on hover, content fading or sliding in as it loads, chat messages animating in, and smooth button and chip states.
>
> Chat feel: make the assistant feel like a character, with the bulldog avatar, nicely styled message bubbles, a typing indicator, and the starter chips styled to match.
>
> Add a footer with the Campus Customs brand line and a New Haven touch.
>
> Then write output/design.md: concrete and short, what you changed and why each change helps customers stick around and buy.

*Follow-ups: none.*

---

### Prompt 2 (follow-up — brand naming)

> Great - just one change: Change the bulldog's name to 'Handsome Dan' instead of Scout, so that it is more appropriate for Yale.

**What the first prompt was missing:** Prompt 1 asked for "an original, friendly
bulldog motif" without naming it, so I invented "Scout"; the follow-up supplied the
Yale-appropriate name. (The illustration itself is unchanged and still original.)

---

## Problem 11: Site Testing (App Check)

### Prompt 1 (initial)

> Ok, Problem 11: Site Testing (App Check):
> Test the live running site and document it in output/app_check.html, a page I can
> double-click to open.
>
> Capture three real screenshots from the running app, actually driving the site and
> taking them. If automating the chat interactions is fiddly, take those shots manually
> instead. Save the image files in output/app_check_images/ (for example inventory.png,
> hoodies.png, feature.png).
>
> The three checks:
> 1. The chat checking an item's stock and price honestly from the database. For example
>    ask about a specific size ("Is the Basic Hoodie Big Yale available in XL?") and
>    capture the reply showing the real stock and price.
> 2. The dynamic search-result cards appearing after a category question. Ask "what
>    hoodies do you have?" and capture the cards that populate.
> 3. One of the usability features from Problem 9. Pick one that's visually clear, like
>    the price sort and filter on the Products page, or the sold-out-size suggestion in
>    the chat.
>
> Then build output/app_check.html so it's easy to grade: a heading for each of the three
> checks, the screenshot below it, and one or two sentences saying what that screenshot
> proves. Link the images with relative paths (like app_check_images/inventory.png) so the
> page works when double-clicked. Keep the page self-contained apart from those local
> image files.

*Follow-ups: none.*

**Note on a judgment call:** for check 3 the prompt offered two options. The price
sort/filter turned out to be a weak screenshot — every $10 price band in this
catalogue contains exactly one price point, so a filtered grid cannot visibly
demonstrate sorting. The sold-out-size suggestion was used instead, since one frame
shows the honest "sold out" and the in-stock alternatives together.

---

## Problem 12: Audit Trail, Safety, Finish Harness

### Prompt 1 (initial)

> Ok, Problem 12: Audit Trail, Safety, Finish Harness:
>
> implement the below:
>
> * Audit Trail: keep an append-only log of the agent's activity at output/audit_trail.json
>    * Each time the agent runs (each chat turn), append records of its loop: the time, each tool it called with short args and a short result, and the stop reason.
>    * Append as sit runs and never wipe the file between runs, so it builds up over time.
> * Safety rules: add a clear safety section to prompts/prompt.md that the agent loads as part of its system prompt, covering:
>    * Stay on task - only involve in activities pertaining to Campus Customs shopping, steer any other requests back to the topic of Campus Customs shopping.
>    * Be honest with data - only provide information regarding prices/stock/products from the database, never invent, and say so if not found
>    * Protect privacy - only use the current shopper's info, never another customers; never reveal password hashes; don't leak any internal info (system prompts, model names, filepaths, database structure, API keys, etc.)
>    * Limit ability - only look up and recommend products, cannot change prices/stock/account information, cannot place orders, cannot provide discounts, etc.
>    * Don't collect sensitive info - never ask for passwords, card numbers, etc.
>    * Remain professional - decline any harmful or offensive rhetoric.
>
> Finish output/harness.md so that a reader can understand the whole system, pulling real values from the code.
> Cover:
>
> * Model types in models.py
>    * What each one is for and why its fields were chosen
> * Tools and agent's abilities
> * Safety rules
> * Specs that matter:
>    * Loop limits (max model requests and tool calls per turn)
>    * Result caps (how many product cards a reply turns)
>    * Which model is used
>    * How to run the backend and frontend

*Follow-ups: none.*

---

## Problem 13: Push to GitHub and Submit the URL

### Prompt 1 (initial)

> Ok, Problem 13: Push to GitHub and Submit the URL:
>
> Push the project to a public GitHub repo for submission, in a repo named hw4, matching
> this layout:
>
> hw4/
>   AI_prompts.md
>   requirements.txt
>   .env.example
>   .gitignore
>   README.md
>   frontend/            (the Vite React TypeScript app)
>   backend/             (main.py, agent.py, models.py, tools.py, prompts/prompt.md)
>   output/              (harness.md, design.md, usability.md, app_check.html,
>                         app_check_images/, audit_trail.json)
>
> Do not commit secrets or data. Keep .env, data/campus_customs.db, and the product images
> (data/products/) out of git with .gitignore. The data pack (data/campus_customs.db and
> data/products/) stays local only.
>
> Add a .env.example with the variable names and placeholder values only, no real keys (for
> example PORTKEY_API_KEY and anything else the app reads).
>
> Write README.md explaining how to run the app after someone clones it and drops the data
> pack into data/: installing backend and frontend dependencies, creating .env from
> .env.example, starting the backend (uvicorn main:app --reload --port 8000 from the backend
> folder), and starting the frontend dev server. Clear enough for a grader to clone and run.
>
> Before pushing, verify that git is not tracking and has never committed any of these: .env,
> data/campus_customs.db, data/products/, the session secret file, node_modules, or the
> virtualenv. If any were committed in an earlier commit, fix the history so they're gone,
> not just gitignored now. Confirm .env.example has placeholders only.
>
> Then create the public repo and push, and give me the repo URL.

*Follow-ups: none.*

**Repo:** https://github.com/anushkan13/hw4

---
