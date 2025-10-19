# deeprehab-visualize

Visualization functions for DeepRehab pose data and analysis results.

## Installation

```bash
pip install deeprehab-visualize
```

## Usage

### Basic Example

```python
import cv2
from deeprehab_visualize import (
    draw_landmarks_on_frame, 
    visualize_angles_on_frame, 
    visualize_score_on_frame,
    create_pose_connections
)

# Load a video frame
frame = cv2.imread("frame.jpg")

# Assume you have landmarks from deeprehab-pose
landmarks = extract_landmarks("video.mp4")[0]  # First frame landmarks

# Draw landmarks on frame
connections = create_pose_connections()
annotated_frame = draw_landmarks_on_frame(frame, landmarks, connections)

# Visualize angles (assuming you have angle data from deeprehab-angles)
angles = {"left_knee": 90.5, "right_knee": 89.2}
annotated_frame = visualize_angles_on_frame(annotated_frame, landmarks, angles)

# Visualize score (assuming you have score data from deeprehab-movements)
score_result = score_deep_squat(landmarks)  # Example scoring function
annotated_frame = visualize_score_on_frame(annotated_frame, score_result)

# Save or display the annotated frame
cv2.imwrite("annotated_frame.jpg", annotated_frame)
```

### Functions

#### `draw_landmarks_on_frame(frame, landmarks, connections=None)`

Draw pose landmarks on a video frame.

Parameters:
- `frame`: Video frame as numpy array (H, W, C)
- `landmarks`: List of landmark objects with x, y, z, visibility attributes
- `connections`: List of tuples defining connections between landmarks

Returns:
- Frame with landmarks drawn on it

#### `visualize_angles_on_frame(frame, landmarks, angles, position=(50, 50))`

Visualize angle measurements on a video frame.

Parameters:
- `frame`: Video frame as numpy array (H, W, C)
- `landmarks`: List of landmark objects
- `angles`: Dictionary of angle measurements (e.g., {'left_knee': 90.0})
- `position`: Position to display text (x, y)

Returns:
- Frame with angle measurements displayed

#### `visualize_score_on_frame(frame, score_result, position=(50, 150))`

Visualize FMS score on a video frame.

Parameters:
- `frame`: Video frame as numpy array (H, W, C)
- `score_result`: ScoreResult object with score, reason, and details
- `position`: Position to display text (x, y)

Returns:
- Frame with score displayed

#### `create_pose_connections()`

Create standard pose connections for visualization.

Returns:
- List of tuples representing connections between landmarks

## Integration with Other DeepRehab Packages

```python
from deeprehab_pose import extract_landmarks
from deeprehab_angles import knee_angle
from deeprehab_movements import score_deep_squat
from deeprehab_visualize import (
    draw_landmarks_on_frame, 
    visualize_angles_on_frame, 
    visualize_score_on_frame,
    create_pose_connections
)
import cv2

# Extract pose landmarks
landmarks_list = extract_landmarks("squat_video.mp4")

# Process each frame
for i, landmarks in enumerate(landmarks_list):
    # Read the corresponding frame
    cap = cv2.VideoCapture("squat_video.mp4")
    for _ in range(i):
        cap.read()
    ret, frame = cap.read()
    
    if ret:
        # Draw pose landmarks
        connections = create_pose_connections()
        annotated_frame = draw_landmarks_on_frame(frame, landmarks, connections)
        
        # Calculate angles
        left_knee = knee_angle(landmarks, "left")
        right_knee = knee_angle(landmarks, "right")
        angles = {"left_knee": left_knee, "right_knee": right_knee}
        annotated_frame = visualize_angles_on_frame(annotated_frame, landmarks, angles)
        
        # Score movement
        score_result = score_deep_squat(landmarks)
        annotated_frame = visualize_score_on_frame(annotated_frame, score_result)
        
        # Save annotated frame
        cv2.imwrite(f"annotated_frame_{i}.jpg", annotated_frame)
```

## License

MIT