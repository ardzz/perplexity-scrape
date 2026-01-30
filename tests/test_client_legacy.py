"""
Test script for Perplexity API Client.
"""

import sys
import pytest
from src.core.perplexity_client import PerplexityClient, PerplexityResponse


def test_basic_query():
    """Test a basic query to Perplexity."""
    print("=" * 60)
    print("Testing Perplexity API Client")
    print("=" * 60)

    try:
        client = PerplexityClient()
        print("✓ Client initialized successfully")
    except ValueError as e:
        print(f"✗ Failed to initialize client: {e}")
        pytest.fail(f"Failed to initialize client: {e}")

    query = "What is the capital of France?"
    print(f"\nQuery: {query}")
    print("-" * 60)

    try:
        print("\nStreaming response...")
        event_count = 0

        for event in client.ask_stream(query):
            event_count += 1

            # Print progress indicators
            if "status" in event:
                print(f"  Status: {event.get('status')}")
            elif "text" in event:
                print(f"  Text chunk received ({len(event['text'])} chars)")
            elif "blocks" in event:
                print(f"  Blocks received: {len(event['blocks'])} blocks")

        print(f"\n✓ Received {event_count} SSE events")

    except Exception as e:
        print(f"\n✗ Streaming failed: {e}")
        import traceback

        traceback.print_exc()
        pytest.fail(f"Streaming failed: {e}")

    # Test full response
    print("\n" + "-" * 60)
    print("Testing full response...")

    try:
        response = client.ask(query)

        print(f"\n✓ Response received:")
        print(f"  - Text length: {len(response.text)} chars")
        print(f"  - Citations: {len(response.citations)}")
        print(f"  - Media items: {len(response.media_items)}")
        print(f"  - Related queries: {len(response.related_queries)}")
        print(f"  - Raw events: {len(response.raw_events)}")

        if response.text:
            print(f"\nResponse preview:")
            print("-" * 40)
            preview = response.text[:500]
            print(preview)
            if len(response.text) > 500:
                print("... (truncated)")

        assert True  # Test passed

    except Exception as e:
        print(f"\n✗ Full response failed: {e}")
        import traceback

        traceback.print_exc()
        pytest.fail(f"Full response failed: {e}")


def main():
    """Run all tests."""
    success = test_basic_query()

    print("\n" + "=" * 60)
    if success:
        print("✓ All tests passed!")
        sys.exit(0)
    else:
        print("✗ Tests failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
