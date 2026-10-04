---
name: go-idioms
description: "Review Go code for idiomatic style, naming and error handling, and teach the rule behind each finding. Covers early returns, declarations, nil vs empty slices, composite literals, function shape, naming (packages, stutter, getters, receivers, acronyms, constructors, enums, tests), and errors (wrapping with %w, errors.Is/As/AsType, errors.Join, sentinels vs custom types, log-or-return, panic, slog). Use when the user asks to review, explain or improve Go code, asks a Go naming or error question, or is learning Go. Review-first: while the user is learning, explain and let them fix; never edit their files unless they ask."
---

## Changes

- 29 Sep 2026: merged from samber's MIT `cc-skills-golang`
  (github.com/samber/cc-skills-golang, commit 19a0626: golang-code-style, golang-naming,
  golang-error-handling) into one review-first skill. Dropped the coding mode, the multi-agent
  audit fan-out, the file-edit tool grants and the promotion of samber/lo and samber/oops.
  Softened house opinions from MUST to SHOULD, fixed the context-variant suffix (the stdlib
  uses `Context`, as in `QueryContext`), dropped the non-standard `In` suffix. Licence in
  `LICENSE`. References in `references/` are samber's text, trimmed.

# Go idioms

## How to work

**Learning mode.** They write the code; you review it.
- Read the code, run `gofmt -l .` and `go vet ./...`, then report findings.
- For each finding: the line, what is off, the rule, and why the rule exists. A two-line
  illustration is fine; a rewrite of their function is not.
- Order findings by what teaches most: correctness and errors first, naming second, style
  last. Cap it at the five that matter; mention the count of the rest.
- Never edit their files. If they say "fix it" or "show me", do exactly that one thing.
- Praise what is already idiomatic, briefly, so the right habit sticks.
- Record what they have understood in `stacks/go/learning.md`.

**Project mode.** When the user asks Claude to write Go for a project, follow these rules in the
code and the conventions in `stacks/go/README.md`.

Rules marked MUST are Go-wide conventions (Effective Go, Go Code Review Comments, the standard
library). SHOULD marks a strong default with legitimate exceptions. Say which when you cite one.

## Errors

1. **MUST check every returned error.** Discarding with `_` needs a comment saying why.
2. **MUST wrap with context:** `fmt.Errorf("fetching user: %w", err)`. The prefix says what
   this function was doing, not "failed to" or "error".
3. **MUST keep error strings lowercase with no trailing punctuation**, acronyms included
   (`"invalid user id"`): they get concatenated into chains.
4. **`%w` inside your code, `%v` at a boundary** where callers must not depend on the cause.
5. **MUST inspect with `errors.Is` (sentinels) and `errors.As` (types)**, never `==` on a
   wrapped error or a bare type assertion. Go 1.26+: `errors.AsType[T](err)`.
6. **`errors.Join`** (1.20+) for several independent errors, e.g. validation.
7. **MUST handle an error once:** log it or return it, never both.
8. **Sentinel** (`var ErrNotFound = errors.New("user: not found")`) when callers match a
   condition; **custom type** (`type ValidationError struct{...}`) when they need data.
9. **MUST NOT panic for expected failures.** Panic is for programmer errors and broken
   invariants; `Must...` functions at init are the classic use. Recover at goroutine and
   HTTP-handler boundaries.
10. **`log/slog`** (1.21+) at the top level: a static message plus attributes
    (`slog.Error("order failed", "error", err, "order_id", id)`).
11. **Never show internal errors to users.** Translate to a safe message; log the detail.

Detail: `references/errors-creation.md`, `references/errors-wrapping.md`,
`references/errors-handling.md`.

## Naming

| Element | Convention | Example |
|---|---|---|
| Identifiers | MUST be MixedCaps, no underscores | `maxRetries`, `ParseHTTPResponse` |
| Package | MUST be lowercase, one word, singular; SHOULD NOT be `util`, `helpers`, `common` | `json`, `tabwriter` |
| File | lowercase, underscores fine | `user_handler.go` |
| Stutter | MUST NOT repeat the package name | `http.Client`, not `http.HTTPClient` |
| Constructor | `New` for a package's one main type, `NewTypeName` when several | `ring.New`, `http.NewRequest` |
| Getter | no `Get` prefix | `u.Name()`, `u.SetName()` |
| Bool method | `Is`, `Has`, `Can` | `IsValid()`, `HasPrefix()` |
| Interface | one-method interfaces take `-er` | `Reader`, `Stringer` |
| Receiver | 1 or 2 letters, same on every method, never `this` or `self` | `func (s *Server)` |
| Acronyms | all caps or all lower | `URL`, `userID`, `xmlParser` |
| Constants | MixedCaps, named for the role | `DefaultPort`, not `PORT_8080` |
| Errors | `Err` prefix for variables, `Error` suffix for types | `ErrNotFound`, `PathError` |
| Enum (iota) | type-name prefix; SHOULD put `Unknown` at 0 | `StatusUnknown`, `StatusReady` |
| Context variant | `Context` suffix | `Query` / `QueryContext` |
| Panicking variant | `Must` prefix | `regexp.MustCompile` |
| Format funcs | `f` suffix | `Errorf`, `Logf` |
| Options | `With` + field | `WithTimeout()` |
| Name length | grows with scope | `i` in a 3-line loop, `userIndex` never |
| Tests | `TestXxx`, subtests in lowercase phrases | `t.Run("empty input", ...)` |

One concept, one name across the codebase (`user` everywhere, not `user`, `account`, `u`).

Detail: `references/naming-*.md`. The bool-field prefix there (`isConnected`) is a preference,
not a rule.

## Style

- **Early return.** Handle errors and edge cases first; the happy path stays at the left edge.
- **Drop `else` after `return`, `break` or `continue`.** Assign a default, then override.
- **`switch`** over an if-else chain on the same value.
- **`var x T` for a zero value, `:=` for anything else.**
- **Nil vs empty slices:** a nil slice is fine in Go and `append` works on it. It encodes to
  JSON `null`, so SHOULD return `[]T{}` from APIs whose clients expect `[]`. Maps MUST be made
  before writing to them.
- **Composite literals** of other packages' structs MUST use field names.
- **Functions** SHOULD do one job; past about four parameters, SHOULD take an options struct.
  `ctx context.Context` MUST come first.
- **Name complex conditions** (three or more operands) with booleans, keeping expensive checks
  last for short-circuiting.
- **Values vs pointers:** small types by value; pointers to mutate, for large structs, or when
  nil means something.
- **Named returns** only when they document; no naked returns outside tiny functions.
- **`range`**, and `for i := range n` (1.22+) for counting.
- **Standard library first:** `slices`, `maps`, `strings.Builder` in loops, `strconv` for simple
  conversions, `%q` for strings in messages. "A little copying is better than a little
  dependency."
- **Generics over `any`** when a type parameter will do.
- **Unexport by default;** exporting later is easy, unexporting breaks callers.
- Formatting is `gofmt`'s job, never a review comment.

Detail: `references/style-details.md`.

## Tools

`gofmt -l .` and `go vet ./...` on every review. `staticcheck` or `golangci-lint` when the
project has them. Quote their output rather than restating it.
