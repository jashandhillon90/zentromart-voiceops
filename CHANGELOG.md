# Refined capstone dataset — release changes

- Standardized **196** occurrences of the fictional placeholder `[COMPANY]` / `[company]` to **ZentroMart** / `zentromart` throughout source documents, CSVs and examples.
- Corrected README inventory: **244** support logs, **52** practice questions and **23** conversations (**96** turns), rather than the earlier advertised 350 / 60 / 24.
- Upgraded `lookup_order` so it does **not expose order or customer details before a caller-provided verification value is checked**. The same two exported mock tools remain available: `lookup_order` and `create_ticket`.
- Updated **25** expected verification tool-call entries in `practice/conversations.csv` to test the secure tool flow. Original customer messages, scenarios, outcomes and reference evidence are preserved.
- Added `ZIP_SCHEMA.md`, the final ZIP-schema section in `README.md`, and `validate_dataset.py` for structural and relational validation.
- Removed a duplicate outdated PDF brief and hidden `.DS_Store` / macOS metadata from the distributable ZIP.
- Preserved intentionally outdated/superseded documents, conflicting marketing language, and imperfect support logs as designed RAG evaluation challenges.
- No fictional customers, orders, order items, catalog entries, policy details, or golden answer facts were regenerated or dropped.

The dataset is a synthetic teaching resource. Fixed date: **20 October 2026**.
