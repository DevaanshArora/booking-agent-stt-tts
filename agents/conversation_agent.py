import re
from .knowledge_agent import KnowledgeAgent
from .booking_agent import BookingAgent

class ConversationalAgent:
    def __init__(self):
        self.knowledge_agent = KnowledgeAgent()
        self.booking_agent = BookingAgent()
        self.context = {}  # Store session state

    def process_input(self, text: str) -> str:
        """
        Main entry point for processing user input.
        Returns the response string.
        """
        text = text.lower()
        
        # 1. Intent Detection
        if "book" in text or "schedule" in text or "test drive" in text:
            return self._handle_booking_intent(text)
        elif "available" in text or "what cars" in text or "show me" in text:
            return self._handle_info_intent(text)
        elif "hello" in text or "hi" in text:
            return "Hello! I can help you book a test drive. What kind of car are you interested in?"
        elif "exit" in text or "bye" in text or "quit" in text:
            return "Goodbye! Have a great day."
        else:
            return "I'm sorry, I didn't quite catch that. You can ask me to book a test drive or list available cars."

    def _handle_info_intent(self, text: str) -> str:
        categories = self.knowledge_agent.get_categories()
        
        # Check if user asked for specific category
        for cat in categories:
            if cat.lower() in text:
                models = self.knowledge_agent.get_models_by_category(cat)
                model_names = [m['model'] for m in models]
                return f"We have the following {cat}s available: {', '.join(model_names)}."
        
        return f"We have the following categories: {', '.join(categories)}. Which one are you interested in?"

    def _handle_booking_intent(self, text: str) -> str:
        # 2. Entity Extraction (Simple Regex/Keyword based for demo)
        
        # Extract Category/Model
        selected_model = None
        categories = self.knowledge_agent.get_categories()
        for cat in categories:
            if cat.lower() in text:
                # If user just says "SUV", pick the first one for simplicity or ask (simplified here)
                models = self.knowledge_agent.get_models_by_category(cat)
                if models:
                    selected_model = models[0]['model'] # Auto-select first for demo
                    break
        
        # Check for specific model names
        if not selected_model:
             # Iterate all models to see if mentioned
             for cat in categories:
                 models = self.knowledge_agent.get_models_by_category(cat)
                 for m in models:
                     if m['model'].lower() in text:
                         selected_model = m['model']
                         break
        
        # Extract Date (tomorrow, today, specific date)
        date = "tomorrow" # Default
        if "today" in text:
            date = "today"
        # (Real implementation would use dateparser)

        # Extract Time
        # Regex to match times like "10 AM", "2:30pm", "2 PM"
        # \b ensures we don't match parts of words (like '4' in 'RAV4')
        time_match = re.search(r'\b((?:1[0-2]|0?[1-9])(?::\d{2})?\s*(?:am|pm|AM|PM))\b', text)
        time = time_match.group(1) if time_match else "10 AM"

        if selected_model:
            success = self.booking_agent.create_booking(selected_model, date, time)
            if success:
                return f"Great! I have booked a test drive for the {selected_model} for {date} at {time}."
            else:
                return "I'm sorry, I encountered an error saving your booking."
        else:
            return "Which car model would you like to book? We have SUVs and Sedans."
