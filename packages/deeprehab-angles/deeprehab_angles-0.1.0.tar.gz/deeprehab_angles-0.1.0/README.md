# DeepRehab Angles

Angle calculation functions for rehabilitation exercises.

## Overview

DeepRehab Angles is a Python package that provides functions for calculating joint angles from body landmarks. It's designed to work with pose estimation data for rehabilitation exercise analysis.

## Features

- Calculate joint angles (knee, shoulder)
- Support for both left and right sides of the body
- Compatible with MediaPipe Pose landmark format
- Only uses Python built-in modules (math)
- Easy to integrate into rehabilitation applications

## Installation

To install the package in development mode:
```bash
pip install -e .
```

To install from source:
```bash
python -m build
pip install dist/deeprehab_angles-0.1.0-py3-none-any.whl
```

## Usage

```python
from deeprehab_angles import knee_angle, shoulder_flexion_angle, Landmark

# Create a list of landmarks (typically from MediaPipe Pose)
landmarks = [Landmark(x, y, z, visibility) for _ in range(33)]

# Set specific landmarks for testing
landmarks[23] = Landmark(0.0, 2.0, 0.0, 1.0)  # Left hip
landmarks[25] = Landmark(0.0, 1.0, 0.0, 1.0)  # Left knee
landmarks[27] = Landmark(1.0, 1.0, 0.0, 1.0)  # Left ankle

# Calculate left knee angle
knee_angle_left = knee_angle(landmarks, "left")
print(f"Left knee angle: {knee_angle_left:.1f}°")

# Set specific landmarks for shoulder
landmarks[12] = Landmark(0.0, 1.0, 0.0, 1.0)  # Right shoulder
landmarks[14] = Landmark(0.0, 0.0, 0.0, 1.0)  # Right elbow
landmarks[16] = Landmark(1.0, 0.0, 0.0, 1.0)  # Right wrist

# Calculate right shoulder flexion angle
shoulder_angle_right = shoulder_flexion_angle(landmarks, "right")
print(f"Right shoulder flexion angle: {shoulder_angle_right:.1f}°")
```

## API

### Main Functions

- `knee_angle(landmarks, side)` - Calculate knee flexion/extension angle
- `shoulder_flexion_angle(landmarks, side)` - Calculate shoulder flexion angle
- `_angle_3p(a, b, c)` - Calculate angle formed by three points

### Data Classes

- `Landmark` - Represents a body landmark with x, y, z coordinates and visibility

## Testing

Run the tests with:
```bash
python -m pytest src/deeprehab_angles/test_angles.py
```

## License

MIT