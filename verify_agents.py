from agents.conversation_agent import ConversationalAgent
import json
import os

def test_agent_flow():
    print("Initializing Agent...")
    agent = ConversationalAgent()

    # Test 1: Info Intent
    print("\n--- Test 1: Info Intent ---")
    input_text = "What cars do you have?"
    print(f"User: {input_text}")
    response = agent.process_input(input_text)
    print(f"Agent: {response}")
    assert "categories" in response.lower() or "suv" in response.lower()

    # Test 2: Specific Category Info
    print("\n--- Test 2: Category Info ---")
    input_text = "Show me SUVs"
    print(f"User: {input_text}")
    response = agent.process_input(input_text)
    print(f"Agent: {response}")
    assert "Highlander" in response or "RAV4" in response

    # Test 3: Booking Intent
    print("\n--- Test 3: Booking Intent ---")
    input_text = "I want to book a test drive for a RAV4 Hybrid tomorrow at 2 PM"
    print(f"User: {input_text}")
    response = agent.process_input(input_text)
    print(f"Agent: {response}")
    assert "booked" in response.lower()

    # Verify Booking Persistence
    print("\n--- Verifying Persistence ---")
    with open("data/bookings.json", "r") as f:
        bookings = json.load(f)
        print(f"Bookings found: {len(bookings)}")
        last_booking = bookings[-1]
        print(f"Last Booking: {last_booking}")
        assert last_booking['car_model'] == "RAV4 Hybrid"
        assert last_booking['time'].lower() == "2 pm"

    print("\n✅ All tests passed!")

if __name__ == "__main__":
    test_agent_flow()
