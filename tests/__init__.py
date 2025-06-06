"""
Test package for surfing annotation tool

This package contains comprehensive tests for the annotation tool including:
- Unit tests for individual components
- Integration tests for workflow validation  
- User acceptance tests for real-world scenarios

Run tests with: pytest dev_tool/tests/
"""

# Test configuration
import pytest
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Test fixtures and utilities can be added here
@pytest.fixture
def sample_video_data():
    """Sample video data for testing"""
    return {
        "file_path": "test_video.mp4",
        "duration": 120.0,
        "fps": 30.0,
        "frame_count": 3600,
        "resolution": (1920, 1080)
    }

@pytest.fixture
def sample_annotation_data():
    """Sample annotation data for testing"""
    return {
        "video_file": "session_001.mp4", 
        "duration": 120.5,
        "surfers": [
            {
                "id": 1,
                "start_time": 10.2,
                "end_time": 25.8,
                "duration": 15.6,
                "bbox": [100, 150, 200, 300],
                "quality": "good"
            },
            {
                "id": 2,
                "start_time": 30.0,
                "end_time": 45.5,
                "duration": 15.5,
                "bbox": [300, 200, 150, 250], 
                "quality": "average"
            }
        ]
    } 