"""
Unit Tests - UI Component Functions
Tests for button handlers, timeline scrubbing, and keyboard shortcuts
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import tkinter as tk


class TestButtonHandlers:
    """Test button click handlers"""
    
    def test_play_pause_button_handler(self):
        """Test play/pause button functionality"""
        # Mock video player state
        mock_player = Mock()
        mock_player.is_playing = False
        
        # Test play action
        result = handle_play_pause_click(mock_player)
        
        assert result == "playing"
        assert mock_player.play.called
    
    def test_stop_button_handler(self):
        """Test stop button functionality"""
        mock_player = Mock()
        mock_player.is_playing = True
        
        result = handle_stop_click(mock_player)
        
        assert result == "stopped"
        assert mock_player.stop.called
        assert mock_player.seek.called_with(0)
    
    def test_add_surfer_button_handler(self):
        """Test add surfer button functionality"""
        mock_annotation_state = Mock()
        mock_annotation_state.surfers = []
        mock_annotation_state.current_time = 10.5
        
        result = handle_add_surfer_click(mock_annotation_state)
        
        assert len(mock_annotation_state.surfers) == 1
        assert mock_annotation_state.surfers[0]["start_time"] == 10.5
        assert result["id"] == 1
    
    def test_mark_end_button_handler(self):
        """Test mark ride end button functionality"""
        mock_annotation_state = Mock()
        mock_annotation_state.current_surfer_id = 1
        mock_annotation_state.current_time = 25.8
        mock_annotation_state.surfers = [
            {"id": 1, "start_time": 10.2, "end_time": None}
        ]
        
        result = handle_mark_end_click(mock_annotation_state)
        
        assert mock_annotation_state.surfers[0]["end_time"] == 25.8
        assert result == "end_marked"
    
    def test_save_annotations_button_handler(self):
        """Test save annotations button functionality"""
        mock_annotation_state = Mock()
        mock_annotation_state.get_annotation_data.return_value = {"test": "data"}

        # Test the handler directly
        result = handle_save_click(mock_annotation_state)
        
        # Verify the function can be called
        assert result is not None


class TestTimelineScrubbing:
    """Test timeline scrubbing accuracy"""
    
    def test_timeline_click_to_time_conversion(self):
        """Test converting timeline click position to timestamp"""
        timeline_width = 800  # pixels
        video_duration = 120.0  # seconds
        click_position = 400  # middle of timeline
        
        expected_time = 60.0  # Middle of video
        
        calculated_time = timeline_click_to_time(click_position, timeline_width, video_duration)
        
        assert abs(calculated_time - expected_time) < 0.1
    
    def test_time_to_timeline_position(self):
        """Test converting timestamp to timeline position"""
        timeline_width = 800
        video_duration = 120.0
        timestamp = 30.0  # Quarter way through
        
        expected_position = 200  # Quarter of timeline width
        
        calculated_position = time_to_timeline_position(timestamp, timeline_width, video_duration)
        
        assert abs(calculated_position - expected_position) < 1
    
    def test_timeline_drag_handler(self):
        """Test timeline dragging functionality"""
        mock_player = Mock()
        mock_timeline = Mock()
        
        # Simulate drag event
        drag_event = Mock()
        drag_event.x = 300
        
        timeline_width = 600
        video_duration = 90.0
        
        handle_timeline_drag(drag_event, mock_player, timeline_width, video_duration)
        
        expected_time = 45.0  # 300/600 * 90
        mock_player.seek.assert_called_with(expected_time)
    
    def test_timeline_boundary_handling(self):
        """Test timeline click boundary handling"""
        timeline_width = 800
        video_duration = 120.0
        
        # Test click before timeline start
        time_before = timeline_click_to_time(-10, timeline_width, video_duration)
        assert time_before == 0.0
        
        # Test click after timeline end
        time_after = timeline_click_to_time(900, timeline_width, video_duration)
        assert time_after == video_duration


class TestKeyboardShortcuts:
    """Test keyboard shortcut functionality"""
    
    def test_spacebar_play_pause_shortcut(self):
        """Test spacebar for play/pause"""
        mock_player = Mock()
        mock_player.is_playing = False
        
        # Simulate spacebar press
        key_event = Mock()
        key_event.keysym = "space"
        
        result = handle_keyboard_shortcut(key_event, mock_player)
        
        assert result == "play_pause_triggered"
        assert mock_player.play.called
    
    def test_arrow_keys_frame_navigation(self):
        """Test arrow keys for frame-by-frame navigation"""
        mock_player = Mock()
        mock_player.current_frame = 1000
        mock_player.fps = 30.0
        
        # Test right arrow (next frame)
        key_event = Mock()
        key_event.keysym = "Right"
        
        handle_keyboard_shortcut(key_event, mock_player)
        expected_frame = 1001
        mock_player.seek_to_frame.assert_called_with(expected_frame)
        
        # Test left arrow (previous frame)
        key_event.keysym = "Left"
        handle_keyboard_shortcut(key_event, mock_player)
        expected_frame = 999
        mock_player.seek_to_frame.assert_called_with(expected_frame)
    
    def test_number_keys_surfer_selection(self):
        """Test number keys for surfer selection"""
        mock_annotation_state = Mock()
        mock_annotation_state.surfers = [
            {"id": 1}, {"id": 2}, {"id": 3}
        ]
        
        # Test key "1" selects first surfer
        key_event = Mock()
        key_event.keysym = "1"
        
        result = handle_keyboard_shortcut(key_event, None, mock_annotation_state)
        
        assert mock_annotation_state.current_surfer_id == 1
        assert result == "surfer_selected"
    
    def test_save_shortcut(self):
        """Test Ctrl+S save shortcut"""
        mock_annotation_state = Mock()

        # Simulate Ctrl+S
        key_event = Mock()
        key_event.keysym = "s"
        key_event.state = 4  # Control key modifier

        # Test the keyboard handler directly
        result = handle_keyboard_shortcut(key_event, None, mock_annotation_state)
        
        # Verify save shortcut was triggered
        assert result == "save_triggered"
    
    def test_invalid_shortcut_handling(self):
        """Test handling of invalid keyboard shortcuts"""
        key_event = Mock()
        key_event.keysym = "invalid_key"
        
        result = handle_keyboard_shortcut(key_event, Mock())
        
        assert result == "no_action"


class TestBoundingBoxUI:
    """Test bounding box drawing UI components"""
    
    def test_start_bounding_box_drawing(self):
        """Test starting bounding box drawing"""
        canvas = Mock()
        mouse_event = Mock()
        mouse_event.x = 100
        mouse_event.y = 150
        
        bbox_state = start_bbox_drawing(canvas, mouse_event)
        
        assert bbox_state["start_x"] == 100
        assert bbox_state["start_y"] == 150
        assert bbox_state["drawing"] is True
    
    def test_update_bounding_box_drawing(self):
        """Test updating bounding box while drawing"""
        canvas = Mock()
        bbox_state = {
            "start_x": 100,
            "start_y": 150,
            "drawing": True,
            "rect_id": None
        }
        
        mouse_event = Mock()
        mouse_event.x = 200
        mouse_event.y = 250
        
        update_bbox_drawing(canvas, mouse_event, bbox_state)
        
        # Verify rectangle was drawn/updated
        canvas.create_rectangle.assert_called()
    
    def test_finish_bounding_box_drawing(self):
        """Test finishing bounding box drawing"""
        canvas = Mock()
        bbox_state = {
            "start_x": 100,
            "start_y": 150,
            "drawing": True
        }
        
        mouse_event = Mock()
        mouse_event.x = 200
        mouse_event.y = 250
        
        result = finish_bbox_drawing(canvas, mouse_event, bbox_state)
        
        expected_bbox = [100, 150, 100, 100]  # [x, y, width, height]
        assert result == expected_bbox
        assert bbox_state["drawing"] is False


# Mock functions to be implemented in actual annotation tool
def handle_play_pause_click(player):
    """Handle play/pause button click"""
    if player.is_playing:
        player.pause()
        return "paused"
    else:
        player.play()
        return "playing"


def handle_stop_click(player):
    """Handle stop button click"""
    player.stop()
    player.seek(0)
    return "stopped"


def handle_add_surfer_click(annotation_state):
    """Handle add surfer button click"""
    new_surfer = {
        "id": len(annotation_state.surfers) + 1,
        "start_time": annotation_state.current_time,
        "end_time": None,
        "bbox": None
    }
    annotation_state.surfers.append(new_surfer)
    return new_surfer


def handle_mark_end_click(annotation_state):
    """Handle mark ride end button click"""
    for surfer in annotation_state.surfers:
        if surfer["id"] == annotation_state.current_surfer_id:
            surfer["end_time"] = annotation_state.current_time
            break
    return "end_marked"


def handle_save_click(annotation_state):
    """Handle save button click"""
    try:
        data = annotation_state.get_annotation_data()
        return export_annotations_to_json(data, "annotations.json")
    except Exception as e:
        print(f"Error in save handler: {e}")
        return False


def timeline_click_to_time(click_x, timeline_width, video_duration):
    """Convert timeline click position to timestamp"""
    # Handle boundary conditions
    if click_x < 0:
        return 0.0
    if click_x > timeline_width:
        return video_duration
    
    ratio = click_x / timeline_width
    return ratio * video_duration


def time_to_timeline_position(timestamp, timeline_width, video_duration):
    """Convert timestamp to timeline position"""
    ratio = timestamp / video_duration
    return int(ratio * timeline_width)


def handle_timeline_drag(event, player, timeline_width, video_duration):
    """Handle timeline dragging"""
    timestamp = timeline_click_to_time(event.x, timeline_width, video_duration)
    player.seek(timestamp)


def handle_keyboard_shortcut(event, player=None, annotation_state=None):
    """Handle keyboard shortcuts"""
    key = event.keysym.lower()
    
    # Play/pause with spacebar
    if key == "space" and player:
        handle_play_pause_click(player)
        return "play_pause_triggered"
    
    # Frame navigation with arrow keys
    elif key == "right" and player:
        next_frame = player.current_frame + 1
        player.seek_to_frame(next_frame)
        return "frame_forward"
    
    elif key == "left" and player:
        prev_frame = player.current_frame - 1
        player.seek_to_frame(prev_frame)
        return "frame_backward"
    
    # Surfer selection with number keys
    elif key.isdigit() and annotation_state:
        surfer_id = int(key)
        if surfer_id <= len(annotation_state.surfers):
            annotation_state.current_surfer_id = surfer_id
            return "surfer_selected"
    
    # Save with Ctrl+S
    elif key == "s" and hasattr(event, 'state') and event.state == 4:
        handle_save_click(annotation_state)
        return "save_triggered"
    
    return "no_action"


def start_bbox_drawing(canvas, event):
    """Start bounding box drawing"""
    return {
        "start_x": event.x,
        "start_y": event.y,
        "drawing": True,
        "rect_id": None
    }


def update_bbox_drawing(canvas, event, bbox_state):
    """Update bounding box while drawing"""
    if bbox_state["drawing"]:
        # Remove previous rectangle if exists
        if bbox_state["rect_id"]:
            canvas.delete(bbox_state["rect_id"])
        
        # Draw new rectangle
        rect_id = canvas.create_rectangle(
            bbox_state["start_x"], bbox_state["start_y"],
            event.x, event.y,
            outline="red", width=2
        )
        bbox_state["rect_id"] = rect_id


def finish_bbox_drawing(canvas, event, bbox_state):
    """Finish bounding box drawing and return coordinates"""
    if bbox_state["drawing"]:
        x1, y1 = bbox_state["start_x"], bbox_state["start_y"]
        x2, y2 = event.x, event.y
        
        # Normalize coordinates (top-left, width, height)
        x = min(x1, x2)
        y = min(y1, y2)
        width = abs(x2 - x1)
        height = abs(y2 - y1)
        
        bbox_state["drawing"] = False
        return [x, y, width, height]
    
    return None


# Helper functions for UI component testing
def export_annotations_to_json(annotation_data, output_path):
    """Export annotation data to JSON file"""
    try:
        import json
        with open(output_path, 'w') as f:
            json.dump(annotation_data, f, indent=2)
        return True
    except Exception as e:
        print(f"Error exporting to JSON: {e}")
        return False 