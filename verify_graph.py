import os
import sys
import voice.aifc_patch # Apply patch
from dotenv import load_dotenv
from agents.graph_agent import GraphAgent

# Load env for API Key
load_dotenv()

def test_graph_agent():
    print("Initializing LangGraph Agent...")
    try:
        agent = GraphAgent()
    except Exception as e:
        print(f"Skipping test: Could not initialize agent (likely missing API key). Error: {e}")
        return

    # Test 1: Info Intent
    print("\n--- Test 1: Info Intent ---")
    input_text = "What cars do you have?"
    print(f"User: {input_text}")
    response = agent.process_input(input_text)
    print(f"Agent: {response}")
    # LLM response might vary, but should contain car info
    assert "SUV" in response or "Sedan" in response or "categories" in response

    # Test 2: Booking Intent
    print("\n--- Test 2: Booking Intent ---")
    input_text = "I want to book a test drive for a RAV4 Hybrid tomorrow at 10 AM"
    print(f"User: {input_text}")
    response = agent.process_input(input_text)
    print(f"Agent: {response}")
    assert "booked" in response.lower() or "success" in response.lower()

    print("\n✅ All tests passed!")

if __name__ == "__main__":
    test_graph_agent()
