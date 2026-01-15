import json
import os

class KnowledgeAgent:
    def __init__(self, data_path: str = "data/cars.json"):
        self.data_path = data_path
        self.cars = self._load_data()

    def _load_data(self):
        try:
            with open(self.data_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Error: Knowledge base not found at {self.data_path}")
            return {}

    def get_categories(self) -> list:
        """Returns available car categories."""
        return list(self.cars.keys())

    def get_models_by_category(self, category: str) -> list:
        """Returns list of models for a given category (case-insensitive)."""
        for cat, models in self.cars.items():
            if cat.lower() == category.lower():
                return models
        return []

    def get_car_details(self, model_name: str) -> dict:
        """Returns details for a specific model."""
        for cat, models in self.cars.items():
            for car in models:
                if car['model'].lower() == model_name.lower():
                    return car
        return None
