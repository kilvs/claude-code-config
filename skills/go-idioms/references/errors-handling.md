# Error Handling Patterns and Logging

## Table of Contents

- [The Single Handling Rule](#the-single-handling-rule)
- [Panic and Recover](#panic-and-recover)
  - [When to panic](#when-to-panic)
  - [Recovering from panics](#recovering-from-panics)
- [Logging Errors with `slog`](#logging-errors-with-slog)

## The Single Handling Rule

An error MUST be handled exactly once: either log it or return it, never both. Doing both causes duplicate log entries and makes debugging harder.

```go
// ✗ Bad: logs AND returns (duplicate noise)
func processOrder(id string) error {
    err := chargeCard(id)
    if err != nil {
        log.Printf("failed to charge card: %v", err)
        return fmt.Errorf("charging card: %w", err)
    }
    return nil
}

// ✓ Good: return with context, let the caller decide
func processOrder(id string) error {
    err := chargeCard(id)
    if err != nil {
        return fmt.Errorf("charging card for order %s: %w", id, err)
    }
    return nil
}

// ✓ Good: handle at the top level (HTTP handler, main, etc.)
func handleOrder(w http.ResponseWriter, r *http.Request) {
    err := processOrder(r.FormValue("id"))
    if err != nil {
        slog.Error("order failed", "error", err)
        http.Error(w, "internal error", http.StatusInternalServerError)
        return
    }
    w.WriteHeader(http.StatusOK)
}
```

## Panic and Recover

### When to panic

Panic MUST only be used for truly unrecoverable states: programmer errors, impossible conditions, or corrupt invariants. NEVER use panic for expected failures like network timeouts or missing files.

```go
// ✓ Acceptable: programmer error in initialization
func MustCompileRegex(pattern string) *regexp.Regexp {
    re, err := regexp.Compile(pattern)
    if err != nil {
        panic(fmt.Sprintf("invalid regex %q: %v", pattern, err))
    }
    return re
}

// ✗ Bad: panic for a normal failure
func GetUser(id string) *User {
    user, err := db.Find(id)
    if err != nil {
        panic(err) // callers cannot recover gracefully
    }
    return user
}
```

### Recovering from panics

Use `recover` in deferred functions at goroutine boundaries (HTTP handlers, worker goroutines) to prevent one panic from crashing the entire process.

```go
func safeHandler(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        defer func() {
            if r := recover(); r != nil {
                slog.Error("panic recovered",
                    "panic", r,
                    "stack", string(debug.Stack()),
                )
                http.Error(w, "internal error", http.StatusInternalServerError)
            }
        }()
        next.ServeHTTP(w, r)
    })
}
```

## Logging Errors with `slog`

Use `log/slog` (Go 1.21+) at the top level, where the error is handled:

```go
slog.Error("order failed", "error", err, "order_id", id)
```

Keep the message static and put IDs and paths in attributes. Pick the level by severity:
`Error` for failures that need attention, `Warn` for degraded but handled, `Info` for normal
events. See https://pkg.go.dev/log/slog.
