/**
 * HTMX Error Handling Extensions for ResumeRocket
 * 
 * This file contains HTMX extensions and utilities for robust error handling:
 * 1. Response Targets Extension (for HTTP error code handling)
 * 2. Retry Extension (for automatic retries on transient failures)
 * 3. Error Logging Extension (for client-side error tracking)
 * 4. Network Status Extension (for monitoring offline/online status)
 * 5. Fallback Content Extension (for providing graceful degradation)
 */

/* ------------------------------ Response Targets Extension ------------------------------ */
/**
 * Allows different targets to be specified for different HTTP response codes
 * Example: hx-target-500="#server-error" hx-target-404="#not-found"
 * 
 * This enables more sophisticated error handling by targeting specific
 * elements for different error conditions.
 */
htmx.defineExtension('response-targets', {
    onEvent: function(name, evt) {
        if (name === 'htmx:beforeSwap') {
            if (evt.detail.xhr && evt.detail.xhr.status !== 200) {
                const status = evt.detail.xhr.status;
                const elt = evt.detail.elt;
                
                // Check for specific status code target
                let statusCodeTarget = elt.getAttribute('hx-target-' + status);
                
                // If no specific target, check for a wildcard target (e.g., hx-target-5* for all 5xx errors)
                if (!statusCodeTarget) {
                    const firstDigit = status.toString()[0];
                    statusCodeTarget = elt.getAttribute('hx-target-' + firstDigit + '*');
                }
                
                // If we found a target, update the swap target
                if (statusCodeTarget) {
                    evt.detail.target = document.querySelector(statusCodeTarget);
                }
            }
        }
    }
});

/* ------------------------------ Retry Extension ------------------------------ */
/**
 * Provides automatic retry capability for failed requests
 * Example: hx-ext="retry" hx-retry="3" hx-retry-delay="1000"
 * 
 * This extension will automatically retry failed AJAX requests a specified
 * number of times with a configurable delay between attempts.
 */
htmx.defineExtension('retry', {
    onEvent: function(name, evt) {
        if (name === 'htmx:xhr:error') {
            // Get the element that triggered the request
            const elt = evt.detail.elt;
            
            // Check if retries are enabled for this element
            const maxRetries = elt.getAttribute('hx-retry');
            if (!maxRetries) return;
            
            // Get current retry count or initialize it
            let currentRetry = parseInt(elt.getAttribute('data-retry-count') || '0');
            
            // If we haven't hit the max retries, try again
            if (currentRetry < parseInt(maxRetries)) {
                // Increment retry count
                currentRetry++;
                elt.setAttribute('data-retry-count', currentRetry);
                
                // Get retry delay (default to 2000ms)
                let retryDelay = parseInt(elt.getAttribute('hx-retry-delay') || '2000');
                
                // Apply exponential backoff if specified
                if (elt.getAttribute('hx-retry-backoff') === 'true') {
                    retryDelay = retryDelay * Math.pow(1.5, currentRetry - 1);
                }
                
                // Show retry notification if it exists
                const retryTarget = elt.getAttribute('hx-retry-indicator');
                if (retryTarget) {
                    const indicator = document.querySelector(retryTarget);
                    if (indicator) {
                        // Show retry message, use the target's custom template or default one
                        indicator.textContent = `Retrying... (${currentRetry}/${maxRetries})`;
                        indicator.style.display = 'block';
                        
                        // Add a countdown for longer delays
                        if (retryDelay > 3000) {
                            let secondsLeft = Math.ceil(retryDelay / 1000);
                            const countdownInterval = setInterval(function() {
                                secondsLeft--;
                                indicator.textContent = `Retrying in ${secondsLeft}s... (${currentRetry}/${maxRetries})`;
                                if (secondsLeft <= 0) {
                                    clearInterval(countdownInterval);
                                }
                            }, 1000);
                        }
                    }
                }
                
                // Schedule the retry
                setTimeout(function() {
                    // Trigger the same event again
                    htmx.trigger(elt, evt.detail.triggerSpec.trigger);
                }, retryDelay);
                
                // Prevent the error from bubbling up
                evt.stopPropagation();
                
                // Log retry attempt
                console.log(`HTMX Retry: Attempt ${currentRetry}/${maxRetries} after ${retryDelay}ms`);
                return false;
            } else {
                // Reset retry count when max retries reached
                elt.setAttribute('data-retry-count', '0');
                
                // Show max retries error if target exists
                const errorTarget = elt.getAttribute('hx-retry-error-target');
                if (errorTarget) {
                    const errorElement = document.querySelector(errorTarget);
                    if (errorElement) {
                        errorElement.style.display = 'block';
                        // Attempt to populate with a template if it exists
                        if (errorElement.querySelector('.retry-error-template')) {
                            const template = errorElement.querySelector('.retry-error-template');
                            template.innerHTML = template.innerHTML
                                .replace('{url}', evt.detail.xhr.responseURL)
                                .replace('{status}', evt.detail.xhr.status)
                                .replace('{retries}', maxRetries);
                        }
                    }
                }
            }
        } else if (name === 'htmx:beforeRequest') {
            // Reset retry count on new requests
            const elt = evt.detail.elt;
            if (elt.getAttribute('hx-retry')) {
                elt.setAttribute('data-retry-count', '0');
            }
        }
    }
});

/* ------------------------------ Error Logging Extension ------------------------------ */
/**
 * Logs HTMX errors to console and optionally to a server endpoint
 * Example: hx-ext="error-logger" hx-error-logger-url="/api/client-errors"
 * 
 * This extension captures AJAX errors and network failures and can
 * send detailed information to a server endpoint for monitoring.
 */
htmx.defineExtension('error-logger', {
    onEvent: function(name, evt) {
        if (name === 'htmx:xhr:error' || 
            name === 'htmx:sendError' || 
            name === 'htmx:responseError') {
            
            // Get the element that triggered the request
            const elt = evt.detail.elt;
            
            // Create error details object
            const errorDetails = {
                type: name,
                timestamp: new Date().toISOString(),
                url: window.location.href,
                target: elt.getAttribute('id') || elt.getAttribute('name') || elt.tagName,
                status: evt.detail.xhr ? evt.detail.xhr.status : null,
                statusText: evt.detail.xhr ? evt.detail.xhr.statusText : null,
                triggerSpec: evt.detail.triggerSpec,
                requestConfig: evt.detail.requestConfig
            };
            
            // Log to console
            console.error('HTMX Error:', errorDetails);
            
            // Check if we should log to server
            const loggerUrl = elt.getAttribute('hx-error-logger-url') || 
                             htmx.config.errorLoggerUrl;
            
            // Send error to server if URL is configured
            if (loggerUrl) {
                fetch(loggerUrl, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRF-Token': document.querySelector('meta[name="csrf-token"]')?.content || ''
                    },
                    body: JSON.stringify(errorDetails)
                }).catch(e => {
                    // Silent catch to avoid cascading errors
                    console.warn('Could not send error log to server:', e);
                });
            }
        }
    }
});

/* ------------------------------ Network Status Extension ------------------------------ */
/**
 * Monitors network connectivity and provides classes and event triggers
 * Example: hx-ext="network-status" hx-offline-class="offline-mode"
 * 
 * This extension adds/removes classes based on network status and can
 * trigger specific behaviors when online/offline status changes.
 */
htmx.defineExtension('network-status', {
    init: function(api) {
        // Add global online/offline event listeners
        window.addEventListener('online', function() {
            // Find elements with the extension
            document.querySelectorAll('[hx-ext~="network-status"]').forEach(function(elt) {
                // Remove offline class if specified
                const offlineClass = elt.getAttribute('hx-offline-class');
                if (offlineClass) {
                    elt.classList.remove(offlineClass);
                }
                
                // Add online class if specified
                const onlineClass = elt.getAttribute('hx-online-class');
                if (onlineClass) {
                    elt.classList.add(onlineClass);
                }
                
                // Trigger online event if specified
                if (elt.getAttribute('hx-trigger-on-online')) {
                    setTimeout(function() {
                        // Allow a short delay to ensure network is stable
                        htmx.trigger(elt, elt.getAttribute('hx-trigger-on-online'));
                    }, 1000);
                }
            });
            
            // Trigger custom event
            htmx.trigger(document.body, 'htmx:networkOnline');
        });
        
        window.addEventListener('offline', function() {
            // Find elements with the extension
            document.querySelectorAll('[hx-ext~="network-status"]').forEach(function(elt) {
                // Add offline class if specified
                const offlineClass = elt.getAttribute('hx-offline-class');
                if (offlineClass) {
                    elt.classList.add(offlineClass);
                }
                
                // Remove online class if specified
                const onlineClass = elt.getAttribute('hx-online-class');
                if (onlineClass) {
                    elt.classList.remove(onlineClass);
                }
                
                // Show offline indicator if specified
                const offlineIndicator = elt.getAttribute('hx-offline-indicator');
                if (offlineIndicator) {
                    const indicator = document.querySelector(offlineIndicator);
                    if (indicator) {
                        indicator.style.display = 'block';
                    }
                }
            });
            
            // Trigger custom event
            htmx.trigger(document.body, 'htmx:networkOffline');
        });
        
        // Initialize elements on page load
        document.addEventListener('DOMContentLoaded', function() {
            const isOnline = navigator.onLine;
            
            document.querySelectorAll('[hx-ext~="network-status"]').forEach(function(elt) {
                // Set initial online/offline classes
                const offlineClass = elt.getAttribute('hx-offline-class');
                const onlineClass = elt.getAttribute('hx-online-class');
                
                if (isOnline) {
                    if (onlineClass) elt.classList.add(onlineClass);
                    if (offlineClass) elt.classList.remove(offlineClass);
                } else {
                    if (offlineClass) elt.classList.add(offlineClass);
                    if (onlineClass) elt.classList.remove(onlineClass);
                    
                    // Show offline indicator if specified
                    const offlineIndicator = elt.getAttribute('hx-offline-indicator');
                    if (offlineIndicator) {
                        const indicator = document.querySelector(offlineIndicator);
                        if (indicator) {
                            indicator.style.display = 'block';
                        }
                    }
                }
            });
        });
    }
});

/* ------------------------------ Fallback Content Extension ------------------------------ */
/**
 * Provides fallback content when requests fail
 * Example: hx-ext="fallback" hx-fallback="#error-template"
 * 
 * This extension will display fallback content from a template when
 * an AJAX request fails, allowing for graceful degradation.
 */
htmx.defineExtension('fallback', {
    onEvent: function(name, evt) {
        if (name === 'htmx:xhr:error') {
            const elt = evt.detail.elt;
            const xhr = evt.detail.xhr;
            
            // Check if fallback is enabled for this element
            const fallbackSelector = elt.getAttribute('hx-fallback');
            if (!fallbackSelector) return;
            
            // Find the fallback template
            const fallbackTemplate = document.querySelector(fallbackSelector);
            if (!fallbackTemplate) return;
            
            // Find the target element
            const targetSelector = elt.getAttribute('hx-target') || 'this';
            let target;
            
            if (targetSelector === 'this') {
                target = elt;
            } else {
                target = document.querySelector(targetSelector);
            }
            
            if (!target) return;
            
            // Clone the template
            const fallbackContent = fallbackTemplate.cloneNode(true);
            fallbackContent.style.display = 'block';
            
            // Replace placeholders if any
            const textContent = fallbackContent.innerHTML
                .replace('{status}', xhr.status)
                .replace('{statusText}', xhr.statusText)
                .replace('{url}', xhr.responseURL)
                .replace('{retry}', elt.getAttribute('hx-retry') || '0')
                .replace('{timestamp}', new Date().toLocaleTimeString());
            
            fallbackContent.innerHTML = textContent;
            
            // Get the target's swap method, defaulting to innerHTML
            const swapMethod = elt.getAttribute('hx-swap') || 'innerHTML';
            
            // Apply the swap
            htmx.swap(target, fallbackContent, swapMethod);
            
            // Register a click handler for retry buttons within the fallback
            const retryButtons = fallbackContent.querySelectorAll('[data-retry="true"]');
            retryButtons.forEach(function(btn) {
                btn.addEventListener('click', function(e) {
                    e.preventDefault();
                    htmx.trigger(elt, evt.detail.triggerSpec.trigger);
                });
            });
            
            // Prevent the error from continuing
            evt.stopPropagation();
            
            // Log the fallback action
            console.log('HTMX Fallback: Applied fallback content for', elt);
            return false;
        }
    }
});