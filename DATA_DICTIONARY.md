# Data dictionary

The pack has four parts: `kb/` (Markdown documents), `data/` (7 CSV files), `practice/` (2 CSV files) and `tools/` (the mock tools package).

In the supplied CSVs, empty cells mean "not applicable" or "not yet recorded", depending on the field. An empty refund-completion date, for example, does not mean the refund has completed. List items inside a cell are separated by ` ; `. Dates are written as YYYY-MM-DD and timestamps as YYYY-MM-DDTHH:MM.

Keep IDs, pincodes, phone numbers and refund references as text. Boolean cells contain `True` or `False`. The mock tools convert empty cells to `None`, boolean cells to booleans and numeric fields to integers, while preserving these identifiers as strings.

## kb/*.md
Each file starts with a header: `doc_id`, `title`, `doc_type` (policy, agent_guide, help, faq, marketing, meta), `audience`, `language`, `version`, `effective_from`, `status` (current or superseded), and `supersedes` / `superseded_by` where relevant. Section headings carry IDs: `## [SECTION-ID] Title`.

## data/products.csv
| Column | Meaning |
| --- | --- |
| sku | Product ID, for example ELE-0012 |
| title | Product name |
| brand | Fictional brand |
| return_category | Policy category code used in the Returns policy (RET-2) |
| price_inr | Price in rupees |
| fulfilled_by | ZentroMart or the name of a marketplace seller |
| assured | Listing shows the Assured badge (check the Marketplace sellers policy before trusting it) |
| warranty_months | Brand warranty in months |
| description | Short description |

## data/customers.csv
| Column | Meaning |
| --- | --- |
| customer_id | Customer ID, for example C100042 |
| name | Fictional name |
| phone | Synthetic phone string using the +91 5 prefix |
| email | Synthetic address on example.com |
| city, state, pincode | Home location |
| is_plus | True if a ZentroMart Plus member |
| plus_since | Date the membership started |
| preferred_language | en, hi, hi-en, ta, kn, te, mr, bn, gu or ml |
| created_at | Account creation date |

## data/orders.csv
One row per order.

| Column | Meaning |
| --- | --- |
| order_id | 8-digit order ID |
| customer_id | Links to customers.csv |
| placed_at | Date and time the order was placed |
| status | Status as of 20 October 2026 |
| payment_method | upi, card, netbanking, wallet or cod |
| delivery_type | standard, express or slot (grocery). Slot start times are not recorded; ask the customer for the time shown in My Orders before applying CAN-3. |
| delivery_pincode | Pincode the order ships to; one of the two verification fields |
| promised_date | Delivery date promised at checkout |
| shipped_on, delivered_on | Dates, if they have happened |
| delivery_attempts | Number of delivery attempts so far |
| subtotal_inr, delivery_fee_inr, cod_fee_inr, total_inr | Amounts in rupees |
| coupon_code, coupon_discount_inr, coupon_min_order_inr | Coupon used, if any |
| contacts_last_7_days | Earlier support contacts about this order in the 7 days before 20 October 2026 |
| cancellation_refund_initiated_on, cancellation_refund_method, cancellation_refund_amount_inr | Refund for a prepaid order cancelled before shipping |
| cancellation_rrn | Synthetic reference for an initiated cancellation refund; keep as text |
| rto_refund_initiated_on, rto_refund_method, rto_refund_amount_inr | Refund for a prepaid order returned to origin |
| rto_rrn | Synthetic reference for an initiated RTO refund; keep as text |
| express_late_credit_inr, express_late_credit_on | Wallet credit for a late Express delivery |
| return_sku, return_reason, return_status | The returned item, why, and where the return stands |
| return_line_no, return_qty | The item line within this order and the number of units returned. The referenced line must have the same SKU as return_sku. |
| return_requested_on, return_pickup_on, return_qc_passed_on | Return milestones |
| return_refund_initiated_on, return_refund_method, return_refund_amount_inr, return_refund_completed_on | Refund for the return |
| return_rrn | Synthetic reference for an initiated return refund; keep as text |
| return_reverse_pickup_fee_inr | Pickup fee deducted, if any |
| damage_sku, damage_issue, damage_reported_at, damage_hours_after_delivery, damage_photos_attached, damage_status | A damaged, wrong or missing item report, if any |
| timeline | Order fulfilment events in time order, for example `2026-10-01T14:27 shipped ; 2026-10-03T11:05 delivered`. Return, refund and damage milestones are in their separate columns; use status for the current overall state. |

Refund amounts are rounded to the nearest whole rupee after coupon adjustments and pickup fees. Half a rupee rounds up. Refund methods use `upi`, `card`, `netbanking`, `wallet`, `cod_wallet` or `cod_bank`; the last two mean Wallet or bank transfer for a COD order.

## data/order_items.csv
One row per item in an order.

| Column | Meaning |
| --- | --- |
| order_id | Links to orders.csv |
| line_no | Item number within the order |
| sku | Links to products.csv |
| title | Product name |
| return_category | Policy category code |
| qty | Quantity |
| unit_price_inr | Price paid per unit |

## data/pincodes.csv
city, state, pincode, metro, serviceable, cod_available, express_available (True or False).

## data/holidays.csv
date, name. Business days skip these dates and Sundays.

## data/support_logs.csv
One row per past chat or call.

| Column | Meaning |
| --- | --- |
| log_id | Log ID |
| channel | voice or chat |
| started_at | Date and time |
| language | Language present in the transcript: en, hi in Devanagari, or hi-en for mixed English and Romanized Hindi |
| customer_id, order_id | Who and which order |
| intent | What the contact was about |
| handled_by | Always human_agent |
| transcript | The conversation, one line per message, each starting with `agent:` or `customer:` |
| resolution | How it ended |
| escalated | True if handed to a senior colleague |
| csat | Customer rating, 1 to 5 |
| qa_reviewed | True if a quality reviewer checked this log |
| qa_findings | Mistakes the reviewer found; only reviewed logs are checked |

## practice/questions.csv
One row per question.

IDs are stable and may have gaps after invalid examples are removed. Do not infer row counts from the largest ID.

| Column | Meaning |
| --- | --- |
| id | Stable question ID, for example PQ0002 |
| language | en, hi (Devanagari), hi-en (Hinglish in Latin script), or another Indian language code |
| question | What the customer writes |
| asr_text | The same question as a speech-to-text transcript might come out: spelled-out numbers, missing punctuation, misheard words. Use it to test the voice feature in Step 4 |
| intent | Question type |
| expected_decision | answer, clarify, escalate or refuse |
| acceptable_decisions | Every decision a reasonable agent could take |
| answerable | False when no document covers the question |
| gold_evidence | Section IDs (and `products.csv:SKU` rows) that support the answer |
| hard_negatives | Sections a weak search is likely to return by mistake |
| must_include | Facts the reply must contain, separated by ` ; `. A fact is a number, a date, or alternatives separated by ` / ` (any one is enough) |
| must_not_include | Phrases that signal a wrong or unsafe answer |
| reference_answer | One acceptable answer |
| reply_language | Language the reply should be in |
| entities | IDs mentioned, such as `sku=ELE-0012` |
| notes | Why the question is tricky, when it is |
| needs_native_review | Whether native-speaker review of the wording is still pending. All retained questions currently have False. |

## practice/conversations.csv
One row per customer message. Rows with the same `conversation_id` form one conversation; read them in `turn` order.

Conversation IDs may have gaps. Turns within each retained conversation are consecutive, starting at 1.

| Column | Meaning |
| --- | --- |
| conversation_id | Stable conversation ID, for example PC002 |
| turn | Message number within the conversation |
| scenario | What the conversation tests |
| language | en, hi or hi-en |
| order_id, customer_id | The order and customer involved |
| customer_message | What the customer writes at this turn |
| expected_decision | answer, clarify, escalate or refuse |
| must_include, must_not_include | Same format as in questions.csv |
| expected_tool_calls | Tool calls the agent should make at this turn, for example `lookup_order(order_id=46637226)` |
| gold_evidence | Section IDs that support the reply |
| notes | What the agent should know at this turn |

For both practice files, `must_include` describes facts rather than exact wording. Every fact separated by ` ; ` is required; alternatives separated by ` / ` are equivalent. Ignore case and accept equivalent dates, spoken numbers and native-script digits. For example, `2026-10-27`, `27 October 2026` and `27 अक्टूबर 2026` express the same date. Do not require English wording in a Hindi reply. `must_not_include` describes forbidden claims; a paraphrase of a forbidden claim is still wrong. Accept any decision listed in `acceptable_decisions` for a single question. Conversation rows use `expected_decision`. Retrieval evidence uses the section IDs in `kb/` and `products.csv:SKU` for catalog rows.

## tools/tools.py
| Function | Returns |
| --- | --- |
| `lookup_order(order_id, verification_value=None)` | Without proof: `verification_required: True`, no order details. With a matching 4-digit phone suffix or 6-digit delivery pincode: `found: True`, `verified: True`, all order columns, `items`, `customer_first_name`, `is_plus` (no phone suffix returned). Invalid proof: `verified: False`, no private order details. The agent enforces one retry. |
| `create_ticket(summary, order_id=None, reason=None, intent=None)` | `created` and `ticket_id`, or `created: False` with an error if the summary is too short. Tickets are saved to `tools/tickets_created.csv` |

### Identity-check boundary
`lookup_order` must not return any order data to an unverified caller. Ask the caller for the last four registered phone digits **or** delivery pincode; pass only the submitted value to `verification_value`. `create_ticket` is a separate mock action, not proof that identity was verified. This is a synthetic training environment, not a production authentication system.
