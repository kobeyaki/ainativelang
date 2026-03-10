# Apple Price AINL App

This app is standalone and added without modifying existing project files.

## Files

- `apple_price.lang` - AINL source
- `build_app.sh` - emits IR/React/OpenAPI/server artifacts to this folder

## Build

From repo root:

```bash
bash user_apps/apple_price/build_app.sh
```

This generates both:

- `apple_price.ir.json` (named artifact)
- `ir.json` (runtime-compatible filename expected by emitted `server.py`)

## Launch app (API + browser)

From repo root:

```bash
python3 user_apps/apple_price/run_app.py
```

Then open:

- http://127.0.0.1:8765/ (simple UI)
- http://127.0.0.1:8765/api/apple-price (raw API JSON)

## Run validator quickly

```bash
python3 scripts/validate_ainl.py user_apps/apple_price/apple_price.lang --emit ir
```
