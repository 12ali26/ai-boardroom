import httpx
import asyncio
import time
from typing import List, Dict, Any, Optional
from .config import settings
from .logger import get_logger


class OpenRouterClient:
    # Model fallback hierarchy
    MODEL_FALLBACKS = {
        "openai/gpt-4": ["openai/gpt-4-turbo", "openai/gpt-3.5-turbo"],
        "anthropic/claude-3-sonnet": ["anthropic/claude-3-haiku", "openai/gpt-3.5-turbo"],
        "google/gemini-pro": ["openai/gpt-3.5-turbo", "anthropic/claude-3-haiku"]
    }
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.openrouter_api_key
        self.base_url = "https://openrouter.ai/api/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://ai-boardroom.local",
            "X-Title": "AI Boardroom"
        }
        
        # Rate limiting
        self.last_request_time = 0
        self.min_request_interval = 1.0  # Minimum 1 second between requests
        
        # Setup logging
        self.logger = get_logger('openrouter')

    async def _rate_limit(self):
        """Apply rate limiting between requests."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last
            self.logger.debug(f"Rate limiting: sleeping for {sleep_time:.2f} seconds")
            await asyncio.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    async def _make_request_with_retry(self, method: str, url: str, **kwargs) -> httpx.Response:
        """Make HTTP request with retry logic."""
        max_retries = 3
        base_delay = 1.0
        
        for attempt in range(max_retries + 1):
            try:
                await self._rate_limit()
                
                async with httpx.AsyncClient(timeout=30.0) as client:
                    if method.upper() == "GET":
                        response = await client.get(url, **kwargs)
                    elif method.upper() == "POST":
                        response = await client.post(url, **kwargs)
                    else:
                        raise ValueError(f"Unsupported method: {method}")
                    
                    response.raise_for_status()
                    return response
                    
            except httpx.HTTPStatusError as e:
                status_code = e.response.status_code
                self.logger.warning(f"HTTP error {status_code} on attempt {attempt + 1}/{max_retries + 1}")
                
                # Don't retry on client errors (4xx) except for rate limits
                if 400 <= status_code < 500 and status_code != 429:
                    raise Exception(f"OpenRouter API client error: {status_code} - {e.response.text}")
                
                if attempt == max_retries:
                    raise Exception(f"OpenRouter API error after {max_retries + 1} attempts: {status_code} - {e.response.text}")
                
                # Exponential backoff with jitter
                delay = base_delay * (2 ** attempt) + (time.time() % 1)
                self.logger.info(f"Retrying in {delay:.2f} seconds...")
                await asyncio.sleep(delay)
                
            except httpx.RequestError as e:
                self.logger.warning(f"Request error on attempt {attempt + 1}/{max_retries + 1}: {str(e)}")
                
                if attempt == max_retries:
                    raise Exception(f"OpenRouter request failed after {max_retries + 1} attempts: {str(e)}")
                
                delay = base_delay * (2 ** attempt)
                self.logger.info(f"Retrying in {delay:.2f} seconds...")
                await asyncio.sleep(delay)
    
    async def list_models(self) -> Dict[str, Any]:
        """List available models from OpenRouter with retry logic."""
        try:
            self.logger.info("Fetching available models from OpenRouter")
            response = await self._make_request_with_retry(
                "GET",
                f"{self.base_url}/models",
                headers=self.headers
            )
            result = response.json()
            self.logger.info(f"Successfully fetched {len(result.get('data', []))} models")
            return result
        except Exception as e:
            self.logger.error(f"Failed to list models: {str(e)}")
            raise

    async def chat_completion(
        self, 
        model: str, 
        messages: List[Dict[str, str]], 
        max_tokens: Optional[int] = None,
        temperature: float = 0.7,
        use_fallback: bool = True
    ) -> Dict[str, Any]:
        """Send a chat completion request to OpenRouter with fallback models."""
        models_to_try = [model]
        
        # Add fallback models if enabled
        if use_fallback and model in self.MODEL_FALLBACKS:
            models_to_try.extend(self.MODEL_FALLBACKS[model])
        
        last_error = None
        
        for attempt_model in models_to_try:
            try:
                self.logger.info(f"Attempting chat completion with model: {attempt_model}")
                
                payload = {
                    "model": attempt_model,
                    "messages": messages,
                    "temperature": temperature
                }
                if max_tokens:
                    payload["max_tokens"] = max_tokens
                
                response = await self._make_request_with_retry(
                    "POST",
                    f"{self.base_url}/chat/completions",
                    headers=self.headers,
                    json=payload
                )
                
                result = response.json()
                
                # Log successful completion
                if attempt_model != model:
                    self.logger.warning(f"Used fallback model {attempt_model} instead of {model}")
                else:
                    self.logger.info(f"Successfully completed chat with {attempt_model}")
                
                # Add metadata about which model was actually used
                result["_ai_boardroom_metadata"] = {
                    "requested_model": model,
                    "actual_model": attempt_model,
                    "used_fallback": attempt_model != model
                }
                
                return result
                
            except Exception as e:
                last_error = e
                self.logger.warning(f"Model {attempt_model} failed: {str(e)}")
                
                # If this is the last model to try, don't continue
                if attempt_model == models_to_try[-1]:
                    break
                
                # Wait a bit before trying the next model
                await asyncio.sleep(0.5)
        
        # All models failed
        self.logger.error(f"All models failed. Last error: {str(last_error)}")
        raise Exception(f"Chat completion failed with all attempted models ({', '.join(models_to_try)}). Last error: {str(last_error)}")


async def test_openrouter_with_fallbacks():
    """Test OpenRouter client with fallback functionality."""
    print("Testing OpenRouter Client with Error Handling")
    print("=" * 50)
    
    client = OpenRouterClient()
    
    # Test 1: List models
    print("1. Testing model listing...")
    try:
        models = await client.list_models()
        print(f"✅ Successfully fetched {len(models.get('data', []))} models")
    except Exception as e:
        print(f"❌ Failed to list models: {e}")
    
    # Test 2: Chat completion with fallback
    print("\n2. Testing chat completion with fallbacks...")
    test_messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Say hello in one sentence."}
    ]
    
    test_models = ["openai/gpt-4", "anthropic/claude-3-sonnet", "invalid/model"]
    
    for model in test_models:
        try:
            print(f"\nTesting model: {model}")
            response = await client.chat_completion(
                model=model,
                messages=test_messages,
                max_tokens=50
            )
            
            metadata = response.get("_ai_boardroom_metadata", {})
            actual_model = metadata.get("actual_model", model)
            used_fallback = metadata.get("used_fallback", False)
            
            if used_fallback:
                print(f"⚠️  Used fallback model: {actual_model}")
            else:
                print(f"✅ Success with requested model: {actual_model}")
            
            content = response["choices"][0]["message"]["content"]
            print(f"Response: {content[:100]}...")
            
        except Exception as e:
            print(f"❌ Failed with {model}: {e}")
    
    print("\nTest completed.")


if __name__ == "__main__":
    import asyncio
    
    # Set up logging for testing
    logging.basicConfig(level=logging.INFO)
    
    asyncio.run(test_openrouter_with_fallbacks())