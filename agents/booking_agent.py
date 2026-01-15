import json
import os
from datetime import datetime

class BookingAgent:
    def __init__(self, data_path: str = "data/bookings.json"):
        self.data_path = data_path
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        if not os.path.exists(self.data_path):
            with open(self.data_path, 'w') as f:
                json.dump([], f)

    def create_booking(self, car_model: str, date: str, time: str) -> bool:
        """
        Creates a new booking and saves it to the JSON file.
        """
        try:
            with open(self.data_path, 'r') as f:
                bookings = json.load(f)
            
            new_booking = {
                "id": len(bookings) + 1,
                "car_model": car_model,
                "date": date,
                "time": time,
                "created_at": datetime.now().isoformat()
            }
            
            bookings.append(new_booking)
            
            with open(self.data_path, 'w') as f:
                json.dump(bookings, f, indent=2)
                
            return True
        except Exception as e:
            print(f"Error creating booking: {e}")
            return False
