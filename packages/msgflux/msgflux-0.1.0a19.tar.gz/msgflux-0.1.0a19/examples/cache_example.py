"""Example demonstrating response caching in chat completion models.

This example shows how to:
1. Enable caching in chat completion models
2. Make identical requests and see cache hits
3. Check cache statistics
4. Clear the cache
"""

import time
from msgflux.models import Model

def main():
    print("=" * 60)
    print("Chat Completion Cache Example")
    print("=" * 60)

    # Create model with caching enabled
    print("\n1. Creating OpenAI chat completion model with cache enabled...")
    model = Model.chat_completion(
        "openai/gpt-4o-mini",
        enable_cache=True,
        cache_size=10,  # Small cache for demo
        temperature=0.7,  # Fixed temperature for deterministic caching
    )
    print(f"   ✓ Model created with cache_size={model.cache_size}")

    # First request (cache miss)
    print("\n2. Making first request (should be a cache MISS)...")
    prompt = "What is 2+2? Give a very short answer."
    start = time.time()
    response1 = model(prompt)
    duration1 = time.time() - start
    print(f"   Response: {response1.consume()}")
    print(f"   Duration: {duration1:.3f}s")

    # Check cache stats
    if model._response_cache:
        stats = model._response_cache.cache_info()
        print(f"   Cache stats: {stats}")

    # Second identical request (cache hit)
    print("\n3. Making identical request (should be a cache HIT)...")
    start = time.time()
    response2 = model(prompt)
    duration2 = time.time() - start
    print(f"   Response: {response2.consume()}")
    print(f"   Duration: {duration2:.3f}s")
    print(f"   Speedup: {duration1/duration2:.1f}x faster")

    # Check cache stats
    if model._response_cache:
        stats = model._response_cache.cache_info()
        print(f"   Cache stats: {stats}")

    # Different request (cache miss)
    print("\n4. Making different request (should be a cache MISS)...")
    start = time.time()
    response3 = model("What is 3+3? Give a very short answer.")
    duration3 = time.time() - start
    print(f"   Response: {response3.consume()}")
    print(f"   Duration: {duration3:.3f}s")

    # Check cache stats
    if model._response_cache:
        stats = model._response_cache.cache_info()
        print(f"   Cache stats: {stats}")

    # Clear cache
    print("\n5. Clearing cache...")
    if model._response_cache:
        model._response_cache.cache_clear()
        stats = model._response_cache.cache_info()
        print(f"   Cache cleared. New stats: {stats}")

    # Request after clear (cache miss)
    print("\n6. Making request after cache clear (should be a cache MISS)...")
    start = time.time()
    response4 = model(prompt)  # Same as first prompt
    duration4 = time.time() - start
    print(f"   Response: {response4.consume()}")
    print(f"   Duration: {duration4:.3f}s")

    # Final stats
    if model._response_cache:
        stats = model._response_cache.cache_info()
        print(f"   Final cache stats: {stats}")

    print("\n" + "=" * 60)
    print("Cache Example Completed!")
    print("=" * 60)


def cache_disabled_example():
    """Example with caching disabled (default behavior)."""
    print("\n\n" + "=" * 60)
    print("Example with Cache DISABLED")
    print("=" * 60)

    # Create model without caching (default)
    print("\n1. Creating model with cache disabled (default)...")
    model = Model.chat_completion(
        "openai/gpt-4o-mini",
        temperature=0.7,
    )
    print(f"   ✓ Model created with enable_cache={model.enable_cache}")

    # Make two identical requests
    prompt = "Count to 3. Be very brief."

    print("\n2. First request...")
    start = time.time()
    response1 = model(prompt)
    duration1 = time.time() - start
    print(f"   Duration: {duration1:.3f}s")

    print("\n3. Second identical request (no cache, full API call)...")
    start = time.time()
    response2 = model(prompt)
    duration2 = time.time() - start
    print(f"   Duration: {duration2:.3f}s")
    print(f"   No caching - both requests hit the API")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    # Run examples
    try:
        main()
        cache_disabled_example()
    except Exception as e:
        print(f"\n⚠ Example failed: {e}")
        print("Note: Make sure OPENAI_API_KEY is set in your environment")
