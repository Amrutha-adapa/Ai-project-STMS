import cv2
import numpy as np
import os
import json
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VideoProcessor:
    """Utility class for video processing operations"""
    
    @staticmethod
    def extract_frames(video_path: str, output_dir: str, frame_interval: int = 10) -> List[str]:
        """
        Extract frames from video at specified intervals
        
        Args:
            video_path: Path to input video file
            output_dir: Directory to save extracted frames
            frame_interval: Extract every Nth frame
            
        Returns:
            List of saved frame file paths
        """
        try:
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                raise ValueError(f"Could not open video file: {video_path}")
            
            frame_count = 0
            saved_frames = []
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                if frame_count % frame_interval == 0:
                    frame_filename = f"frame_{frame_count:04d}.jpg"
                    frame_path = os.path.join(output_dir, frame_filename)
                    
                    # Save frame
                    cv2.imwrite(frame_path, frame)
                    saved_frames.append(frame_path)
                    
                    logger.info(f"Saved frame {frame_count} to {frame_path}")
                
                frame_count += 1
            
            cap.release()
            logger.info(f"Extracted {len(saved_frames)} frames from video")
            return saved_frames
            
        except Exception as e:
            logger.error(f"Error extracting frames: {str(e)}")
            return []
    
    @staticmethod
    def draw_lane_dividers(frame: np.ndarray, num_lanes: int = 4) -> np.ndarray:
        """
        Draw lane divider lines on frame
        
        Args:
            frame: Input frame
            num_lanes: Number of lanes to divide
            
        Returns:
            Frame with lane dividers drawn
        """
        height, width = frame.shape[:2]
        lane_width = width // num_lanes
        
        # Draw vertical lines for lane dividers
        for i in range(1, num_lanes):
            x = lane_width * i
            cv2.line(frame, (x, 0), (x, height), (255, 255, 255), 2)
        
        # Add lane labels
        for i in range(num_lanes):
            x = (lane_width * i) + (lane_width // 2)
            y = 30
            lane_label = chr(65 + i)  # A, B, C, D
            cv2.putText(frame, f"Lane {lane_label}", (x-30, y), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        return frame
    
    @staticmethod
    def draw_bounding_boxes(frame: np.ndarray, detections: List[Dict], 
                           lane_counts: Dict[str, int]) -> np.ndarray:
        """
        Draw bounding boxes and labels on frame
        
        Args:
            frame: Input frame
            detections: List of detection dictionaries
            lane_counts: Current vehicle counts per lane
            
        Returns:
            Frame with bounding boxes drawn
        """
        for detection in detections:
            x1, y1, x2, y2 = detection['bbox']
            confidence = detection['confidence']
            vehicle_type = detection['class']
            lane = detection['lane']
            
            # Draw bounding box
            color = (0, 255, 0)  # Green
            cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), color, 2)
            
            # Draw label
            label = f"{vehicle_type} {confidence:.2f}"
            cv2.putText(frame, label, (int(x1), int(y1)-10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        
        # Draw lane counts
        y_offset = 60
        for lane, count in lane_counts.items():
            x = 20
            cv2.putText(frame, f"Lane {lane}: {count} vehicles", (x, y_offset), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            y_offset += 25
        
        return frame

class LaneDetector:
    """Utility class for lane detection and vehicle counting"""
    
    @staticmethod
    def determine_lane(x_coord: float, frame_width: int, num_lanes: int = 4) -> str:
        """
        Determine which lane a vehicle is in based on x-coordinate
        
        Args:
            x_coord: X-coordinate of vehicle
            frame_width: Width of frame
            num_lanes: Number of lanes
            
        Returns:
            Lane identifier (A, B, C, D)
        """
        lane_width = frame_width // num_lanes
        
        if x_coord < lane_width:
            return 'A'
        elif x_coord < lane_width * 2:
            return 'B'
        elif x_coord < lane_width * 3:
            return 'C'
        else:
            return 'D'
    
    @staticmethod
    def count_vehicles_by_lane(detections: List[Dict]) -> Dict[str, int]:
        """
        Count vehicles in each lane
        
        Args:
            detections: List of detection dictionaries
            
        Returns:
            Dictionary with vehicle counts per lane
        """
        lane_counts = {'A': 0, 'B': 0, 'C': 0, 'D': 0}
        
        for detection in detections:
            lane = detection.get('lane', 'A')
            if lane in lane_counts:
                lane_counts[lane] += 1
        
        return lane_counts

class SignalController:
    """Utility class for traffic signal timing calculations"""
    
    @staticmethod
    def calculate_adaptive_timing(vehicle_counts: Dict[str, int]) -> Dict[str, Dict]:
        """
        Calculate adaptive signal timing based on vehicle density
        
        Args:
            vehicle_counts: Vehicle counts per lane
            
        Returns:
            Dictionary with signal states and timing for each lane
        """
        # Find lane with maximum vehicles
        max_lane = max(vehicle_counts, key=vehicle_counts.get)
        max_count = vehicle_counts[max_lane]
        
        # Calculate green time based on density
        if max_count > 15:
            green_time = 30
        elif max_count > 10:
            green_time = 25
        elif max_count > 5:
            green_time = 20
        else:
            green_time = 15
        
        # Set signal states
        signals = {}
        for lane, count in vehicle_counts.items():
            if lane == max_lane:
                signals[lane] = {
                    'count': count,
                    'signal': 'Green',
                    'time': green_time,
                    'priority': 'High'
                }
            else:
                signals[lane] = {
                    'count': count,
                    'signal': 'Red',
                    'time': 15,
                    'priority': 'Low'
                }
        
        return signals
    
    @staticmethod
    def calculate_cycle_time(signals: Dict[str, Dict]) -> int:
        """
        Calculate total cycle time for all signals
        
        Args:
            signals: Signal states dictionary
            
        Returns:
            Total cycle time in seconds
        """
        total_time = 0
        for lane_data in signals.values():
            total_time += lane_data['time']
        
        return total_time
    
    @staticmethod
    def get_next_phase(signals: Dict[str, Dict], current_lane: str) -> Tuple[str, int]:
        """
        Get next phase information
        
        Args:
            signals: Current signal states
            current_lane: Currently active lane
            
        Returns:
            Tuple of (next_lane, time_remaining)
        """
        lanes = list(signals.keys())
        current_index = lanes.index(current_lane)
        next_index = (current_index + 1) % len(lanes)
        next_lane = lanes[next_index]
        
        return next_lane, signals[next_lane]['time']

class DataExporter:
    """Utility class for exporting data and results"""
    
    @staticmethod
    def save_traffic_data(data: Dict, output_path: str) -> bool:
        """
        Save traffic data to JSON file
        
        Args:
            data: Traffic data dictionary
            output_path: Output file path
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Add timestamp
            data['timestamp'] = datetime.now().isoformat()
            data['exported_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Save to file
            with open(output_path, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"Traffic data saved to {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving traffic data: {str(e)}")
            return False
    
    @staticmethod
    def export_video_summary(video_path: str, detections: List[Dict], 
                           lane_counts: Dict[str, int], output_path: str) -> bool:
        """
        Export video processing summary
        
        Args:
            video_path: Path to processed video
            detections: List of detections
            lane_counts: Vehicle counts per lane
            output_path: Output file path
            
        Returns:
            True if successful, False otherwise
        """
        try:
            summary = {
                'video_path': video_path,
                'total_detections': len(detections),
                'lane_counts': lane_counts,
                'vehicle_types': {},
                'processing_summary': {
                    'timestamp': datetime.now().isoformat(),
                    'detection_count': len(detections),
                    'lanes_analyzed': list(lane_counts.keys())
                }
            }
            
            # Count vehicle types
            for detection in detections:
                vehicle_type = detection.get('class', 'unknown')
                summary['vehicle_types'][vehicle_type] = summary['vehicle_types'].get(vehicle_type, 0) + 1
            
            # Save summary
            with open(output_path, 'w') as f:
                json.dump(summary, f, indent=2)
            
            logger.info(f"Video summary exported to {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error exporting video summary: {str(e)}")
            return False

def create_sample_data() -> Dict:
    """Create sample traffic data for testing"""
    return {
        'laneA': {'count': 12, 'signal': 'Green', 'time': 30, 'priority': 'High'},
        'laneB': {'count': 7, 'signal': 'Red', 'time': 15, 'priority': 'Low'},
        'laneC': {'count': 15, 'signal': 'Red', 'time': 15, 'priority': 'Low'},
        'laneD': {'count': 9, 'signal': 'Red', 'time': 15, 'priority': 'Low'},
        'timestamp': datetime.now().isoformat(),
        'cycle_time': 75,
        'total_vehicles': 43
    }
