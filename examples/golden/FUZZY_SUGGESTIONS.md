# Fuzzy Error Suggestions for AINL Compiler

When a small model produces near-miss syntax or semantic errors, the compiler should suggest corrections rather than hard fail. This table maps error patterns to tolerant fixes.

## 1. Label & Jump Errors

| Error (model output) | Problem | Suggested Fix |
|----------------------|---------|---------------|
| `L0` without colon | Missing colon after label | Insert `:` immediately after label name |
| `L0 :` (space before colon) | Non-standard spacing | Accept and canonicalize to `L0:` |
| `J L0` written as `goto L0` | Wrong keyword | Replace `goto` with `J` |
| `L0 J L1` (missing newline/separator) | Two instructions on one line | Insert newline after label body |
| `L10:` but later `J L1` (different number format) | Inconsistent label naming | Accept mixed; canonicalize to string equality |

## 2. Adapter Target Typos

| Error | Problem | Suggested Fix |
|-------|---------|---------------|
| `R http.Get ...` (capital G) | Case mismatch | Lowercase target: `GET` → `get` (but note http expects uppercase; better canonicalize both) |
| `R http.get ...` (should be GET) | Wrong case for HTTP method | Map lowercase `get` → `GET` automatically |
| `R email.check ...` (using dot instead of space) | Wrong syntax for target | Replace `.` with space: `email.check` → `email check` |
| `R db.F` vs `db.f` | Case-sensitive target | Keep case; if unknown, suggest from adapter's target list |
| `R cache.set` vs `cache Set` | Capitalized target | Normalize to lowercase `set` |

## 3. Argument Arity Mismatches

| Error | Problem | Suggested Fix |
|-------|---------|---------------|
| `R http.GET url` missing headers optional | Accept missing optional args; fill with defaults |
| `R fs.read` with no args | Missing required path | Add placeholder: `fs.read \"\"` and flag error |
| `core.add` with 3 args | Too many | Truncate to first two; warn |
| `core.min` with 1 arg | Too few | Require at least 2; suggest `min(x, INF)` if intent is single value |

## 4. Type Confusion

| Error | Problem | Suggested Fix |
|-------|---------|---------------|
| `core.add \"5\" 10` (string + number) | Implicit coercion needed | Coerce string to number: `core.add (core.parse \"5\") 10` or auto-coerce with warning |
| `fs.write path 123` (number instead of string) | Convert to string automatically: `fs.write path (core.stringify 123)` |
| `If (req.status 200)` (missing comparison) | Likely meant equality | Change to `core.eq req.status 200` |
| `X path (core.concat \"/data/\" id)` but `id` is number | Auto-stringify args in concat: treat all as str |

## 5. Quoting & String Errors

| Error | Problem | Suggested Fix |
|-------|---------|---------------|
| `R http.GET https://example.com` (unquoted URL) | URL must be string literal or variable | If bare word, quote it; if variable, keep as is |
| `\"path\": \"/data\"` inside AINL (should be assignment) | JSON object literal in wrong place | Suggest using `X obj {\"path\":\"/data\"}` or use core.parse |
| Mismatched quotes `\"hello` (only one) | Unterminated string | Add closing quote |

## 6. Variable Scoping & Declaration

| Error | Problem | Suggested Fix |
|-------|---------|---------------|
| `X x 5` without prior `D State x:N` | Implicit state? | Recommend explicit: `D State x:N` at top; or auto-create state with warning |
| `Set counter counter+1` (using same var in expression) | Might be uninitialized | Ensure initial value exists; if not, default 0 |
| `cache.get \"state\" \"last_run\" ->last_run` (variable name same as key) | Confusing but legal | Accept; maybe rename variable for clarity |

## 7. Common Pattern Fixes

| Pattern | Issue | Auto-rewrite |
|---------|------|--------------|
| `If (status == 200) ->L1 ->L2` | `==` instead of `core.eq` | Rewrite to `If (core.eq status 200) ->L1 ->L2` |
| `If (status >= 200 && status < 300) ->L1 ->L2` | Logical `&&` not in AINL | Replace with nested If or use `core.and` if available |
| `X next i + 1` | Infix arithmetic not supported | Rewrite to `X next (core.add i 1)` |
| `R http.GET {url: endpoint}` | Passing object instead of args | Extract: `R http.GET endpoint` (args are positional) |
| `L0: R ...\nL1: R ...` without jumps | Linear fallthrough? | Accept as valid; labels are just markers. Execution flows to next label unless `J` or conditional. |

## 8. Oversight & Debugging

If compilation fails, provide:

- Exact line/column in source AINL.
- A snippet of the offending instruction.
- A suggested correction based on nearest adapter.target match (Levenshtein distance).
- Reference to the adapter registry for correct signature.

Example output:

```
Error line 12: Unknown adapter 'htp'
Did you mean 'http'?
Usage: R http.GET url [headers] ->var
```

## Implementation Hooks

Modify `compiler_v2.py` to:

1. Tokenize early and catch unrecognized adapter names → suggest closest.
2. Validate arity after parsing; for missing/extra args, insert defaults or drop extras with warnings.
3. Normalize method names for known adapters (e.g., http methods to uppercase).
4. Introduce a `--tolerant` flag that applies these rewrites automatically and emits a `suggestions.json` alongside `ir.json`.

## Philosophy

- Fail only on unrecoverable errors (syntax that cannot be guessed).
- For semantic mismatches, rewrite to something runnable and warn.
- The goal is to keep the training distribution happy and the runtime forgiving, so small models learn they can be slightly sloppy and still get a working program.
