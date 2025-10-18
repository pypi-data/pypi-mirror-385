"""Basic example of tracing msgflux workflows with msgtrace."""

from msgtrace.integration import quick_start

# Note: This example requires msgflux to be installed
try:
    from msgflux.message import Message
    from msgflux.nn import Predictor
except ImportError:
    print("This example requires msgflux to be installed.")
    print("Install it with: pip install msgflux")
    exit(1)


def main():
    """Run a basic tracing example."""
    print("Starting msgtrace...")
    observer = quick_start(port=4321)

    print("\nCreating a simple predictor...")
    predictor = Predictor(
        name="sentiment_analyzer",
        task_template="Analyze the sentiment of this text: {text}",
        generation_schema={
            "sentiment": str,  # positive, negative, neutral
            "confidence": float,  # 0.0 to 1.0
            "explanation": str,
        },
    )

    print("\nRunning predictions (traces will be captured)...")

    # Test messages
    test_texts = [
        "I absolutely love this product! It's amazing!",
        "This is terrible. Very disappointed.",
        "It's okay, nothing special.",
    ]

    for i, text in enumerate(test_texts, 1):
        print(f"\n[{i}/{len(test_texts)}] Processing: {text[:50]}...")
        message = Message(inputs={"text": text})

        result = predictor(message)
        output = result.get("outputs")

        print(f"    Sentiment: {output.get('sentiment')}")
        print(f"    Confidence: {output.get('confidence'):.2%}")

    print("\n" + "=" * 70)
    print("✅ All predictions completed!")
    print("\nView traces:")
    print("  - API Docs: http://localhost:4321/docs")
    print("  - List: curl http://localhost:4321/api/v1/traces")
    print("  - CLI: msgtrace list")
    print("  - Stats: msgtrace stats")
    print("\nPress Ctrl+C to stop the server...")

    try:
        # Keep server running
        import time

        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\nStopping server...")
        observer.stop()
        print("✅ Goodbye!")


if __name__ == "__main__":
    main()
