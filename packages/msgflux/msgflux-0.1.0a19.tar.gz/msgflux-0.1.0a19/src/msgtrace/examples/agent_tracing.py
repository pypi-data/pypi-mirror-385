"""Example of tracing agent workflows with msgtrace."""

from msgtrace.integration import quick_start

# Note: This example requires msgflux to be installed
try:
    from msgflux.message import Message
    from msgflux.nn import Agent, Tool
except ImportError:
    print("This example requires msgflux to be installed.")
    print("Install it with: pip install msgflux")
    exit(1)


# Define tools for the agent
@Tool
def calculate(expression: str) -> float:
    """Calculate a mathematical expression.

    Args:
        expression: Math expression to evaluate (e.g., "2 + 2")

    Returns:
        Result of the calculation
    """
    try:
        # Safe evaluation (in production, use a proper math parser)
        result = eval(expression, {"__builtins__": {}}, {})
        return float(result)
    except Exception as e:
        return f"Error: {e}"


@Tool
def get_weather(city: str) -> str:
    """Get weather information for a city.

    Args:
        city: Name of the city

    Returns:
        Weather description
    """
    # Mock implementation
    weather_data = {
        "San Francisco": "Sunny, 72°F",
        "New York": "Cloudy, 65°F",
        "London": "Rainy, 55°F",
    }
    return weather_data.get(city, f"Weather data for {city} not available")


def main():
    """Run an agent tracing example."""
    print("Starting msgtrace with extended telemetry...")
    observer = quick_start(
        port=4321,
        enable_state_dict=True,  # Capture module states
        enable_platform=True,  # Capture platform info
    )

    print("\nCreating an agent with tools...")
    agent = Agent(
        name="helpful_assistant",
        tools=[calculate, get_weather],
        system_prompt="You are a helpful assistant. Use the available tools to answer questions.",
    )

    print("\nRunning agent tasks (traces will be captured)...")

    tasks = [
        "What is 15 * 24?",
        "What's the weather in San Francisco?",
        "Calculate 100 / 5 and tell me the weather in London",
    ]

    for i, task in enumerate(tasks, 1):
        print(f"\n[{i}/{len(tasks)}] Task: {task}")
        message = Message(inputs={"task": task})

        result = agent(message)
        response = result.get("outputs.response")

        print(f"    Response: {response[:100]}...")

    print("\n" + "=" * 70)
    print("✅ All agent tasks completed!")
    print("\n📊 Traces captured:")
    print("  - Agent workflows")
    print("  - Tool executions")
    print("  - Module hierarchies")
    print("  - State transitions")
    print("\nView traces:")
    print("  - API Docs: http://localhost:4321/docs")
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
