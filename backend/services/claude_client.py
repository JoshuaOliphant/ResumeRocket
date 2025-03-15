import os
import json
import hashlib
import logging
from anthropic import Anthropic

logger = logging.getLogger(__name__)

class ClaudeClient:
    """
    Centralized client for interacting with Anthropic's Claude API.
    Supports both Anthropic's prompt caching feature and local file caching.
    """
    
    def __init__(self):
        # Initialize Anthropic client
        self.anthropic_key = os.environ.get('ANTHROPIC_API_KEY')
        if not self.anthropic_key:
            raise ValueError('ANTHROPIC_API_KEY environment variable must be set')
            
        self.client = Anthropic(api_key=self.anthropic_key)
        
        # Set default model 
        self.model = os.environ.get('CLAUDE_MODEL', "claude-3-7-sonnet-20250219")
        
        # Cache configuration
        self.use_anthropic_cache = os.environ.get('USE_ANTHROPIC_CACHE', 'true').lower() == 'true'
        self.use_local_cache = os.environ.get('USE_LOCAL_CACHE', 'true').lower() == 'true'
        self.cache_dir = os.environ.get('PROMPT_CACHE_DIR', 'cache/prompts')
        self.cache_prefix = os.environ.get('CACHE_PREFIX', '')
        
        # Create cache directory if it doesn't exist
        if self.use_local_cache and not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir, exist_ok=True)
            
        logger.info(f"Initialized ClaudeClient with model={self.model}, "
                    f"anthropic_cache={self.use_anthropic_cache}, "
                    f"local_cache={self.use_local_cache}")
    
    def _generate_cache_key(self, model, messages=None, system=None, **kwargs):
        """Generate a deterministic cache key from request parameters"""
        # Create a dictionary with all relevant parameters
        cache_dict = {
            "model": model,
            "prefix": self.cache_prefix
        }
        
        if messages:
            cache_dict["messages"] = messages
        
        if system:
            cache_dict["system"] = system
            
        # Add any additional kwargs, filtering out non-serializable items
        for key, value in kwargs.items():
            if key not in ('stream', 'timeout'):
                cache_dict[key] = value
        
        # Convert to a stable JSON string
        cache_str = json.dumps(cache_dict, sort_keys=True)
        
        # Create hash
        return hashlib.md5(cache_str.encode()).hexdigest()
    
    def _get_from_local_cache(self, cache_key):
        """Attempt to retrieve a response from local file cache"""
        if not self.use_local_cache:
            return None
            
        cache_path = os.path.join(self.cache_dir, f"{cache_key}.json")
        
        if os.path.exists(cache_path):
            try:
                with open(cache_path, 'r') as f:
                    logger.info(f"Local cache hit for {cache_key}")
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error reading from local cache: {str(e)}")
                return None
        return None
        
    def _save_to_local_cache(self, cache_key, response_data):
        """Save a response to the local file cache"""
        if not self.use_local_cache:
            return
            
        cache_path = os.path.join(self.cache_dir, f"{cache_key}.json")
        
        try:
            with open(cache_path, 'w') as f:
                json.dump(response_data, f)
                logger.info(f"Saved to local cache: {cache_key}")
        except Exception as e:
            logger.error(f"Error writing to local cache: {str(e)}")
    
    def _prepare_system_prompt(self, system_text):
        """
        Prepare system prompt with appropriate cache_control if enabled.
        Accepts either a string or a list of system message objects.
        """
        if not system_text:
            return None
            
        # If string provided, convert to proper format with cache_control if needed
        if isinstance(system_text, str):
            system_obj = {
                "type": "text",
                "text": system_text
            }
            
            if self.use_anthropic_cache:
                system_obj["cache_control"] = {"type": "ephemeral"}
                
            return [system_obj]
            
        # If list of system messages provided, add cache_control to the last one if needed
        elif isinstance(system_text, list):
            if self.use_anthropic_cache and system_text:
                # Make a deep copy to avoid modifying the original
                system_copy = []
                for i, msg in enumerate(system_text):
                    msg_copy = msg.copy()
                    # Add cache_control to the last system message
                    if i == len(system_text) - 1 and "cache_control" not in msg_copy:
                        msg_copy["cache_control"] = {"type": "ephemeral"}
                    system_copy.append(msg_copy)
                return system_copy
            return system_text
            
        # Handle unexpected input
        logger.warning(f"Unexpected system prompt format: {type(system_text)}")
        return system_text
    
    def create_message(self, system=None, messages=None, max_tokens=8192, stream=False, **kwargs):
        """
        Create a message using Claude API with prompt caching support.
        
        Args:
            system: System prompt text or list of system message objects
            messages: List of message objects
            max_tokens: Maximum tokens for response
            stream: Whether to stream the response
            **kwargs: Additional parameters for the API call
            
        Returns:
            The API response, either from cache or a fresh request
        """
        try:
            # Default to empty messages list if not provided
            if messages is None:
                messages = []
                
            # Prepare system prompt with cache_control if enabled
            prepared_system = self._prepare_system_prompt(system)
            
            # Generate cache key
            cache_key = self._generate_cache_key(
                model=self.model,
                messages=messages,
                system=prepared_system,
                max_tokens=max_tokens,
                stream=stream,
                **kwargs
            )
            
            # Check local cache first if not streaming
            if not stream and self.use_local_cache:
                cached_response = self._get_from_local_cache(cache_key)
                if cached_response:
                    # Convert cached response to object with attributes matching the Anthropic response
                    return type('obj', (object,), {
                        'content': cached_response['content'],
                        'model': cached_response.get('model', self.model),
                        'usage': cached_response.get('usage', {})
                    })
            
            # Prepare API call parameters
            api_params = {
                'model': self.model,
                'max_tokens': max_tokens,
                'messages': messages,
                **kwargs
            }
            
            # Add system if provided
            if prepared_system:
                api_params['system'] = prepared_system
            
            # Stream or normal response
            if stream:
                return self.client.messages.stream(**api_params)
            else:
                # Make the API call
                response = self.client.messages.create(**api_params)
                
                # Track cache metrics
                self._track_cache_metrics(response)
                
                # Save to local cache if enabled
                if self.use_local_cache:
                    response_data = {
                        'content': response.content,
                        'model': response.model,
                        'usage': response.usage,
                    }
                    self._save_to_local_cache(cache_key, response_data)
                
                return response
                
        except Exception as e:
            logger.error(f"Error in Claude API call: {str(e)}")
            raise
    
    def _track_cache_metrics(self, response):
        """Track and log cache performance metrics"""
        try:
            # Extract metrics from the response
            cache_creation_tokens = response.usage.get('cache_creation_input_tokens', 0)
            cache_read_tokens = response.usage.get('cache_read_input_tokens', 0)
            input_tokens = response.usage.get('input_tokens', 0)
            output_tokens = response.usage.get('output_tokens', 0)
            
            # Calculate approximate costs (based on Claude 3.7 Sonnet pricing)
            base_input_rate = 0.003  # $3/MTok
            cache_write_rate = 0.00375  # $3.75/MTok
            cache_read_rate = 0.0003  # $0.30/MTok
            output_rate = 0.015  # $15/MTok
            
            # Actual cost with caching
            actual_cost = (
                (input_tokens * base_input_rate / 1000000) +
                (cache_creation_tokens * cache_write_rate / 1000000) +
                (cache_read_tokens * cache_read_rate / 1000000) +
                (output_tokens * output_rate / 1000000)
            )
            
            # Cost without caching (if all tokens were charged at full rate)
            no_cache_cost = (
                ((input_tokens + cache_read_tokens) * base_input_rate / 1000000) +
                (output_tokens * output_rate / 1000000)
            )
            
            # Calculate savings
            savings = max(0, no_cache_cost - actual_cost)
            savings_pct = (savings / no_cache_cost * 100) if no_cache_cost > 0 else 0
            
            # Log metrics
            if cache_read_tokens > 0 or cache_creation_tokens > 0:
                logger.info(
                    f"Claude API cache metrics: "
                    f"Input={input_tokens}, "
                    f"Output={output_tokens}, "
                    f"CacheWrite={cache_creation_tokens}, "
                    f"CacheRead={cache_read_tokens}, "
                    f"Cost=${actual_cost:.6f}, "
                    f"Savings=${savings:.6f} ({savings_pct:.1f}%)"
                )
            
        except Exception as e:
            logger.error(f"Error tracking cache metrics: {str(e)}")