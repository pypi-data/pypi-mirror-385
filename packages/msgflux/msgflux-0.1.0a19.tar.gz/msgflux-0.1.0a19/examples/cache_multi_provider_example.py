"""Example demonstrating response caching across multiple providers.

This example shows how to enable caching for:
- OpenAI
- Anthropic
- Google
- Mistral

All providers now support the same cache interface!
"""

import time
from msgflux.models import Model


def test_provider_cache(provider_model: str, prompt: str):
    """Test cache for a specific provider."""
    provider_name = provider_model.split("/")[0]
    print(f"\n{'='*60}")
    print(f"Testing {provider_name.upper()} Cache")
    print('='*60)

    # Create model with cache enabled
    print(f"\n1. Creating {provider_name} model with cache enabled...")
    model = Model.chat_completion(
        provider_model,
        enable_cache=True,
        cache_size=10,
        temperature=0.7,
    )
    print(f"   ✓ Model created with cache enabled")

    # First request (cache miss)
    print(f"\n2. First request to {provider_name} (cache MISS)...")
    start = time.time()
    try:
        response1 = model(prompt)
        result1 = response1.consume()
        duration1 = time.time() - start
        print(f"   Response: {result1[:100]}..." if len(str(result1)) > 100 else f"   Response: {result1}")
        print(f"   Duration: {duration1:.3f}s")

        # Check cache stats
        if model._response_cache:
            stats = model._response_cache.cache_info()
            print(f"   Cache stats: hits={stats['hits']}, misses={stats['misses']}, size={stats['currsize']}")

        # Second identical request (cache hit)
        print(f"\n3. Second identical request to {provider_name} (cache HIT)...")
        start = time.time()
        response2 = model(prompt)
        result2 = response2.consume()
        duration2 = time.time() - start
        print(f"   Response: {result2[:100]}..." if len(str(result2)) > 100 else f"   Response: {result2}")
        print(f"   Duration: {duration2:.3f}s")
        print(f"   Speedup: {duration1/duration2:.1f}x faster!")

        # Check cache stats
        if model._response_cache:
            stats = model._response_cache.cache_info()
            print(f"   Cache stats: hits={stats['hits']}, misses={stats['misses']}, size={stats['currsize']}")

        # Verify results match
        if result1 == result2:
            print(f"   ✓ Results match (cached correctly)")
        else:
            print(f"   ⚠ Results differ (unexpected)")

    except Exception as e:
        print(f"   ⚠ Test skipped: {e}")
        print(f"   (Make sure {provider_name.upper()}_API_KEY is set)")


def main():
    """Run cache tests for all providers."""
    print("="*60)
    print("Multi-Provider Cache Example")
    print("="*60)

    prompt = "What is 2+2? Answer in one short sentence."

    # Test each provider
    providers = [
        "openai/gpt-4o-mini",
        "anthropic/claude-3-5-haiku-20241022",
        "google/gemini-1.5-flash",
        "mistral/mistral-small-latest",
    ]

    for provider_model in providers:
        try:
            test_provider_cache(provider_model, prompt)
        except Exception as e:
            print(f"\n⚠ {provider_model} test failed: {e}")

    print("\n" + "="*60)
    print("Cache Example Completed!")
    print("="*60)
    print("\nKey Features:")
    print("  • Cache works across all providers (OpenAI, Anthropic, Google, Mistral)")
    print("  • Significantly faster for identical requests")
    print("  • Optional - disabled by default")
    print("  • Configurable cache size")
    print("  • Uses only Python builtins (no external dependencies)")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n⚠ Example failed: {e}")
