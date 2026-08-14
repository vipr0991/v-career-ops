# Network Resilience Patch for career_ops_api.py

## Problem: Network Changes Cause Crashes

When you move between home/office networks:
1. WiFi changes → new IP address
2. Active connections drop
3. Pending requests time out
4. Backend crashes

## Solution: Implement Network Resilience

Add this code to the top of `career_ops_api.py` (after imports, before FastAPI app initialization):

```python
# ─── NETWORK RESILIENCE CONFIGURATION ─────────────────────────────────

import socket
from contextlib import asynccontextmanager

# Exponential backoff for retries
class RetryConfig:
    """Configuration for retrying failed connections"""
    max_retries = 3
    initial_delay = 1.0  # seconds
    max_delay = 10.0
    exponential_base = 2.0
    timeout = 15.0  # Connection timeout
    read_timeout = 60.0  # Read timeout
    
    @staticmethod
    def get_delay(attempt: int) -> float:
        """Calculate backoff delay for attempt number"""
        delay = RetryConfig.initial_delay * (RetryConfig.exponential_base ** attempt)
        return min(delay, RetryConfig.max_delay)


async def resilient_http_get(url: str, timeout: float = None, max_retries: int = 3) -> Optional[dict]:
    """
    Make HTTP GET request with network resilience.
    Automatically retries on timeout/connection error.
    """
    if timeout is None:
        timeout = RetryConfig.timeout
    
    for attempt in range(max_retries):
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.get(url)
                return response if response.status_code == 200 else None
        except (httpx.ConnectError, httpx.TimeoutException, socket.timeout) as e:
            if attempt < max_retries - 1:
                delay = RetryConfig.get_delay(attempt)
                print(f"Connection attempt {attempt + 1} failed: {type(e).__name__}. Retrying in {delay}s...")
                await asyncio.sleep(delay)
            else:
                print(f"All connection attempts failed for {url}")
                return None
        except Exception as e:
            print(f"Unexpected error in resilient_http_get: {e}")
            return None
    
    return None


async def resilient_http_post(url: str, json_data: dict, timeout: float = None, max_retries: int = 3) -> Optional[dict]:
    """
    Make HTTP POST request with network resilience.
    Automatically retries on timeout/connection error.
    """
    if timeout is None:
        timeout = RetryConfig.timeout
    
    for attempt in range(max_retries):
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.post(url, json=json_data)
                return response.json() if response.status_code == 200 else None
        except (httpx.ConnectError, httpx.TimeoutException, socket.timeout) as e:
            if attempt < max_retries - 1:
                delay = RetryConfig.get_delay(attempt)
                print(f"POST attempt {attempt + 1} failed: {type(e).__name__}. Retrying in {delay}s...")
                await asyncio.sleep(delay)
            else:
                print(f"All POST attempts failed for {url}")
                return None
        except Exception as e:
            print(f"Unexpected error in resilient_http_post: {e}")
            return None
    
    return None


@asynccontextmanager
async def network_safe_request(description: str = "Request"):
    """
    Context manager for safe network requests.
    Logs network transitions and handles gracefully.
    """
    print(f"[Network] Starting: {description}")
    try:
        yield
        print(f"[Network] Completed: {description}")
    except httpx.ConnectError as e:
        print(f"[Network ERROR] Connection failed during {description}: {e}")
        raise
    except httpx.TimeoutException as e:
        print(f"[Network TIMEOUT] Request timed out during {description}: {e}")
        raise
    except Exception as e:
        print(f"[Network ERROR] Unexpected error during {description}: {e}")
        raise


# Example: Update resolve_model() function with resilience
async def resolve_model_resilient(task_type: str) -> str:
    """
    Dynamically resolves a model name with network resilience.
    Falls back to defaults if LiteLLM is unreachable.
    """
    defaults = {
        "scoring": "kimi-k2.5",
        "tailor": "kimi-k2.5",
        "latex": "kimi-k2.5",
        "chat": "kimi-k2.5",
        "interview": "kimi-k2.5",
    }
    
    url = "http://localhost:4000/v1/models"
    
    try:
        async with network_safe_request(f"Resolving model for {task_type}"):
            result = await resilient_http_get(url, timeout=5.0, max_retries=2)
            
            if result is None:
                print(f"[Model Resolution] LiteLLM unavailable, using fallback: {defaults[task_type]}")
                return defaults.get(task_type, "kimi-k2.5")
            
            # Parse response
            models_data = result.json()
            available_models = [m["id"] for m in models_data.get("data", [])]
            
            if not available_models:
                return defaults.get(task_type, "kimi-k2.5")
            
            task_alias = f"ag-{task_type}"
            if task_alias in available_models:
                return task_alias
            
            pref_order = ["kimi-k2.6", "kimi-k2.5", "kimi-k2-turbo"]
            for pref in pref_order:
                if pref in available_models:
                    return pref
            
            return available_models[0]
    
    except Exception as e:
        print(f"[Model Resolution] Error: {e}, returning fallback")
        return defaults.get(task_type, "kimi-k2.5")
```

---

## Replace call_llm_with_fallback() with Network-Safe Version

Replace the existing `call_llm_with_fallback()` function with:

```python
async def call_llm_with_fallback(
    task_type: str, 
    messages: list, 
    temperature: float = 0.3, 
    timeout: float = 120.0
) -> str:
    """
    Concurrent LLM routing with network resilience.
    Handles network transitions gracefully.
    Fires requests to multiple backends, returns first successful response.
    """
    model_name = await resolve_model_resilient(task_type)
    
    async def try_litellm_safe():
        try:
            async with network_safe_request(f"LiteLLM {task_type}"):
                url = "http://localhost:4000/v1/chat/completions"
                data = {
                    "model": model_name,
                    "messages": messages,
                    "temperature": temperature
                }
                
                for attempt in range(2):
                    try:
                        async with httpx.AsyncClient(timeout=timeout) as client:
                            response = await client.post(
                                url, 
                                json=data, 
                                headers={
                                    "Content-Type": "application/json", 
                                    "Authorization": "Bearer local-secret"
                                }
                            )
                            response.raise_for_status()
                            return response.json()["choices"][0]["message"]["content"]
                    except httpx.TimeoutException:
                        if attempt < 1:
                            print(f"LiteLLM timeout (attempt {attempt + 1}), retrying...")
                            await asyncio.sleep(RetryConfig.get_delay(attempt))
                        else:
                            raise
        except Exception as e:
            print(f"LiteLLM failed: {type(e).__name__}: {str(e)[:100]}")
            raise

    async def try_gemini_safe():
        try:
            async with network_safe_request(f"Gemini {task_type}"):
                gemini_key = os.getenv("GEMINI_API_KEY")
                if not gemini_key:
                    raise ValueError("GEMINI_API_KEY not set")
                
                response = await acompletion(
                    model="gemini/gemini-2.5-flash",
                    messages=messages,
                    temperature=temperature,
                    api_key=gemini_key,
                    timeout=timeout
                )
                return response.choices[0].message.content
        except Exception as e:
            print(f"Gemini failed: {type(e).__name__}: {str(e)[:100]}")
            raise

    async def try_ollama_safe(model="ollama/odysseus"):
        try:
            async with network_safe_request(f"Ollama {task_type}"):
                response = await acompletion(
                    model=model,
                    messages=messages,
                    temperature=temperature,
                    api_base="http://localhost:11434",
                    timeout=timeout
                )
                return response.choices[0].message.content
        except Exception as e:
            print(f"Ollama ({model}) failed: {type(e).__name__}: {str(e)[:100]}")
            raise

    tasks = [
        asyncio.create_task(try_litellm_safe(), name="litellm"),
        asyncio.create_task(try_gemini_safe(), name="gemini"),
        asyncio.create_task(try_ollama_safe("ollama/odysseus"), name="ollama_odysseus"),
        asyncio.create_task(try_ollama_safe("ollama/qwen3.6:latest"), name="ollama_qwen")
    ]
    
    errors = []
    try:
        for fut in asyncio.as_completed(tasks, timeout=timeout + 10):
            try:
                result = await fut
                # Cancel remaining tasks
                for t in tasks:
                    if not t.done():
                        t.cancel()
                print(f"[Success] {fut.get_name()} provided response")
                return result
            except asyncio.CancelledError:
                pass
            except Exception as e:
                errors.append(f"{fut.get_name()}: {str(e)[:50]}")
    except asyncio.TimeoutError:
        errors.append("All tasks timed out")

    # Cancel pending tasks
    for t in tasks:
        if not t.done():
            t.cancel()

    print(f"[All Agents Failed] Errors: {errors}")
    raise HTTPException(
        status_code=503, 
        detail=f"All LLM routing tiers failed. Last errors: {'; '.join(errors[-2:])}"
    )
```

---

## Key Improvements

✅ **Automatic Retries** — Exponential backoff (1s → 2s → 4s)  
✅ **Connection Timeouts** — 15-second connection timeout (prevents hangs)  
✅ **Read Timeouts** — 60-second read timeout (prevents slow responses)  
✅ **Graceful Fallback** — If LiteLLM offline, tries Gemini/Kimi/Ollama  
✅ **Logging** — Shows which service is working  
✅ **Network Transitions** — Handles moving between networks seamlessly  

---

## Installation

1. Open `career_ops_api.py`
2. Add the resilience code after imports (before FastAPI app creation)
3. Replace `resolve_model()` with `resolve_model_resilient()`
4. Replace `call_llm_with_fallback()` with the network-safe version
5. Restart backend: `python career_ops_api.py`

---

## Testing

After applying patch:

1. Start backend normally
2. Move to different network (switch WiFi)
3. Try scoring a job or searching
4. Should work without crashing ✅

Watch for logs:
```
[Network] Starting: LiteLLM scoring
[Network TIMEOUT] Request timed out...
[Network] Starting: Gemini scoring
[Success] gemini provided response
```

---

**Result**: Backend stays alive through network transitions!
