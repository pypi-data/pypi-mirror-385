# Rate Limiting Guide

OmniGen provides flexible rate limiting to control API usage and prevent hitting provider rate limits. You can choose between two approaches:

1. **Concurrency Limiting** (Recommended) - Simple control of concurrent API calls
2. **RPM-based Rate Limiting** - Traditional requests-per-minute limiting

## Table of Contents

- [Quick Start](#quick-start)
- [Concurrency Limiting (Recommended)](#concurrency-limiting-recommended)
- [RPM-based Rate Limiting](#rpm-based-rate-limiting)
- [Comparison](#comparison)
- [Configuration Examples](#configuration-examples)
- [Advanced Usage](#advanced-usage)
- [Troubleshooting](#troubleshooting)

---

## Quick Start

### Option 1: Concurrency Limiting (Simplest)

```yaml
providers:
  user_followup:
    name: "openai"
    model: "gpt-4o-mini"
    max_concurrent_calls: 50  # Allow max 50 concurrent requests
```

### Option 2: RPM-based Rate Limiting

```yaml
providers:
  user_followup:
    name: "openai"
    model: "gpt-4o-mini"
    rate_limit_rpm: 500  # Max 500 requests per minute
```

---

## Concurrency Limiting (Recommended)

### What is it?

Concurrency limiting controls the **maximum number of API calls running at the same time**. When the limit is reached, new requests wait until a slot becomes available.

### Why use it?

- ✅ **Simpler to understand**: "Allow max 50 concurrent calls" is intuitive
- ✅ **Easier to configure**: Just one number to set
- ✅ **Predictable behavior**: Consistent throughput
- ✅ **Better for parallel workloads**: Works naturally with `parallel_workers`

### How it works

Uses a semaphore to limit concurrent requests:

```python
limiter = ConcurrencyLimiter(max_concurrent=50)
if limiter.acquire(timeout=120):  # Wait for slot (max 2 minutes)
    try:
        response = api_call()
    finally:
        limiter.release()  # Free the slot
```

### Configuration

```yaml
providers:
  user_followup:
    name: "openai"
    model: "gpt-4o-mini"
    max_concurrent_calls: 50  # Required: number of concurrent calls
```

### Choosing the right value

**Guidelines:**
- Start with `50` for most use cases
- Increase to `100-200` for high-throughput scenarios
- Decrease to `10-25` for conservative API usage

**Provider Recommendations:**
- OpenAI Tier 1: `50-100` concurrent calls
- OpenAI Tier 2+: `100-200` concurrent calls
- Anthropic: `25-50` concurrent calls
- OpenRouter: `50-100` concurrent calls

---

## RPM-based Rate Limiting

### What is it?

RPM (Requests Per Minute) limiting controls the **total number of requests allowed in a 60-second window** using a token bucket algorithm.

### Why use it?

- ✅ **Precise rate control**: Exact requests per minute
- ✅ **Traditional approach**: Familiar to most developers
- ✅ **Provider alignment**: Matches provider rate limit tiers

### How it works

Uses a token bucket algorithm:

```python
limiter = RateLimiter(requests_per_minute=500)
limiter.acquire(timeout=120)  # Wait for token (max 2 minutes)
# Make API call
limiter.record_request()  # Record successful request
```

### Configuration

```yaml
providers:
  user_followup:
    name: "openai"
    model: "gpt-4o-mini"
    rate_limit_rpm: 500  # Optional: defaults auto-detected
```

### Auto-detection

If you don't specify `rate_limit_rpm`, OmniGen automatically detects the limit based on provider and model:

**OpenAI (Tier 1):**
- `gpt-4o`, `gpt-4o-mini`, `gpt-4-turbo`: 500 RPM
- `gpt-3.5-turbo`: 3500 RPM
- `o1-preview`, `o1-mini`: 500 RPM

**Anthropic:**
- All Claude models: 50 RPM

**OpenRouter:**
- All models: 200 RPM

**Custom/Unknown:**
- Default: 60 RPM

---

## Comparison

| Feature | Concurrency Limiting | RPM-based Limiting |
|---------|---------------------|-------------------|
| **Simplicity** | ✅ Very simple | ⚠️ More complex |
| **Configuration** | One number | One number + auto-detect |
| **Mental Model** | "X calls at once" | "X calls per minute" |
| **Predictability** | ✅ Consistent | ⚠️ Bursty |
| **Parallel Workers** | ✅ Natural fit | ⚠️ Requires tuning |
| **Provider Alignment** | ⚠️ Not direct | ✅ Direct match |
| **Overhead** | Low (semaphore) | Medium (token bucket) |

### When to use Concurrency Limiting:

- You want simplicity
- You're using parallel workers
- You want consistent throughput
- You're not constrained by exact RPM limits

### When to use RPM-based Limiting:

- You have specific RPM tier limits
- You need precise rate control
- You're familiar with token bucket algorithms
- Provider explicitly specifies RPM limits

---

## Configuration Examples

### Example 1: Simple Concurrency Limiting

```yaml
providers:
  user_followup:
    name: "openai"
    model: "gpt-4o-mini"
    max_concurrent_calls: 50
  
  assistant_response:
    name: "openai"
    model: "gpt-4o-mini"
    max_concurrent_calls: 50

generation:
  parallel_workers: 10  # Works well with concurrency limiting
```

### Example 2: RPM-based with Auto-detection

```yaml
providers:
  user_followup:
    name: "openai"
    model: "gpt-4o-mini"
    # Auto-detects: 500 RPM
  
  assistant_response:
    name: "anthropic"
    model: "claude-3-haiku"
    # Auto-detects: 50 RPM
```

### Example 3: Custom RPM Overrides

```yaml
providers:
  user_followup:
    name: "openai"
    model: "gpt-4o-mini"
    rate_limit_rpm: 300  # Override default 500 RPM
  
  assistant_response:
    name: "openai"
    model: "gpt-4o-mini"
    rate_limit_rpm: 300
```

### Example 4: Shared Rate Limit

Share a single rate limiter across multiple roles:

```yaml
providers:
  user_followup:
    name: "openai"
    model: "gpt-4o-mini"
    rate_limit_shared_key: "my_openai_account"
    rate_limit_rpm: 500
  
  assistant_response:
    name: "openai"
    model: "gpt-4o-mini"
    rate_limit_shared_key: "my_openai_account"  # Shares with user_followup
    rate_limit_rpm: 500
```

### Example 5: Mixed Approach (NOT RECOMMENDED)

If both are specified, concurrency limiting takes precedence:

```yaml
providers:
  user_followup:
    name: "openai"
    model: "gpt-4o-mini"
    max_concurrent_calls: 50  # This will be used
    rate_limit_rpm: 500       # This will be ignored
```

---

## Advanced Usage

### Per-Role Rate Limiters

By default, each role gets its own independent rate limiter:

```yaml
providers:
  user_followup:
    name: "openai"
    model: "gpt-4o-mini"
    max_concurrent_calls: 50  # Independent limiter for user_followup
  
  assistant_response:
    name: "openai"
    model: "gpt-4o-mini"
    max_concurrent_calls: 50  # Independent limiter for assistant_response
```

This means you can have up to 100 total concurrent calls (50 + 50).

### Shared Rate Limiters

To share a single limiter across roles (useful for single API key):

```yaml
providers:
  user_followup:
    name: "openai"
    model: "gpt-4o-mini"
    rate_limit_shared_key: "my_key"
    max_concurrent_calls: 50
  
  assistant_response:
    name: "openai"
    model: "gpt-4o-mini"
    rate_limit_shared_key: "my_key"  # Shares limiter with user_followup
    max_concurrent_calls: 50
```

Now both roles share a pool of 50 concurrent calls.

### Timeout Configuration

Both limiters support timeout on acquire:

```python
# Default timeout: 120 seconds
limiter.acquire(timeout=120)
```

If a request can't acquire a slot within the timeout, it will fail.

---

## Troubleshooting

### Issue: "Concurrency limit timeout"

**Symptoms:**
```
WARNING: Concurrency limit timeout after 120s for openai_user_followup
```

**Solutions:**
1. Increase `max_concurrent_calls`
2. Reduce `parallel_workers`
3. Check for API slowness

### Issue: "Rate limit timeout"

**Symptoms:**
```
WARNING: Rate limit timeout after 60s for openai_user_followup
```

**Solutions:**
1. Increase `rate_limit_rpm`
2. Reduce `parallel_workers`
3. Check if RPM is too restrictive

### Issue: High API errors

**Symptoms:**
- 429 errors from provider
- "Rate limit exceeded" errors

**Solutions:**
1. **If using concurrency limiting:**
   - Decrease `max_concurrent_calls`
   - Provider may have stricter limits

2. **If using RPM limiting:**
   - Decrease `rate_limit_rpm`
   - Check provider's actual limits
   - Enable `rate_limit_shared_key` if multiple roles

### Issue: Slow throughput

**Symptoms:**
- Generation takes too long
- Low concurrent requests

**Solutions:**
1. **If using concurrency limiting:**
   - Increase `max_concurrent_calls`
   - Increase `parallel_workers`

2. **If using RPM limiting:**
   - Increase `rate_limit_rpm`
   - Check if auto-detected limit is too conservative

### Monitoring Rate Limiting

Use the rate limiter stats API:

```python
from omnigen.utils.rate_limiter import ProviderRateLimitManager

manager = ProviderRateLimitManager()
stats = manager.get_all_stats()

for name, limiter_stats in stats.items():
    print(f"{name}: {limiter_stats}")
```

**Concurrency Limiter Stats:**
```python
{
    'max_concurrent': 50,
    'active_calls': 35,
    'total_requests': 1000,
    'available_slots': 15
}
```

**Rate Limiter Stats:**
```python
{
    'provider': 'openai_user_followup',
    'rpm_limit': 500,
    'current_rpm': 450,
    'tokens_available': 50,
    'total_requests': 1000,
    'utilization': 90.0
}
```

---

## Best Practices

### 1. Start with Concurrency Limiting

For most use cases, concurrency limiting is simpler and more intuitive:

```yaml
max_concurrent_calls: 50  # Start here
```

### 2. Match Parallel Workers

Set `max_concurrent_calls` >= `parallel_workers` for optimal throughput:

```yaml
generation:
  parallel_workers: 10

providers:
  user_followup:
    max_concurrent_calls: 50  # 5x workers = good headroom
```

### 3. Use Shared Keys Wisely

If you have one API key shared across roles, use `rate_limit_shared_key`:

```yaml
providers:
  user_followup:
    rate_limit_shared_key: "shared_openai"
    max_concurrent_calls: 50
  
  assistant_response:
    rate_limit_shared_key: "shared_openai"
    max_concurrent_calls: 50
```

### 4. Monitor and Adjust

- Start conservative (lower limits)
- Monitor API errors and throughput
- Gradually increase limits
- Watch for 429 errors

### 5. Production Recommendations

**High Volume (1000+ conversations):**
```yaml
providers:
  user_followup:
    max_concurrent_calls: 100
  assistant_response:
    max_concurrent_calls: 100

generation:
  parallel_workers: 20
```

**Conservative (safety first):**
```yaml
providers:
  user_followup:
    max_concurrent_calls: 25
  assistant_response:
    max_concurrent_calls: 25

generation:
  parallel_workers: 5
```

---

## Migration Guide

### From RPM to Concurrency Limiting

If you're currently using RPM-based limiting:

**Before:**
```yaml
providers:
  user_followup:
    rate_limit_rpm: 500
```

**After:**
```yaml
providers:
  user_followup:
    max_concurrent_calls: 50  # ~10% of RPM is a good starting point
```

**Why 10%?**
- If RPM = 500, that's ~8.3 requests/second
- With 10 parallel workers, each worker makes ~1 request/second
- 50 concurrent calls allows for API latency (0.5-1s per request)

### Rough Conversion Formula

```
max_concurrent_calls ≈ rate_limit_rpm × average_api_latency / 60

Example:
- rate_limit_rpm = 500
- average_api_latency = 2 seconds
- max_concurrent_calls ≈ 500 × 2 / 60 ≈ 17 concurrent calls

However, this is just a rough guide. Start with 50 and adjust based on monitoring.
```

---

## Version History

- **v0.2.0** (2025-01) - Added `max_concurrent_calls` concurrency limiting
- **v0.1.7** (2024-12) - Added RPM-based rate limiting with auto-detection
- **v0.1.6** (2024-12) - Initial rate limiting support

---

## See Also

- [Configuration Examples](../examples/conversation_extension/config_with_checkpoint.yaml)
- [Provider Configuration](../src/omnigen/core/provider_config.py)
- [Rate Limiter Implementation](../src/omnigen/utils/rate_limiter.py)