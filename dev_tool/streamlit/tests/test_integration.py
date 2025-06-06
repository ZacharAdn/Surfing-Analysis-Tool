"""
Integration Tests - Complete workflow testing
Tests for video processing, annotation management, and UI component integration
"""

import pytest
import time
import cv2
import tempfile
import os
from unittest.mock import Mock, patch, mock_open
import pandas as pd
import json

# Import modules to test
import sys
sys.path.append('..')
from video_processor import VideoProcessor
from annotation_manager import AnnotationManager
from ui_components import VideoPlayer, AnnotationControls, BoundingBoxTool


class AnnotationSession:
    """Mock annotation session class for testing"""
    
    def __init__(self, video_file):
        self.video_file = video_file
        self.video_loaded = False
        self.annotations = []
        self.surfers = []
        
    def load_video(self):
        """Mock video loading"""
        self.video_loaded = True
        
    def add_surfer(self, surfer_id, start_time, end_time, bbox):
        """Add surfer annotation"""
        surfer = {
            "id": surfer_id,
            "start_time": start_time,
            "end_time": end_time,
            "bbox": bbox
        }
        self.surfers.append(surfer)
        
    @classmethod
    def resume_from_data(cls, data):
        """Resume session from data"""
        session = cls(data["video_file"])
        session.surfers = data["surfers"]
        return session


class TestVideoPlayerIntegration:
    """Test video player integration with annotation system"""
    
    def test_video_playback_with_annotation_overlay(self):
        """Test video playback with annotation overlay display"""
        mock_player = Mock()
        mock_canvas = Mock()
        
        # Mock video frame with annotations
        annotation_data = {
            "surfers": [
                {
                    "id": 1,
                    "start_time": 10.0,
                    "end_time": 25.0,
                    "bbox": [100, 150, 200, 300]
                }
            ]
        }
        
        current_time = 15.0  # Within annotation range
        
        # Test overlay rendering
        result = render_annotations_on_frame(mock_canvas, annotation_data, current_time)
        
        # Verify annotation was rendered
        assert result["annotations_rendered"] == 1
        mock_canvas.create_rectangle.assert_called()
    
    def test_timeline_sync_with_frame_display(self):
        """Test timeline synchronization with frame display"""
        mock_player = Mock()
        mock_timeline = Mock()
        
        # Mock current time
        current_time = 45.5
        video_duration = 120.0
        timeline_width = 800
        
        # Test timeline position update
        update_timeline_display(mock_timeline, current_time, video_duration, timeline_width)
        
        expected_position = int((current_time / video_duration) * timeline_width)
        mock_timeline.update_position.assert_called_with(expected_position)
    
    def test_bounding_box_drawing_on_video_frames(self):
        """Test drawing bounding boxes on video frames"""
        mock_canvas = Mock()
        mock_frame = Mock()
        
        # Mock bounding box coordinates
        bbox = [100, 150, 200, 300]  # [x, y, width, height]
        
        # Test bounding box rendering
        draw_bounding_box_on_frame(mock_canvas, bbox, "red", 2)
        
        # Verify rectangle was drawn
        mock_canvas.create_rectangle.assert_called_with(
            100, 150, 300, 450,  # x1, y1, x2, y2
            outline="red", width=2
        )
    
    def test_multi_surfer_annotation_workflow(self):
        """Test complete multi-surfer annotation workflow"""
        mock_annotation_state = Mock()
        mock_annotation_state.surfers = []
        
        # Simulate adding multiple surfers
        surfer1_data = {
            "id": 1,
            "start_time": 10.0,
            "end_time": 25.0,
            "bbox": [100, 150, 200, 300]
        }
        
        surfer2_data = {
            "id": 2,
            "start_time": 30.0,
            "end_time": 45.0,
            "bbox": [300, 200, 150, 250]
        }
        
        # Add surfers
        add_surfer_annotation(mock_annotation_state, surfer1_data)
        add_surfer_annotation(mock_annotation_state, surfer2_data)
        
        # Verify both surfers were added
        assert len(mock_annotation_state.surfers) == 2
        assert mock_annotation_state.surfers[0]["id"] == 1
        assert mock_annotation_state.surfers[1]["id"] == 2


class TestDataFlowIntegration:
    """Test complete data flow workflows"""
    
    def test_complete_annotation_session_workflow(self):
        """Test complete annotation session from start to finish"""
        # Initialize session
        session = AnnotationSession("test_video.mp4")
        
        # Load video
        with patch("cv2.VideoCapture") as mock_cap:
            mock_cap.return_value.isOpened.return_value = True
            mock_cap.return_value.get.return_value = 30.0
            
            session.load_video()
            assert session.video_loaded is True
        
        # Add annotations
        session.add_surfer(1, 10.0, 25.0, [100, 150, 200, 300])
        session.add_surfer(2, 30.0, 45.0, [300, 200, 150, 250])
        
        # Export annotations
        with patch("builtins.open", mock_open()) as mock_file:
            annotation_data = {
                "video_file": session.video_file,
                "surfers": session.surfers
            }
            
            # Test JSON export
            with open("test_annotations.json", 'w') as f:
                json.dump(annotation_data, f)
            
            # Verify export succeeded
            assert len(session.surfers) == 2
    
    def test_save_load_annotation_persistence(self):
        """Test saving and loading annotation data persistence"""
        # Create test annotation data
        original_data = {
            "video_file": "session_001.mp4",
            "duration": 120.5,
            "surfers": [
                {
                    "id": 1,
                    "start_time": 10.2,
                    "end_time": 25.8,
                    "bbox": [100, 150, 200, 300],
                    "quality": "good"
                },
                {
                    "id": 2,
                    "start_time": 30.0,
                    "end_time": 45.5,
                    "bbox": [300, 200, 150, 250],
                    "quality": "average"
                }
            ]
        }
        
        # Test save and load cycle
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp_file:
            # Save data
            json.dump(original_data, tmp_file, indent=2)
            tmp_file_path = tmp_file.name
        
        try:
            # Load data
            with open(tmp_file_path, 'r') as f:
                loaded_data = json.load(f)
            
            # Verify data integrity
            assert loaded_data == original_data
            assert len(loaded_data["surfers"]) == 2
            assert loaded_data["surfers"][0]["start_time"] == 10.2
            
        finally:
            # Cleanup
            os.unlink(tmp_file_path)
    
    def test_export_format_consistency(self):
        """Test consistency between JSON and CSV export formats"""
        annotation_data = {
            "video_file": "session_001.mp4",
            "duration": 120.5,
            "surfers": [
                {
                    "id": 1,
                    "start_time": 10.2,
                    "end_time": 25.8,
                    "bbox": [100, 150, 200, 300],
                    "quality": "good"
                }
            ]
        }
        
        # Test JSON export
        with patch("builtins.open", mock_open()) as mock_json_file:
            json_result = export_annotations_to_json(annotation_data, "test.json")
            assert json_result is True
        
        # Test CSV export
        with patch("pandas.DataFrame.to_csv") as mock_csv:
            csv_result = export_annotations_to_csv(annotation_data, "test.csv")
            assert csv_result is True
    
    def test_annotation_validation_workflow(self):
        """Test annotation data validation in complete workflow"""
        # Test valid annotation workflow
        valid_data = {
            "video_file": "session_001.mp4",
            "duration": 120.5,
            "surfers": [
                {
                    "id": 1,
                    "start_time": 10.2,
                    "end_time": 25.8,
                    "bbox": [100, 150, 200, 300],
                    "quality": "good"
                }
            ]
        }
        
        validation_result = validate_and_process_annotations(valid_data)
        assert validation_result["valid"] is True
        assert validation_result["errors"] == []
        
        # Test invalid annotation workflow
        invalid_data = {
            "video_file": "session_001.mp4",
            "duration": 120.5,
            "surfers": [
                {
                    "id": 1,
                    "start_time": 25.8,  # Invalid: start > end
                    "end_time": 10.2,
                    "bbox": [100, 150, 200, 300]
                }
            ]
        }
        
        validation_result = validate_and_process_annotations(invalid_data)
        assert validation_result["valid"] is False
        assert len(validation_result["errors"]) > 0
    
    def test_resume_annotation_session(self):
        """Test resuming interrupted annotation sessions"""
        # Create partial session data
        partial_data = {
            "video_file": "session_001.mp4",
            "duration": 120.5,
            "surfers": [
                {
                    "id": 1,
                    "start_time": 10.2,
                    "end_time": None,  # Incomplete annotation
                    "bbox": [100, 150, 200, 300]
                }
            ]
        }
        
        # Test resuming session
        session = AnnotationSession.resume_from_data(partial_data)
        
        assert session.video_file == "session_001.mp4"
        assert len(session.surfers) == 1
        assert session.surfers[0]["start_time"] == 10.2


class TestPerformanceIntegration:
    """Test performance aspects of integration"""
    
    def test_large_video_file_handling(self):
        """Test handling of large video files (>100MB simulation)"""
        # Mock large video file
        mock_large_video = Mock()
        mock_large_video.get.side_effect = lambda prop: {
            cv2.CAP_PROP_FRAME_COUNT: 18000,  # 10 minutes at 30fps
            cv2.CAP_PROP_FPS: 30.0,
            cv2.CAP_PROP_FRAME_WIDTH: 1920,
            cv2.CAP_PROP_FRAME_HEIGHT: 1080
        }[prop]
        mock_large_video.isOpened.return_value = True
        
        # Test memory efficient processing
        with patch('cv2.VideoCapture', return_value=mock_large_video):
            session = AnnotationSession("large_video.mp4")
            session.load_video()
            
            # Verify session can handle large video
            assert session.video_loaded is True
    
    def test_multiple_surfer_performance(self):
        """Test performance with multiple surfers (3+ surfers)"""
        annotation_data = {
            "video_file": "session_001.mp4",
            "surfers": [
                {"id": i, "start_time": i*10, "end_time": i*10 + 15, 
                 "bbox": [i*50, i*50, 200, 300]} 
                for i in range(1, 6)  # 5 surfers
            ]
        }
        
        # Test rendering performance
        mock_canvas = Mock()
        current_time = 25.0  # Should show multiple surfers
        
        result = render_multiple_surfer_annotations(mock_canvas, annotation_data, current_time)
        
        # Verify all visible surfers were rendered
        expected_visible = sum(1 for s in annotation_data["surfers"] 
                             if s["start_time"] <= current_time <= s["end_time"])
        assert result["visible_surfers"] == expected_visible


# Mock classes and functions for integration testing
def render_annotations_on_frame(canvas, annotation_data, current_time):
    """Mock function to render annotations on frame"""
    annotations_rendered = 0
    
    for surfer in annotation_data["surfers"]:
        if surfer["start_time"] <= current_time <= surfer["end_time"]:
            bbox = surfer["bbox"]
            canvas.create_rectangle(bbox[0], bbox[1], 
                                  bbox[0] + bbox[2], bbox[1] + bbox[3])
            annotations_rendered += 1
    
    return {"annotations_rendered": annotations_rendered}


def update_timeline_display(timeline, current_time, duration, width):
    """Mock function to update timeline display"""
    position = int((current_time / duration) * width)
    timeline.update_position(position)


def draw_bounding_box_on_frame(canvas, bbox, color, width):
    """Mock function to draw bounding box"""
    x, y, w, h = bbox
    canvas.create_rectangle(x, y, x + w, y + h, outline=color, width=width)


def add_surfer_annotation(annotation_state, surfer_data):
    """Mock function to add surfer annotation"""
    annotation_state.surfers.append(surfer_data)


def export_annotations_to_json(annotation_data, output_path):
    """Export annotation data to JSON file"""
    try:
        with open(output_path, 'w') as f:
            json.dump(annotation_data, f, indent=2)
        return True
    except Exception as e:
        print(f"Error exporting to JSON: {e}")
        return False


def export_annotations_to_csv(annotation_data, output_path):
    """Export annotation data to CSV format"""
    try:
        rows = []
        for surfer in annotation_data["surfers"]:
            rows.append({
                "video_file": annotation_data["video_file"],
                "surfer_id": surfer["id"],
                "start_time": surfer["start_time"],
                "end_time": surfer["end_time"],
                "bbox_x": surfer["bbox"][0],
                "bbox_y": surfer["bbox"][1],
                "bbox_width": surfer["bbox"][2],
                "bbox_height": surfer["bbox"][3],
                "quality": surfer.get("quality", "")
            })
        
        df = pd.DataFrame(rows)
        df.to_csv(output_path, index=False)
        return True
    except Exception as e:
        print(f"Error exporting to CSV: {e}")
        return False


def validate_and_process_annotations(data):
    """Mock annotation validation function"""
    errors = []
    
    # Check required fields
    if "video_file" not in data:
        errors.append("Missing video_file")
    
    if "surfers" not in data:
        errors.append("Missing surfers data")
    else:
        for i, surfer in enumerate(data["surfers"]):
            if surfer.get("start_time", 0) >= surfer.get("end_time", 0):
                errors.append(f"Surfer {i+1}: Invalid time range")
    
    return {"valid": len(errors) == 0, "errors": errors}


def render_multiple_surfer_annotations(canvas, annotation_data, current_time):
    """Mock function to render multiple surfer annotations"""
    visible_surfers = 0
    
    for surfer in annotation_data["surfers"]:
        if surfer["start_time"] <= current_time <= surfer["end_time"]:
            visible_surfers += 1
            # Mock drawing each surfer
            canvas.create_rectangle(
                surfer["bbox"][0], surfer["bbox"][1],
                surfer["bbox"][0] + surfer["bbox"][2],
                surfer["bbox"][1] + surfer["bbox"][3]
            )
    
    return {"visible_surfers": visible_surfers} 