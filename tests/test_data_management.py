"""
Unit Tests - Data Management Functions
Tests for JSON export/import, annotation data validation, and file handling
"""

import pytest
import json
import os
import tempfile
import pandas as pd
from unittest.mock import Mock, patch, mock_open


class TestJSONExportImport:
    """Test JSON export and import functionality"""
    
    def test_export_annotations_to_json(self):
        """Test exporting annotation data to JSON format"""
        annotation_data = {
            "video_file": "test_session.mp4",
            "duration": 120.5,
            "surfers": [
                {
                    "id": 1,
                    "start_time": 10.2,
                    "end_time": 25.8,
                    "duration": 15.6,
                    "bbox": [100, 150, 200, 300],
                    "quality": "good"
                }
            ]
        }
        
        output_path = "test_annotations.json"
        
        m = mock_open()
        with patch("builtins.open", m) as mock_file:
            result = export_annotations_to_json(annotation_data, output_path)
            
            # Verify file was opened for writing
            mock_file.assert_called_once_with(output_path, 'w')
            
            # Verify JSON data was written correctly
            handle = m()
            written_calls = handle.write.call_args_list
            written_data = ''.join(call[0][0] for call in written_calls)
            parsed_data = json.loads(written_data)
            assert parsed_data == annotation_data
            assert result is True
    
    def test_import_annotations_from_json(self):
        """Test importing annotation data from JSON file"""
        json_content = {
            "video_file": "test_session.mp4",
            "duration": 120.5,
            "surfers": [
                {
                    "id": 1,
                    "start_time": 10.2,
                    "end_time": 25.8,
                    "duration": 15.6,
                    "bbox": [100, 150, 200, 300],
                    "quality": "good"
                }
            ]
        }
        
        with patch("builtins.open", mock_open(read_data=json.dumps(json_content))):
            with patch("os.path.exists", return_value=True):
                result = import_annotations_from_json("test_annotations.json")
                
                assert result == json_content
                assert result["video_file"] == "test_session.mp4"
                assert len(result["surfers"]) == 1
    
    def test_import_invalid_json_file(self):
        """Test handling of invalid JSON files"""
        invalid_json = "{ invalid json content"
        
        with patch("builtins.open", mock_open(read_data=invalid_json)):
            with patch("os.path.exists", return_value=True):
                with pytest.raises(ValueError, match="Invalid JSON format"):
                    import_annotations_from_json("invalid.json")
    
    def test_import_nonexistent_json_file(self):
        """Test handling of non-existent JSON files"""
        with patch("os.path.exists", return_value=False):
            with pytest.raises(FileNotFoundError):
                import_annotations_from_json("nonexistent.json")


class TestAnnotationDataValidation:
    """Test annotation data structure validation"""
    
    def test_valid_annotation_structure(self):
        """Test validation of correct annotation data structure"""
        valid_data = {
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
                }
            ]
        }
        
        is_valid = validate_annotation_data(valid_data)
        assert is_valid is True
    
    def test_missing_required_fields(self):
        """Test validation with missing required fields"""
        invalid_data = {
            "video_file": "session_001.mp4",
            # Missing duration and surfers
        }
        
        is_valid = validate_annotation_data(invalid_data)
        assert is_valid is False
    
    def test_invalid_surfer_data(self):
        """Test validation with invalid surfer data structure"""
        invalid_data = {
            "video_file": "session_001.mp4",
            "duration": 120.5,
            "surfers": [
                {
                    "id": 1,
                    # Missing start_time, end_time, bbox
                    "quality": "good"
                }
            ]
        }
        
        is_valid = validate_annotation_data(invalid_data)
        assert is_valid is False
    
    def test_invalid_time_ranges(self):
        """Test validation with invalid time ranges"""
        invalid_data = {
            "video_file": "session_001.mp4",
            "duration": 120.5,
            "surfers": [
                {
                    "id": 1,
                    "start_time": 25.8,  # Start after end
                    "end_time": 10.2,
                    "duration": -15.6,
                    "bbox": [100, 150, 200, 300],
                    "quality": "good"
                }
            ]
        }
        
        is_valid = validate_annotation_data(invalid_data)
        assert is_valid is False


class TestFilePathHandling:
    """Test file path handling and error cases"""
    
    def test_create_annotation_filename(self):
        """Test creating annotation filename from video path"""
        video_path = "/path/to/surfing_session_001.mp4"
        expected_annotation_path = "/path/to/surfing_session_001_annotations.json"
        
        annotation_path = create_annotation_filename(video_path)
        assert annotation_path == expected_annotation_path
    
    def test_create_output_directory(self):
        """Test creating output directory for annotations"""
        output_dir = "/tmp/test_annotations"
        
        with patch("os.makedirs") as mock_makedirs:
            with patch("os.path.exists", return_value=False):
                create_output_directory(output_dir)
                mock_makedirs.assert_called_once_with(output_dir, exist_ok=True)
    
    def test_validate_video_file_path(self):
        """Test video file path validation"""
        valid_extensions = [".mp4", ".mov", ".avi", ".mkv"]
        
        # Test valid paths
        for ext in valid_extensions:
            path = f"video{ext}"
            with patch("os.path.exists", return_value=True):
                assert validate_video_file_path(path) is True
        
        # Test invalid extension
        with patch("os.path.exists", return_value=True):
            assert validate_video_file_path("video.txt") is False
        
        # Test non-existent file
        with patch("os.path.exists", return_value=False):
            assert validate_video_file_path("video.mp4") is False
    
    def test_backup_existing_annotations(self):
        """Test creating backup of existing annotation files"""
        annotation_path = "session_001_annotations.json"
        backup_path = "session_001_annotations_backup.json"
        
        with patch("os.path.exists", return_value=True):
            with patch("shutil.copy2") as mock_copy:
                backup_annotations(annotation_path)
                mock_copy.assert_called_once()


class TestCSVExport:
    """Test CSV export functionality for quick analysis"""
    
    def test_export_annotations_to_csv(self):
        """Test exporting annotation data to CSV format"""
        annotation_data = {
            "video_file": "test_session.mp4",
            "duration": 120.5,
            "surfers": [
                {
                    "id": 1,
                    "start_time": 10.2,
                    "end_time": 25.8,
                    "duration": 15.6,
                    "bbox": [100, 150, 200, 300],
                    "quality": "good"
                }
            ]
        }
        
        output_path = "test_annotations.csv"
        
        with patch("pandas.DataFrame.to_csv") as mock_to_csv:
            result = export_annotations_to_csv(annotation_data, output_path)
            
            # Verify CSV export was called
            mock_to_csv.assert_called_once_with(output_path, index=False)
            assert result is True


# Mock functions to be implemented in actual annotation tool
def export_annotations_to_json(annotation_data, output_path):
    """Export annotation data to JSON file"""
    try:
        with open(output_path, 'w') as f:
            json.dump(annotation_data, f, indent=2)
        return True
    except Exception as e:
        print(f"Error exporting to JSON: {e}")
        return False


def import_annotations_from_json(json_path):
    """Import annotation data from JSON file"""
    if not os.path.exists(json_path):
        raise FileNotFoundError(f"JSON file not found: {json_path}")
    
    try:
        with open(json_path, 'r') as f:
            data = json.load(f)
        return data
    except json.JSONDecodeError:
        raise ValueError("Invalid JSON format")


def validate_annotation_data(data):
    """Validate annotation data structure"""
    required_fields = ["video_file", "duration", "surfers"]
    
    # Check required top-level fields
    for field in required_fields:
        if field not in data:
            return False
    
    # Validate surfers data
    for surfer in data["surfers"]:
        required_surfer_fields = ["id", "start_time", "end_time", "bbox"]
        for field in required_surfer_fields:
            if field not in surfer:
                return False
        
        # Check time validity
        if surfer["start_time"] >= surfer["end_time"]:
            return False
    
    return True


def create_annotation_filename(video_path):
    """Create annotation filename from video path"""
    base_path = os.path.splitext(video_path)[0]
    return f"{base_path}_annotations.json"


def create_output_directory(output_dir):
    """Create output directory for annotations"""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)


def validate_video_file_path(file_path):
    """Validate video file path and extension"""
    valid_extensions = [".mp4", ".mov", ".avi", ".mkv"]
    
    if not os.path.exists(file_path):
        return False
    
    file_ext = os.path.splitext(file_path)[1].lower()
    return file_ext in valid_extensions


def backup_annotations(annotation_path):
    """Create backup of existing annotation file"""
    if os.path.exists(annotation_path):
        backup_path = annotation_path.replace('.json', '_backup.json')
        import shutil
        shutil.copy2(annotation_path, backup_path)
        return backup_path
    return None


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
                "duration": surfer.get("duration", surfer["end_time"] - surfer["start_time"]),
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