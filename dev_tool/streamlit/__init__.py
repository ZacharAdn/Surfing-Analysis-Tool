"""
Surfing Video Annotation Tool
A comprehensive tool for annotating surfing videos with multi-surfer tracking capabilities
"""

__version__ = "1.0.0"
__author__ = "Surfing Analysis Project"
__description__ = "Video annotation tool for surfing movement analysis"

# Import main components
from .video_processor import VideoProcessor
from .annotation_manager import AnnotationManager
from .ui_components import VideoPlayer, AnnotationControls, BoundingBoxTool

__all__ = [
    'VideoProcessor',
    'AnnotationManager', 
    'VideoPlayer',
    'AnnotationControls',
    'BoundingBoxTool'
] 