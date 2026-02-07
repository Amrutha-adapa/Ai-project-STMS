from flask import Flask, request, jsonify, send_file, Response
from flask_cors import CORS
import os
import cv2
import numpy as np
import json
import time
from datetime import datetime
import random
from werkzeug.utils import secure_filename
import threading
import queue

# Import YOLO (optional - will use dummy mode if not available)
try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False
    print("YOLO not available, using dummy mode")

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend integration

# Configuration
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['PROCESSED_FOLDER'] = 'static/processed'
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max file size
app.config['ALLOWED_EXTENSIONS'] = {'mp4', 'avi', 'mov', 'mkv'}

# Create directories if they don't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['PROCESSED_FOLDER'], exist_ok=True)

# Global variables for video processing
current_video_data = {
    'laneA': {'count': 0, 'signal': 'Red', 'time': 15},
    'laneB': {'count': 0, 'signal': 'Red', 'time': 15},
    'laneC': {'count': 0, 'signal': 'Red', 'time': 15},
    'laneD': {'count': 0, 'signal': 'Red', 'time': 15}
}

# Video processing queue
video_queue = queue.Queue()
processing_status = {'status': 'idle', 'progress': 0}

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def calculate_signal_timing(vehicle_counts):
    """Calculate adaptive signal timing based on vehicle density"""
    max_count = max(vehicle_counts.values())
    max_lane = max(vehicle_counts, key=vehicle_counts.get)
    
    # Base timing
    base_green_time = 15
    max_green_time = 30
    
    # Calculate timing based on density
    if max_count > 15:
        green_time = max_green_time
    elif max_count > 10:
        green_time = 25
    elif max_count > 5:
        green_time = 20
    else:
        green_time = base_green_time
    
    # Update signal states
    signals = {}
    for lane, count in vehicle_counts.items():
        if lane == max_lane:
            signals[lane] = {
                'count': count,
                'signal': 'Green',
                'time': green_time
            }
        else:
            signals[lane] = {
                'count': count,
                'signal': 'Red',
                'time': base_green_time
            }
    
    return signals

def process_video_yolo(video_path):
    """Process video using YOLO model"""
    if not YOLO_AVAILABLE:
        return process_video_dummy(video_path)
    
    try:
        # Load YOLO model
        model = YOLO('yolov8n.pt')  # Use nano model for speed
        
        # Open video
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise Exception("Could not open video file")
        
        frame_count = 0
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        vehicle_counts = {'laneA': 0, 'laneB': 0, 'laneC': 0, 'laneD': 0}
        
        # Process frames
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Update progress
            frame_count += 1
            processing_status['progress'] = int((frame_count / total_frames) * 100)
            
            # Run YOLO detection
            results = model(frame)
            
            # Process detections
            for result in results:
                boxes = result.boxes
                if boxes is not None:
                    for box in boxes:
                        # Get detection info
                        cls = int(box.cls[0])
                        conf = float(box.conf[0])
                        
                        # Filter for vehicles (car, truck, bus, motorcycle)
                        if cls in [2, 3, 5, 7] and conf > 0.5:  # COCO classes
                            # Get bounding box coordinates
                            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                            
                            # Determine lane based on x-coordinate
                            frame_width = frame.shape[1]
                            lane_width = frame_width // 4
                            
                            if x1 < lane_width:
                                vehicle_counts['laneA'] += 1
                            elif x1 < lane_width * 2:
                                vehicle_counts['laneB'] += 1
                            elif x1 < lane_width * 3:
                                vehicle_counts['laneC'] += 1
                            else:
                                vehicle_counts['laneD'] += 1
                            
                            # Draw bounding box
                            cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
                            cv2.putText(frame, f'Vehicle {conf:.2f}', (int(x1), int(y1)-10), 
                                      cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            
            # Add lane dividers
            for i in range(1, 4):
                x = (frame_width // 4) * i
                cv2.line(frame, (x, 0), (x, frame.shape[0]), (255, 255, 255), 2)
            
            # Save processed frame
            processed_path = os.path.join(app.config['PROCESSED_FOLDER'], f'frame_{frame_count:04d}.jpg')
            cv2.imwrite(processed_path, frame)
            
            # Limit processing for demo (process every 10th frame)
            if frame_count % 10 == 0:
                time.sleep(0.1)  # Small delay to prevent overwhelming
        
        cap.release()
        
        # Calculate signal timing
        signals = calculate_signal_timing(vehicle_counts)
        
        return {
            'success': True,
            'vehicle_counts': vehicle_counts,
            'signals': signals,
            'processed_frames': frame_count,
            'message': 'Video processed successfully with YOLO'
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'message': 'Error processing video with YOLO, falling back to dummy mode'
        }

def process_video_dummy(video_path):
    """Process video using dummy data (for when YOLO is not available)"""
    try:
        # Simulate video processing
        processing_status['progress'] = 0
        
        # Generate random vehicle counts
        vehicle_counts = {
            'laneA': random.randint(8, 20),
            'laneB': random.randint(5, 15),
            'laneC': random.randint(6, 18),
            'laneD': random.randint(4, 16)
        }
        
        # Simulate processing time
        for i in range(10):
            processing_status['progress'] = (i + 1) * 10
            time.sleep(0.2)
        
        # Calculate signal timing
        signals = calculate_signal_timing(vehicle_counts)
        
        return {
            'success': True,
            'vehicle_counts': vehicle_counts,
            'signals': signals,
            'processed_frames': 0,
            'message': 'Video processed in dummy mode (random data)'
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'message': 'Error in dummy mode processing'
        }

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'yolo_available': YOLO_AVAILABLE,
        'mode': 'YOLO' if YOLO_AVAILABLE else 'Dummy'
    })

@app.route('/upload', methods=['POST'])
def upload_video():
    """Simple upload endpoint that saves video and returns success"""
    try:
        # Check if video file was uploaded
        if 'video' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No video file provided'
            }), 400
        
        file = request.files['video']
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No file selected'
            }), 400
        
        if file and allowed_file(file.filename):
            # Secure filename and save
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{timestamp}_{filename}"
            video_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(video_path)
            
            return jsonify({
                'success': True,
                'message': 'Video uploaded successfully',
                'filename': filename
            })
        
        else:
            return jsonify({
                'success': False,
                'error': 'Invalid file type. Allowed: mp4, avi, mov, mkv'
            }), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Error uploading video'
        }), 500

@app.route('/process_video', methods=['POST'])
def process_video():
    """Main endpoint for video processing"""
    try:
        # Check if video file was uploaded
        if 'video' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No video file provided'
            }), 400
        
        file = request.files['video']
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No file selected'
            }), 400
        
        if file and allowed_file(file.filename):
            # Secure filename and save
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{timestamp}_{filename}"
            video_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(video_path)
            
            # Update processing status
            processing_status['status'] = 'processing'
            processing_status['progress'] = 0
            
            # Process video
            if YOLO_AVAILABLE:
                result = process_video_yolo(video_path)
            else:
                result = process_video_dummy(video_path)
            
            # Update global data
            if result['success']:
                global current_video_data
                current_video_data = result['signals']
            
            # Update processing status
            processing_status['status'] = 'completed'
            processing_status['progress'] = 100
            
            # Clean up uploaded file
            if os.path.exists(video_path):
                os.remove(video_path)
            
            return jsonify(result)
        
        else:
            return jsonify({
                'success': False,
                'error': 'Invalid file type. Allowed: mp4, avi, mov, mkv'
            }), 400
            
    except Exception as e:
        processing_status['status'] = 'error'
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Error processing video'
        }), 500

@app.route('/traffic_data', methods=['GET'])
def get_traffic_data():
    """Get current traffic data and signal states"""
    return jsonify({
        'success': True,
        'data': current_video_data,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/processing_status', methods=['GET'])
def get_processing_status():
    """Get current video processing status"""
    return jsonify(processing_status)

@app.route('/video_feed/<filename>')
def video_feed(filename):
    """Serve processed video frames"""
    try:
        file_path = os.path.join(app.config['PROCESSED_FOLDER'], filename)
        if os.path.exists(file_path):
            return send_file(file_path, mimetype='image/jpeg')
        else:
            return jsonify({'error': 'Frame not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/simulate_traffic', methods=['POST'])
def simulate_traffic():
    """Simulate traffic data updates (for testing)"""
    try:
        data = request.get_json()
        lane = data.get('lane', 'A')
        count = data.get('count', random.randint(5, 20))
        
        # Update the specified lane
        if f'lane{lane}' in current_video_data:
            current_video_data[f'lane{lane}']['count'] = count
            
            # Recalculate signal timing
            vehicle_counts = {lane: data['count'] for lane, data in current_video_data.items()}
            signals = calculate_signal_timing(vehicle_counts)
            current_video_data.update(signals)
            
            return jsonify({
                'success': True,
                'message': f'Updated lane {lane} with count {count}',
                'data': current_video_data
            })
        else:
            return jsonify({
                'success': False,
                'error': f'Invalid lane: {lane}'
            }), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/reset_signals', methods=['POST'])
def reset_signals():
    """Reset all signals to default state"""
    global current_video_data
    current_video_data = {
        'laneA': {'count': 0, 'signal': 'Red', 'time': 15},
        'laneB': {'count': 0, 'signal': 'Red', 'time': 15},
        'laneC': {'count': 0, 'signal': 'Red', 'time': 15},
        'laneD': {'count': 0, 'signal': 'Red', 'time': 15}
    }
    
    return jsonify({
        'success': True,
        'message': 'Signals reset to default state',
        'data': current_video_data
    })

@app.route('/get_processed_frames', methods=['GET'])
def get_processed_frames():
    """Get list of processed video frames"""
    try:
        frames = []
        processed_dir = app.config['PROCESSED_FOLDER']
        
        if os.path.exists(processed_dir):
            for filename in os.listdir(processed_dir):
                if filename.endswith('.jpg'):
                    frames.append({
                        'filename': filename,
                        'url': f'/video_feed/{filename}',
                        'size': os.path.getsize(os.path.join(processed_dir, filename))
                    })
        
        return jsonify({
            'success': True,
            'frames': frames,
            'count': len(frames)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    print("🚦 Smart Traffic Management System Backend")
    print(f"YOLO Available: {YOLO_AVAILABLE}")
    print(f"Mode: {'YOLO' if YOLO_AVAILABLE else 'Dummy'}")
    print("Starting Flask server...")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
