# Safe Optimization Policy (AINL)

This policy defines how to improve benchmark results without harming AINL's primary goal:
reliable generation and execution by AI agents, including small models.

## Optimization Rule

> **Make the language easy. Make the compiler powerful.**
> Source-language optimization is allowed only when it reduces the number of
> canonical patterns a small model must learn.
> If it introduces ambiguity, equivalent parallel styles, or hidden behavior,
> reject it or keep it compatibility-only.

## Safe / Recommended Now

- Capability-driven emission (emit only what an artifact actually needs).
- Shared helper extraction and runtime support factoring in generated outputs.
- Minimal emit modes for measurement and deployment.
- IR/codegen compaction below the source-language surface.
- Benchmark redesign that separates source compactness from generated artifact size.
- Training/example bias toward strict canonical forms.
- Segregating compatibility-heavy artifacts from benchmark headlines.

## Safe But Requires Design Discipline

Only acceptable when they create one better canonical form:

- First-class constructs for frequent patterns (CRUD, auth, scrape, schedule, queue, retry).
- Reduction of repetitive label plumbing.
- Higher-level syntax only when formally constrained and unambiguous.

## Dangerous / Avoid For Now

- Multiple shorthand syntaxes for the same behavior.
- Hidden defaults in source syntax.
- Context-sensitive omission rules.
- Many equivalent ways to author the same program.
- Expanding compatibility syntax as a primary surface.
- Human-aesthetic compression that reduces model predictability.

## Small-Model Impact

Small models are helped by:

- One canonical authoring form.
- Fixed slot order and predictable line shapes.
- Explicit syntax and strict grammar.
- Low aliasing and low syntax branching.

Small models are harmed by:

- Several equally valid styles.
- Excessive shorthand.
- Ambiguous bare literals.
- Hidden semantics.
- Context-sensitive parsing expectations.

## Required Acceptance Test For Language-Surface Changes

Every language-level optimization proposal must answer:

1. Does this reduce the number of canonical patterns a small model must learn?
2. Does it preserve formal constrained decoding?
3. Does it avoid introducing an additional equivalent authoring style?
4. Can it be taught with a few examples and strict tests?
5. Is the benefit impossible to achieve purely in compiler/emitter/runtime layers?

If any answer is weak, defer the proposal.

## Recommended Order Of Implementation

### Phase 1 - Optimize Below The Language Surface

- Capability-driven emission.
- Shared runtime/helper extraction.
- Minimal emit mode.
- IR compaction.
- Benchmark methodology cleanup.
- Canonical example cleanup.

### Phase 2 - Add Canonical First-Class Constructs Carefully

Only after phase 1 is stable:

- Replace repeated verbose patterns with one canonical compact construct.
- Deprecate old verbose form over time when safe.
- Do not let old and new forms coexist equally in training/examples.

### Phase 3 - Compatibility Cleanup

- Bias corpus and examples toward canonical strict AINL.
- Keep compatibility forms only where required.
- Prevent legacy syntax from dominating benchmarks and onboarding surfaces.

## Before Optimizing AINL Source Syntax

- Can this be solved in compiler/emitter/runtime instead?
- Does this reduce or increase canonical patterns?
- Does this keep the grammar equally or more constrained?
- Would a 1B/3B model find this easier, not just shorter?
- Will docs/tests/examples overwhelmingly reinforce one canonical form?

## Benchmark Interpretation Note

Preferred benchmark improvement levers:

- Emit only needed targets.
- Factor repeated helper boilerplate.
- Shrink generated artifacts honestly.
- Compare against fair baselines.

Do not improve benchmark numbers by making source syntax cryptic or less regular.

## Alignment With Current Ownership Boundaries

- Compiler is source of truth for semantics and strict validation: `compiler_v2.py`.
- Runtime owns execution semantics: `runtime/engine.py`.
- Grammar/constraint stack owns formal admissibility:
  `compiler_grammar.py`, `grammar_constraint.py`, `grammar_priors.py`.
- Compatibility paths remain explicit and bounded:
  `runtime/compat.py`, `runtime.py`, `legacy.steps`.
