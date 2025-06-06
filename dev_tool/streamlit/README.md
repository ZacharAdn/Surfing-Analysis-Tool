# Surfing Video Annotation Tool (Streamlit Version - BACKUP)

This is the complete backup of the original Streamlit-based annotation tool.

## Status: ✅ COMPLETE & ARCHIVED

This version was fully developed and tested with:
- ✅ 75 tests with 100% pass rate
- ✅ Multi-surfer annotation support
- ✅ JSON/CSV export capabilities
- ✅ Comprehensive feature set

## Why Archived?

This version was replaced due to performance limitations:
- Streamlit's `st.rerun()` caused slow page refreshes during video playback
- Auto-play functionality was not smooth enough for real annotation work
- Native video controls needed for better user experience

## Features (Complete)

- **Video Playback**: Load and navigate through videos
- **Multi-Surfer Annotation**: Track multiple surfers simultaneously
- **Bounding Box Drawing**: Draw and adjust bounding boxes
- **Timeline Visualization**: Visual timeline of annotations
- **Quality Rating**: Rate ride quality for analysis
- **Data Export**: Export in JSON and CSV formats
- **Session Management**: Save and resume sessions

## Setup (If Needed)

```bash
cd dev_tool/streamlit
python -m venv surfing_annotation_env
source surfing_annotation_env/bin/activate
pip install -r requirements.txt
streamlit run annotation_app.py
```

## Test Suite

```bash
# Run all tests
pytest tests/ --cov=. --cov-report=html

# Results: 75/75 tests passing (100%)
# Coverage: 57% overall
```

## Files Structure

```
streamlit/
├── annotation_app.py       # Main Streamlit application
├── video_processor.py      # Video handling
├── annotation_manager.py   # Data management
├── ui_components.py        # UI components
├── tests/                  # Complete test suite
├── .streamlit/             # Configuration
├── requirements.txt        # Dependencies
└── README.md              # This file
```

## Migration Note

All development has moved to the PyQt version in `../pyqt/` for better performance and user experience. 