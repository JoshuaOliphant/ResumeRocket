# HTMX Error Handling Guide

This document explains the error handling system implemented for HTMX-based interactions in ResumeRocket.

## Overview

Our error handling implementation is built on several layers:

1. **Component-Level Error Handling** - Individual components can handle their specific errors
2. **Global Error Handling** - A site-wide error handling system catches unhandled errors
3. **Automatic Retry Logic** - Transient errors are automatically retried with exponential backoff
4. **Fallback Content** - When operations fail, meaningful fallback content is provided
5. **User Feedback** - Clear messages with recovery options are presented to users

## Components

### 1. Error State Components

We've created several reusable error components:

- `templates/components/shared/error.html` - Generic error component with multiple states
- `templates/components/shared/timeout_error.html` - Specialized component for timeout errors
- `templates/components/shared/connection_error.html` - Network/connection error component with auto-retry
- `templates/components/shared/offline_fallback.html` - Offline mode component with cached content
- `templates/components/shared/htmx_error_handler.html` - Global error handler with retry logic

### 2. HTMX Extensions

The `static/js/htmx-extensions.js` file provides several extensions:

- **Response Targets** - Directs responses to different targets based on HTTP status codes
- **Retry** - Provides automatic retry for failed requests
- **Error Logging** - Logs client-side errors to the server
- **Network Status** - Handles online/offline transitions
- **Fallback Content** - Provides graceful degradation

### 3. Server Error Logging

The `/api/client-error` endpoint captures client-side errors for monitoring.

## How to Use

### Basic Error Handling

For basic error handling in HTMX interactions:

```html
<!-- Add response targets extension -->
<div hx-ext="response-targets">
  <!-- Standard HTMX request -->
  <button hx-get="/api/data" 
          hx-target="#result"
          <!-- Target different elements for different status codes -->
          hx-target-500="#server-error"
          hx-target-404="#not-found"
          hx-target-4*="#client-error">
    Fetch Data
  </button>
  
  <!-- Error targets -->
  <div id="server-error" style="display:none">Server error occurred</div>
  <div id="not-found" style="display:none">Resource not found</div>
  <div id="client-error" style="display:none">Client error occurred</div>
</div>
```

### Automatic Retry

To enable automatic retry for an HTMX request:

```html
<div hx-ext="retry">
  <button hx-get="/api/data" 
          hx-target="#result"
          <!-- Configure retry behavior -->
          hx-retry="3" 
          hx-retry-delay="2000"
          hx-retry-backoff="true"
          hx-retry-indicator="#retry-indicator"
          hx-retry-error-target="#max-retries-error">
    Fetch Data
  </button>
  
  <!-- Retry status indicator -->
  <div id="retry-indicator" style="display:none"></div>
  
  <!-- Max retries error container -->
  <div id="max-retries-error" style="display:none">
    <div class="retry-error-template">
      Failed after {retries} attempts. URL: {url}, Status: {status}
    </div>
  </div>
</div>
```

### Using the Global Error Handler

The global error handler is included in `base.html` and automatically catches unhandled HTMX errors.

If you need a page-specific error handler with custom settings:

```html
{% include "components/shared/htmx_error_handler.html" with 
   auto_retry=true,
   max_retries=5,
   retry_delay=1000,
   retry_backoff=true
%}
```

### Network Status Monitoring

To add network awareness to elements:

```html
<div hx-ext="network-status" 
     hx-offline-class="disabled" 
     hx-online-class="enabled"
     hx-offline-indicator="#offline-message"
     hx-trigger-on-online="htmx:load">
  <!-- This content changes appearance when offline -->
  <button>Action</button>
</div>

<div id="offline-message" style="display:none">
  You are currently offline
</div>
```

### Providing Fallback Content

For critical operations that need fallback content:

```html
<div hx-ext="fallback">
  <button hx-get="/api/important-data" 
          hx-target="#result"
          hx-fallback="#error-template">
    Fetch Important Data
  </button>
  
  <template id="error-template">
    <div class="error-message">
      <p>Failed to load data (Status: {status})</p>
      <div class="fallback-content">
        <!-- Static fallback content -->
        <p>Here's what we have cached:</p>
        <div class="cached-data">...</div>
      </div>
      <button data-retry="true">Try Again</button>
    </div>
  </template>
</div>
```

## Error Logging

All client-side errors are automatically logged to the server via the `/api/client-error` endpoint. These logs are available in your regular application logs.

## Best Practices

1. **Use Appropriate Error Components** - Choose the right error component for your specific situation
2. **Provide Helpful Recovery Options** - Always give users a way to recover from errors
3. **Include Fallback Content** - When possible, provide useful content even when operations fail
4. **Tune Retry Settings** - Adjust retry counts and delays based on the operation's importance
5. **Test Error Scenarios** - Regularly test your application with network throttling and failures

## Testing Error Handling

You can test error handling by:

1. Disconnecting from the internet
2. Using browser dev tools to throttle connections
3. Temporarily modifying server routes to return errors
4. Using the browser's "Block requests" feature for specific endpoints

Remember that error handling is about maintaining a quality user experience even when things go wrong.