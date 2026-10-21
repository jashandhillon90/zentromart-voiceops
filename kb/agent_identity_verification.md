---
doc_id: AGT-IDV
title: Verifying the customer
doc_type: agent_guide
audience: agent
language: en
version: 1.2
effective_from: 2026-07-01
status: current
---

# Verifying the customer

## [IDV-1] When verification is needed
Before sharing anything about a specific order (status, items, address, amounts, refund details), verify the customer. General policy questions need no verification.

## [IDV-2] How to verify
Ask for the order ID, then ask for **one** of: the last 4 digits of the registered phone number, or the delivery pincode for that order. Compare with the `phone_last4` or `delivery_pincode` fields from order lookup.

## [IDV-3] If verification fails
Allow one retry. If it fails again, do not share order details. Offer general policy help and suggest the customer contact support from the registered phone number.

## [IDV-4] Never read out
Never read out the full phone number, email or street address, even to a verified customer.
