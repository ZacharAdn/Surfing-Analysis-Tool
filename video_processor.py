"""
Video Processor Module
Handles video loading, frame extraction, and timeline calculations
"""

import cv2
import numpy as np
import os
from typing import Optional, Tuple


class VideoProcessor:
    """Handles video file operations and frame extraction"""
    
    def __init__(self):
        self.cap = None
        self.video_path = None
        self.fps = 0.0
        self.frame_count = 0
        self.duration = 0.0
        self.width = 0
        self.height = 0
        self.is_loaded = False
    
    def load_video(self, video_path: str) -> bool:
        """
        Load video file and extract metadata
        
        Args:
            video_path: Path to video file
            
        Returns:
            bool: True if video loaded successfully, False otherwise
        """
        try:
            # Validate file exists
            if not os.path.exists(video_path):
                raise FileNotFoundError(f"Video file not found: {video_path}")
            
            # Validate file extension
            valid_extensions = ['.mp4', '.mov', '.avi', '.mkv', '.wmv']
            file_ext = os.path.splitext(video_path)[1].lower()
            if file_ext not in valid_extensions:
                raise ValueError(f"Unsupported video format: {file_ext}")
            
            # Open video capture
            self.cap = cv2.VideoCapture(video_path)
            
            if not self.cap.isOpened():
                raise ValueError("Cannot open video file - may be corrupted or unsupported format")
            
            # Extract video metadata
            self.video_path = video_path
            self.fps = self.cap.get(cv2.CAP_PROP_FPS)
            self.frame_count = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
            self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            # Calculate duration
            if self.fps > 0:
                self.duration = self.frame_count / self.fps
            else:
                self.duration = 0.0
            
            self.is_loaded = True
            return True
            
        except Exception as e:
            print(f"Error loading video: {str(e)}")
            self.cleanup()
            return False
    
    def get_frame_at_time(self, timestamp: float) -> Optional[np.ndarray]:
        """
        Extract frame at specific timestamp
        
        Args:
            timestamp: Time in seconds
            
        Returns:
            numpy.ndarray: Frame image or None if error
        """
        if not self.is_loaded or not self.cap:
            return None
        
        try:
            # Validate timestamp
            if timestamp < 0 or timestamp > self.duration:
                return None
            
            # Calculate frame number
            frame_number = int(timestamp * self.fps)
            
            # Seek to frame
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
            
            # Read frame
            ret, frame = self.cap.read()
            
            if ret:
                return frame
            else:
                return None
                
        except Exception as e:
            print(f"Error extracting frame at time {timestamp}: {str(e)}")
            return None
    
    def get_frame_at_frame_number(self, frame_number: int) -> Optional[np.ndarray]:
        """
        Extract frame at specific frame number
        
        Args:
            frame_number: Frame index
            
        Returns:
            numpy.ndarray: Frame image or None if error
        """
        if not self.is_loaded or not self.cap:
            return None
        
        try:
            # Validate frame number
            if frame_number < 0 or frame_number >= self.frame_count:
                return None
            
            # Seek to frame
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
            
            # Read frame
            ret, frame = self.cap.read()
            
            if ret:
                return frame
            else:
                return None
                
        except Exception as e:
            print(f"Error extracting frame {frame_number}: {str(e)}")
            return None
    
    def timestamp_to_frame(self, timestamp: float) -> int:
        """
        Convert timestamp to frame number
        
        Args:
            timestamp: Time in seconds
            
        Returns:
            int: Frame number
        """
        if self.fps > 0:
            return int(timestamp * self.fps)
        return 0
    
    def frame_to_timestamp(self, frame_number: int) -> float:
        """
        Convert frame number to timestamp
        
        Args:
            frame_number: Frame index
            
        Returns:
            float: Timestamp in seconds
        """
        if self.fps > 0:
            return frame_number / self.fps
        return 0.0
    
    def get_video_info(self) -> dict:
        """
        Get video information dictionary
        
        Returns:
            dict: Video metadata
        """
        return {
            'video_path': self.video_path,
            'fps': self.fps,
            'frame_count': self.frame_count,
            'duration': self.duration,
            'width': self.width,
            'height': self.height,
            'is_loaded': self.is_loaded
        }
    
    def validate_bounding_box(self, bbox: list) -> bool:
        """
        Validate bounding box coordinates against frame dimensions
        
        Args:
            bbox: [x, y, width, height]
            
        Returns:
            bool: True if valid, False otherwise
        """
        if not self.is_loaded or len(bbox) != 4:
            return False
        
        x, y, width, height = bbox
        
        # Check for negative coordinates or zero area
        if x < 0 or y < 0 or width <= 0 or height <= 0:
            return False
        
        # Check if bounding box is within frame boundaries
        if x + width > self.width or y + height > self.height:
            return False
        
        return True
    
    def extract_frame_sequence(self, start_time: float, end_time: float, 
                             step: float = 1.0) -> list:
        """
        Extract sequence of frames between start and end time
        
        Args:
            start_time: Start timestamp in seconds
            end_time: End timestamp in seconds
            step: Time step between frames in seconds
            
        Returns:
            list: List of (timestamp, frame) tuples
        """
        frames = []
        
        if not self.is_loaded:
            return frames
        
        current_time = start_time
        while current_time <= end_time:
            frame = self.get_frame_at_time(current_time)
            if frame is not None:
                frames.append((current_time, frame))
            current_time += step
        
        return frames
    
    def get_frame_dimensions(self) -> Tuple[int, int]:
        """
        Get frame dimensions
        
        Returns:
            tuple: (width, height)
        """
        return (self.width, self.height)
    
    def is_valid_timestamp(self, timestamp: float) -> bool:
        """
        Check if timestamp is valid for current video
        
        Args:
            timestamp: Time in seconds
            
        Returns:
            bool: True if valid, False otherwise
        """
        return self.is_loaded and 0 <= timestamp <= self.duration
    
    def get_total_frames(self) -> int:
        """
        Get total number of frames in video
        
        Returns:
            int: Total frame count
        """
        return self.frame_count
    
    def cleanup(self):
        """Clean up video capture resources"""
        if self.cap:
            self.cap.release()
            self.cap = None
        
        self.video_path = None
        self.fps = 0.0
        self.frame_count = 0
        self.duration = 0.0
        self.width = 0
        self.height = 0
        self.is_loaded = False
    
    def __del__(self):
        """Destructor to ensure cleanup"""
        self.cleanup()


def validate_video_file_path(file_path: str) -> bool:
    """
    Validate video file path and extension
    
    Args:
        file_path: Path to video file
        
    Returns:
        bool: True if valid video file, False otherwise
    """
    if not os.path.exists(file_path):
        return False
    
    valid_extensions = ['.mp4', '.mov', '.avi', '.mkv', '.wmv']
    file_ext = os.path.splitext(file_path)[1].lower()
    return file_ext in valid_extensions


def get_video_duration(video_path: str) -> float:
    """
    Get video duration without loading full video processor
    
    Args:
        video_path: Path to video file
        
    Returns:
        float: Duration in seconds, 0 if error
    """
    try:
        cap = cv2.VideoCapture(video_path)
        if cap.isOpened():
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
            duration = frame_count / fps if fps > 0 else 0
            cap.release()
            return duration
        return 0
    except Exception:
        return 0 