# Surfing Video Annotation Tool Specification

## Core Requirements

### Video Player (PyQt-based)
- **Native Video Playback**: Smooth, real-time video playback using Qt's multimedia capabilities
- **Playback Controls**: 
  - Play/Pause with space bar
  - Frame-by-frame navigation (←/→)
  - Speed control (0.25x - 2x)
  - Jump controls (±10s, ±1s)
- **Timeline**: 
  - Clickable/draggable timeline
  - Current time display
  - Frame counter
  - Visual markers for annotations

### Annotation Features
- **Multi-Surfer Support**: Track up to 5 surfers simultaneously
- **Ride Marking**:
  - Quick start/end time marking (keyboard shortcuts)
  - Quality rating (poor/average/good/excellent)
- **Bounding Boxes**:
  - Draw with mouse drag
  - Resize/move existing boxes
  - Color-coded per surfer
  - Optional: Basic motion tracking

### Data Management
- **File Formats**:
  - Input: MP4, MOV, AVI (up to 4K resolution)
  - Output: JSON annotations, CSV exports
- **Auto-save**: Periodic state saving
- **Session Resume**: Load previous work

## Technical Stack
- **Framework**: PyQt6 for native performance
- **Video Processing**: OpenCV + Qt Multimedia
- **Data Storage**: JSON/SQLite
- **Python Version**: 3.8+

## Output Schema
```json
{
  "video_file": "session_001.mp4",
  "metadata": {
    "duration": 120.5,
    "fps": 30,
    "resolution": [3840, 2160]
  },
  "surfers": [
    {
      "id": 1,
      "start_time": 45.2,
      "end_time": 67.8,
      "quality": "good",
      "bbox_history": [
        {"time": 45.2, "bbox": [100, 150, 200, 300]},
        {"time": 45.5, "bbox": [105, 155, 205, 305]}
      ]
    }
  ]
}
```

## UI Layout
```
+------------------------+
|     Video Player       |
|                        |
+------------------------+
|     Timeline Bar      |
+--------+-------------+
|Surfer  |  Controls   |
|List    |  & Stats    |
+--------+-------------+
```

## Performance Goals
- Instant video seeking
- No frame drops during playback
- <100ms response time for all controls
- Support for 30min+ 4K videos 