# AutopilotMeteor

An autonomous spaceship game where an AI-controlled spacecraft automatically navigates through a field of incoming meteors using intelligent avoidance algorithms.

## Overview

AutopilotMeteor is a Python-based arcade game featuring a self-piloting spaceship that uses real-time decision-making to avoid meteors falling from all sides of the screen. The game demonstrates autonomous navigation, collision avoidance, and game analytics tracking.

## Features

- **Autonomous AI Navigation**: The spaceship automatically detects and avoids meteors within a detection radius
- **Smart Avoidance Algorithm**: Calculates repulsion vectors from nearby threats and centers itself when safe
- **Real-time Analytics**: Tracks near-miss events with detailed telemetry data
- **Game Statistics**: Records gameplay data including timestamps, positions, velocities, and event severity
- **Visual Feedback**: The spaceship rotates based on its movement direction for realistic visuals

## Requirements

- Python 3.7 or higher
- pygame

## Installation

1. Clone this repository:
```bash
git clone https://github.com/DaytonFishell/AutopilotMeteor.git
cd AutopilotMeteor
```

2. Install the required dependencies:
```bash
pip install pygame
```

## Usage

Run the game:
```bash
python spaceship_game.py
```

### How to Play

The game is fully autonomous - just watch the spaceship navigate through the meteor field! The goal is to see how long the autopilot can survive.

- **Score**: Increases automatically over time (displayed in top-left corner)
- **Game Over**: Occurs when the spaceship collides with a meteor
- **Quit**: Close the window or wait for collision

### Controls

No manual controls - the spaceship flies itself! Press the window close button or wait for a collision to end the game.

## Game Mechanics

### Spaceship Autopilot

The spaceship uses a sophisticated avoidance algorithm:

1. **Detection**: Scans for meteors within a 110-pixel radius
2. **Avoidance**: Calculates repulsion vectors from detected threats
3. **Centering**: Returns toward screen center when no danger is present
4. **Speed Limiting**: Caps velocity at 5 pixels per frame
5. **Boundary Protection**: Stays within screen bounds

### Meteors

- Spawn randomly from all four edges of the screen
- Move in random directions at varying speeds (1-3 pixels/frame)
- Continuously spawn throughout the game (5% chance per frame)

### Game Constants

| Parameter | Value | Description |
|-----------|-------|-------------|
| Screen Size | 800x600 | Game window dimensions |
| Detection Radius | 110px | How far the ship can "see" meteors |
| Avoidance Strength | 0.5 | Force applied to avoid threats |
| Centering Strength | 0.1 | Force pulling ship to center |
| Max Speed | 5 px/frame | Maximum ship velocity |
| Near-Miss Threshold | 50px | Distance to record an event |
| Critical Threshold | 35px | Distance considered critical |

## Analytics

After each game, analytics are automatically saved to `game_analytics.json`:

```json
{
  "total_runtime": 45.2,
  "total_near_misses": 127,
  "near_misses": [
    {
      "timestamp": 12.4,
      "distance": 42.3,
      "ship_position": [400, 300],
      "meteor_position": [380, 320],
      "ship_velocity": [2.1, -1.5],
      "meteor_velocity": [-1.8, 2.2],
      "severity": "WARNING"
    }
  ]
}
```

### Event Severity Levels

- **CRITICAL**: Distance < 35 pixels (very close call)
- **WARNING**: Distance < 50 pixels but ≥ 35 pixels (close call)

## Testing

Run the test suite:
```bash
pytest test_spaceship_game.py
```

The test suite includes:
- Game loop initialization and cleanup tests
- Collision detection verification
- Event handling tests

## Project Structure

```
AutopilotMeteor/
├── spaceship_game.py       # Main game implementation
├── test_spaceship_game.py  # Test suite
├── README.md               # This file
└── game_analytics.json     # Generated after each game
```

## Code Architecture

### Classes

- **`NearMissEvent`**: Data structure for recording close encounters
- **`GameTracker`**: Monitors and records near-miss events, saves analytics
- **`Spaceship`**: The autonomous player ship with AI navigation
- **`Meteor`**: Falling obstacles that spawn from screen edges

See [DOCUMENTATION.md](DOCUMENTATION.md) for detailed technical documentation.

## Contributing

Contributions are welcome! Feel free to submit issues or pull requests.

## License

This project is open source and available under the MIT License.

## Future Enhancements

Potential improvements:
- Difficulty levels with adjustable spawn rates
- Multiple spaceships with competitive AI
- Power-ups and special abilities
- High score leaderboard
- Visual effects for near-misses
- Sound effects and background music

## Author

Dayton Fishell

## Acknowledgments

Built with Pygame, the cross-platform set of Python modules designed for writing video games.
