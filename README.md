# Capstone practice dataset: ZentroMart customer support

Everything here is synthetic. ZentroMart is a fictional Indian online store. No real customers, orders, phone numbers or recordings were used. Phone numbers use an unallocated prefix (+91 5…) and every email is on example.com.

**Today's date for this dataset is 20 October 2026.** Use it for every deadline and delay calculation, not your computer's clock.

## What you're building with it

A support agent for ZentroMart that answers customers who write in by chat, email or support ticket. In Step 4 you add voice as a feature: customers can send a voice message, which your agent transcribes with Gnani STT over WebSocket, and your agent can reply with audio streamed from Gnani TTS. No prerecorded audio files are supplied. Record your own voice to test Gnani STT/TTS.

## What's in the folder

Every data file is a CSV: 9 in total. The company documents are Markdown files, because they are written documents meant to be read and searched, and the tools are one Python file.

| File | Contents | Used in |
| --- | --- | --- |
| `kb/*.md` | 21 company documents: policies, agent guides, help articles, FAQs (one in Hindi) and a marketing page | Steps 2 to 4 |
| `data/products.csv` | 70 products with return category, price, seller and warranty | Steps 2 and 3 |
| `data/customers.csv` | 300 fictional customers | Step 3, through the tools |
| `data/orders.csv` | 1,000 orders, one row each: payment, delivery, returns, refunds and a timeline | Step 3 |
| `data/order_items.csv` | What was bought in each order, one row per item, linked by `order_id` | Step 3 |
| `data/pincodes.csv` | Where ZentroMart delivers, and where cash on delivery and Express are available | Steps 2 and 3 |
| `data/holidays.csv` | The holidays that business-day counts skip | Steps 2 and 3 |
| `data/support_logs.csv` | 244 past support chats and calls handled by human agents | Optional |
| `practice/questions.csv` | 52 single questions with expected decisions, key facts, the document sections that answer them, and a speech-to-text version of each question | Steps 1, 2 and 4 |
| `practice/conversations.csv` | 23 multi-turn support conversations (96 customer-message rows), one row per customer message, with the expected behaviour at every turn | Step 3 |
| `tools/tools.py` | Two offline mock tools for identity-checked order lookup and ticket creation | Step 3 |

Field-by-field descriptions are in `DATA_DICTIONARY.md`.

## Working with the CSV files

- They open in Google Sheets or Excel, and in Python with `pandas.read_csv`. Use `dtype=str` so order IDs, pincodes and SKUs stay as text.
- Some cells hold a short list. List items are separated by ` ; ` (space, semicolon, space).
- In the `must_include` column, ` / ` separates alternatives: any one of them is enough.
- Empty cells mean "not applicable", for example no return on that order.

## The mock tools (identity-checked)

`tools/tools.py` runs locally and reads the CSV files in `data/`. No real accounts or personal information are needed. **Order details are withheld until verification succeeds.** The tool cannot securely authenticate real customers: it only simulates the capstone's identity-checking flow, with synthetic data.

```python
from tools import lookup_order, create_ticket

pending = lookup_order("8978 2837")
# -> {"verification_required": True, ...}; no private order details

# Ask the caller for the last four digits of their registered phone
# OR their delivery pincode. Never say the expected value aloud.
order = lookup_order("8978 2837", verification_value="4533")
assert order["found"] and order["verified"]
# Only NOW use order["status"], order["items"], and order["total_inr"].

ticket = create_ticket(
    summary="Verified caller reports a damaged TV on order 89782837; "
            "human review is required under the damage policy.",
    order_id="89782837", reason="high_value_damage",
)
```

- `lookup_order(order_id)` returns a verification prompt only. It does **not** return order status, items, pincode, phone details, amount, or customer information.
- `lookup_order(order_id, verification_value=...)` checks a **4-digit registered phone suffix** or **6-digit delivery pincode**, returning order details only on a match. Failed and unknown lookups do not disclose private data.
- Ask for only one verification value at a time, allow at most one retry, and do not share order details if both attempts fail. This is a rule for your conversation agent; it does not impose a persistent rate limit inside the mock tool.
- Keep verified order state in the current conversation only. Do not expose or repeat verification secrets in your response, logs, or handover summary.
- `create_ticket` records a handover in `tools/tickets_created.csv` and returns a ticket ID. Only say a ticket was created if the tool returned `created=True`. This file is generated at runtime and is not supplied in the ZIP.
- Practice conversations specify an unverified lookup when an order ID first appears and a verification lookup when the caller provides the phone suffix/pincode. See `practice/conversations.csv`.

## Things that make this realistic

Real support data is messy, and so is this. Build for it:

- **Documents disagree.** Policies, help articles, FAQs and a marketing page sometimes say different things. `kb/00_about_this_knowledge_base.md` says which one wins.
- **Policies change over time.** Every document has a `status` and an `effective_from` date in its header. Some answers depend on when an order was placed or delivered.
- **Customers don't use the documents' words.** People write "send it back" and "nobody came to collect it", while the documents say "reverse pickup". Keyword search alone will miss a lot.
- **Some answers need two sources.** A policy plus a catalog row, or a policy plus an order record.
- **Some questions have no answer** in the documents. The right reply says so and offers a human colleague.
- **Customers write in Hindi or Hinglish**, and a few in other Indian languages, while most documents are in English.
- **Timelines use business days**: Monday to Saturday, skipping the holidays in `data/holidays.csv`.
- **Verify before you share.** The agent guide `agent_identity_verification.md` explains how.
- **The support logs are not a source of truth.** They were written by human agents, and a few contain mistakes. Use them to learn how customers talk; answer from the documents.

## Section IDs

Every section heading carries an ID in square brackets, such as `## [RET-2] Return windows by category`. Keep this ID with each chunk you index, and report the IDs your agent used. That's how retrieval is scored, so you're free to chunk however you like.

## ZIP schema — folder structure, table keys and usage

The archive extracts directly into the following files and folders (no duplicate PDF or hidden macOS files):

```text
Capstone_Project_Dataset_FTTT_2026/
├── README.md                # Read first; project rules and usage
├── DATA_DICTIONARY.md       # Every CSV field, type and meaning
├── ZIP_SCHEMA.md            # Structure and relational schema overview
├── CHANGELOG.md             # Changes from the supplied draft archive
├── validate_dataset.py     # Offline, standard-library validation
├── kb/                     # 21 Markdown knowledge documents
│   ├── 00_about_this_knowledge_base.md
│   ├── agent_*.md           # Verification, conversation, escalation
│   ├── pol_*.md             # Current + superseded policies
│   ├── help_*.md, faq_*.md, mkt_*.md
├── data/                   # 7 CSV data tables
│   ├── customers.csv        # 300   PK: customer_id
│   ├── orders.csv           # 1,000 PK: order_id; FK: customer_id
│   ├── order_items.csv      # 1,783 PK: (order_id, line_no); FK: sku
│   ├── products.csv         # 70    PK: sku
│   ├── pincodes.csv         # 36    PK: pincode
│   ├── holidays.csv         # 4     PK: date
│   └── support_logs.csv     # 244   PK: log_id; references order/customer
├── practice/               # Text-only practice; no supplied audio
│   ├── questions.csv        # 52 individual questions
│   └── conversations.csv    # 96 turns across 23 conversations
└── tools/
    ├── __init__.py
    └── tools.py             # lookup_order and create_ticket
```

**Relational joins:** `customers.customer_id → orders.customer_id`, `orders.order_id → order_items.order_id`, `order_items.sku → products.sku`, and `orders.delivery_pincode → pincodes.pincode`. Customer pincodes also reference `pincodes.pincode`. The composite key for each order item is `(order_id, line_no)`. Join the logs by `order_id` and `customer_id` for optional analysis; do not treat them as policy authority.

**How to use:** Index `kb/*.md` for retrieval, retaining `[SECTION-ID]`, `status`, and `effective_from`. Use `data/*.csv` for factual lookups, `tools/` for simulated verified orders and escalations, and `practice/*.csv` for evaluation. Interpret time-dependent scenarios using **20 October 2026**, the fixed dataset reference date; exclude Sundays and listed holidays from business-day calculations. Run `python validate_dataset.py` from the extracted folder before starting.

See `ZIP_SCHEMA.md` for a concise table of join keys and `DATA_DICTIONARY.md` for every field.
