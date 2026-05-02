# Error Recovery Strategies

Comprehensive recovery patterns for different failure scenarios.

## Table of Contents

- [Retry Strategies](#retry-strategies)
- [Timeout Handling](#timeout-handling)
- [Idempotency](#idempotency)
- [Dead Letter Queues](#dead-letter-queues)
- [Compensation / Saga Pattern](#compensation--saga-pattern)

## Retry Strategies

### Exponential Backoff with Jitter

```python
import random
import time

def retry_with_jitter(func, max_attempts=5, base_delay=1.0):
    for attempt in range(max_attempts):
        try:
            return func()
        except Exception as e:
            if attempt == max_attempts - 1:
                raise
            delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
            time.sleep(delay)
```

### Retry Budget

Limit total retries across a time window to prevent thundering herd:

```python
class RetryBudget:
    def __init__(self, max_retries_per_second: float = 10.0):
        self.tokens = max_retries_per_second
        self.max_tokens = max_retries_per_second
        self.last_refill = time.monotonic()

    def can_retry(self) -> bool:
        self._refill()
        if self.tokens >= 1:
            self.tokens -= 1
            return True
        return False

    def _refill(self):
        now = time.monotonic()
        elapsed = now - self.last_refill
        self.tokens = min(self.max_tokens, self.tokens + elapsed * self.max_tokens)
        self.last_refill = now
```

## Timeout Handling

Always set timeouts and handle them explicitly:

```python
import asyncio

async def fetch_with_timeout(url: str, timeout: float = 5.0):
    try:
        async with asyncio.timeout(timeout):
            return await fetch(url)
    except asyncio.TimeoutError:
        logger.warning(f"Request to {url} timed out after {timeout}s")
        return None  # or fallback
```

```typescript
async function fetchWithTimeout(url: string, timeoutMs = 5000): Promise<Response> {
  const controller = new AbortController();
  const id = setTimeout(() => controller.abort(), timeoutMs);
  try {
    return await fetch(url, { signal: controller.signal });
  } finally {
    clearTimeout(id);
  }
}
```

## Idempotency

Ensure operations can be safely retried:

```python
def process_payment(payment_id: str, amount: float, idempotency_key: str):
    # Check if already processed
    existing = db.get_payment_by_key(idempotency_key)
    if existing:
        return existing  # Return cached result

    # Process and store with key
    result = payment_gateway.charge(amount)
    db.save_payment(payment_id, result, idempotency_key)
    return result
```

## Dead Letter Queues

Route failed messages for later inspection:

```python
def process_message(message):
    try:
        handle(message)
    except RetryableError:
        message.retry()
    except Exception as e:
        # Send to dead letter queue for manual review
        dead_letter_queue.send(message, error=str(e))
        logger.error(f"Message sent to DLQ: {e}")
```

## Compensation / Saga Pattern

Roll back distributed transactions step by step:

```python
class Saga:
    def __init__(self):
        self.compensations = []

    def step(self, action, compensation):
        try:
            result = action()
            self.compensations.append(compensation)
            return result
        except Exception:
            self.rollback()
            raise

    def rollback(self):
        for comp in reversed(self.compensations):
            try:
                comp()
            except Exception as e:
                logger.error(f"Compensation failed: {e}")

# Usage
saga = Saga()
saga.step(
    action=lambda: reserve_inventory(item_id),
    compensation=lambda: release_inventory(item_id),
)
saga.step(
    action=lambda: charge_payment(user_id, amount),
    compensation=lambda: refund_payment(user_id, amount),
)
saga.step(
    action=lambda: create_shipment(order_id),
    compensation=lambda: cancel_shipment(order_id),
)
```
