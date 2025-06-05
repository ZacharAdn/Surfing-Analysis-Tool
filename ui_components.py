"""
UI Components Module
Contains UI helper classes and components for the annotation tool
"""

import streamlit as st
import cv2
import numpy as np
from typing import Optional, Tuple, List


class VideoPlayer:
    """Video player component for Streamlit interface"""
    
    def __init__(self):
        self.current_frame = None
        self.is_playing = False
        self.playback_speed = 1.0
    
    def display_frame(self, frame: np.ndarray, annotations: List = None):
        """
        Display video frame with optional annotations
        
        Args:
            frame: Video frame as numpy array
            annotations: List of annotation overlays
        """
        if frame is not None:
            display_frame = frame.copy()
            
            # Draw annotations if provided
            if annotations:
                display_frame = self.draw_annotations(display_frame, annotations)
            
            # Display in Streamlit
            st.image(display_frame, channels="BGR", use_column_width=True)
    
    def draw_annotations(self, frame: np.ndarray, annotations: List) -> np.ndarray:
        """
        Draw annotations on frame
        
        Args:
            frame: Input frame
            annotations: List of annotations to draw
            
        Returns:
            numpy.ndarray: Frame with annotations
        """
        annotated_frame = frame.copy()
        
        for annotation in annotations:
            if 'bbox' in annotation and annotation['bbox']:
                x, y, w, h = annotation['bbox']
                
                # Color based on surfer ID
                colors = [(0, 255, 0), (255, 0, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255)]
                color = colors[annotation.get('id', 0) % len(colors)]
                
                # Draw rectangle
                cv2.rectangle(annotated_frame, (x, y), (x + w, y + h), color, 2)
                
                # Draw label
                label = f"Surfer {annotation.get('id', '?')}"
                cv2.putText(annotated_frame, label, (x, y - 10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
        
        return annotated_frame
    
    def create_timeline_marker(self, current_time: float, duration: float, width: int = 800):
        """
        Create timeline position marker
        
        Args:
            current_time: Current timestamp
            duration: Total video duration
            width: Timeline width in pixels
            
        Returns:
            int: Position on timeline
        """
        if duration > 0:
            position = int((current_time / duration) * width)
            return max(0, min(position, width))
        return 0


class AnnotationControls:
    """Annotation control components"""
    
    def __init__(self):
        self.selected_tool = "select"
        self.drawing_mode = False
    
    def render_playback_controls(self):
        """Render video playback control buttons"""
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            if st.button("⏮️", help="Previous frame"):
                return "previous"
        
        with col2:
            if st.button("⏸️", help="Play/Pause"):
                return "play_pause"
        
        with col3:
            if st.button("⏹️", help="Stop"):
                return "stop"
        
        with col4:
            if st.button("⏭️", help="Next frame"):
                return "next"
        
        with col5:
            if st.button("⚡", help="Toggle speed"):
                return "speed"
        
        return None
    
    def render_annotation_tools(self):
        """Render annotation tool selection"""
        tools = {
            "select": "🖱️ Select",
            "bbox": "📦 Bounding Box",
            "timeline": "📏 Timeline"
        }
        
        selected_tool = st.selectbox(
            "Tool",
            options=list(tools.keys()),
            format_func=lambda x: tools[x],
            key="annotation_tool"
        )
        
        return selected_tool
    
    def render_surfer_controls(self):
        """Render surfer-specific controls"""
        surfer_actions = {}
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("➕ Add Surfer", key="add_surfer"):
                surfer_actions["add"] = True
        
        with col2:
            if st.button("🗑️ Delete", key="delete_surfer"):
                surfer_actions["delete"] = True
        
        # Quality selector
        quality = st.selectbox(
            "Ride Quality",
            ["", "poor", "average", "good", "excellent"],
            key="surfer_quality"
        )
        
        if quality:
            surfer_actions["quality"] = quality
        
        return surfer_actions
    
    def render_timeline_controls(self, duration: float):
        """
        Render timeline control slider
        
        Args:
            duration: Video duration in seconds
            
        Returns:
            float: Selected timestamp
        """
        timestamp = st.slider(
            "Timeline",
            min_value=0.0,
            max_value=duration,
            value=0.0,
            step=0.1,
            format="%.1f s",
            key="timeline_slider"
        )
        
        return timestamp


class BoundingBoxTool:
    """Bounding box drawing and editing tool"""
    
    def __init__(self):
        self.drawing = False
        self.start_point = None
        self.current_bbox = None
        self.bbox_history = []
    
    def start_drawing(self, point: Tuple[int, int]):
        """
        Start drawing bounding box
        
        Args:
            point: Starting point (x, y)
        """
        self.drawing = True
        self.start_point = point
        self.current_bbox = None
    
    def update_drawing(self, point: Tuple[int, int]):
        """
        Update bounding box while drawing
        
        Args:
            point: Current point (x, y)
        """
        if self.drawing and self.start_point:
            x1, y1 = self.start_point
            x2, y2 = point
            
            # Normalize coordinates
            x = min(x1, x2)
            y = min(y1, y2)
            width = abs(x2 - x1)
            height = abs(y2 - y1)
            
            self.current_bbox = [x, y, width, height]
    
    def finish_drawing(self, point: Tuple[int, int]) -> Optional[List[int]]:
        """
        Finish drawing bounding box
        
        Args:
            point: End point (x, y)
            
        Returns:
            list: Bounding box coordinates [x, y, width, height] or None
        """
        if self.drawing and self.start_point:
            self.update_drawing(point)
            self.drawing = False
            
            if self.current_bbox and self.current_bbox[2] > 0 and self.current_bbox[3] > 0:
                bbox = self.current_bbox.copy()
                self.bbox_history.append(bbox)
                self.current_bbox = None
                self.start_point = None
                return bbox
        
        return None
    
    def cancel_drawing(self):
        """Cancel current drawing operation"""
        self.drawing = False
        self.start_point = None
        self.current_bbox = None
    
    def validate_bbox(self, bbox: List[int], frame_width: int, frame_height: int) -> bool:
        """
        Validate bounding box coordinates
        
        Args:
            bbox: Bounding box [x, y, width, height]
            frame_width: Frame width
            frame_height: Frame height
            
        Returns:
            bool: True if valid, False otherwise
        """
        if not bbox or len(bbox) != 4:
            return False
        
        x, y, width, height = bbox
        
        # Check for negative coordinates or zero area
        if x < 0 or y < 0 or width <= 0 or height <= 0:
            return False
        
        # Check if bounding box is within frame boundaries
        if x + width > frame_width or y + height > frame_height:
            return False
        
        return True
    
    def draw_bbox_on_frame(self, frame: np.ndarray, bbox: List[int], 
                          color: Tuple[int, int, int] = (0, 255, 0), 
                          thickness: int = 2) -> np.ndarray:
        """
        Draw bounding box on frame
        
        Args:
            frame: Input frame
            bbox: Bounding box coordinates
            color: Rectangle color (B, G, R)
            thickness: Line thickness
            
        Returns:
            numpy.ndarray: Frame with bounding box
        """
        if not self.validate_bbox(bbox, frame.shape[1], frame.shape[0]):
            return frame
        
        frame_copy = frame.copy()
        x, y, width, height = bbox
        
        cv2.rectangle(frame_copy, (x, y), (x + width, y + height), color, thickness)
        
        return frame_copy
    
    def get_bbox_center(self, bbox: List[int]) -> Tuple[int, int]:
        """
        Get center point of bounding box
        
        Args:
            bbox: Bounding box coordinates
            
        Returns:
            tuple: Center point (x, y)
        """
        x, y, width, height = bbox
        center_x = x + width // 2
        center_y = y + height // 2
        return (center_x, center_y)
    
    def resize_bbox(self, bbox: List[int], scale_factor: float) -> List[int]:
        """
        Resize bounding box by scale factor
        
        Args:
            bbox: Original bounding box
            scale_factor: Scale factor (1.0 = no change)
            
        Returns:
            list: Resized bounding box
        """
        x, y, width, height = bbox
        
        # Calculate new dimensions
        new_width = int(width * scale_factor)
        new_height = int(height * scale_factor)
        
        # Calculate new position to keep center the same
        new_x = x + (width - new_width) // 2
        new_y = y + (height - new_height) // 2
        
        return [new_x, new_y, new_width, new_height]


class TimelineVisualization:
    """Timeline visualization and interaction component"""
    
    def __init__(self):
        self.timeline_height = 50
        self.annotation_height = 20
    
    def create_timeline_image(self, duration: float, surfers: List, 
                            current_time: float, width: int = 800) -> np.ndarray:
        """
        Create timeline visualization image
        
        Args:
            duration: Video duration in seconds
            surfers: List of surfer annotations
            current_time: Current timestamp
            width: Timeline width in pixels
            
        Returns:
            numpy.ndarray: Timeline image
        """
        height = self.timeline_height + len(surfers) * self.annotation_height
        timeline_img = np.zeros((height, width, 3), dtype=np.uint8)
        
        # Draw main timeline
        cv2.rectangle(timeline_img, (0, 0), (width, self.timeline_height), (50, 50, 50), -1)
        
        # Draw time markers
        for i in range(0, int(duration) + 1, 10):  # Every 10 seconds
            x = int((i / duration) * width)
            cv2.line(timeline_img, (x, 0), (x, self.timeline_height), (100, 100, 100), 1)
            
            # Add time label
            cv2.putText(timeline_img, f"{i}s", (x + 2, 15), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
        
        # Draw current time indicator
        current_x = int((current_time / duration) * width)
        cv2.line(timeline_img, (current_x, 0), (current_x, height), (0, 255, 255), 2)
        
        # Draw surfer annotations
        colors = [(0, 255, 0), (255, 0, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255)]
        
        for i, surfer in enumerate(surfers):
            y_start = self.timeline_height + i * self.annotation_height
            y_end = y_start + self.annotation_height
            
            start_time = surfer.get('start_time')
            end_time = surfer.get('end_time')
            
            if start_time is not None:
                start_x = int((start_time / duration) * width)
                
                if end_time is not None:
                    end_x = int((end_time / duration) * width)
                    color = colors[surfer['id'] % len(colors)]
                    cv2.rectangle(timeline_img, (start_x, y_start), (end_x, y_end), color, -1)
                else:
                    # Only start time - draw ongoing annotation
                    color = colors[surfer['id'] % len(colors)]
                    cv2.rectangle(timeline_img, (start_x, y_start), (width, y_end), 
                                (*color[:2], color[2]//2), -1)  # Semi-transparent
                
                # Add surfer label
                cv2.putText(timeline_img, f"S{surfer['id']}", (start_x + 2, y_start + 15), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.3, (255, 255, 255), 1)
        
        return timeline_img
    
    def timeline_click_to_time(self, click_x: int, timeline_width: int, duration: float) -> float:
        """
        Convert timeline click position to timestamp
        
        Args:
            click_x: Click position on timeline
            timeline_width: Total timeline width
            duration: Video duration
            
        Returns:
            float: Timestamp in seconds
        """
        # Handle boundary conditions
        if click_x <= 0:
            return 0.0
        if click_x >= timeline_width:
            return duration
        
        ratio = click_x / timeline_width
        return ratio * duration


# Utility functions for UI components
def format_time(seconds: float) -> str:
    """
    Format time in seconds to MM:SS format
    
    Args:
        seconds: Time in seconds
        
    Returns:
        str: Formatted time string
    """
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes:02d}:{secs:02d}"


def create_color_palette(num_colors: int) -> List[Tuple[int, int, int]]:
    """
    Create color palette for multiple surfers
    
    Args:
        num_colors: Number of colors needed
        
    Returns:
        list: List of BGR color tuples
    """
    base_colors = [
        (0, 255, 0),    # Green
        (255, 0, 0),    # Blue
        (0, 0, 255),    # Red
        (255, 255, 0),  # Cyan
        (255, 0, 255),  # Magenta
        (0, 255, 255),  # Yellow
        (128, 0, 128),  # Purple
        (255, 165, 0),  # Orange
    ]
    
    # Repeat colors if needed
    colors = []
    for i in range(num_colors):
        colors.append(base_colors[i % len(base_colors)])
    
    return colors 