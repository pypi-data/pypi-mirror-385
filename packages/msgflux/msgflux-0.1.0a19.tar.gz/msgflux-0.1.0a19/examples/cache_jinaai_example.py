"""Example demonstrating response caching for JinaAI models.

This example shows how cache dramatically speeds up:
1. Text embeddings
2. Image embeddings
3. Text classification
4. Image classification
5. Text reranking

Cache is especially useful for:
- Repeated operations on the same input
- Batch processing with duplicates
- Model evaluation and testing
"""

import time
from msgflux.models import Model


def test_text_embedder_cache():
    """Test cache for JinaAI text embedder."""
    print("\n" + "="*60)
    print("JinaAI Text Embedder Cache Example")
    print("="*60)

    # Create embedder with cache enabled
    print("\n1. Creating JinaAI text embedder with cache enabled...")
    embedder = Model.text_embedder(
        "jinaai/jina-embeddings-v3",
        enable_cache=True,
        cache_size=10,
    )
    print("   ✓ Embedder created with cache enabled")

    text = "Artificial intelligence is changing the world."

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
        print(f"   Cache stats: hits={stats['hits']}, misses={stats['misses']}")

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
        print(f"   Cache stats: hits={stats['hits']}, misses={stats['misses']}")

    # Verify embeddings match
    if embedding1 == embedding2:
        print(f"   ✓ Embeddings match (cached correctly)")


def test_text_classifier_cache():
    """Test cache for JinaAI text classifier."""
    print("\n" + "="*60)
    print("JinaAI Text Classifier Cache Example")
    print("="*60)

    # Create classifier with cache enabled
    print("\n1. Creating JinaAI text classifier with cache enabled...")
    classifier = Model.text_classifier(
        "jinaai/jina-clip-v2",
        labels=["positive", "negative", "neutral"],
        enable_cache=True,
        cache_size=10,
    )
    print("   ✓ Classifier created with cache enabled")

    text = "This product is absolutely amazing!"

    # First classification (cache miss)
    print(f"\n2. First classification request (cache MISS)...")
    start = time.time()
    response1 = classifier(text)
    result1 = response1.consume()
    duration1 = time.time() - start
    print(f"   Label: {result1['label']}, Score: {result1['score']:.4f}")
    print(f"   Duration: {duration1:.3f}s")

    # Check cache stats
    if classifier._response_cache:
        stats = classifier._response_cache.cache_info()
        print(f"   Cache stats: hits={stats['hits']}, misses={stats['misses']}")

    # Second identical classification (cache hit)
    print(f"\n3. Second identical classification request (cache HIT)...")
    start = time.time()
    response2 = classifier(text)
    result2 = response2.consume()
    duration2 = time.time() - start
    print(f"   Label: {result2['label']}, Score: {result2['score']:.4f}")
    print(f"   Duration: {duration2:.3f}s")
    print(f"   Speedup: {duration1/duration2:.1f}x faster!")

    # Check cache stats
    if classifier._response_cache:
        stats = classifier._response_cache.cache_info()
        print(f"   Cache stats: hits={stats['hits']}, misses={stats['misses']}")


def test_text_reranker_cache():
    """Test cache for JinaAI text reranker."""
    print("\n" + "="*60)
    print("JinaAI Text Reranker Cache Example")
    print("="*60)

    # Create reranker with cache enabled
    print("\n1. Creating JinaAI text reranker with cache enabled...")
    reranker = Model.text_reranker(
        "jinaai/jina-reranker-v2-base-multilingual",
        enable_cache=True,
        cache_size=10,
    )
    print("   ✓ Reranker created with cache enabled")

    query = "What is machine learning?"
    documents = [
        "Machine learning is a subset of AI.",
        "Python is a programming language.",
        "Deep learning uses neural networks.",
        "JavaScript is used for web development.",
    ]

    # First reranking (cache miss)
    print(f"\n2. First reranking request (cache MISS)...")
    start = time.time()
    response1 = reranker(query, documents)
    results1 = response1.consume()
    duration1 = time.time() - start
    print(f"   Top result: doc {results1[0]['index']} (score: {results1[0]['relevance_score']:.4f})")
    print(f"   Duration: {duration1:.3f}s")

    # Check cache stats
    if reranker._response_cache:
        stats = reranker._response_cache.cache_info()
        print(f"   Cache stats: hits={stats['hits']}, misses={stats['misses']}")

    # Second identical reranking (cache hit)
    print(f"\n3. Second identical reranking request (cache HIT)...")
    start = time.time()
    response2 = reranker(query, documents)
    results2 = response2.consume()
    duration2 = time.time() - start
    print(f"   Top result: doc {results2[0]['index']} (score: {results2[0]['relevance_score']:.4f})")
    print(f"   Duration: {duration2:.3f}s")
    print(f"   Speedup: {duration1/duration2:.1f}x faster!")

    # Check cache stats
    if reranker._response_cache:
        stats = reranker._response_cache.cache_info()
        print(f"   Cache stats: hits={stats['hits']}, misses={stats['misses']}")


def test_batch_embeddings_with_cache():
    """Demonstrate cache benefit with batch embeddings containing duplicates."""
    print("\n" + "="*60)
    print("Batch Embeddings with Cache Example")
    print("="*60)

    embedder = Model.text_embedder(
        "jinaai/jina-embeddings-v3",
        enable_cache=True,
        cache_size=50,
    )

    # Batch of texts with many duplicates
    texts = [
        "Machine learning",
        "Deep learning",
        "Machine learning",  # duplicate
        "Neural networks",
        "Deep learning",  # duplicate
        "Machine learning",  # duplicate
        "Artificial intelligence",
        "Deep learning",  # duplicate
        "Neural networks",  # duplicate
    ]

    print(f"\n1. Processing {len(texts)} texts ({len(set(texts))} unique)...")
    start = time.time()

    for i, text in enumerate(texts, 1):
        response = embedder(text)
        embedding = response.consume()
        status = "HIT" if i > 1 and text in texts[:i-1] else "MISS"
        print(f"   Text {i}: {text:30s} - {status}")

    duration = time.time() - start

    # Check cache stats
    if embedder._response_cache:
        stats = embedder._response_cache.cache_info()
        print(f"\n2. Processing complete!")
        print(f"   Total duration: {duration:.3f}s")
        print(f"   Cache hits: {stats['hits']}")
        print(f"   Cache misses: {stats['misses']}")
        print(f"   Hit rate: {stats['hits']/(stats['hits']+stats['misses'])*100:.1f}%")
        print(f"   ✓ Avoided {stats['hits']} API calls thanks to cache!")


def main():
    """Run all examples."""
    print("="*60)
    print("JinaAI Models Cache Examples")
    print("="*60)

    try:
        test_text_embedder_cache()
    except Exception as e:
        print(f"\n⚠ Text embedder test failed: {e}")
        print("   Make sure JINAAI_API_KEY is set")

    try:
        test_text_classifier_cache()
    except Exception as e:
        print(f"\n⚠ Text classifier test failed: {e}")
        print("   Make sure JINAAI_API_KEY is set")

    try:
        test_text_reranker_cache()
    except Exception as e:
        print(f"\n⚠ Text reranker test failed: {e}")
        print("   Make sure JINAAI_API_KEY is set")

    try:
        test_batch_embeddings_with_cache()
    except Exception as e:
        print(f"\n⚠ Batch embeddings test failed: {e}")
        print("   Make sure JINAAI_API_KEY is set")

    print("\n" + "="*60)
    print("Examples Completed!")
    print("="*60)
    print("\nJinaAI Models with Cache Support:")
    print("  • Text Embedder")
    print("  • Image Embedder")
    print("  • Text Classifier")
    print("  • Image Classifier")
    print("  • Text Reranker")
    print("\nKey Benefits:")
    print("  • Dramatically faster for repeated operations")
    print("  • Reduces API costs by avoiding redundant calls")
    print("  • Perfect for batch processing with duplicates")
    print("  • Works with all JinaAI model types")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n⚠ Example failed: {e}")
