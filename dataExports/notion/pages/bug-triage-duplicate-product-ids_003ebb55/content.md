Reported by **Daniel Levi** on <mention-date start="2026-10-14"/>
## Problem
About 3% of products in the Greenleaf export share the same product ID across different stores, so sales are counted twice in the Top Products card.
## Root cause
Each store system generates its own IDs. They are only unique per store.
## Fix
- Use (store_id, product_id) as the key instead of product_id alone
- Add a test with the sample file from store #12
## Status
Fixed in the importer on Oct 16. Verified by Priya Shah.