import pygame
import random
import math
import time
import json
from dataclasses import dataclass
from typing import List, Tuple

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
SPACESHIP_SIZE = 10
METEOR_SIZE = 25
MAX_SPEED = 5
DETECTION_RADIUS = 110
AVOIDANCE_STRENGTH = 0.5
CENTERING_STRENGTH = 0.1

# Set up display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Autopilot Spaceship")

@dataclass
class NearMissEvent:
    timestamp: float  # Time since game start
    distance: float  # Distance between ship and meteor
    ship_position: tuple[float, float]
    meteor_position: tuple[float, float]
    ship_velocity: tuple[float, float]
    meteor_velocity: tuple[float, float]

class GameTracker:
    """A class for tracking and analyzing game events and near-misses between spaceship and meteors.
    This class maintains records of near-miss events during gameplay and provides functionality
    to save analytics data to a JSON file. It tracks distances between the spaceship and meteors,
    recording events when they come within a defined danger threshold.
    Attributes:
        start_time (float): The timestamp when tracking began
        near_misses (List[NearMissEvent]): List of recorded near-miss events
        danger_threshold (int): Distance threshold (in pixels) to consider an event a near miss (default: 50)
        critical_threshold (int): Distance threshold (in pixels) to consider an event critical (default: 35)
    Methods:
        track_frame(spaceship, meteors): Analyzes current frame for near-miss events
        save_analytics(filename): Saves collected analytics data to a JSON file
    """
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
            if distance < self.danger_threshold and distance > SPACESHIP_SIZE + METEOR_SIZE:
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

class Spaceship:
    def __init__(self):
        self.x = WIDTH // 2
        self.y = HEIGHT // 2
        self.velocity_x = 0
        self.velocity_y = 0
        self.angle = 0  # New angle attribute
        
    def avoid_meteors(self, meteors):
        avoidance_vector = [0, 0]
        in_danger = False
        
        for meteor in meteors:
            distance = math.hypot(self.x - meteor.x, self.y - meteor.y)
            if distance < DETECTION_RADIUS and distance > 0:
                in_danger = True
                avoidance_vector[0] += (self.x - meteor.x) / distance
                avoidance_vector[1] += (self.y - meteor.y) / distance
                
        # Normalize and apply avoidance
        length = math.hypot(*avoidance_vector)
        if length > 0:
            self.velocity_x += (avoidance_vector[0] / length) * AVOIDANCE_STRENGTH
            self.velocity_y += (avoidance_vector[1] / length) * AVOIDANCE_STRENGTH
            
        # If not in danger, move towards the center of the screen
        if not in_danger:
            center_x = WIDTH / 2
            center_y = HEIGHT / 2
            dx = center_x - self.x
            dy = center_y - self.y
            norm = math.hypot(dx, dy)
            if norm != 0:
                dx /= norm
                dy /= norm
            self.velocity_x += dx * CENTERING_STRENGTH
            self.velocity_y += dy * CENTERING_STRENGTH
            
        # Limit speed
        speed = math.hypot(self.velocity_x, self.velocity_y)
        if speed > MAX_SPEED:
            self.velocity_x = (self.velocity_x / speed) * MAX_SPEED
            self.velocity_y = (self.velocity_y / speed) * MAX_SPEED
            
        # Calculate angle
        if self.velocity_x != 0 or self.velocity_y != 0:
            self.angle = math.degrees(math.atan2(-self.velocity_y, self.velocity_x))
            
        self.x += self.velocity_x
        self.y += self.velocity_y
        
        # Keep within screen bounds
        self.x = max(SPACESHIP_SIZE, min(WIDTH - SPACESHIP_SIZE, self.x))
        self.y = max(SPACESHIP_SIZE, min(HEIGHT - SPACESHIP_SIZE, self.y))
        
    def draw(self):
        # Define the original points of the spaceship
        points = [
            (self.x, self.y + SPACESHIP_SIZE),  # New front of the ship
            (self.x - SPACESHIP_SIZE, self.y - SPACESHIP_SIZE),
            (self.x + SPACESHIP_SIZE, self.y - SPACESHIP_SIZE)
        ]
        
        # Rotate the points
        rotated_points = [
            (
                self.x + (x - self.x) * math.cos(math.radians(self.angle)) - (y - self.y) * math.sin(math.radians(self.angle)),
                self.y + (x - self.x) * math.sin(math.radians(self.angle)) + (y - self.y) * math.cos(math.radians(self.angle))
            )
            for x, y in points
        ]
        
        # Draw the rotated polygon
        pygame.draw.polygon(screen, BLUE, rotated_points)

class Meteor:
    def __init__(self):
        side = random.choice(['left', 'right', 'top', 'bottom'])
        if side == 'left':
            self.x = 0
            self.y = random.randint(0, HEIGHT)
        elif side == 'right':
            self.x = WIDTH
            self.y = random.randint(0, HEIGHT)
        elif side == 'top':
            self.x = random.randint(0, WIDTH)
            self.y = 0
        else:
            self.x = random.randint(0, WIDTH)
            self.y = HEIGHT
            
        angle = random.uniform(0, 2 * math.pi)
        self.speed = random.randint(1, 3)
        self.velocity_x = math.cos(angle) * self.speed
        self.velocity_y = math.sin(angle) * self.speed
        
    def update(self):
        self.x += self.velocity_x
        self.y += self.velocity_y
        
    def draw(self):
        pygame.draw.circle(screen, RED, (int(self.x), int(self.y)), METEOR_SIZE)

def main():
    clock = pygame.time.Clock()
    spaceship = Spaceship()
    meteors = []
    running = True
    score = 0
    font = pygame.font.Font(None, 36)
    tracker = GameTracker()  # Initialize the game tracker

    while running:
        screen.fill((0, 0, 0))
        
        # Spawn meteors
        if random.random() < 0.05:
            meteors.append(Meteor())
            
        # Update and draw meteors
        for meteor in meteors[:]:
            meteor.update()
            meteor.draw()
            
            # Remove off-screen meteors
            if (meteor.x < -METEOR_SIZE or meteor.x > WIDTH + METEOR_SIZE or 
                meteor.y < -METEOR_SIZE or meteor.y > HEIGHT + METEOR_SIZE):
                meteors.remove(meteor)
                
        # Spaceship AI and drawing
        spaceship.avoid_meteors(meteors)
        spaceship.draw()
        
        # Track near misses
        tracker.track_frame(spaceship, meteors)
        
        # Collision detection
        for meteor in meteors:
            distance = math.hypot(spaceship.x - meteor.x, spaceship.y - meteor.y)
            if distance < SPACESHIP_SIZE + METEOR_SIZE:
                running = False
                
        # Update score
        score += 1
        text = font.render(f"Score: {score//10}", True, WHITE)
        screen.blit(text, (10, 10))
        
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
        pygame.display.flip()
        clock.tick(60)
        
    # Game over screen
    screen.fill((0, 0, 0))
    text = font.render(f"Game Over! Final Score: {score//10}", True, WHITE)
    screen.blit(text, (WIDTH//2 - 180, HEIGHT//2 - 18))
    pygame.display.flip()
    
    # Save analytics before quitting
    tracker.save_analytics()
    
    pygame.time.wait(3000)
    pygame.quit()

if __name__ == "__main__":
    main()