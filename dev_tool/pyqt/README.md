# Surfing Video Annotation Tool (PyQt Version)

Native desktop application for annotating surfing videos with multi-surfer support and real-time playback.

## Features
- Smooth video playback with frame-by-frame navigation
- Multi-surfer tracking and annotation
- Bounding box drawing with mouse controls
- Quality rating system
- JSON/CSV export capabilities

## Directory Structure
```
pyqt/
├── src/              # Source code
├── tests/            # Test files
└── data/             # Data directory
    ├── videos/       # Video files
    ├── annotations/  # JSON annotations
    └── exports/      # CSV exports
```

## Requirements
- Python 3.8+
- PyQt6
- OpenCV
- NumPy
- Pandas

## Setup
```bash
# Create virtual environment
python -m venv surfing_annotation_env
source surfing_annotation_env/bin/activate  # Windows: surfing_annotation_env\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Usage
```bash
python src/main.py
```
