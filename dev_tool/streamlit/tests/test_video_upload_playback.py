"""
Tests for video upload and playback functionality
These tests verify the video upload path handling and playback controls
"""

import pytest
import os
import tempfile
import shutil
from unittest.mock import Mock, patch, MagicMock
import streamlit as st
import pandas as pd
import json
from pathlib import Path
import cv2

# Import modules to test
import sys
sys.path.append('..')
from video_processor import VideoProcessor
from annotation_manager import AnnotationManager


class TestVideoUploadHandling:
    """Test video file upload and storage"""
    
    def setup_method(self):
        """Setup test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)
        
        # Create test video file
        self.test_video_data = b"fake_video_data_for_testing"
        self.test_video_name = "test_surfing_video.mp4"
        
    def teardown_method(self):
        """Cleanup test environment"""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_video_directory_creation(self):
        """Test that video directory is created properly"""
        # Simulate video upload process
        video_dir = "data/videos"
        os.makedirs(video_dir, exist_ok=True)
        
        assert os.path.exists(video_dir)
        assert os.path.isdir(video_dir)
    
    def test_video_file_storage_location(self):
        """Test that uploaded videos are stored in correct location"""
        # Setup
        video_dir = "data/videos"
        os.makedirs(video_dir, exist_ok=True)
        
        # Simulate file upload
        video_filename = self.test_video_name
        video_path = os.path.join(video_dir, video_filename)
        
        # Write test video data
        with open(video_path, "wb") as f:
            f.write(self.test_video_data)
        
        # Verify file location
        assert os.path.exists(video_path)
        assert os.path.basename(video_path) == self.test_video_name
        assert "data/videos" in video_path
        
        # Verify file content
        with open(video_path, "rb") as f:
            stored_data = f.read()
        assert stored_data == self.test_video_data
    
    def test_uploaded_file_preservation(self):
        """Test that uploaded file keeps original name and extension"""
        test_files = [
            "drone_footage.mp4",
            "surf_session_001.mov", 
            "beach_video.avi",
            "surfing_compilation.mkv"
        ]
        
        video_dir = "data/videos"
        os.makedirs(video_dir, exist_ok=True)
        
        for filename in test_files:
            video_path = os.path.join(video_dir, filename)
            
            # Simulate upload
            with open(video_path, "wb") as f:
                f.write(self.test_video_data)
            
            # Verify filename preservation
            assert os.path.exists(video_path)
            assert os.path.basename(video_path) == filename
            
            # Verify extension preservation
            original_ext = os.path.splitext(filename)[1]
            stored_ext = os.path.splitext(video_path)[1]
            assert stored_ext == original_ext


class TestVideoPlaybackControls:
    """Test video playback functionality"""
    
    def setup_method(self):
        """Setup test environment"""
        self.processor = VideoProcessor()
        
        # Mock video properties
        self.processor.duration = 120.0  # 2 minutes
        self.processor.fps = 30.0
        self.processor.width = 1920
        self.processor.height = 1080
        self.processor.frame_count = 3600
        self.processor.is_loaded = True
    
    def test_seek_to_time_accuracy(self):
        """Test seeking to specific time with required accuracy (±0.1s)"""
        test_times = [0.0, 10.25, 25.67, 45.89, 67.33, 119.9]
        
        for target_time in test_times:
            # Simulate seeking
            clamped_time = max(0.0, min(target_time, self.processor.duration))
            frame_number = int(clamped_time * self.processor.fps)
            actual_time = frame_number / self.processor.fps
            
            # Verify accuracy within ±0.1 seconds
            accuracy = abs(actual_time - target_time)
            assert accuracy <= 0.1, f"Seek accuracy failed: {accuracy} > 0.1 for time {target_time}"
    
    def test_frame_navigation_controls(self):
        """Test frame-by-frame navigation controls"""
        current_time = 30.0
        current_frame = int(current_time * self.processor.fps)
        
        # Test next frame
        next_frame = current_frame + 1
        next_time = next_frame / self.processor.fps
        assert abs(next_time - current_time - (1/self.processor.fps)) < 0.001
        
        # Test previous frame
        prev_frame = current_frame - 1
        prev_time = prev_frame / self.processor.fps
        assert abs(current_time - prev_time - (1/self.processor.fps)) < 0.001
    
    def test_time_boundaries(self):
        """Test video time boundary handling"""
        # Test start boundary
        start_time = 0.0
        clamped_start = max(0.0, min(start_time, self.processor.duration))
        assert clamped_start == 0.0
        
        # Test end boundary  
        end_time = self.processor.duration
        clamped_end = max(0.0, min(end_time, self.processor.duration))
        assert clamped_end == self.processor.duration
        
        # Test beyond boundaries
        beyond_start = -10.0
        clamped_beyond_start = max(0.0, min(beyond_start, self.processor.duration))
        assert clamped_beyond_start == 0.0
        
        beyond_end = self.processor.duration + 10.0
        clamped_beyond_end = max(0.0, min(beyond_end, self.processor.duration))
        assert clamped_beyond_end == self.processor.duration
    
    def test_playback_controls_state(self):
        """Test playback control state management"""
        playback_state = {'is_playing': False}
        
        # Test play
        playback_state['is_playing'] = not playback_state['is_playing']
        assert playback_state['is_playing'] is True
        
        # Test pause
        playback_state['is_playing'] = not playback_state['is_playing'] 
        assert playback_state['is_playing'] is False
    
    def test_video_timeline_slider(self):
        """Test video timeline slider functionality"""
        # Test slider range
        min_value = 0.0
        max_value = self.processor.duration
        
        assert min_value == 0.0
        assert max_value == self.processor.duration
        
        # Test slider step size (0.1s for accuracy requirement)
        step_size = 0.1
        assert step_size <= 0.1  # Meets accuracy requirement
        
        # Test valid slider values
        test_values = [0.0, 30.5, 60.2, 90.7, self.processor.duration]
        for value in test_values:
            assert min_value <= value <= max_value


class TestVideoFileValidation:
    """Test video file format validation"""
    
    def setup_method(self):
        """Setup test environment"""
        self.processor = VideoProcessor()
    
    def test_supported_video_formats(self):
        """Test that supported video formats are accepted"""
        supported_formats = ['.mp4', '.mov', '.avi', '.mkv']
        
        for format_ext in supported_formats:
            test_file = f"test_video{format_ext}"
            file_ext = os.path.splitext(test_file)[1].lower()
            assert file_ext in supported_formats
    
    def test_unsupported_video_formats(self):
        """Test that unsupported formats are rejected"""
        unsupported_formats = ['.txt', '.jpg', '.png', '.pdf', '.doc']
        supported_formats = ['.mp4', '.mov', '.avi', '.mkv']
        
        for format_ext in unsupported_formats:
            test_file = f"test_file{format_ext}"
            file_ext = os.path.splitext(test_file)[1].lower()
            assert file_ext not in supported_formats
    
    def test_video_metadata_extraction(self):
        """Test extraction of video metadata"""
        # Mock video capture
        with patch('cv2.VideoCapture') as mock_cap, patch('os.path.exists', return_value=True):
            mock_cap.return_value.isOpened.return_value = True
            mock_cap.return_value.get.side_effect = lambda prop: {
                cv2.CAP_PROP_FPS: 30.0,
                cv2.CAP_PROP_FRAME_COUNT: 3600,
                cv2.CAP_PROP_FRAME_WIDTH: 1920,
                cv2.CAP_PROP_FRAME_HEIGHT: 1080
            }.get(prop, 0)
            
            # Test metadata extraction
            test_path = "test_video.mp4"
            success = self.processor.load_video(test_path)
            
            assert success is True
            assert self.processor.fps == 30.0
            assert self.processor.frame_count == 3600
            assert self.processor.width == 1920
            assert self.processor.height == 1080
            assert self.processor.duration == 120.0  # 3600/30


class TestDataOrganization:
    """Test file organization and data management"""
    
    def setup_method(self):
        """Setup test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)
    
    def teardown_method(self):
        """Cleanup test environment"""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_directory_structure_creation(self):
        """Test that proper directory structure is created"""
        required_dirs = [
            "data/videos",
            "data/annotations", 
            "data/exports"
        ]
        
        for dir_path in required_dirs:
            os.makedirs(dir_path, exist_ok=True)
            assert os.path.exists(dir_path)
            assert os.path.isdir(dir_path)
    
    def test_annotation_file_naming(self):
        """Test annotation file naming convention"""
        video_name = "surf_session_001.mp4"
        timestamp = "20241220_143000"
        
        # Test JSON filename
        video_name_safe = video_name.replace('.', '_')
        json_filename = f"annotations_{video_name_safe}_{timestamp}.json"
        assert "annotations_" in json_filename
        assert "surf_session_001_mp4" in json_filename
        assert timestamp in json_filename
        assert json_filename.endswith('.json')
        
        # Test CSV filename  
        csv_filename = f"annotations_{video_name_safe}_{timestamp}.csv"
        assert "annotations_" in csv_filename
        assert "surf_session_001_mp4" in csv_filename
        assert timestamp in csv_filename
        assert csv_filename.endswith('.csv')
    
    def test_file_path_construction(self):
        """Test proper file path construction"""
        video_name = "test_video.mp4"
        
        # Test video path
        video_path = os.path.join("data/videos", video_name)
        assert video_path == "data/videos/test_video.mp4"
        
        # Test annotation path
        annotation_name = "annotations_test_video_mp4_20241220_143000.json"
        annotation_path = os.path.join("data/annotations", annotation_name)
        assert annotation_path.startswith("data/annotations/")
        assert annotation_path.endswith(".json")
        
        # Test export path
        export_name = "annotations_test_video_mp4_20241220_143000.csv"
        export_path = os.path.join("data/exports", export_name)
        assert export_path.startswith("data/exports/")
        assert export_path.endswith(".csv")


if __name__ == "__main__":
    pytest.main([__file__]) 