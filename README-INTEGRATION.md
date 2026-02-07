# 🚦 Smart Traffic Management System - Frontend + Backend Integration

This project integrates a modern HTML frontend with a Flask backend to create a complete Smart Traffic Management System.

## 🏗️ System Architecture

- **Frontend**: HTML + Tailwind CSS + JavaScript (runs on Live Server)
- **Backend**: Flask + Python + YOLO/OpenCV (runs on port 5000)
- **Communication**: RESTful API calls between frontend and backend

## 🚀 Quick Start

### 1. Start the Backend
```bash
cd backend
python app.py
```
The Flask server will start on `http://localhost:5000`

### 2. Open the Frontend
- Open `integrated-frontend.html` in your browser
- Or use Live Server extension in VS Code
- The frontend will automatically try to connect to the backend

### 3. Test the Connection
- Click "Get Started" to enter the dashboard
- Check the "Backend Connection Status" section
- Click "Test Connection" to verify backend connectivity

## 📱 Frontend Features

### 🏠 Home Page
- Landing page with gradient background
- "Get Started" button to enter dashboard

### 📊 Dashboard
- **Overview Tab**: System status and backend connection info
- **Traffic Analysis Tab**: Real-time vehicle counts and charts
- **Vehicle Detection Tab**: Video upload and processing
- **Signal Simulation Tab**: Traffic light control system

### 🔌 Backend Integration
- Automatic connection checking
- Real-time data fetching
- Video upload and processing
- Traffic signal control

## 🎯 Backend API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Backend health check |
| `/traffic_data` | GET | Current traffic data |
| `/process_video` | POST | Upload and process video |
| `/simulate_traffic` | POST | Simulate traffic updates |
| `/reset_signals` | POST | Reset all signals |

## 📹 Video Processing Workflow

1. **Upload Video**: Click upload area and select traffic video
2. **Process Video**: Click "Process Video" button
3. **Backend Processing**: Flask processes video with YOLO/dummy mode
4. **Results Display**: Vehicle counts and signal updates shown
5. **Real-time Updates**: Traffic data refreshes automatically

## 🚦 Traffic Light Control

### Manual Control
- Click individual lane buttons to set specific lanes to green
- Other lanes automatically turn red

### Auto Mode
- Enable auto mode for automatic signal cycling
- Signals change based on simulated traffic density
- Can be disabled at any time

## 🔧 Configuration

### Backend URL
Change the backend URL in `integrated-frontend.html`:
```javascript
const BACKEND_URL = 'http://localhost:5000';
```

### CORS Settings
The backend includes CORS support for frontend integration:
```python
CORS(app)  # Enable CORS for frontend integration
```

## 🧪 Testing

### Test Backend Connection
1. Open the dashboard
2. Check "Backend Connection Status"
3. Click "Test Connection" button

### Test Video Processing
1. Go to "Vehicle Detection" tab
2. Upload a test video file
3. Click "Process Video"
4. Check results and traffic updates

### Test Traffic Simulation
1. Go to "Signal Simulation" tab
2. Click individual lane buttons
3. Enable/disable auto mode
4. Watch real-time signal changes

## 🚨 Troubleshooting

### Frontend Issues
- **Backend not connecting**: Check if Flask server is running on port 5000
- **CORS errors**: Ensure backend CORS is enabled
- **Video upload fails**: Check file size and format

### Backend Issues
- **Port already in use**: Change port in `app.py`
- **YOLO not working**: Check dependencies in `requirements.txt`
- **Memory issues**: Use smaller YOLO model or dummy mode

## 📁 File Structure

```
project/
├── integrated-frontend.html    # Main frontend file
├── backend/                    # Flask backend
│   ├── app.py                 # Main Flask application
│   ├── config.py              # Configuration settings
│   ├── utils.py               # Utility functions
│   ├── requirements.txt       # Python dependencies
│   └── README.md             # Backend documentation
└── README-INTEGRATION.md      # This file
```

## 🌟 Key Benefits

- **Real-time Integration**: Live data flow between frontend and backend
- **Modern UI**: Beautiful, responsive interface with Tailwind CSS
- **AI-Powered**: YOLO vehicle detection with fallback dummy mode
- **Adaptive Control**: Smart traffic signal timing based on vehicle density
- **Easy Testing**: Simple connection testing and debugging tools

## 🚀 Next Steps

1. **Customize UI**: Modify colors, layouts, and styling
2. **Add Features**: Implement more traffic analysis tools
3. **Database Integration**: Add persistent data storage
4. **Real-time Streaming**: Implement WebSocket for live video feeds
5. **Mobile App**: Create React Native or Flutter mobile version

## 🤝 Support

- Check backend logs for detailed error information
- Use browser developer tools for frontend debugging
- Test individual API endpoints with tools like Postman
- Ensure all dependencies are properly installed

---

**Happy coding! 🚦✨**

