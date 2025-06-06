"""
Annotation Manager Module
Handles surfer annotations, data validation, and export/import operations
"""

import json
import csv
import os
from typing import List, Dict, Optional, Any
from datetime import datetime
import copy


class AnnotationManager:
    """Manages surfer annotations and session data"""
    
    def __init__(self):
        self.video_file = None
        self.duration = 0.0
        self.fps = 0.0
        self.surfers = []
        self.next_surfer_id = 1
        self.session_created = None
        self.session_modified = None
    
    def initialize_session(self, video_file: str, duration: float, fps: float):
        """
        Initialize new annotation session
        
        Args:
            video_file: Name of the video file
            duration: Video duration in seconds
            fps: Video frame rate
        """
        self.video_file = video_file
        self.duration = duration
        self.fps = fps
        self.surfers = []
        self.next_surfer_id = 1
        self.session_created = datetime.now().isoformat()
        self.session_modified = self.session_created
    
    def add_surfer(self, start_time: Optional[float] = None) -> int:
        """
        Add new surfer annotation
        
        Args:
            start_time: Optional start time for the surfer
            
        Returns:
            int: Surfer ID
        """
        surfer_id = self.next_surfer_id
        self.next_surfer_id += 1
        
        surfer = {
            'id': surfer_id,
            'start_time': start_time,
            'end_time': None,
            'duration': None,
            'bbox': None,
            'quality': None,
            'created': datetime.now().isoformat()
        }
        
        self.surfers.append(surfer)
        self._update_modified_time()
        
        return surfer_id
    
    def delete_surfer(self, surfer_id: int) -> bool:
        """
        Delete surfer annotation
        
        Args:
            surfer_id: ID of surfer to delete
            
        Returns:
            bool: True if deleted, False if not found
        """
        for i, surfer in enumerate(self.surfers):
            if surfer['id'] == surfer_id:
                del self.surfers[i]
                self._update_modified_time()
                return True
        return False
    
    def get_surfer(self, surfer_id: int) -> Optional[Dict]:
        """
        Get surfer by ID
        
        Args:
            surfer_id: Surfer ID
            
        Returns:
            dict: Surfer data or None if not found
        """
        for surfer in self.surfers:
            if surfer['id'] == surfer_id:
                return surfer
        return None
    
    def get_all_surfers(self) -> List[Dict]:
        """
        Get all surfer annotations
        
        Returns:
            list: List of all surfer dictionaries
        """
        return copy.deepcopy(self.surfers)
    
    def set_surfer_start_time(self, surfer_id: int, start_time: float) -> bool:
        """
        Set start time for surfer
        
        Args:
            surfer_id: Surfer ID
            start_time: Start time in seconds
            
        Returns:
            bool: True if successful, False if surfer not found
        """
        surfer = self.get_surfer(surfer_id)
        if surfer:
            surfer['start_time'] = start_time
            self._update_duration(surfer)
            self._update_modified_time()
            return True
        return False
    
    def set_surfer_end_time(self, surfer_id: int, end_time: float) -> bool:
        """
        Set end time for surfer
        
        Args:
            surfer_id: Surfer ID
            end_time: End time in seconds
            
        Returns:
            bool: True if successful, False if surfer not found
        """
        surfer = self.get_surfer(surfer_id)
        if surfer:
            surfer['end_time'] = end_time
            self._update_duration(surfer)
            self._update_modified_time()
            return True
        return False
    
    def set_surfer_bbox(self, surfer_id: int, bbox: List[int]) -> bool:
        """
        Set bounding box for surfer
        
        Args:
            surfer_id: Surfer ID
            bbox: Bounding box [x, y, width, height]
            
        Returns:
            bool: True if successful, False if surfer not found or invalid bbox
        """
        if not self._validate_bbox(bbox):
            return False
        
        surfer = self.get_surfer(surfer_id)
        if surfer:
            surfer['bbox'] = bbox
            self._update_modified_time()
            return True
        return False
    
    def set_surfer_quality(self, surfer_id: int, quality: str) -> bool:
        """
        Set quality rating for surfer
        
        Args:
            surfer_id: Surfer ID
            quality: Quality rating (poor, average, good, excellent)
            
        Returns:
            bool: True if successful, False if surfer not found or invalid quality
        """
        valid_qualities = ['poor', 'average', 'good', 'excellent']
        if quality not in valid_qualities:
            return False
        
        surfer = self.get_surfer(surfer_id)
        if surfer:
            surfer['quality'] = quality
            self._update_modified_time()
            return True
        return False
    
    def get_active_surfers(self, timestamp: float) -> List[Dict]:
        """
        Get surfers active at specific timestamp
        
        Args:
            timestamp: Time in seconds
            
        Returns:
            list: List of active surfer dictionaries
        """
        active_surfers = []
        
        for surfer in self.surfers:
            start_time = surfer.get('start_time')
            end_time = surfer.get('end_time')
            
            # Check if surfer is active at timestamp
            if start_time is not None:
                if end_time is not None:
                    # Both start and end times defined
                    if start_time <= timestamp <= end_time:
                        active_surfers.append(copy.deepcopy(surfer))
                else:
                    # Only start time defined
                    if timestamp >= start_time:
                        active_surfers.append(copy.deepcopy(surfer))
        
        return active_surfers
    
    def get_annotation_data(self) -> Dict[str, Any]:
        """
        Get complete annotation data for export
        
        Returns:
            dict: Complete annotation data
        """
        return {
            'video_file': self.video_file,
            'duration': self.duration,
            'fps': self.fps,
            'session_created': self.session_created,
            'session_modified': self.session_modified,
            'surfer_count': len(self.surfers),
            'surfers': copy.deepcopy(self.surfers)
        }
    
    def load_annotation_data(self, data: Dict[str, Any]) -> bool:
        """
        Load annotation data from dictionary
        
        Args:
            data: Annotation data dictionary
            
        Returns:
            bool: True if loaded successfully, False otherwise
        """
        try:
            # Validate required fields
            if not self._validate_annotation_data(data):
                return False
            
            # Load data
            self.video_file = data.get('video_file')
            self.duration = data.get('duration', 0.0)
            self.fps = data.get('fps', 30.0)
            self.session_created = data.get('session_created')
            self.session_modified = data.get('session_modified')
            self.surfers = data.get('surfers', [])
            
            # Update next surfer ID
            if self.surfers:
                max_id = max(surfer['id'] for surfer in self.surfers)
                self.next_surfer_id = max_id + 1
            else:
                self.next_surfer_id = 1
            
            self._update_modified_time()
            return True
            
        except Exception as e:
            print(f"Error loading annotation data: {str(e)}")
            return False
    
    def export_to_json(self, file_path: str) -> bool:
        """
        Export annotations to JSON file
        
        Args:
            file_path: Output file path
            
        Returns:
            bool: True if exported successfully, False otherwise
        """
        try:
            data = self.get_annotation_data()
            
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
            
            return True
            
        except Exception as e:
            print(f"Error exporting to JSON: {str(e)}")
            return False
    
    def import_from_json(self, file_path: str) -> bool:
        """
        Import annotations from JSON file
        
        Args:
            file_path: Input file path
            
        Returns:
            bool: True if imported successfully, False otherwise
        """
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")
            
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            return self.load_annotation_data(data)
            
        except Exception as e:
            print(f"Error importing from JSON: {str(e)}")
            return False
    
    def export_to_csv(self, file_path: str) -> bool:
        """
        Export annotations to CSV file
        
        Args:
            file_path: Output file path
            
        Returns:
            bool: True if exported successfully, False otherwise
        """
        try:
            with open(file_path, 'w', newline='') as csvfile:
                fieldnames = [
                    'video_file', 'surfer_id', 'start_time', 'end_time', 
                    'duration', 'bbox_x', 'bbox_y', 'bbox_width', 'bbox_height', 
                    'quality', 'created'
                ]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                # Write header
                writer.writeheader()
                
                # Write data rows
                for surfer in self.surfers:
                    row = {
                        'video_file': self.video_file,
                        'surfer_id': surfer['id'],
                        'start_time': surfer.get('start_time'),
                        'end_time': surfer.get('end_time'),
                        'duration': surfer.get('duration'),
                        'bbox_x': surfer['bbox'][0] if surfer.get('bbox') else None,
                        'bbox_y': surfer['bbox'][1] if surfer.get('bbox') else None,
                        'bbox_width': surfer['bbox'][2] if surfer.get('bbox') else None,
                        'bbox_height': surfer['bbox'][3] if surfer.get('bbox') else None,
                        'quality': surfer.get('quality'),
                        'created': surfer.get('created')
                    }
                    writer.writerow(row)
            
            return True
            
        except Exception as e:
            print(f"Error exporting to CSV: {str(e)}")
            return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get session statistics
        
        Returns:
            dict: Session statistics
        """
        completed_surfers = [s for s in self.surfers 
                           if s.get('start_time') is not None and s.get('end_time') is not None]
        
        durations = [s.get('duration', 0) for s in completed_surfers if s.get('duration')]
        qualities = [s.get('quality') for s in self.surfers if s.get('quality')]
        
        stats = {
            'total_surfers': len(self.surfers),
            'completed_surfers': len(completed_surfers),
            'completion_rate': len(completed_surfers) / len(self.surfers) if self.surfers else 0,
            'avg_ride_duration': sum(durations) / len(durations) if durations else 0,
            'max_ride_duration': max(durations) if durations else 0,
            'min_ride_duration': min(durations) if durations else 0,
            'quality_distribution': {q: qualities.count(q) for q in set(qualities)} if qualities else {}
        }
        
        return stats
    
    def _update_duration(self, surfer: Dict):
        """Update duration for surfer if both start and end times are set"""
        start_time = surfer.get('start_time')
        end_time = surfer.get('end_time')
        
        if start_time is not None and end_time is not None:
            surfer['duration'] = end_time - start_time
        else:
            surfer['duration'] = None
    
    def _update_modified_time(self):
        """Update session modified timestamp"""
        self.session_modified = datetime.now().isoformat()
    
    def _validate_bbox(self, bbox: List[int]) -> bool:
        """Validate bounding box format"""
        if not isinstance(bbox, list) or len(bbox) != 4:
            return False
        
        x, y, width, height = bbox
        return all(isinstance(val, (int, float)) and val >= 0 for val in bbox) and width > 0 and height > 0
    
    def _validate_annotation_data(self, data: Dict[str, Any]) -> bool:
        """Validate annotation data structure"""
        required_fields = ['video_file', 'duration', 'surfers']
        
        # Check required top-level fields
        for field in required_fields:
            if field not in data:
                print(f"Missing required field: {field}")
                return False
        
        # Validate surfers data
        surfers = data.get('surfers', [])
        if not isinstance(surfers, list):
            print("Surfers must be a list")
            return False
        
        # Validate each surfer
        for i, surfer in enumerate(surfers):
            if not isinstance(surfer, dict):
                print(f"Surfer {i} must be a dictionary")
                return False
            
            if 'id' not in surfer:
                print(f"Surfer {i} missing required field: id")
                return False
            
            # Validate time ranges if both start and end are present
            start_time = surfer.get('start_time')
            end_time = surfer.get('end_time')
            
            if start_time is not None and end_time is not None:
                if start_time >= end_time:
                    print(f"Surfer {i}: Invalid time range (start >= end)")
                    return False
        
        return True


def create_annotation_filename(video_path: str) -> str:
    """
    Create annotation filename from video path
    
    Args:
        video_path: Path to video file
        
    Returns:
        str: Annotation filename
    """
    base_path = os.path.splitext(video_path)[0]
    return f"{base_path}_annotations.json"


def backup_annotations(annotation_path: str) -> bool:
    """
    Create backup of existing annotation file
    
    Args:
        annotation_path: Path to annotation file
        
    Returns:
        bool: True if backup created, False otherwise
    """
    try:
        if os.path.exists(annotation_path):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = annotation_path.replace('.json', f'_backup_{timestamp}.json')
            
            import shutil
            shutil.copy2(annotation_path, backup_path)
            return True
        return False
    except Exception as e:
        print(f"Error creating backup: {str(e)}")
        return False 