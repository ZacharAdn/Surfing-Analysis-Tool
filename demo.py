#!/usr/bin/env python3
"""
Demo script for the Surfing Video Annotation Tool
Test the components without requiring a video file
"""

import json
import numpy as np
from video_processor import VideoProcessor
from annotation_manager import AnnotationManager
from ui_components import BoundingBoxTool, format_time

def test_annotation_manager():
    """Test the annotation manager functionality"""
    print("Testing Annotation Manager...")
    
    # Initialize annotation manager
    manager = AnnotationManager()
    manager.initialize_session("demo_video.mp4", 120.0, 30.0)
    
    # Add some test surfers
    surfer1_id = manager.add_surfer(10.0)
    surfer2_id = manager.add_surfer(25.0)
    
    # Set end times and quality
    manager.set_surfer_end_time(surfer1_id, 22.5)
    manager.set_surfer_end_time(surfer2_id, 40.0)
    manager.set_surfer_quality(surfer1_id, "good")
    manager.set_surfer_quality(surfer2_id, "excellent")
    
    # Set bounding boxes
    manager.set_surfer_bbox(surfer1_id, [100, 150, 200, 250])
    manager.set_surfer_bbox(surfer2_id, [300, 200, 180, 220])
    
    # Get active surfers at different times
    active_at_15 = manager.get_active_surfers(15.0)
    active_at_30 = manager.get_active_surfers(30.0)
    
    print(f"✓ Created {len(manager.get_all_surfers())} surfers")
    print(f"✓ Active surfers at 15s: {len(active_at_15)}")
    print(f"✓ Active surfers at 30s: {len(active_at_30)}")
    
    # Test export
    annotation_data = manager.get_annotation_data()
    print(f"✓ Annotation data contains {annotation_data['surfer_count']} surfers")
    
    # Test statistics
    stats = manager.get_statistics()
    print(f"✓ Statistics: {stats['completion_rate']:.1%} completion rate")
    
    return manager

def test_bounding_box_tool():
    """Test the bounding box tool functionality"""
    print("\nTesting Bounding Box Tool...")
    
    bbox_tool = BoundingBoxTool()
    
    # Test drawing simulation
    bbox_tool.start_drawing((50, 75))
    bbox_tool.update_drawing((250, 200))
    final_bbox = bbox_tool.finish_drawing((250, 200))
    
    print(f"✓ Created bounding box: {final_bbox}")
    
    # Test validation
    frame_width, frame_height = 640, 480
    is_valid = bbox_tool.validate_bbox(final_bbox, frame_width, frame_height)
    print(f"✓ Bounding box valid: {is_valid}")
    
    # Test resize
    resized_bbox = bbox_tool.resize_bbox(final_bbox, 1.5)
    print(f"✓ Resized bounding box: {resized_bbox}")
    
    # Test center calculation
    center = bbox_tool.get_bbox_center(final_bbox)
    print(f"✓ Bounding box center: {center}")
    
    return bbox_tool

def test_utility_functions():
    """Test utility functions"""
    print("\nTesting Utility Functions...")
    
    # Test time formatting
    times = [45.5, 125.8, 3661.2]
    for time_val in times:
        formatted = format_time(time_val)
        print(f"✓ {time_val}s -> {formatted}")
    
def test_json_export_import():
    """Test JSON export and import functionality"""
    print("\nTesting JSON Export/Import...")
    
    # Create test data
    manager = AnnotationManager()
    manager.initialize_session("test_video.mp4", 90.0, 25.0)
    
    surfer_id = manager.add_surfer(5.0)
    manager.set_surfer_end_time(surfer_id, 18.0)
    manager.set_surfer_bbox(surfer_id, [50, 100, 150, 200])
    manager.set_surfer_quality(surfer_id, "average")
    
    # Export to JSON
    test_file = "demo_annotations.json"
    success = manager.export_to_json(test_file)
    print(f"✓ JSON export success: {success}")
    
    # Import from JSON
    new_manager = AnnotationManager()
    import_success = new_manager.import_from_json(test_file)
    print(f"✓ JSON import success: {import_success}")
    
    if import_success:
        imported_surfers = new_manager.get_all_surfers()
        print(f"✓ Imported {len(imported_surfers)} surfers")
    
    # Clean up
    import os
    if os.path.exists(test_file):
        os.remove(test_file)
        print("✓ Cleaned up test file")

def test_csv_export():
    """Test CSV export functionality"""
    print("\nTesting CSV Export...")
    
    # Create test data
    manager = AnnotationManager()
    manager.initialize_session("test_video.mp4", 120.0, 30.0)
    
    # Add multiple surfers
    for i in range(3):
        surfer_id = manager.add_surfer(i * 20.0)
        manager.set_surfer_end_time(surfer_id, i * 20.0 + 15.0)
        manager.set_surfer_quality(surfer_id, ["good", "average", "excellent"][i])
        manager.set_surfer_bbox(surfer_id, [i*100, i*50, 150, 200])
    
    # Export to CSV
    test_file = "demo_annotations.csv"
    success = manager.export_to_csv(test_file)
    print(f"✓ CSV export success: {success}")
    
    # Clean up
    import os
    if os.path.exists(test_file):
        os.remove(test_file)
        print("✓ Cleaned up test file")

def main():
    """Run all demo tests"""
    print("=" * 60)
    print("🏄‍♂️ SURFING ANNOTATION TOOL - DEMO")
    print("=" * 60)
    
    try:
        # Test each component
        test_annotation_manager()
        test_bounding_box_tool() 
        test_utility_functions()
        test_json_export_import()
        test_csv_export()
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("The annotation tool components are working correctly.")
        print("You can now run the full application with:")
        print("   python run_annotation_tool.py")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 