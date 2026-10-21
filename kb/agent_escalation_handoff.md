---
doc_id: AGT-ESC
title: Escalation and human handover
doc_type: agent_guide
audience: agent
language: en
version: 2.0
effective_from: 2026-07-01
status: current
---

# Escalation and human handover

## [ESC-1] When to hand over to a human
Hand over at once when any of these is true:

1. **Damaged, defective or wrong item worth more than ₹10,000.**
2. **Customer reports an order, payment or account activity they did not make.**
3. **Customer mentions legal action, a consumer court or a police complaint.**
4. **Third or later contact about the same issue within 7 days.**
5. **Refund more than 3 business days past its maximum timeline.**
6. **Customer asks for a human agent.**
7. **Product safety risk such as a swelling battery, burning smell, sparks or injury.**

For the repeat-contact rule, use the `contacts_last_7_days` field returned by order lookup. It counts earlier contacts only, not the current one. Escalate when it is 2 or more.

## [ESC-2] What to do first
Create a ticket with `create_ticket` before handing over. Tell the customer a human colleague will contact them, and never promise an outcome, amount or time beyond what a policy states.

## [ESC-3] Handover summary
The ticket summary must contain: the customer's issue, the detected intent, the order ID if any, what the customer has already told you, what you already checked, and the reason for escalation.

## [ESC-4] Things you must never do
- Promise compensation, refunds or exceptions that a policy does not allow.
- Say an action is done unless the tool call succeeded.
- Share another customer's details.
