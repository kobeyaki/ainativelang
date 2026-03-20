# Example: Basic Scraper (products)

This program runs as a cron job and periodically scrapes a product list.

```text
S core cron
Cr L_scrape "0 * * * *"   # hourly

L_scrape:
  R http.Get "https://example.com/products" ->resp
  R db.C Product * ->stored
  J stored
```

### Explanation

- `S core cron` declares a cron‑driven service.
- `Cr L_scrape "0 * * * *"` schedules label `L_scrape` to run once per hour.
- In `L_scrape`:
  - `R http.Get ... ->resp` fetches the product page as `resp`.
  - `R db.C Product * ->stored` represents “store products into the `Product` table” (the compiler would normally expand `*` into concrete fields).
  - `J stored` returns the result of the `db.C` call (e.g. inserted records count).

This example demonstrates the **cron + HTTP + DB** pattern: scrape → transform/store → return.
