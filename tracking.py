import math
from dataclasses import dataclass
from typing import List
import time
import json

@dataclass
class NearMissEvent:
    timestamp: float  # Time since game start
    distance: float  # Distance between ship and meteor
    ship_position: tuple[float, float]
    meteor_position: tuple[float, float]
    ship_velocity: tuple[float, float]
    meteor_velocity: tuple[float, float]

class GameTracker:
    def __init__(self):
        self.start_time = time.time()
        self.near_misses: List[NearMissEvent] = []
        self.danger_threshold = 50  # Distance to consider a near miss
        self.critical_threshold = 35  # Distance to consider a critical near miss
        
    def track_frame(self, spaceship, meteors):
        current_time = time.time() - self.start_time
        
        for meteor in meteors:
            distance = math.hypot(spaceship.x - meteor.x, spaceship.y - meteor.y)
            
            # Check for near misses
            if distance < self.danger_threshold and distance > spaceship.SPACESHIP_SIZE + meteor.METEOR_SIZE:
                # Calculate relative velocity
                relative_velocity = math.hypot(
                    spaceship.velocity_x - meteor.velocity_x,
                    spaceship.velocity_y - meteor.velocity_y
                )
                
                event = NearMissEvent(
                    timestamp=current_time,
                    distance=distance,
                    ship_position=(spaceship.x, spaceship.y),
                    meteor_position=(meteor.x, meteor.y),
                    ship_velocity=(spaceship.velocity_x, spaceship.velocity_y),
                    meteor_velocity=(meteor.velocity_x, meteor.velocity_y)
                )
                self.near_misses.append(event)
    
    def save_analytics(self, filename="game_analytics.json"):
        analytics = {
            "total_runtime": time.time() - self.start_time,
            "total_near_misses": len(self.near_misses),
            "near_misses": [
                {
                    "timestamp": event.timestamp,
                    "distance": event.distance,
                    "ship_position": event.ship_position,
                    "meteor_position": event.meteor_position,
                    "ship_velocity": event.ship_velocity,
                    "meteor_velocity": event.meteor_velocity,
                    "severity": "CRITICAL" if event.distance < self.critical_threshold else "WARNING"
                }
                for event in self.near_misses
            ]
        }
        
        with open(filename, 'w') as f:
            json.dump(analytics, f, indent=2)

# Modify the main game file to use this tracker:
def create_game_tracker_hook():
    """
    Add this to spaceship_game.py's main function:
    
    tracker = GameTracker()
    
    # Inside the main game loop, after updating positions:
    tracker.track_frame(spaceship, meteors)
    
    # When the game ends:
    tracker.save_analytics()
    """
    pass
