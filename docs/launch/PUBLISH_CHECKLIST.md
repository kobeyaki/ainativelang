1. Confirm final tag: `v1.1.0`
2. Confirm final release title: `AINL v1.1.0 — First Public GitHub Release (Open-Core Baseline)`
3. Confirm GitHub release body matches current repo truth
4. Create/push annotated tag if not already present
5. Publish GitHub release using the final body
6. After publish, convert `docs/issues/*.md` into actual GitHub issues
7. Group post-release issues under a practical milestone such as:

   * `Post-v1.1.0`
8. Link the published release from any relevant project channels
9. Do a final quick sanity pass on:

   * README links
   * docs index links
   * release doc links
10. Do **not** reopen semantics during release unless a concrete blocker is found
