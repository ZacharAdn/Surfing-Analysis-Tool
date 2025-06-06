#!/usr/bin/env python3
"""
Startup script for the Surfing Video Annotation Tool
Run this script to start the annotation application
"""

import sys
import os
import subprocess
from pathlib import Path

def check_requirements():
    """Check if required packages are installed"""
    try:
        import streamlit
        import cv2
        import numpy
        import pandas
        print("✓ All required packages are installed")
        return True
    except ImportError as e:
        print(f"✗ Missing required package: {e}")
        print("Please install requirements with: pip install -r requirements.txt")
        return False

def setup_directories():
    """Create necessary directories"""
    directories = [
        "data",
        "output",
        "annotations",
        "temp"
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✓ Directory '{directory}' ready")

def run_application():
    """Run the Streamlit application"""
    try:
        # Change to dev_tool directory
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        
        # Run streamlit app
        print("\n🏄‍♂️ Starting Surfing Video Annotation Tool...")
        print("The application will open in your web browser.")
        print("If it doesn't open automatically, go to: http://localhost:8501")
        print("\nPress Ctrl+C to stop the application.\n")
        
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            "annotation_app.py",
            "--server.port=8501",
            "--server.address=localhost",
            "--browser.gatherUsageStats=false"
        ])
        
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")
    except Exception as e:
        print(f"❌ Error running application: {e}")

def main():
    """Main startup function"""
    print("=" * 60)
    print("🏄‍♂️ SURFING VIDEO ANNOTATION TOOL")
    print("=" * 60)
    print()
    
    # Check requirements
    if not check_requirements():
        sys.exit(1)
    
    # Setup directories
    setup_directories()
    
    # Run application
    run_application()

if __name__ == "__main__":
    main() 