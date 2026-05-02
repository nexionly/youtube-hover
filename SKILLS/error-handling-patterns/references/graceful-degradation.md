# Graceful Degradation Pattern

Provide fallback functionality when errors occur, maintaining service availability even when components fail.

## Python Implementation

```python
from typing import Optional, Callable, TypeVar

T = TypeVar('T')

def with_fallback(
    primary: Callable[[], T],
    fallback: Callable[[], T],
    log_error: bool = True
) -> T:
    """Try primary function, fall back to fallback on error."""
    try:
        return primary()
    except Exception as e:
        if log_error:
            logger.error(f"Primary function failed: {e}")
        return fallback()

# Usage
def get_user_profile(user_id: str) -> UserProfile:
    return with_fallback(
        primary=lambda: fetch_from_cache(user_id),
        fallback=lambda: fetch_from_database(user_id)
    )

# Multiple fallbacks
def get_exchange_rate(currency: str) -> float:
    return (
        try_function(lambda: api_provider_1.get_rate(currency))
        or try_function(lambda: api_provider_2.get_rate(currency))
        or try_function(lambda: cache.get_rate(currency))
        or DEFAULT_RATE
    )

def try_function(func: Callable[[], Optional[T]]) -> Optional[T]:
    try:
        return func()
    except Exception:
        return None
```

## TypeScript Implementation

```typescript
async function withFallback<T>(
  primary: () => Promise<T>,
  fallback: () => Promise<T>,
  logError = true,
): Promise<T> {
  try {
    return await primary();
  } catch (error) {
    if (logError) {
      console.error("Primary function failed:", error);
    }
    return fallback();
  }
}

// Multiple fallbacks with priority chain
async function withFallbackChain<T>(
  ...fns: Array<() => Promise<T>>
): Promise<T> {
  for (const fn of fns) {
    try {
      return await fn();
    } catch {
      continue;
    }
  }
  throw new Error("All fallbacks exhausted");
}

// Usage
const data = await withFallbackChain(
  () => fetchFromPrimaryAPI(),
  () => fetchFromSecondaryAPI(),
  () => fetchFromCache(),
);
```

## Strategies

| Strategy | Use Case | Example |
|----------|----------|---------|
| **Cache fallback** | Primary data source down | Serve stale cached data |
| **Default values** | Config unavailable | Use sensible defaults |
| **Feature toggle** | Non-critical feature fails | Disable feature gracefully |
| **Provider chain** | Primary provider down | Switch to backup provider |
| **Reduced functionality** | Partial system failure | Serve read-only mode |
