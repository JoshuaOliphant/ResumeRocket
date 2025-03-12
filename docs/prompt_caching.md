# Prompt Caching in ResumeRocket

ResumeRocket implements prompt caching for Claude API calls to reduce API costs and improve response times for repeated prompts.

## How It Works

The caching system works by:

1. Generating a unique hash key for each API request based on the model, messages, system prompt, and other parameters
2. Before making an API call, checking if a cached response exists for the hash key
3. If cached, returning the cached response without making an API call
4. If not cached, making the API call and storing the response in cache

The system uses two caching mechanisms:
- **Local file cache**: Saves responses to disk for reuse across application restarts
- **Claude's `cache_seed` parameter**: Enables Claude's server-side caching for additional efficiency

## Configuration

Caching can be configured using environment variables:

```
# Enable/disable caching (defaults to true)
USE_PROMPT_CACHE=true

# Directory to store cache files (defaults to cache/prompts)
PROMPT_CACHE_DIR=cache/prompts
```

## Caching Implementation

Caching has been implemented in all services that use the Claude API:

- `AISuggestions`: For resume improvement suggestions
- `ResumeCustomizer`: For resume customization and ATS analysis
- `FeedbackLoop`: For evaluation and optimization workflows

Each class includes the following caching utilities:
- `_generate_cache_key()`: Creates a unique deterministic hash for requests
- `_get_from_cache()`: Attempts to retrieve cached responses
- `_save_to_cache()`: Stores responses in the cache

## Handling Streaming Responses

For streaming responses, the caching system:
1. Collects the complete streamed response
2. Saves it to cache after streaming completes
3. For cached responses, simulates streaming by chunking the response

## Benefits

- **Cost Reduction**: Minimizes Claude API calls for identical prompts
- **Performance Improvement**: Cached responses return instantly
- **Consistency**: Ensures consistent responses for identical inputs
- **Bandwidth Efficiency**: Reduces network traffic for repetitive operations

## Maintenance

The cache directory may grow over time. Consider implementing a cache cleanup policy that removes old cache entries based on:
- Age (e.g., delete entries older than 30 days)
- Size (e.g., maintain cache below a certain size)
- Usage patterns (e.g., keep frequently accessed entries)