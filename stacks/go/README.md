# Go playbook

**Status:** learning, since 22 Sep 2026.

## What it is used for
Backend services, CLIs and tooling. No client project yet. Progress goes in `learning.md`.

## Conventions
Default until a real project says otherwise:
- Latest stable Go, one module per project, `gofmt` and `go vet` always, `golangci-lint` when a
  project grows.
- Standard layout: `cmd/<app>` for binaries, `internal/` for private packages; no `pkg/` until
  something is actually shared.
- Tests with the standard `testing` package, table-driven; `go test ./...` before every commit.
- Practice projects in their own folder, one per project.

## Accounts and tools
`brew install go`; Go 1.27.1 installed (checked 29 Sep 2026). Skill `skills/go-idioms/` for
reviewing Go: review-first while learning, style, naming and
error handling.

## Gotchas that became rules
| Date | What happened | Rule |
|---|---|---|

## Pointers
`skills/go-idioms/`.
