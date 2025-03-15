# Anthropic Prompt Caching Implementation

## Overview

ResumeRocket now leverages Anthropic's prompt caching feature to optimize Claude API usage. This implementation significantly reduces API costs and improves response times for common operations.

## Implementation Details

### Centralized Claude Client

A centralized `ClaudeClient` class has been created to handle all Claude API interactions:

- Located at `/backend/services/claude_client.py`
- Manages both Anthropic's server-side caching and optional local file caching
- Handles streaming and non-streaming API calls
- Automatically adds `cache_control` parameters to system prompts
- Tracks and logs cache performance metrics

### Key Features

1. **Structured Prompt Design**:
   - System prompts are structured for optimal caching (static instruction content)
   - User prompts contain dynamic content (resume/job-specific information)
   - System prompts are automatically marked with `cache_control: {"type": "ephemeral"}`

2. **Dual Caching Mechanisms**:
   - **Primary**: Anthropic's server-side caching (90% cost reduction for cached tokens)
   - **Secondary**: Local file caching for redundancy and offline usage

3. **Performance Monitoring**:
   - Tracks cache hits, misses, and cost savings
   - Logs detailed metrics for optimization and reporting

4. **Cache-Friendly API Structure**:
   - Consistent message/system structure across API calls
   - Separation of static and dynamic content for better cache utilization

## Services Updated

The following services have been updated to use prompt caching:

1. **ResumeCustomizer**:
   - Uses cached system prompts for analysis, implementation, and simulation phases
   - Supports both regular and streaming API interactions with caching

2. **AISuggestions**:
   - Uses cached system prompts for suggestions generation
   - Implements streaming responses with prompt caching

## Configuration Options

Prompt caching can be configured using the following environment variables:

```
# Enable/disable Anthropic's server-side caching (defaults to true)
USE_ANTHROPIC_CACHE=true

# Enable/disable local file caching (defaults to true)
USE_LOCAL_CACHE=true

# Directory for local cache files (defaults to cache/prompts)
PROMPT_CACHE_DIR=cache/prompts

# Optional prefix for cache keys (useful for environments)
CACHE_PREFIX=

# Default Claude model to use
CLAUDE_MODEL=claude-3-7-sonnet-20250219
```

## Cost Savings

With prompt caching implemented, the system benefits from Anthropic's pricing structure:

- **Cache write tokens**: 25% more expensive than base input tokens ($3.75/MTok vs $3/MTok for Claude 3.7 Sonnet)
- **Cache read tokens**: 90% cheaper than base input tokens ($0.30/MTok vs $3/MTok for Claude 3.7 Sonnet)

For our typical resume customization workflow:
1. ~15,000 tokens in system prompts (cached)
2. ~2,000-5,000 tokens in user messages (not cached)

Estimated savings:
- First request: 5% more expensive (due to cache write premium)
- Subsequent requests: 60-80% cheaper (due to cache read discount)
- Overall cost reduction: 30-50% depending on usage patterns

## Developer Notes

When making changes to the Claude API integration:

1. **Prompt Structure**:
   - Keep system prompts static when possible (cached portion)
   - Put variable/dynamic content in user messages (non-cached portion)
   - Use the `ClaudeClient.create_message()` method for all API calls

2. **Cache Optimization**:
   - Pay attention to the `_prepare_system_prompt()` method in `ClaudeClient`
   - Monitor cache performance through the logs
   - Use caching for streaming responses with `client.messages.stream()`

3. **Prompt Versioning**:
   - Major changes to system prompts will invalidate existing caches
   - Consider adding a version parameter for controlled cache invalidation

## Monitoring and Maintenance

- Cache performance metrics are logged at INFO level
- Local cache files can be periodically cleaned up to manage disk space
- Performance can be tracked via log analysis to optimize caching strategies