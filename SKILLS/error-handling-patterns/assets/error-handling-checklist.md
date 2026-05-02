# Error Handling Review Checklist

Use this checklist when reviewing error handling in code.

## Input Validation
- [ ] All user inputs validated before processing
- [ ] Validation errors return helpful, specific messages
- [ ] Multiple validation errors collected (not fail-on-first)

## Exception Handling
- [ ] Custom exceptions used (not generic `Exception`)
- [ ] Exception hierarchy matches domain model
- [ ] Exceptions include error codes for programmatic handling
- [ ] Exceptions include contextual details (IDs, values, timestamps)
- [ ] No empty catch blocks
- [ ] No overly broad catch blocks (`except Exception`)
- [ ] Exceptions caught at the right abstraction level

## Resource Cleanup
- [ ] Files/connections closed in `finally` / context managers / `defer`
- [ ] Database transactions committed or rolled back
- [ ] Temporary resources cleaned up on error
- [ ] Locks released on all code paths

## Logging
- [ ] Errors logged with sufficient context to reproduce
- [ ] No sensitive data in error logs (passwords, tokens, PII)
- [ ] Log levels used appropriately (error vs warning vs info)
- [ ] No duplicate logging (log once at the right level)
- [ ] Stack traces preserved for unexpected errors

## External Services
- [ ] Timeouts set on all external calls
- [ ] Retry logic with exponential backoff for transient failures
- [ ] Circuit breaker for frequently failing services
- [ ] Fallback behavior defined for degraded mode
- [ ] Idempotency keys used for retryable operations

## User-Facing Errors
- [ ] Error messages are user-friendly (not stack traces)
- [ ] Error messages suggest corrective action when possible
- [ ] HTTP status codes are correct and specific
- [ ] Error response format is consistent across API

## Async / Concurrent
- [ ] Unhandled promise rejections caught
- [ ] Async error boundaries in place (React, etc.)
- [ ] Concurrent errors don't corrupt shared state
- [ ] Background task errors are logged and monitored

## Testing
- [ ] Error paths have unit tests
- [ ] Edge cases tested (empty input, null, boundary values)
- [ ] External service failures simulated in tests
- [ ] Error messages verified in tests
