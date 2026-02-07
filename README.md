# 🚦 Smart Traffic Management System - Backend

A Flask-based backend system for intelligent traffic management using YOLO object detection and adaptive signal timing.

## 🏗️ Architecture

- **Flask Server**: RESTful API endpoints for video processing and traffic management
- **YOLO Integration**: Real-time vehicle detection using YOLOv8
- **Adaptive Signal Control**: Dynamic traffic light timing based on vehicle density
- **Dummy Mode**: Fallback mode when YOLO is not available (beginner-friendly)

## 🚀 Features

### Core Functionality
- ✅ Video upload and processing
- ✅ Vehicle detection and classification
- ✅ Lane-based vehicle counting
- ✅ Adaptive traffic signal timing
- ✅ Real-time processing status
- ✅ Processed frame streaming

### API Endpoints
- `POST /process_video` - Upload and process traffic videos
- `GET /traffic_data` - Get current traffic data
- `GET /processing_status` - Get video processing status
- `GET /health` - Health check and system status
- `POST /simulate_traffic` - Simulate traffic data updates
- `POST /reset_signals` - Reset all signals to default

## 📁 Project Structure

```
backend/
├── app.py              # Main Flask application
├── config.py           # Configuration settings
├── utils.py            # Utility functions and classes
├── requirements.txt    # Python dependencies
├── README.md          # This file
├── models/            # YOLO model files (auto-downloaded)
├── static/            # Static files and processed frames
│   └── processed/     # Processed video frames
├── uploads/           # Temporary video uploads
└── logs/              # Application logs
```

## 🛠️ Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager
- 4GB+ RAM (8GB+ recommended for YOLO)

### Step 1: Clone and Setup
```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### Step 2: Install Dependencies
```bash
# Install required packages
pip install -r requirements.txt
```

### Step 3: Run the Application
```bash
# Start Flask server
python app.py
```

The server will start on `http://localhost:5000`

## 🔧 Configuration

### Environment Variables
```bash
# Optional: Set custom configuration
export FLASK_DEBUG=True
export SECRET_KEY=your-secret-key
export YOLO_DEVICE=cuda  # Use GPU if available
```

### Configuration File
Edit `config.py` to customize:
- Signal timing parameters
- Vehicle detection thresholds
- File upload limits
- CORS origins

## 📡 API Documentation

### 1. Process Video
**Endpoint:** `POST /process_video`

**Request:**
- Content-Type: `multipart/form-data`
- Body: `video` file (mp4, avi, mov, mkv)

**Response:**
```json
{
  "success": true,
  "vehicle_counts": {
    "laneA": 12,
    "laneB": 7,
    "laneC": 15,
    "laneD": 9
  },
  "signals": {
    "laneA": {
      "count": 12,
      "signal": "Green",
      "time": 30
    },
    "laneB": {
      "count": 7,
      "signal": "Red",
      "time": 15
    }
  },
  "processed_frames": 150,
  "message": "Video processed successfully"
}
```

### 2. Get Traffic Data
**Endpoint:** `GET /traffic_data`

**Response:**
```json
{
  "success": true,
  "data": {
    "laneA": {"count": 12, "signal": "Green", "time": 30},
    "laneB": {"count": 7, "signal": "Red", "time": 15},
    "laneC": {"count": 15, "signal": "Red", "time": 15},
    "laneD": {"count": 9, "signal": "Red", "time": 15}
  },
  "timestamp": "2024-01-15T10:30:00"
}
```

### 3. Processing Status
**Endpoint:** `GET /processing_status`

**Response:**
```json
{
  "status": "processing",
  "progress": 45
}
```

## 🎯 Usage Examples

### Python Client Example
```python
import requests

# Upload video for processing
with open('traffic_video.mp4', 'rb') as video_file:
    files = {'video': video_file}
    response = requests.post('http://localhost:5000/process_video', files=files)
    
    if response.status_code == 200:
        result = response.json()
        print(f"Processed {result['processed_frames']} frames")
        print(f"Vehicle counts: {result['vehicle_counts']}")

# Get current traffic data
response = requests.get('http://localhost:5000/traffic_data')
traffic_data = response.json()['data']
print(f"Lane A: {traffic_data['laneA']['count']} vehicles")
```

### JavaScript/Frontend Example
```javascript
// Upload video
const formData = new FormData();
formData.append('video', videoFile);

fetch('http://localhost:5000/process_video', {
    method: 'POST',
    body: formData
})
.then(response => response.json())
.then(data => {
    console.log('Processing result:', data);
    updateTrafficDisplay(data.signals);
});

// Get real-time traffic data
setInterval(() => {
    fetch('http://localhost:5000/traffic_data')
        .then(response => response.json())
        .then(data => {
            updateTrafficLights(data.data);
        });
}, 5000);
```

## 🔍 YOLO Integration

### Model Download
The system automatically downloads YOLOv8n (nano) model on first run:
- **Model**: `yolov8n.pt` (6.7 MB)
- **Speed**: ~10-15 FPS on CPU, ~30+ FPS on GPU
- **Accuracy**: Good for real-time traffic monitoring

### Vehicle Classes Detected
- **Car** (class 2)
- **Motorcycle** (class 3)
- **Bus** (class 5)
- **Truck** (class 7)

### Customization
```python
# In app.py, change model size:
model = YOLO('yolov8s.pt')  # Small model (22 MB)
model = YOLO('yolov8m.pt')  # Medium model (52 MB)
model = YOLO('yolov8l.pt')  # Large model (87 MB)
model = YOLO('yolov8x.pt')  # Extra large model (136 MB)
```

## 🎮 Dummy Mode

When YOLO is not available, the system automatically switches to dummy mode:
- Generates realistic random vehicle counts
- Simulates processing time
- Maintains API compatibility
- Perfect for testing and development

### Enable Dummy Mode
```python
# Force dummy mode by commenting out YOLO import
# from ultralytics import YOLO
YOLO_AVAILABLE = False
```

## 📊 Signal Timing Logic

### Adaptive Timing Algorithm
1. **Count vehicles** in each lane
2. **Identify highest density** lane
3. **Calculate green time** based on density:
   - 0-5 vehicles: 15 seconds
   - 6-10 vehicles: 20 seconds
   - 11-15 vehicles: 25 seconds
   - 16+ vehicles: 30 seconds
4. **Set other lanes** to red with base timing

### Example Response
```json
{
  "laneA": {"count": 18, "signal": "Green", "time": 30},
  "laneB": {"count": 7, "signal": "Red", "time": 15},
  "laneC": {"count": 12, "signal": "Red", "time": 15},
  "laneD": {"count": 5, "signal": "Red", "time": 15}
}
```

## 🚨 Error Handling

### Common Errors
- **File too large**: Increase `MAX_CONTENT_LENGTH` in config
- **Invalid file type**: Check `ALLOWED_EXTENSIONS`
- **YOLO model not found**: Check internet connection for auto-download
- **Memory issues**: Reduce frame processing or use smaller YOLO model

### Error Response Format
```json
{
  "success": false,
  "error": "Error description",
  "message": "User-friendly message"
}
```

## 🔧 Development

### Running in Development Mode
```bash
export FLASK_DEBUG=True
export FLASK_ENV=development
python app.py
```

### Testing Endpoints
```bash
# Health check
curl http://localhost:5000/health

# Get traffic data
curl http://localhost:5000/traffic_data

# Simulate traffic update
curl -X POST http://localhost:5000/simulate_traffic \
  -H "Content-Type: application/json" \
  -d '{"lane": "A", "count": 15}'
```

### Logging
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🚀 Deployment

### Production Setup
```bash
# Install production dependencies
pip install gunicorn

# Run with Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app

# Or with systemd service
sudo systemctl start traffic-management
```

### Docker Deployment
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

## 📈 Performance

### Benchmarks (CPU: Intel i7-8700K)
- **YOLOv8n**: ~12 FPS, ~2GB RAM
- **YOLOv8s**: ~8 FPS, ~3GB RAM
- **YOLOv8m**: ~5 FPS, ~4GB RAM

### Optimization Tips
1. **Use GPU** if available (CUDA)
2. **Process every Nth frame** (adjust `FRAME_SKIP`)
3. **Reduce video resolution** before upload
4. **Use smaller YOLO model** for speed

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

### Common Issues
- **Import errors**: Check Python version and dependencies
- **CUDA errors**: Install PyTorch with CUDA support
- **Memory errors**: Reduce batch size or use smaller model

### Getting Help
- Check the logs in console output
- Verify all dependencies are installed
- Test with dummy mode first
- Check file permissions for uploads/processed folders

---

**Happy coding! 🚦✨**
