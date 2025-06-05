"""
Surfing Video Annotation Tool
Main application for annotating surfing videos with multi-surfer support
"""

import streamlit as st
import cv2
import json
import os
import pandas as pd
from datetime import datetime
import numpy as np
from pathlib import Path

# Import our modules
from video_processor import VideoProcessor
from annotation_manager import AnnotationManager
from ui_components import VideoPlayer, AnnotationControls, BoundingBoxTool

# Page configuration
st.set_page_config(
    page_title="Surfing Video Annotation Tool",
    page_icon="🏄‍♂️",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    """Main application function"""
    st.title("🏄‍♂️ Surfing Video Annotation Tool")
    st.markdown("Annotate surfing videos with multiple surfer tracking and analysis")
    
    # Initialize session state
    initialize_session_state()
    
    # Sidebar for file management
    with st.sidebar:
        st.header("📁 File Management")
        handle_file_operations()
        
        st.header("🎮 Controls")
        display_annotation_controls()
        
        st.header("📊 Session Info")
        display_session_info()
    
    # Main content area
    if st.session_state.video_loaded:
        col1, col2 = st.columns([3, 1])
        
        with col1:
            display_video_player()
            display_timeline()
            
        with col2:
            display_surfer_management()
            display_annotation_list()
    else:
        display_welcome_screen()

def initialize_session_state():
    """Initialize Streamlit session state variables"""
    if 'video_processor' not in st.session_state:
        st.session_state.video_processor = VideoProcessor()
    
    if 'annotation_manager' not in st.session_state:
        st.session_state.annotation_manager = AnnotationManager()
    
    if 'video_loaded' not in st.session_state:
        st.session_state.video_loaded = False
    
    if 'current_frame' not in st.session_state:
        st.session_state.current_frame = 0
    
    if 'current_time' not in st.session_state:
        st.session_state.current_time = 0.0
    
    if 'selected_surfer' not in st.session_state:
        st.session_state.selected_surfer = None
    
    if 'drawing_bbox' not in st.session_state:
        st.session_state.drawing_bbox = False

def handle_file_operations():
    """Handle video file loading and annotation saving/loading"""
    
    # Video file upload
    uploaded_file = st.file_uploader(
        "Choose a video file",
        type=['mp4', 'mov', 'avi', 'mkv'],
        help="Upload your drone surfing footage"
    )
    
    if uploaded_file is not None:
        if st.button("Load Video"):
            load_video(uploaded_file)
    
    # Load existing annotations
    if st.session_state.video_loaded:
        st.subheader("💾 Save/Load Annotations")
        
        # Save annotations
        if st.button("Save Annotations"):
            save_annotations()
        
        # Load annotations
        annotation_file = st.file_uploader(
            "Load existing annotations",
            type=['json'],
            help="Load previously saved annotation session"
        )
        
        if annotation_file is not None:
            if st.button("Load Annotations"):
                load_annotations(annotation_file)

def load_video(uploaded_file):
    """Load video file and initialize video processor"""
    try:
        # Create proper video directory if it doesn't exist
        video_dir = "data/videos"
        os.makedirs(video_dir, exist_ok=True)
        
        # Save uploaded file to proper location with original name
        video_filename = uploaded_file.name
        video_path = os.path.join(video_dir, video_filename)
        
        # Save the uploaded file
        with open(video_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        # Load video using video processor
        success = st.session_state.video_processor.load_video(video_path)
        
        if success:
            st.session_state.video_loaded = True
            st.session_state.current_frame = 0
            st.session_state.current_time = 0.0
            st.session_state.video_path = video_path
            
            # Initialize annotation manager with video info
            st.session_state.annotation_manager.initialize_session(
                video_file=video_filename,
                duration=st.session_state.video_processor.duration,
                fps=st.session_state.video_processor.fps
            )
            
            st.success(f"✅ Video loaded successfully!")
            st.info(f"📁 Saved to: {video_path}")
            st.info(f"⏱️ Duration: {st.session_state.video_processor.duration:.1f}s")
            st.info(f"🎬 FPS: {st.session_state.video_processor.fps:.1f}")
        else:
            st.error("❌ Failed to load video. Please check the file format.")
            
    except Exception as e:
        st.error(f"❌ Error loading video: {str(e)}")

def save_annotations():
    """Save current annotations to JSON file with proper file organization"""
    try:
        # Create annotations directory
        annotations_dir = "data/annotations"
        os.makedirs(annotations_dir, exist_ok=True)
        
        annotation_data = st.session_state.annotation_manager.get_annotation_data()
        
        # Generate filename with timestamp and video name
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        video_name = st.session_state.annotation_manager.video_file.replace('.', '_')
        filename = f"annotations_{video_name}_{timestamp}.json"
        filepath = os.path.join(annotations_dir, filename)
        
        # Save to file
        with open(filepath, 'w') as f:
            json.dump(annotation_data, f, indent=2)
        
        st.success(f"✅ Annotations saved successfully!")
        st.info(f"📁 Saved to: {filepath}")
        
        # Provide download link
        st.download_button(
            label="💾 Download Annotations",
            data=json.dumps(annotation_data, indent=2),
            file_name=filename,
            mime="application/json",
            help="Download annotations file to your computer"
        )
        
        # Export to CSV option
        if st.button("📊 Export to CSV"):
            export_to_csv()
        
    except Exception as e:
        st.error(f"❌ Error saving annotations: {str(e)}")

def export_to_csv():
    """Export annotations to CSV format"""
    try:
        # Create exports directory
        exports_dir = "data/exports"
        os.makedirs(exports_dir, exist_ok=True)
        
        # Get annotation data and convert to CSV format
        csv_data = st.session_state.annotation_manager.export_to_csv()
        
        # Generate CSV filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        video_name = st.session_state.annotation_manager.video_file.replace('.', '_')
        csv_filename = f"annotations_{video_name}_{timestamp}.csv"
        csv_filepath = os.path.join(exports_dir, csv_filename)
        
        # Save CSV file
        csv_data.to_csv(csv_filepath, index=False)
        
        st.success(f"✅ CSV export successful!")
        st.info(f"📁 Saved to: {csv_filepath}")
        
        # Provide download link
        st.download_button(
            label="📊 Download CSV",
            data=csv_data.to_csv(index=False),
            file_name=csv_filename,
            mime="text/csv",
            help="Download CSV file for data analysis"
        )
        
    except Exception as e:
        st.error(f"❌ Error exporting to CSV: {str(e)}")

def load_annotations(annotation_file):
    """Load annotations from JSON file"""
    try:
        annotation_data = json.load(annotation_file)
        st.session_state.annotation_manager.load_annotation_data(annotation_data)
        st.success("Annotations loaded successfully!")
        
    except Exception as e:
        st.error(f"Error loading annotations: {str(e)}")

def display_annotation_controls():
    """Display annotation control buttons"""
    
    if not st.session_state.video_loaded:
        st.info("Load a video to start annotating")
        return
    
    # Playback controls
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("⏮️ Previous"):
            previous_frame()
    
    with col2:
        if st.button("⏯️ Play/Pause"):
            toggle_playback()
    
    with col3:
        if st.button("⏭️ Next"):
            next_frame()
    
    # Time navigation
    max_time = st.session_state.video_processor.duration
    current_time = st.slider(
        "Time (seconds)",
        min_value=0.0,
        max_value=max_time,
        value=st.session_state.current_time,
        step=0.1,
        key="time_slider"
    )
    
    if current_time != st.session_state.current_time:
        seek_to_time(current_time)

def display_video_player():
    """Display video player with current frame and enhanced controls"""
    
    if not st.session_state.video_loaded:
        return
    
    # Get current frame
    frame = st.session_state.video_processor.get_frame_at_time(st.session_state.current_time)
    
    if frame is not None:
        # Draw annotations on frame
        annotated_frame = draw_annotations_on_frame(frame)
        
        # Display frame
        st.image(annotated_frame, channels="BGR", use_column_width=True)
        
        # Enhanced playback controls
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            if st.button("⏮️ Start", help="Go to beginning"):
                seek_to_time(0.0)
                
        with col2:
            if st.button("⏪ -1s", help="Go back 1 second"):
                new_time = max(0, st.session_state.current_time - 1.0)
                seek_to_time(new_time)
                
        with col3:
            if st.button("⏯️ Play/Pause", help="Toggle playback"):
                toggle_playback()
                
        with col4:
            if st.button("⏩ +1s", help="Go forward 1 second"):
                new_time = min(st.session_state.video_processor.duration, 
                              st.session_state.current_time + 1.0)
                seek_to_time(new_time)
                
        with col5:
            if st.button("⏭️ End", help="Go to end"):
                seek_to_time(st.session_state.video_processor.duration - 0.1)
        
        # Time slider for seeking
        current_time = st.slider(
            "Seek to time",
            min_value=0.0,
            max_value=st.session_state.video_processor.duration,
            value=st.session_state.current_time,
            step=0.1,
            format="%.1fs",
            key="time_slider"
        )
        
        # Update time if slider changed
        if abs(current_time - st.session_state.current_time) > 0.05:
            seek_to_time(current_time)
        
        # Display frame info
        st.caption(f"Frame: {st.session_state.current_frame} | "
                  f"Time: {st.session_state.current_time:.2f}s / {st.session_state.video_processor.duration:.2f}s | "
                  f"FPS: {st.session_state.video_processor.fps:.1f}")
    else:
        st.error("❌ Unable to load video frame. Please check the video file.")

def draw_annotations_on_frame(frame):
    """Draw current annotations on the frame"""
    annotated_frame = frame.copy()
    
    # Get active surfers at current time
    active_surfers = st.session_state.annotation_manager.get_active_surfers(st.session_state.current_time)
    
    for surfer in active_surfers:
        if surfer.get('bbox'):
            x, y, w, h = surfer['bbox']
            
            # Choose color based on surfer ID
            colors = [(0, 255, 0), (255, 0, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255)]
            color = colors[surfer['id'] % len(colors)]
            
            # Draw bounding box
            cv2.rectangle(annotated_frame, (x, y), (x + w, y + h), color, 2)
            
            # Draw surfer label
            label = f"Surfer {surfer['id']}"
            cv2.putText(annotated_frame, label, (x, y - 10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
    
    return annotated_frame

def display_timeline():
    """Display timeline with annotations"""
    if not st.session_state.video_loaded:
        return
    
    st.subheader("📈 Timeline")
    
    # Create timeline visualization
    duration = st.session_state.video_processor.duration
    surfers = st.session_state.annotation_manager.get_all_surfers()
    
    if surfers:
        # Create timeline chart
        timeline_data = []
        for surfer in surfers:
            if surfer.get('start_time') is not None and surfer.get('end_time') is not None:
                timeline_data.append({
                    'Surfer': f"Surfer {surfer['id']}",
                    'Start': surfer['start_time'],
                    'End': surfer['end_time'],
                    'Duration': surfer['end_time'] - surfer['start_time']
                })
        
        if timeline_data:
            df = pd.DataFrame(timeline_data)
            st.dataframe(df, use_container_width=True)

def display_surfer_management():
    """Display surfer management controls"""
    
    st.subheader("🏄‍♂️ Surfer Management")
    
    if not st.session_state.video_loaded:
        return
    
    # Add new surfer
    if st.button("➕ Add Surfer", use_container_width=True):
        add_new_surfer()
    
    # Select active surfer
    surfers = st.session_state.annotation_manager.get_all_surfers()
    if surfers:
        surfer_options = [f"Surfer {s['id']}" for s in surfers]
        selected_surfer_idx = st.selectbox(
            "Select Surfer",
            range(len(surfer_options)),
            format_func=lambda x: surfer_options[x],
            key="surfer_select"
        )
        
        if selected_surfer_idx is not None:
            st.session_state.selected_surfer = surfers[selected_surfer_idx]['id']
    
    # Surfer action buttons
    if st.session_state.selected_surfer:
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🟢 Mark Start"):
                mark_surfer_start()
        
        with col2:
            if st.button("🔴 Mark End"):
                mark_surfer_end()
        
        # Quality rating
        quality = st.selectbox(
            "Ride Quality",
            ["", "poor", "average", "good", "excellent"],
            key="quality_select"
        )
        
        if quality:
            set_surfer_quality(quality)

def display_annotation_list():
    """Display list of current annotations"""
    
    st.subheader("📝 Annotations")
    
    surfers = st.session_state.annotation_manager.get_all_surfers()
    
    if not surfers:
        st.info("No annotations yet. Add a surfer to start annotating.")
        return
    
    for surfer in surfers:
        with st.expander(f"Surfer {surfer['id']}", expanded=False):
            st.write(f"**ID:** {surfer['id']}")
            st.write(f"**Start Time:** {surfer.get('start_time', 'Not set')}")
            st.write(f"**End Time:** {surfer.get('end_time', 'Not set')}")
            st.write(f"**Quality:** {surfer.get('quality', 'Not rated')}")
            
            if surfer.get('bbox'):
                st.write(f"**Bounding Box:** {surfer['bbox']}")
            
            # Delete button
            if st.button(f"🗑️ Delete Surfer {surfer['id']}", key=f"delete_{surfer['id']}"):
                delete_surfer(surfer['id'])

def display_session_info():
    """Display current session information with enhanced details"""
    
    if st.session_state.video_loaded:
        st.write(f"**📹 Video:** {st.session_state.annotation_manager.video_file}")
        st.write(f"**📁 Path:** {st.session_state.get('video_path', 'N/A')}")
        st.write(f"**⏱️ Duration:** {st.session_state.video_processor.duration:.1f}s")
        st.write(f"**🎬 FPS:** {st.session_state.video_processor.fps:.1f}")
        st.write(f"**📐 Resolution:** {st.session_state.video_processor.width}x{st.session_state.video_processor.height}")
        
        surfer_count = len(st.session_state.annotation_manager.get_all_surfers())
        st.write(f"**🏄‍♂️ Surfers:** {surfer_count}")
        
        # Progress indicator
        completed_surfers = len([s for s in st.session_state.annotation_manager.get_all_surfers() 
                               if s.get('start_time') and s.get('end_time')])
        if surfer_count > 0:
            progress = completed_surfers / surfer_count
            st.progress(progress)
            st.write(f"**📊 Progress:** {completed_surfers}/{surfer_count} completed ({progress:.1%})")
            
        # Storage info
        st.subheader("💾 File Organization")
        st.write("- **Videos:** `data/videos/`")
        st.write("- **Annotations:** `data/annotations/`") 
        st.write("- **Exports:** `data/exports/`")

def display_welcome_screen():
    """Display welcome screen when no video is loaded"""
    
    st.markdown("""
    ## Welcome to the Surfing Video Annotation Tool! 🏄‍♂️
    
    This tool helps you annotate surfing videos with multiple surfer tracking and analysis capabilities.
    
    ### How to use:
    1. **Upload a video** using the file uploader in the sidebar
    2. **Add surfers** using the controls
    3. **Mark start and end times** for each ride
    4. **Draw bounding boxes** around surfers
    5. **Rate ride quality** for analysis
    6. **Save annotations** for later use
    
    ### Supported formats:
    - MP4, MOV, AVI, MKV video files
    - JSON annotation files for loading previous sessions
    
    Get started by uploading a video file!
    """)

# Navigation functions
def previous_frame():
    """Go to previous frame"""
    if st.session_state.current_frame > 0:
        st.session_state.current_frame -= 1
        st.session_state.current_time = st.session_state.current_frame / st.session_state.video_processor.fps

def next_frame():
    """Go to next frame"""
    max_frame = int(st.session_state.video_processor.duration * st.session_state.video_processor.fps)
    if st.session_state.current_frame < max_frame - 1:
        st.session_state.current_frame += 1
        st.session_state.current_time = st.session_state.current_frame / st.session_state.video_processor.fps

def seek_to_time(time):
    """Seek to specific time with improved accuracy"""
    if not st.session_state.video_loaded:
        return
        
    # Clamp time to valid range
    time = max(0.0, min(time, st.session_state.video_processor.duration))
    
    # Update session state
    st.session_state.current_time = time
    st.session_state.current_frame = int(time * st.session_state.video_processor.fps)
    
    # Force UI refresh
    st.rerun()

def toggle_playback():
    """Toggle video playback - enhanced implementation"""
    if not st.session_state.video_loaded:
        return
        
    # Initialize playback state if not exists
    if 'is_playing' not in st.session_state:
        st.session_state.is_playing = False
    
    # Toggle playback state
    st.session_state.is_playing = not st.session_state.is_playing
    
    if st.session_state.is_playing:
        st.success("▶️ Playback started (manual frame advance)")
        st.info("Use the +1s button or slider to advance through the video")
    else:
        st.info("⏸️ Playback paused")

# Annotation functions
def add_new_surfer():
    """Add a new surfer at current time"""
    surfer_id = st.session_state.annotation_manager.add_surfer(st.session_state.current_time)
    st.session_state.selected_surfer = surfer_id
    st.success(f"Added Surfer {surfer_id}")

def mark_surfer_start():
    """Mark start time for selected surfer"""
    if st.session_state.selected_surfer:
        st.session_state.annotation_manager.set_surfer_start_time(
            st.session_state.selected_surfer, 
            st.session_state.current_time
        )
        st.success(f"Marked start time for Surfer {st.session_state.selected_surfer}")

def mark_surfer_end():
    """Mark end time for selected surfer"""
    if st.session_state.selected_surfer:
        st.session_state.annotation_manager.set_surfer_end_time(
            st.session_state.selected_surfer,
            st.session_state.current_time
        )
        st.success(f"Marked end time for Surfer {st.session_state.selected_surfer}")

def set_surfer_quality(quality):
    """Set quality rating for selected surfer"""
    if st.session_state.selected_surfer:
        st.session_state.annotation_manager.set_surfer_quality(
            st.session_state.selected_surfer,
            quality
        )

def delete_surfer(surfer_id):
    """Delete a surfer annotation"""
    st.session_state.annotation_manager.delete_surfer(surfer_id)
    if st.session_state.selected_surfer == surfer_id:
        st.session_state.selected_surfer = None
    st.success(f"Deleted Surfer {surfer_id}")

if __name__ == "__main__":
    main() 