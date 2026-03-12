# AutopilotMeteor - Technical Documentation

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Core Components](#core-components)
3. [Autopilot Algorithm](#autopilot-algorithm)
4. [Physics and Mathematics](#physics-and-mathematics)
5. [Game Loop](#game-loop)
6. [Analytics System](#analytics-system)
7. [Configuration](#configuration)

## Architecture Overview

AutopilotMeteor is built using object-oriented design with four main classes working together to create an autonomous spaceship game. The architecture follows a typical game loop pattern with separation of concerns:

- **Game Logic**: Handled by the `main()` function
- **Player Entity**: Managed by the `Spaceship` class
- **Obstacles**: Represented by the `Meteor` class
- **Analytics**: Tracked by the `GameTracker` class
- **Event Data**: Stored in `NearMissEvent` dataclass

## Core Components

### 1. NearMissEvent (Dataclass)

A data structure for recording close encounters between the spaceship and meteors.

**Location**: `spaceship_game.py:29-35`

**Attributes**:
- `timestamp` (float): Time elapsed since game start in seconds
- `distance` (float): Distance between ship and meteor in pixels
- `ship_position` (tuple[float, float]): (x, y) coordinates of the ship
- `meteor_position` (tuple[float, float]): (x, y) coordinates of the meteor
- `ship_velocity` (tuple[float, float]): (vx, vy) velocity components of the ship
- `meteor_velocity` (tuple[float, float]): (vx, vy) velocity components of the meteor

**Purpose**: Provides a structured format for storing telemetry data during near-miss events for post-game analysis.

### 2. GameTracker Class

Monitors gameplay and records analytics about near-miss events.

**Location**: `spaceship_game.py:37-94`

**Attributes**:
- `start_time` (float): Timestamp when tracking began (from `time.time()`)
- `near_misses` (List[NearMissEvent]): Collection of all recorded near-miss events
- `danger_threshold` (int): Distance threshold of 50 pixels for recording events
- `critical_threshold` (int): Distance threshold of 35 pixels for critical classification

**Methods**:

#### `track_frame(spaceship, meteors)`
Called every frame to analyze current game state.

**Algorithm**:
1. Calculate current elapsed time
2. For each meteor:
   - Compute Euclidean distance to spaceship
   - If distance < danger_threshold AND distance > collision radius:
     - Create NearMissEvent with current telemetry
     - Append to near_misses list

**Performance**: O(n) where n is the number of meteors on screen

#### `save_analytics(filename="game_analytics.json")`
Exports analytics data to a JSON file.

**Output Format**:
```json
{
  "total_runtime": <float>,
  "total_near_misses": <int>,
  "near_misses": [
    {
      "timestamp": <float>,
      "distance": <float>,
      "ship_position": [x, y],
      "meteor_position": [x, y],
      "ship_velocity": [vx, vy],
      "meteor_velocity": [vx, vy],
      "severity": "CRITICAL" | "WARNING"
    }
  ]
}
```

**Severity Classification**:
- CRITICAL: distance < 35 pixels
- WARNING: 35 ≤ distance < 50 pixels

### 3. Spaceship Class

The autonomous player-controlled entity with AI navigation.

**Location**: `spaceship_game.py:96-169`

**Attributes**:
- `x, y` (float): Current position coordinates (initialized to screen center)
- `velocity_x, velocity_y` (float): Current velocity components in pixels/frame
- `angle` (float): Current rotation angle in degrees for visual representation

**Methods**:

#### `avoid_meteors(meteors)`
The core autopilot AI algorithm. See [Autopilot Algorithm](#autopilot-algorithm) for details.

**Location**: `spaceship_game.py:104-149`

#### `draw()`
Renders the spaceship as a rotated triangle.

**Location**: `spaceship_game.py:151-169`

**Algorithm**:
1. Define three points of an isosceles triangle pointing upward
2. Apply 2D rotation transformation using rotation matrix:
   ```
   x' = x + (px - x) * cos(θ) - (py - y) * sin(θ)
   y' = y + (px - x) * sin(θ) + (py - y) * cos(θ)
   ```
3. Draw rotated polygon to screen

**Visual Design**: Blue triangle with base of 20 pixels and height of 20 pixels

### 4. Meteor Class

Represents falling obstacles that spawn from screen edges.

**Location**: `spaceship_game.py:171-197`

**Attributes**:
- `x, y` (float): Current position coordinates
- `velocity_x, velocity_y` (float): Velocity components in pixels/frame
- `speed` (int): Random speed value between 1-3

**Initialization Algorithm**:
1. Randomly select spawn edge (left, right, top, or bottom)
2. Position meteor at selected edge with random coordinate
3. Generate random movement angle (0 to 2π radians)
4. Calculate velocity components using polar to Cartesian conversion:
   ```
   velocity_x = cos(angle) * speed
   velocity_y = sin(angle) * speed
   ```

**Methods**:

#### `update()`
Updates position based on velocity (simple Euler integration).

#### `draw()`
Renders meteor as a red circle with 25-pixel radius.

## Autopilot Algorithm

The spaceship's autonomous navigation is implemented in the `avoid_meteors()` method using a force-based approach with multiple behaviors.

**Location**: `spaceship_game.py:104-149`

### Algorithm Steps

#### 1. Threat Detection and Avoidance (Lines 108-119)

```python
for meteor in meteors:
    distance = math.hypot(self.x - meteor.x, self.y - meteor.y)
    if distance < DETECTION_RADIUS and distance > 0:
        in_danger = True
        avoidance_vector[0] += (self.x - meteor.x) / distance
        avoidance_vector[1] += (self.y - meteor.y) / distance
```

**Process**:
- Scans all meteors within 110-pixel detection radius
- Calculates normalized direction vector away from each threat
- Accumulates all avoidance vectors (allows handling multiple simultaneous threats)
- Normalizes and applies with strength factor of 0.5

**Mathematical Formula**:
```
For each meteor within detection radius:
  direction = (ship_pos - meteor_pos) / distance(ship, meteor)
  avoidance_force += direction * AVOIDANCE_STRENGTH
```

#### 2. Centering Behavior (Lines 122-132)

```python
if not in_danger:
    center_x = WIDTH / 2
    center_y = HEIGHT / 2
    dx = center_x - self.x
    dy = center_y - self.y
    # Normalize and apply
    self.velocity_x += dx * CENTERING_STRENGTH
    self.velocity_y += dy * CENTERING_STRENGTH
```

**Purpose**: When no threats are detected, gently pulls ship back toward screen center to optimize positioning for future threats.

**Strength**: 0.1 (much weaker than avoidance to prevent overriding emergency maneuvers)

#### 3. Speed Limiting (Lines 135-138)

```python
speed = math.hypot(self.velocity_x, self.velocity_y)
if speed > MAX_SPEED:
    self.velocity_x = (self.velocity_x / speed) * MAX_SPEED
    self.velocity_y = (self.velocity_y / speed) * MAX_SPEED
```

**Purpose**: Caps maximum velocity at 5 pixels/frame to maintain control and predictability.

**Method**: Vector normalization and rescaling

#### 4. Visual Orientation (Lines 141-142)

```python
self.angle = math.degrees(math.atan2(-self.velocity_y, self.velocity_x))
```

Calculates rotation angle based on velocity direction for realistic visual feedback.

#### 5. Position Update and Boundary Enforcement (Lines 144-149)

```python
self.x += self.velocity_x
self.y += self.velocity_y

self.x = max(SPACESHIP_SIZE, min(WIDTH - SPACESHIP_SIZE, self.x))
self.y = max(SPACESHIP_SIZE, min(HEIGHT - SPACESHIP_SIZE, self.y))
```

Applies velocity to position and clamps to screen boundaries.

### Behavior Characteristics

**Strengths**:
- Handles multiple simultaneous threats effectively
- Smooth, natural-looking movement
- Predictable and deterministic behavior
- Computationally efficient (O(n) per frame)

**Limitations**:
- Reactive rather than predictive (doesn't anticipate future meteor positions)
- Can get trapped between converging meteors
- No pathfinding or long-term planning

## Physics and Mathematics

### Distance Calculations

Euclidean distance using the Pythagorean theorem:
```python
distance = math.hypot(dx, dy)
# Equivalent to: sqrt(dx² + dy²)
```

### Vector Normalization

Converting a vector to unit length:
```python
length = math.hypot(vx, vy)
unit_x = vx / length
unit_y = vy / length
```

### Rotation Matrix

2D rotation transformation:
```
[x']   [cos(θ)  -sin(θ)] [x - cx]   [cx]
[y'] = [sin(θ)   cos(θ)] [y - cy] + [cy]

Where (cx, cy) is the center of rotation
```

### Polar to Cartesian Conversion

Converting angle and magnitude to x/y components:
```python
velocity_x = cos(angle) * speed
velocity_y = sin(angle) * speed
```

## Game Loop

**Location**: `spaceship_game.py:199-261`

### Initialization (Lines 200-206)

1. Create pygame clock for frame rate control
2. Initialize spaceship at screen center
3. Create empty meteors list
4. Set running flag and score counter
5. Create font for score display
6. Initialize GameTracker

### Main Loop (Lines 208-249)

Each frame (60 FPS):

1. **Clear Screen** (Line 209): Fill with black
2. **Spawn Meteors** (Lines 212-213): 5% chance per frame
3. **Update Meteors** (Lines 216-223):
   - Call update() on each meteor
   - Render meteor
   - Remove if off-screen (optimization)
4. **Spaceship AI** (Lines 226-227):
   - Execute avoidance algorithm
   - Render spaceship
5. **Track Analytics** (Line 230): Record near-miss events
6. **Collision Detection** (Lines 233-236):
   - Check distance to all meteors
   - End game if collision detected
7. **Update Score** (Lines 239-241): Increment and display
8. **Event Handling** (Lines 244-246): Check for quit events
9. **Render** (Line 248): Flip display buffer
10. **Frame Rate Control** (Line 249): Cap at 60 FPS

### Game Over Sequence (Lines 251-261)

1. Clear screen
2. Display final score centered
3. Save analytics to JSON file
4. Wait 3 seconds
5. Quit pygame

### Performance Characteristics

- **Frame Rate**: 60 FPS (16.67ms per frame)
- **Meteor Limit**: Unbounded (naturally limited by spawn rate and despawn)
- **Average Meteors**: Typically 10-30 on screen simultaneously

## Analytics System

### Data Collection

The GameTracker monitors every frame for near-miss events using a distance-based threshold system.

**Near-Miss Criteria**:
- Distance < 50 pixels (danger threshold)
- Distance > collision radius (SPACESHIP_SIZE + METEOR_SIZE = 35 pixels)

This creates a detection zone between 35-50 pixels where events are recorded but no collision occurs.

### Data Storage

All near-miss events are stored in memory during gameplay and written to disk at game end.

**Memory Usage**: Approximately 150-200 bytes per event

**Typical Game**: 50-200 near-miss events depending on duration

### Use Cases

The analytics data can be used for:
- Analyzing autopilot performance
- Identifying difficult game states
- Training machine learning models
- Visualizing spaceship trajectories
- Optimizing avoidance parameters

## Configuration

### Tunable Constants

All game parameters are defined as constants at the top of `spaceship_game.py` (lines 12-22):

```python
WIDTH, HEIGHT = 800, 600          # Screen dimensions
SPACESHIP_SIZE = 10               # Collision radius
METEOR_SIZE = 25                  # Collision radius
MAX_SPEED = 5                     # Speed cap (px/frame)
DETECTION_RADIUS = 110            # Sensor range
AVOIDANCE_STRENGTH = 0.5          # Repulsion force
CENTERING_STRENGTH = 0.1          # Return-to-center force
```

### Adjusting Difficulty

**To make easier**:
- Increase `DETECTION_RADIUS` (more warning time)
- Increase `AVOIDANCE_STRENGTH` (stronger reactions)
- Decrease meteor spawn rate (line 212: change 0.05 to lower value)
- Increase `MAX_SPEED` (faster escape ability)

**To make harder**:
- Decrease `DETECTION_RADIUS` (less warning time)
- Decrease `AVOIDANCE_STRENGTH` (weaker reactions)
- Increase meteor spawn rate (line 212: change 0.05 to higher value)
- Decrease `MAX_SPEED` (slower escape ability)
- Increase meteor speed range (line 188: change `random.randint(1, 3)` to higher values)

### Frame Rate

Controlled at line 249:
```python
clock.tick(60)  # 60 FPS
```

Higher frame rates provide smoother visuals but increase computational load. Lower frame rates reduce CPU usage but may make gameplay less responsive.

## Development and Testing

### Running Tests

```bash
pytest test_spaceship_game.py
```

### Test Coverage

The test suite (`test_spaceship_game.py`) includes:

1. **Main Game Loop Test**: Verifies initialization, game loop execution, and cleanup
2. **Collision Detection Test**: Ensures game ends when ship hits meteor
3. **Quit Event Test**: Validates proper handling of window close events

### Adding New Tests

Tests use pytest with mocking to avoid requiring actual pygame display:

```python
@pytest.fixture
def mock_pygame():
    with patch('spaceship_game.pygame') as mock:
        # Setup mocks
        yield mock
```

This allows testing game logic without rendering windows.

## Code Quality

### Style Guidelines

- Follow PEP 8 conventions
- Use descriptive variable names
- Keep functions focused and single-purpose
- Document complex algorithms with comments

### Performance Considerations

- Use `math.hypot()` instead of manual `sqrt(dx*dx + dy*dy)`
- Remove off-screen meteors to prevent unbounded list growth
- Avoid creating new objects in tight loops
- Use efficient data structures (lists for dynamic collections)

## Future Technical Improvements

### Potential Enhancements

1. **Predictive Avoidance**: Calculate future meteor positions to anticipate threats
2. **Quadtree Spatial Partitioning**: Optimize collision detection for large meteor counts
3. **Neural Network Controller**: Replace hand-coded AI with trained network
4. **Replay System**: Record and replay game sessions
5. **Performance Profiling**: Add timing instrumentation for optimization
6. **Configuration File**: Move constants to external JSON/YAML file
7. **Multi-threading**: Separate rendering from logic for better performance

### API Extensibility

The current architecture supports extension through:
- Subclassing `Spaceship` for different AI strategies
- Adding new `GameTracker` analytics types
- Creating custom `Meteor` variants with different behaviors
- Implementing alternative rendering backends
