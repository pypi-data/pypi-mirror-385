# DeepRehab Pose

Pose estimation for rehabilitation exercises.

## Overview

DeepRehab Pose is a Python package that provides pose estimation capabilities for rehabilitation exercises. It uses MediaPipe to detect body landmarks in video files and can be used to analyze patient movements during physical therapy sessions.

## Features

- Extract body landmarks from video files
- Process video frames to identify 33 body points
- Handle invalid or corrupted video files
- Return structured landmark data for further analysis

## Installation

To install the package in development mode:
```bash
pip install -e .
```

To install from source:
```bash
python -m build
pip install dist/deeprehab_pose-0.1.0-py3-none-any.whl
```

## Usage

```python
from deeprehab_pose import extract_landmarks, InvalidVideoError

try:
    # Extract landmarks from a video file
    landmarks = extract_landmarks("path/to/video.mp4")
    
    # Process the landmarks
    for frame_index, frame_landmarks in enumerate(landmarks):
        print(f"Frame {frame_index}: {len(frame_landmarks)} landmarks detected")
        
except InvalidVideoError as e:
    print(f"Error processing video: {e}")
```

## API

### Main Functions

- `extract_landmarks(video_path)` - Extract body landmarks from a video file
- `InvalidVideoError` - Exception raised for invalid video files

### Data Classes

- `Landmark` - Represents a body landmark with x, y, z coordinates and visibility

## Testing

Run the tests with:
```bash
python -m pytest src/deeprehab_pose/test_pose.py
```

## License

MIT