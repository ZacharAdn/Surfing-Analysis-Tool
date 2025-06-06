# 🏄‍♂️ Surfing Movement Analysis Project

A comprehensive machine learning project for analyzing surfing videos to understand optimal movement patterns and provide actionable feedback for surfer improvement.

## 🎯 Project Overview

This project uses computer vision and machine learning to analyze drone-filmed surfing footage, with the goal of identifying optimal movement patterns and predicting ride success. The system provides actionable feedback to help surfers improve their technique.

**Primary Target:** Predict time on wave (seconds) until fall or wave closure  
**Secondary Metrics:** Movement quality scores, prediction accuracy  
**End Goal:** Actionable feedback application for surfer improvement

## 📋 Development Stages

### 🎬 Stage 1: Data Understanding & EDA + Annotation Tool ✅ **COMPLETED**
- ✅ **Annotation Tool Development**: Complete video player interface with multi-surfer support
- ✅ **Manual Labeling**: Mark start/end times for each surfer's ride
- ✅ **Bounding Box Tool**: Crop relevant areas around each surfer
- ✅ **Data Organization**: Structured annotations for video collection
- ✅ **Basic Analysis**: Ride duration statistics and visual pattern discovery

### 🤖 Stage 2: Baseline Model Development 🔄 **IN PROGRESS**
- **Simple Feature Extraction**: Basic pose detection (center of mass, board angle)
- **Binary Classification**: Predict "successful ride" vs "wipeout" from frames
- **Time-based Labeling**: Use time on wave until fall/closure as success metric
- **Basic ML Models**: Start with Random Forest and Logistic Regression
- **Performance Evaluation**: Establish baseline accuracy metrics

### 🚀 Stage 3: Model Enhancement 📋 **PLANNED**
- **Sequential Modeling**: LSTM/RNN for movement sequences over time
- **Advanced Features**: Body angle changes, weight distribution, timing patterns
- **Movement Prediction**: Predict optimal next movement from current position
- **Performance Optimization**: Fine-tune models for higher accuracy
- **Feature Engineering**: Create more sophisticated movement indicators

### 📱 Stage 4: Simple Application 📋 **PLANNED**
- **Streamlit App**: Upload video → automatic analysis interface
- **Key Outputs**: 
  - Ride duration prediction
  - Movement quality scoring
  - Improvement suggestions
- **Dashboard**: Movement patterns and success correlations visualization
- **User-friendly Interface**: Simple upload and results display

## 🗂️ Project Structure

```
surfing/
├── dev_tool/                    # Stage 1: Video Annotation Tool
│   ├── annotation_app.py        # Main Streamlit application
│   ├── video_processor.py       # Video handling and frame extraction
│   ├── annotation_manager.py    # Annotation data management
│   ├── ui_components.py         # UI helper components
│   ├── tests/                   # Comprehensive test suite (75 tests)
│   ├── .streamlit/              # Configuration files
│   └── requirements.txt         # Dependencies
├── data/                        # Video data and annotations
│   ├── videos/                  # Raw surfing footage
│   ├── annotations/             # Manual annotations (JSON)
│   └── exports/                 # Processed data (CSV)
├── models/                      # ML models and training scripts (Stage 2+)
├── analysis/                    # Data analysis notebooks and scripts
├── specs/                       # Project specifications and documentation
└── README.md                    # This file
```

## 🚀 Quick Start

### Stage 1: Video Annotation Tool

1. **Setup Environment:**
   ```bash
   cd dev_tool
   python -m venv surfing_annotation_env
   source surfing_annotation_env/bin/activate  # Windows: surfing_annotation_env\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Run Annotation Tool:**
   ```bash
   streamlit run annotation_app.py
   ```

3. **Access Application:**
   Open `http://localhost:8501` in your browser

### Video Annotation Workflow

1. **Upload Video**: Support for MP4, MOV, AVI, MKV files (up to 1.5GB)
2. **Add Surfers**: Track multiple surfers simultaneously
3. **Mark Ride Times**: Precise start/end time marking
4. **Draw Bounding Boxes**: Define surfer locations in frames
5. **Rate Quality**: Assess ride quality (poor, average, good, excellent)
6. **Export Data**: Save annotations in JSON/CSV formats

## 🛠️ Technical Features

### Annotation Tool (Stage 1)
- **Multi-surfer Support**: Track up to 5+ surfers simultaneously
- **Precise Navigation**: ±0.1 second accuracy with timeline scrubbing
- **Enhanced Controls**: Frame-by-frame navigation and quick jumps
- **Data Export**: JSON and CSV formats for analysis
- **Session Management**: Save and resume annotation work
- **Large File Support**: Handle videos up to 1.5GB

### Testing & Quality
- **75 Test Suite**: 100% passing rate
- **Coverage**: 57% code coverage with detailed reports
- **CI/CD Ready**: Comprehensive testing framework
- **Performance Tested**: Large file and multi-surfer scenarios

## 📊 Data Pipeline

### Input Data
- **Video Format**: Drone-filmed surfing footage
- **Supported Codecs**: H.264, H.265, VP9
- **Resolution**: 1080p+ recommended for optimal analysis
- **Frame Rate**: 30+ FPS for smooth motion analysis

### Annotation Schema
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

### Output Formats
- **JSON**: Complete annotation data with metadata
- **CSV**: Tabular format for statistical analysis
- **Video Clips**: Extracted surfer segments (Stage 2+)

## 🔬 Machine Learning Pipeline (Stages 2-4)

### Feature Extraction
- **Pose Detection**: MediaPipe/OpenPose integration
- **Movement Tracking**: Optical flow analysis
- **Board Dynamics**: Angle and position tracking
- **Environmental Factors**: Wave characteristics

### Model Architecture
- **Baseline Models**: Random Forest, Logistic Regression
- **Sequential Models**: LSTM/RNN for temporal patterns
- **Computer Vision**: CNN for visual feature extraction
- **Ensemble Methods**: Combine multiple model outputs

### Performance Metrics
- **Regression**: Time on wave prediction (RMSE, MAE)
- **Classification**: Ride success prediction (Accuracy, F1)
- **Quality Scoring**: Movement assessment (Custom metrics)

## 🎯 Success Criteria

### Stage 1 (Completed) ✅
- [x] Functional annotation tool with multi-surfer support
- [x] 100% test pass rate with comprehensive coverage
- [x] Export capabilities for downstream analysis
- [x] User-friendly interface for manual labeling

### Stage 2 (Target)
- [ ] Baseline model with >70% accuracy for ride success prediction
- [ ] Feature extraction pipeline for pose and movement data
- [ ] Performance benchmarking against manual annotations

### Stage 3 (Target)
- [ ] Advanced sequential models with >80% accuracy
- [ ] Real-time movement prediction capabilities
- [ ] Comprehensive feature engineering pipeline

### Stage 4 (Target)
- [ ] End-to-end application with video upload → analysis
- [ ] User dashboard with actionable insights
- [ ] Performance optimization for real-time feedback

## 🛡️ Configuration & Security

### Upload Limits
- **Default**: 200MB (Streamlit default)
- **Configured**: 1.5GB via `.streamlit/config.toml`
- **Recommendation**: Use video compression for files >1GB

### Privacy & Data
- **Local Processing**: All data remains on your machine
- **No Cloud Dependencies**: Complete offline operation
- **Data Ownership**: Full control over video and annotation data

## 📚 Dependencies

### Core Libraries
```
streamlit>=1.28.0
opencv-python>=4.8.0
numpy>=1.24.0
pandas>=2.0.0
```

### Development Tools
```
pytest>=7.0.0
pytest-cov>=4.0.0
black>=23.0.0
flake8>=6.0.0
```

### Future ML Stack (Stages 2+)
```
scikit-learn>=1.3.0
tensorflow>=2.13.0
mediapipe>=0.10.0
torch>=2.0.0
```

## 🤝 Contributing

1. **Fork the repository**
2. **Create feature branch**: `git checkout -b feature/your-feature`
3. **Add tests**: Ensure new functionality is tested
4. **Run test suite**: `pytest tests/ --cov=.`
5. **Submit pull request**: Include description of changes

### Development Setup
```bash
git clone https://github.com/ZacharAdn/Surfing-Analysis-Tool.git
cd Surfing-Analysis-Tool
python -m venv venv
source venv/bin/activate
pip install -r dev_tool/requirements.txt
```

## 📈 Roadmap

### Near Term (Q1 2025)
- [ ] Complete Stage 2: Baseline ML models
- [ ] Implement pose detection pipeline
- [ ] Create feature extraction framework

### Medium Term (Q2 2025)
- [ ] Advanced sequential modeling (Stage 3)
- [ ] Real-time analysis capabilities
- [ ] Performance optimization

### Long Term (Q3-Q4 2025)
- [ ] Complete end-to-end application (Stage 4)
- [ ] Mobile application development
- [ ] Commercial deployment readiness

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Surfing Community**: For providing domain expertise and testing feedback
- **Open Source Libraries**: Streamlit, OpenCV, and the broader Python ecosystem
- **Research Community**: Computer vision and sports analytics researchers

---

**Built with ❤️ for the surfing community** 🏄‍♂️🌊 