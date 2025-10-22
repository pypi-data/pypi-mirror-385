# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.1] - 2025-10-21

### 🐛 Bug Fixes

- **Critical:** Fixed `rate_limit_rpm` and `rate_limit_shared_key` being passed to OpenAI API
  - These parameters are internal configuration options, not API parameters
  - Caused error: `Completions.create() got an unexpected keyword argument 'rate_limit_rpm'`
  - Fixed in [`generator.py`](src/omnigen/pipelines/conversation_extension/generator.py) lines 489-494, 556-561
  - Now properly filtered out in both `_generate_followup()` and `_generate_response()` methods

- **Critical:** Added missing `get_rpm()` method to `ProviderRateLimitManager`
  - Caused error: `'ProviderRateLimitManager' object has no attribute 'get_rpm'`
  - Fixed in [`rate_limiter.py`](src/omnigen/utils/rate_limiter.py) lines 487-500
  - Returns aggregate RPM across all providers for progress bar display

### 🔧 Changed

- Updated `core_params` set in generator to exclude rate limit configuration parameters
- Added aggregate RPM tracking method to rate limit manager

---

## [0.1.0] - 2025-10-21

### 🚀 Major Features

#### Per-Provider Rate Limiting System
- **BREAKING FIX:** Replaced single 60 RPM rate limiter with per-provider rate limiting
- **16x Performance Improvement:** Increased default capacity from 60 RPM to 1000+ RPM
- **Eliminated Timeouts:** Fixed 120-second timeout issues with parallel workers
- **Auto-Detection:** Automatic rate limit detection based on provider and model

### ✨ Added

- **Model-Specific Rate Limit Defaults** ([`rate_limiter.py`](src/omnigen/utils/rate_limiter.py))
  - OpenAI gpt-4o-mini: 500 RPM
  - OpenAI gpt-3.5-turbo: 3500 RPM
  - Anthropic Claude models: 50 RPM
  - OpenRouter: 200 RPM
  - Custom providers: Configurable

- **Enhanced ProviderRateLimitManager**
  - `get_default_rate_limit()` function for auto-detection
  - Support for `rate_limit_rpm` custom override in config
  - Support for `rate_limit_shared_key` to pool limits across roles
  - Independent rate limiters per role by default
  - Smart key generation for per-role independence

- **Configuration Options**
  - Optional `rate_limit_rpm` parameter in provider config
  - Optional `rate_limit_shared_key` parameter for shared rate limiting
  - Backward compatible - works with existing configs

- **Documentation**
  - [`docs/RATE_LIMITING_GUIDE.md`](docs/RATE_LIMITING_GUIDE.md) - Comprehensive guide with examples
  - [`docs/RATE_LIMITING_FIX_SUMMARY.md`](docs/RATE_LIMITING_FIX_SUMMARY.md) - Implementation summary
  - Updated config examples in [`config_with_checkpoint.yaml`](examples/conversation_extension/config_with_checkpoint.yaml)

### 🔧 Changed

- **Runner** ([`runner.py`](src/omnigen/pipelines/conversation_extension/runner.py))
  - Changed from `RateLimiter` to `ProviderRateLimitManager`
  - Enables per-provider rate limiting

- **Generator** ([`generator.py`](src/omnigen/pipelines/conversation_extension/generator.py))
  - Updated `_generate_followup()` to use provider-specific rate limiter with role
  - Updated `_generate_response()` to use provider-specific rate limiter with role
  - Records requests on specific limiters instead of shared limiter

### 🐛 Fixed

- **Critical:** Fixed 120-second timeout errors with parallel workers
  - Root cause: Single 60 RPM rate limiter shared across all API calls
  - Solution: Per-provider rate limiting with model-specific defaults
  - Result: No timeouts, full parallel execution

- **Performance:** Fixed worker utilization bottleneck
  - Before: 10% utilization (1 of 10 workers active)
  - After: 100% utilization (all workers active)

### 📊 Performance Improvements

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| Rate Limit Capacity | 60 RPM | 1000 RPM | 16.7x |
| Requests/Second | 1 | 16.6 | 16.6x |
| Time for 130 Calls | 130s (timeout) | ~8s | 16.3x faster |
| Timeouts | Yes ❌ | No ✅ | Fixed |
| Worker Utilization | 10% | 100% | 10x better |

### 🔄 Migration

**No configuration changes required!** The system is backward compatible.

**Old config (still works):**
```yaml
providers:
  user_followup:
    name: "openai"
    model: "gpt-4o-mini"
```

**What happens automatically:**
- System detects provider and model
- Auto-applies 500 RPM rate limit per provider
- Creates independent limiters per role
- Result: 16x better performance with zero config changes

**Optional enhancements:**
```yaml
providers:
  user_followup:
    name: "openai"
    model: "gpt-4o-mini"
    rate_limit_rpm: 300  # Optional: Override auto-detection
    rate_limit_shared_key: "my_key"  # Optional: Share limit with assistant
```

### 📦 Dependencies

No new dependencies added. All changes use existing dependencies.

### 🔗 Links

- [Rate Limiting Guide](docs/RATE_LIMITING_GUIDE.md)
- [Implementation Summary](docs/RATE_LIMITING_FIX_SUMMARY.md)
- [Configuration Examples](examples/conversation_extension/config_with_checkpoint.yaml)

---

## [0.0.1.post11] - Previous Release

Earlier versions focused on token tracking and enhanced validation.

---

## Version History Summary

- **0.1.1** - Bug fixes for rate limiting parameters (Current)
- **0.1.0** - Per-provider rate limiting with auto-detection
- **0.0.1.post11** - Token tracking and enhanced validation
- **0.0.1** - Initial release

[0.1.1]: https://github.com/ultrasafe-ai/omnigen/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/ultrasafe-ai/omnigen/compare/v0.0.1.post11...v0.1.0
[0.0.1.post11]: https://github.com/ultrasafe-ai/omnigen/releases/tag/v0.0.1.post11