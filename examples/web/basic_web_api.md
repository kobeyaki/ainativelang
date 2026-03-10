# Example: Basic Web API (users list)

This is a minimal v0.9 AINL program that exposes a single HTTP endpoint and reads from a database.

```text
S core web /api
E /users G ->L_users ->users

L_users:
  R db.F User * ->users
  J users
```

### Explanation

- `S core web /api` declares a web service rooted at `/api`.
- `E /users G ->L_users ->users` binds `GET /api/users` to label `L_users` and declares that the endpoint returns the variable `users`.
- `L_users` is the label implementation:
  - `R db.F User * ->users` calls the `db.F` adapter (find `User` records) and stores the result in frame variable `users`.
  - `J users` returns `users` as the endpoint output.

This example shows the **canonical pattern**:

- One `E` per route.
- One label per endpoint.
- A single `R` node followed by a terminal `J`.

