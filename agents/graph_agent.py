import os
from typing import Annotated, Literal, TypedDict
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver

from .knowledge_agent import KnowledgeAgent
from .booking_agent import BookingAgent

# Initialize Legacy Agents to reuse logic
knowledge_agent = KnowledgeAgent()
booking_agent = BookingAgent()

# --- Define Tools ---

@tool
def lookup_cars(category: str = None):
    """
    Look up available car models. 
    If a category is provided (e.g., 'SUV', 'Sedan'), returns models for that category.
    If no category is provided, returns all available categories.
    """
    if category:
        models = knowledge_agent.get_models_by_category(category)
        if not models:
            return f"No models found for category: {category}. Available categories: {knowledge_agent.get_categories()}"
        return str(models)
    else:
        return f"Available categories: {knowledge_agent.get_categories()}"

@tool
def book_test_drive(model: str, date: str, time: str):
    """
    Book a test drive for a specific car model at a given date and time.
    Returns the result of the booking attempt.
    """
    success = booking_agent.create_booking(model, date, time)
    if success:
        return f"Successfully booked a test drive for {model} on {date} at {time}."
    else:
        return "Failed to create booking. Please try again."

# --- Define Graph ---

class State(TypedDict):
    messages: Annotated[list, add_messages]

class GraphAgent:
    def __init__(self):
        self.tools = [lookup_cars, book_test_drive]
        self.llm = ChatOpenAI(model="gpt-4o", temperature=0)
        self.llm_with_tools = self.llm.bind_tools(self.tools)
        
        # Build Graph
        graph_builder = StateGraph(State)
        
        graph_builder.add_node("chatbot", self.chatbot)
        graph_builder.add_node("tools", ToolNode(self.tools))
        
        graph_builder.add_edge(START, "chatbot")
        graph_builder.add_conditional_edges(
            "chatbot",
            tools_condition,
        )
        graph_builder.add_edge("tools", "chatbot")
        
        self.graph = graph_builder.compile(checkpointer=MemorySaver())
        self.config = {"configurable": {"thread_id": "1"}}

    def chatbot(self, state: State):
        return {"messages": [self.llm_with_tools.invoke(state["messages"])]}

    def process_input(self, user_input: str) -> str:
        """
        Process user input through the LangGraph agent.
        """
        from datetime import datetime
        current_date = datetime.now().strftime("%Y-%m-%d")

        # Add system message if it's the first turn (simplified check)
        # In a real app, we'd manage this better, but for now we rely on the prompt.
        system_prompt = (
            f"Current Date: {current_date}\n"
            "You are a helpful auto dealership assistant. "
            "Your goal is to help customers book test drives. "
            "First, help them find a car model using 'lookup_cars'. "
            "Then, once they decide on a model, date, and time, use 'book_test_drive'. "
            "Always confirm the booking details with the user. "
            "Always speak in English."
        )
        
        inputs = {"messages": [SystemMessage(content=system_prompt), HumanMessage(content=user_input)]}
        
        # Stream the graph to get the final response
        final_response = ""
        for event in self.graph.stream(inputs, self.config, stream_mode="values"):
            message = event["messages"][-1]
            if isinstance(message, str): # Should not happen with ChatOpenAI but safe guard
                 final_response = message
            elif message.content:
                final_response = message.content
                
        return final_response
