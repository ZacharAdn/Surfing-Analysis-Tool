"""
Unit Tests - Video Processing Functions
Tests for video loading, format validation, frame extraction, and timeline calculations
"""

import pytest
import cv2
import numpy as np
import os
from unittest.mock import Mock, patch, MagicMock


class TestVideoLoading:
    """Test video loading and format validation"""
    
    def test_load_valid_mp4_video(self):
        """Test loading valid MP4 video file"""
        # Mock video file path
        video_path = "test_video.mp4"
        
        with patch('cv2.VideoCapture') as mock_cap, patch('os.path.exists', return_value=True):
            mock_cap.return_value.isOpened.return_value = True
            mock_cap.return_value.get.return_value = 30.0  # FPS
            
            # Test video loading function
            result = load_video(video_path)
            assert result is True
            mock_cap.assert_called_once_with(video_path)
    
    def test_load_invalid_video_format(self):
        """Test handling of invalid video formats"""
        invalid_path = "test_file.txt"
        
        with patch('cv2.VideoCapture') as mock_cap:
            mock_cap.return_value.isOpened.return_value = False
            
            # Test that the function raises ValueError for invalid format
            with pytest.raises(ValueError, match="Unsupported video format"):
                load_video(invalid_path)
    
    def test_load_nonexistent_video(self):
        """Test handling of non-existent video files"""
        nonexistent_path = "nonexistent_video.mp4"
        
        with patch('cv2.VideoCapture') as mock_cap:
            mock_cap.return_value.isOpened.return_value = False
            
            with pytest.raises(FileNotFoundError):
                load_video(nonexistent_path)


class TestFrameExtraction:
    """Test frame extraction accuracy"""
    
    def test_extract_frame_at_timestamp(self):
        """Test extracting frame at specific timestamp"""
        timestamp = 10.5  # 10.5 seconds
        expected_frame_number = 315  # At 30 FPS
        
        with patch('cv2.VideoCapture') as mock_cap:
            mock_cap.return_value.get.return_value = 30.0  # FPS
            mock_cap.return_value.set.return_value = True
            mock_frame = np.zeros((480, 640, 3), dtype=np.uint8)
            mock_cap.return_value.read.return_value = (True, mock_frame)
            
            frame = extract_frame_at_timestamp(mock_cap.return_value, timestamp)
            
            # Verify frame position was set correctly
            mock_cap.return_value.set.assert_called_with(cv2.CAP_PROP_POS_FRAMES, expected_frame_number)
            assert frame is not None
            assert frame.shape == (480, 640, 3)
    
    def test_extract_frame_beyond_video_length(self):
        """Test handling timestamp beyond video duration"""
        timestamp = 999.0  # Very long timestamp
        
        with patch('cv2.VideoCapture') as mock_cap:
            mock_cap.return_value.get.return_value = 30.0  # FPS
            mock_cap.return_value.read.return_value = (False, None)
            
            with pytest.raises(ValueError, match="Timestamp beyond video duration"):
                extract_frame_at_timestamp(mock_cap.return_value, timestamp)


class TestTimelineCalculations:
    """Test timeline calculations and conversions"""
    
    def test_timestamp_to_frame_number(self):
        """Test converting timestamp to frame number"""
        fps = 30.0
        timestamp = 10.5
        expected_frame = 315
        
        frame_number = timestamp_to_frame(timestamp, fps)
        assert frame_number == expected_frame
    
    def test_frame_number_to_timestamp(self):
        """Test converting frame number to timestamp"""
        fps = 30.0
        frame_number = 315
        expected_timestamp = 10.5
        
        timestamp = frame_to_timestamp(frame_number, fps)
        assert abs(timestamp - expected_timestamp) < 0.1  # Within tolerance
    
    def test_get_video_duration(self):
        """Test calculating total video duration"""
        with patch('cv2.VideoCapture') as mock_cap:
            mock_cap.return_value.get.side_effect = lambda prop: {
                cv2.CAP_PROP_FRAME_COUNT: 3600,  # Total frames
                cv2.CAP_PROP_FPS: 30.0           # FPS
            }[prop]
            
            duration = get_video_duration(mock_cap.return_value)
            expected_duration = 120.0  # 3600/30 = 120 seconds
            
            assert abs(duration - expected_duration) < 0.1


class TestBoundingBoxValidation:
    """Test bounding box coordinate validation"""
    
    def test_valid_bounding_box(self):
        """Test validation of correct bounding box coordinates"""
        bbox = [100, 150, 200, 300]  # [x, y, width, height]
        frame_size = (640, 480)  # (width, height)
        
        is_valid = validate_bounding_box(bbox, frame_size)
        assert is_valid is True
    
    def test_bounding_box_outside_frame(self):
        """Test handling bounding box outside frame boundaries"""
        bbox = [600, 450, 100, 100]  # Extends beyond 640x480 frame
        frame_size = (640, 480)
        
        is_valid = validate_bounding_box(bbox, frame_size)
        assert is_valid is False
    
    def test_negative_bounding_box_coordinates(self):
        """Test handling negative bounding box coordinates"""
        bbox = [-10, -20, 100, 100]
        frame_size = (640, 480)
        
        is_valid = validate_bounding_box(bbox, frame_size)
        assert is_valid is False
    
    def test_zero_area_bounding_box(self):
        """Test handling bounding box with zero area"""
        bbox = [100, 150, 0, 0]
        frame_size = (640, 480)
        
        is_valid = validate_bounding_box(bbox, frame_size)
        assert is_valid is False


# Mock functions to be implemented in actual annotation tool
def load_video(video_path):
    """Mock function for video loading with proper error handling"""
    import cv2
    import os
    
    # Check file extension first
    valid_extensions = ['.mp4', '.mov', '.avi', '.mkv']
    file_ext = os.path.splitext(video_path)[1].lower()
    if file_ext not in valid_extensions:
        raise ValueError(f"Unsupported video format: {file_ext}")
    
    # Check if file exists
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")
    
    # Try to open video
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError("Cannot open video file")
    
    cap.release()
    return True


def extract_frame_at_timestamp(cap, timestamp):
    """Mock function for frame extraction"""
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_number = int(timestamp * fps)
    
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
    ret, frame = cap.read()
    
    if not ret:
        raise ValueError("Timestamp beyond video duration")
    return frame


def timestamp_to_frame(timestamp, fps):
    """Convert timestamp to frame number"""
    return int(timestamp * fps)


def frame_to_timestamp(frame_number, fps):
    """Convert frame number to timestamp"""
    return frame_number / fps


def get_video_duration(cap):
    """Get total video duration in seconds"""
    frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    fps = cap.get(cv2.CAP_PROP_FPS)
    return frame_count / fps


def validate_bounding_box(bbox, frame_size):
    """Validate bounding box coordinates against frame dimensions"""
    if len(bbox) != 4:
        return False
    
    x, y, width, height = bbox
    frame_width, frame_height = frame_size
    
    # Check if bounding box is within frame boundaries
    if x < 0 or y < 0:
        return False
    if x + width > frame_width or y + height > frame_height:
        return False
    if width <= 0 or height <= 0:
        return False
    
    return True 