"""Example demonstrating response caching for TextEmbedder and Moderation models.

This example shows how cache dramatically speeds up:
1. Text embeddings for the same input
2. Content moderation for the same text

Cache is especially useful for:
- Repeated embeddings of common queries
- Batch processing with duplicates
- Content moderation of frequently seen text
"""

import time
from msgflux.models import Model


def test_embedder_cache():
    """Test cache for text embedder."""
    print("\n" + "="*60)
    print("Text Embedder Cache Example")
    print("="*60)

    # Create embedder with cache enabled
    print("\n1. Creating text embedder with cache enabled...")
    embedder = Model.text_embedder(
        "openai/text-embedding-3-small",
        enable_cache=True,
        cache_size=10,
    )
    print("   ✓ Embedder created with cache enabled")

    text = "Machine learning is transforming how we build software."

    # First embedding (cache miss)
    print(f"\n2. First embedding request (cache MISS)...")
    start = time.time()
    response1 = embedder(text)
    embedding1 = response1.consume()
    duration1 = time.time() - start
    print(f"   Embedding dimension: {len(embedding1)}")
    print(f"   Duration: {duration1:.3f}s")

    # Check cache stats
    if embedder._response_cache:
        stats = embedder._response_cache.cache_info()
        print(f"   Cache stats: hits={stats['hits']}, misses={stats['misses']}, size={stats['currsize']}")

    # Second identical embedding (cache hit)
    print(f"\n3. Second identical embedding request (cache HIT)...")
    start = time.time()
    response2 = embedder(text)
    embedding2 = response2.consume()
    duration2 = time.time() - start
    print(f"   Embedding dimension: {len(embedding2)}")
    print(f"   Duration: {duration2:.3f}s")
    print(f"   Speedup: {duration1/duration2:.1f}x faster!")

    # Check cache stats
    if embedder._response_cache:
        stats = embedder._response_cache.cache_info()
        print(f"   Cache stats: hits={stats['hits']}, misses={stats['misses']}, size={stats['currsize']}")

    # Verify embeddings match
    if embedding1 == embedding2:
        print(f"   ✓ Embeddings match (cached correctly)")
    else:
        print(f"   ⚠ Embeddings differ (unexpected)")


def test_moderation_cache():
    """Test cache for content moderation."""
    print("\n" + "="*60)
    print("Content Moderation Cache Example")
    print("="*60)

    # Create moderation model with cache enabled
    print("\n1. Creating moderation model with cache enabled...")
    moderator = Model.moderation(
        "openai/omni-moderation-latest",
        enable_cache=True,
        cache_size=10,
    )
    print("   ✓ Moderator created with cache enabled")

    text = "This is a safe and appropriate message for everyone."

    # First moderation check (cache miss)
    print(f"\n2. First moderation request (cache MISS)...")
    start = time.time()
    response1 = moderator(text)
    result1 = response1.consume()
    duration1 = time.time() - start
    print(f"   Safe: {result1.safe}")
    print(f"   Flagged: {result1.results.flagged}")
    print(f"   Duration: {duration1:.3f}s")

    # Check cache stats
    if moderator._response_cache:
        stats = moderator._response_cache.cache_info()
        print(f"   Cache stats: hits={stats['hits']}, misses={stats['misses']}, size={stats['currsize']}")

    # Second identical moderation check (cache hit)
    print(f"\n3. Second identical moderation request (cache HIT)...")
    start = time.time()
    response2 = moderator(text)
    result2 = response2.consume()
    duration2 = time.time() - start
    print(f"   Safe: {result2.safe}")
    print(f"   Flagged: {result2.results.flagged}")
    print(f"   Duration: {duration2:.3f}s")
    print(f"   Speedup: {duration1/duration2:.1f}x faster!")

    # Check cache stats
    if moderator._response_cache:
        stats = moderator._response_cache.cache_info()
        print(f"   Cache stats: hits={stats['hits']}, misses={stats['misses']}, size={stats['currsize']}")

    # Verify results match
    if result1.safe == result2.safe:
        print(f"   ✓ Results match (cached correctly)")
    else:
        print(f"   ⚠ Results differ (unexpected)")


def test_batch_processing_with_duplicates():
    """Demonstrate cache benefit with batch processing containing duplicates."""
    print("\n" + "="*60)
    print("Batch Processing with Duplicates Example")
    print("="*60)

    embedder = Model.text_embedder(
        "openai/text-embedding-3-small",
        enable_cache=True,
        cache_size=50,
    )

    # Batch of texts with many duplicates (simulating real-world scenario)
    texts = [
        "Machine learning",
        "Deep learning",
        "Machine learning",  # duplicate
        "Neural networks",
        "Deep learning",  # duplicate
        "Machine learning",  # duplicate
        "Artificial intelligence",
        "Deep learning",  # duplicate
    ]

    print(f"\n1. Processing {len(texts)} texts ({len(set(texts))} unique)...")
    start = time.time()

    for i, text in enumerate(texts, 1):
        response = embedder(text)
        embedding = response.consume()
        print(f"   Text {i}: {text[:30]:30s} - dim: {len(embedding)}")

    duration = time.time() - start

    # Check cache stats
    if embedder._response_cache:
        stats = embedder._response_cache.cache_info()
        print(f"\n2. Processing complete!")
        print(f"   Total duration: {duration:.3f}s")
        print(f"   Cache hits: {stats['hits']}")
        print(f"   Cache misses: {stats['misses']}")
        print(f"   Cache hit rate: {stats['hits']/(stats['hits']+stats['misses'])*100:.1f}%")
        print(f"   ✓ Avoided {stats['hits']} API calls thanks to cache!")


def main():
    """Run all examples."""
    print("="*60)
    print("Embedder & Moderation Cache Examples")
    print("="*60)

    try:
        test_embedder_cache()
    except Exception as e:
        print(f"\n⚠ Embedder test failed: {e}")
        print("   Make sure OPENAI_API_KEY is set")

    try:
        test_moderation_cache()
    except Exception as e:
        print(f"\n⚠ Moderation test failed: {e}")
        print("   Make sure OPENAI_API_KEY is set")

    try:
        test_batch_processing_with_duplicates()
    except Exception as e:
        print(f"\n⚠ Batch processing test failed: {e}")
        print("   Make sure OPENAI_API_KEY is set")

    print("\n" + "="*60)
    print("Examples Completed!")
    print("="*60)
    print("\nKey Benefits:")
    print("  • Dramatically faster for repeated operations")
    print("  • Reduces API costs by avoiding redundant calls")
    print("  • Perfect for batch processing with duplicates")
    print("  • Works with both embeddings and moderation")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n⚠ Example failed: {e}")
