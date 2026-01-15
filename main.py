import sys
import time

from dotenv import load_dotenv
from voice.stt import STTProvider
from voice.tts import TTSProvider
# from agents.conversation_agent import ConversationalAgent # Legacy
from agents.graph_agent import GraphAgent

# Load environment variables (API keys)
load_dotenv()

def main():
    print("Initializing Auto Voice Agent (LangGraph Powered)...")
    
    # Initialize components
    stt = STTProvider()
    tts = TTSProvider()
    # agent = ConversationalAgent()
    try:
        agent = GraphAgent()
    except Exception as e:
        print(f"Error initializing LangGraph Agent: {e}")
        print("Ensure OPENAI_API_KEY is set in .env")
        return
    
    welcome_msg = "Welcome to the Auto Dealership Voice Assistant. How can I help you today?"
    tts.speak(welcome_msg)
    
    while True:
        try:
            # 1. Listen
            user_input = stt.listen()
            
            if not user_input:
                continue
                
            # 2. Process
            response = agent.process_input(user_input)
            
            # 3. Respond
            tts.speak(response)
            
            # Exit condition
            if "goodbye" in response.lower():
                break
                
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"An error occurred: {e}")
            break

if __name__ == "__main__":
    main()
