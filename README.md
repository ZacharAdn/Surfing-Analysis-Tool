# 🏄‍♂️ Surfing Video Annotation Tool

A comprehensive tool for annotating surfing videos with multiple surfer tracking and analysis capabilities.

## Features

- **Video Playback**: Load and navigate through surfing videos with frame-by-frame control
- **Multi-Surfer Annotation**: Track multiple surfers simultaneously with unique IDs
- **Bounding Box Drawing**: Draw and adjust bounding boxes around surfers
- **Timeline Visualization**: Visual timeline showing all surfer annotations
- **Quality Rating**: Rate ride quality for analysis
- **Data Export**: Export annotations in JSON and CSV formats
- **Session Management**: Save and resume annotation sessions

## Installation

1. **Create Virtual Environment** (recommended):
```bash
python -m venv surfing_annotation_env
source surfing_annotation_env/bin/activate  # On Windows: surfing_annotation_env\Scripts\activate
```

2. **Install Dependencies**:
```bash
cd dev_tool
pip install -r requirements.txt
```

## Usage

### Starting the Application

```bash
python run_annotation_tool.py
```

The application will open in your web browser at `http://localhost:8501`

### Basic Workflow

1. **Load Video**: Upload your surfing video file (MP4, MOV, AVI, MKV)
2. **Add Surfers**: Click "Add Surfer" to create new surfer annotations
3. **Mark Ride Start**: Select a surfer and click "Mark Start" at the beginning of a ride
4. **Mark Ride End**: Click "Mark End" when the ride finishes (fall or wave closure)
5. **Set Quality**: Rate the ride quality (poor, average, good, excellent)
6. **Save Annotations**: Export your work to JSON or CSV format

### Navigation Controls

- **Previous/Next Frame**: Navigate frame-by-frame through the video
- **Timeline Slider**: Jump to any point in the video
- **Surfer Selection**: Choose which surfer to annotate

### Keyboard Shortcuts

- **Space**: Play/Pause (when implemented)
- **Arrow Keys**: Frame navigation
- **Number Keys**: Quick surfer selection
- **Ctrl+S**: Save annotations

## File Structure

```
dev_tool/
├── annotation_app.py          # Main Streamlit application
├── video_processor.py         # Video handling and frame extraction
├── annotation_manager.py      # Annotation data management
├── ui_components.py          # UI helper components
├── requirements.txt          # Python dependencies
├── run_annotation_tool.py    # Startup script
└── README.md                # This file

data/                         # Place your video files here
output/                      # Exported annotations
annotations/                 # Saved annotation sessions
temp/                       # Temporary files
```

## Output Format

### JSON Format
```json
{
  "video_file": "session_001.mp4",
  "duration": 120.5,
  "fps": 30.0,
  "surfers": [
    {
      "id": 1,
      "start_time": 10.2,
      "end_time": 25.8,
      "duration": 15.6,
      "bbox": [100, 150, 200, 300],
      "quality": "good",
      "created": "2024-01-01T12:00:00"
    }
  ]
}
```

### CSV Format
Includes columns: video_file, surfer_id, start_time, end_time, duration, bbox coordinates, quality, created timestamp

## Supported Video Formats

- MP4
- MOV
- AVI
- MKV
- WMV

## Requirements

- Python 3.8+
- OpenCV
- Streamlit
- NumPy
- Pandas

## Troubleshooting

### Common Issues

1. **Video won't load**: Check that the video format is supported and the file isn't corrupted
2. **Missing dependencies**: Run `pip install -r requirements.txt`
3. **Port already in use**: The application uses port 8501 by default

### Performance Tips

- For large video files (>100MB), be patient during initial loading
- Close other browser tabs to free up memory
- Save your work frequently to avoid data loss

## Development

The tool is built with modular components:

- `VideoProcessor`: Handles video operations
- `AnnotationManager`: Manages surfer data and validation
- `UI Components`: Streamlit interface elements

## Future Enhancements

- Real-time video playback
- Automatic surfer detection
- Advanced bounding box tracking
- Batch processing for multiple videos
- Integration with machine learning models

## Support

For issues or questions, please refer to the project documentation or create an issue in the project repository.

## Configuration

### Video Upload Limits
- **Default**: 200MB (Streamlit default)
- **Configured**: 1GB (via .streamlit/config.toml)
- **Large Files**: For files >1GB, consider video compression

### Performance Optimization
- For large video files (>100MB), be patient during initial loading
- Close other browser tabs to free up memory
- Consider reducing video resolution for smoother performance

## Testing

### Running Tests
```bash
# Run all tests
python -m pytest tests/

# Run with coverage
python -m pytest tests/ --cov=. --cov-report=html --cov-report=term-missing

# View coverage report
open htmlcov/index.html
```

### Test Coverage Status
- **Total Tests**: 75 tests (100% passing)
- **Coverage**: 57% overall
  - Tests: 95-99% coverage
  - Main application files: Need more integration testing
- **Coverage Report**: Available in `htmlcov/` directory

### Test Categories
- **Unit Tests**: Individual component testing
- **Integration Tests**: Component interaction testing  
- **User Acceptance Tests**: End-to-end workflow testing
- **Performance Tests**: Large file and multi-surfer scenarios

## Development

### Project Structure
```
dev_tool/
├── annotation_app.py       # Main Streamlit application
├── video_processor.py      # Video handling and frame extraction
├── annotation_manager.py   # Annotation data management
├── ui_components.py        # Reusable UI components
├── tests/                  # Comprehensive test suite
│   ├── test_video_upload_playback.py
│   ├── test_data_management.py
│   ├── test_integration.py
│   └── ...
└── .streamlit/
    └── config.toml         # Streamlit configuration
```

### Adding Tests
Tests are organized by functionality. To add new tests:
1. Create test file in `tests/` directory
2. Follow naming convention: `test_[feature].py`
3. Use pytest fixtures and mocks appropriately
4. Run coverage to ensure new code is tested

## API Reference

### AnnotationManager
- `add_surfer(start_time)`: Add new surfer
- `set_surfer_bbox(surfer_id, bbox)`: Set bounding box
- `export_to_csv()`: Export annotations to CSV

### VideoProcessor  
- `load_video(path)`: Load video file
- `get_frame_at_time(timestamp)`: Extract frame at time
- `get_video_info()`: Get video metadata

## Troubleshooting

### Common Issues
1. **Video won't load**: Check file format (MP4, MOV, AVI, MKV supported)
2. **Upload fails**: Check file size limit (max 1GB with current config)
3. **Performance issues**: Close other applications, use smaller video files
4. **Save fails**: Ensure proper write permissions for data directories

### Error Messages
- `"Unsupported video format"`: Use supported video formats
- `"Cannot open video file"`: Check file corruption or codec issues
- `"File too large"`: Increase upload limit in config.toml or compress video

## Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature-name`
3. Add tests for new functionality
4. Ensure all tests pass: `pytest tests/`
5. Check coverage: `pytest --cov=.`
6. Submit pull request

## License

This project is licensed under the MIT License. 