# Error Aggregation Pattern

Collect multiple errors instead of failing on the first error. Ideal for validation, batch processing, and form handling.

## TypeScript Implementation

```typescript
class ErrorCollector {
  private errors: Error[] = [];

  add(error: Error): void {
    this.errors.push(error);
  }

  hasErrors(): boolean {
    return this.errors.length > 0;
  }

  getErrors(): Error[] {
    return [...this.errors];
  }

  throw(): never {
    if (this.errors.length === 1) {
      throw this.errors[0];
    }
    throw new AggregateError(
      this.errors,
      `${this.errors.length} errors occurred`,
    );
  }
}

// Usage: Validate multiple fields
function validateUser(data: any): User {
  const errors = new ErrorCollector();

  if (!data.email) {
    errors.add(new ValidationError("Email is required"));
  } else if (!isValidEmail(data.email)) {
    errors.add(new ValidationError("Email is invalid"));
  }

  if (!data.name || data.name.length < 2) {
    errors.add(new ValidationError("Name must be at least 2 characters"));
  }

  if (!data.age || data.age < 18) {
    errors.add(new ValidationError("Age must be 18 or older"));
  }

  if (errors.hasErrors()) {
    errors.throw();
  }

  return data as User;
}
```

## Python Implementation

```python
from dataclasses import dataclass, field
from typing import List

@dataclass
class ErrorCollector:
    errors: List[Exception] = field(default_factory=list)

    def add(self, error: Exception) -> None:
        self.errors.append(error)

    def has_errors(self) -> bool:
        return len(self.errors) > 0

    def raise_if_errors(self) -> None:
        if len(self.errors) == 1:
            raise self.errors[0]
        if self.errors:
            raise ExceptionGroup(
                f"{len(self.errors)} errors occurred",
                self.errors
            )

# Usage
def validate_config(config: dict) -> dict:
    collector = ErrorCollector()

    if "host" not in config:
        collector.add(ValueError("Missing 'host'"))
    if "port" not in config:
        collector.add(ValueError("Missing 'port'"))
    elif not isinstance(config["port"], int):
        collector.add(TypeError("'port' must be an integer"))

    collector.raise_if_errors()
    return config
```

## When to Use

- **Form validation** — Show all invalid fields at once
- **Batch processing** — Report all failures, not just the first
- **Configuration validation** — List all missing/invalid settings
- **Data import** — Collect row-level errors for review
