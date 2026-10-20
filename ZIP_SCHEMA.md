# Capstone Project Dataset FTTT 2026 — ZIP Schema

This is a **synthetic** dataset for a fictional Indian online retailer, **ZentroMart**. Reference date: **2026-10-20**. Data is provided as UTF-8 CSVs, indexed Markdown policy/reference articles, and offline mock Python tools. There are **no prerecorded audio files** in the archive.

## Folder and resource inventory

| Path | Type | Count | Role |
| --- | --- | ---: | --- |
| `kb/*.md` | Markdown | 21 documents | Policy-grounded RAG retrieval. Preserve metadata and section IDs. |
| `data/customers.csv` | CSV | 300 rows | Synthetic customer records; identity/Plus membership. |
| `data/orders.csv` | CSV | 1,000 rows | Orders, fulfilment, refunds, returns, damage and timeline. |
| `data/order_items.csv` | CSV | 1,783 rows | Order line items and quantities. |
| `data/products.csv` | CSV | 70 rows | Product catalog, category and warranty. |
| `data/pincodes.csv` | CSV | 36 rows | Serviceability, COD and Express delivery. |
| `data/holidays.csv` | CSV | 4 rows | Holidays excluded from business days. |
| `data/support_logs.csv` | CSV | 244 rows | Historical, imperfect human support logs; NOT policy authority. |
| `practice/questions.csv` | CSV | 52 rows | Single-turn prompts, reference answers, ASR-like text and evidence. |
| `practice/conversations.csv` | CSV | 96 rows / 23 conversations | Multi-turn contexts, verification, and expected actions. |
| `tools/tools.py` | Python | 2 exported functions | Identity-gated lookup and ticket creation. |
| `validate_dataset.py` | Python | 1 script | Offline schema/relational integrity checks. |

## Relational schema

```text
customers (customer_id PK) ──1:N──> orders (order_id PK, customer_id FK)
                                      │
                                      └──1:N──> order_items (order_id, line_no PK)
                                                      │
                                                      └──N:1──> products (sku PK)

orders.delivery_pincode ──N:1──> pincodes.pincode (PK)
customers.pincode       ──N:1──> pincodes.pincode (PK)

support_logs.order_id ──N:1──> orders.order_id
support_logs.customer_id ──N:1──> customers.customer_id

holidays.date is a standalone date/calendar reference table.
```

Keep `order_id`, `customer_id`, `sku`, `pincode`, phone values and refund reference numbers as **strings**. `line_no` distinguishes repeated items within an order. Empty fields generally mean not applicable/not recorded; see `DATA_DICTIONARY.md` for the exact definition of each of the 9 CSV schemas.

## Working sequence

1. Read `README.md` and `DATA_DICTIONARY.md`, and run `python validate_dataset.py`.
2. Load the CSV files with `pandas.read_csv(..., dtype=str, keep_default_na=False)` or Python's `csv` module; preserve IDs as text.
3. Parse and chunk `kb/*.md` while retaining header metadata and `[SECTION-ID]` headings; prioritize current policies over historical or marketing content.
4. For an order-specific request, first get `order_id`, then ask for a phone suffix (4 digits) or order delivery pincode (6 digits). Use `lookup_order(order_id, verification_value=...)` to unlock details. The unverified call cannot return private data. Allow one retry before refusing specific-order details.
5. Track conversation state, run `create_ticket()` for human handovers, and confirm a ticket only when `created=True`.
6. Evaluate with `practice/questions.csv` (including `asr_text`) and with `practice/conversations.csv` grouped by `conversation_id` and ordered by `turn`.
7. For time math use the fixed reference date **20 October 2026**. Business days are Monday–Saturday excluding `data/holidays.csv`; return eligibility uses calendar days.
8. Use your own recording to test speech in/out via Gnani; the ZIP provides textual practice, not actual voice clips.

**Note:** The sample `tools/` package is intentionally offline and **not production-grade identity verification**. Do not use the synthetic contact records or 4-digit checks for any real personal data.
