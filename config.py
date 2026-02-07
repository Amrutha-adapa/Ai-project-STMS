import os

class Config:
    """Configuration class for the Smart Traffic Management System Backend"""
    
    # Flask Configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DEBUG = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    
    # File Upload Configuration
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100MB max file size
    UPLOAD_FOLDER = 'uploads'
    PROCESSED_FOLDER = 'static/processed'
    ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv', 'webm'}
    
    # YOLO Configuration
    YOLO_MODEL = 'yolov8n.pt'  # Use nano model for speed
    YOLO_CONFIDENCE_THRESHOLD = 0.5
    YOLO_DEVICE = 'cpu'  # Change to 'cuda' if GPU available
    
    # Vehicle Detection Configuration
    VEHICLE_CLASSES = {
        2: 'car',
        3: 'motorcycle', 
        5: 'bus',
        7: 'truck'
    }
    
    # Lane Configuration
    LANES = ['A', 'B', 'C', 'D']
    LANE_COUNT = 4
    
    # Signal Timing Configuration
    BASE_GREEN_TIME = 15  # seconds
    MAX_GREEN_TIME = 30   # seconds
    YELLOW_TIME = 3       # seconds
    RED_TIME = 15         # seconds
    
    # Traffic Density Thresholds
    DENSITY_THRESHOLDS = {
        'low': 5,      # 0-5 vehicles
        'medium': 10,  # 6-10 vehicles  
        'high': 15,    # 11-15 vehicles
        'very_high': 16 # 16+ vehicles
    }
    
    # Video Processing Configuration
    FRAME_SKIP = 10  # Process every Nth frame for performance
    PROCESSING_DELAY = 0.1  # Delay between frames (seconds)
    
    # API Configuration
    API_VERSION = 'v1'
    API_PREFIX = '/api/v1'
    
    # CORS Configuration
    CORS_ORIGINS = [
        'http://localhost:3000',
        'http://localhost:5000',
        'http://127.0.0.1:5000',
        'http://127.0.0.1:3000'
    ]
    
    # Logging Configuration
    LOG_LEVEL = 'INFO'
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Database Configuration (for future use)
    DATABASE_URI = os.environ.get('DATABASE_URI') or 'sqlite:///traffic_system.db'
    
    # Redis Configuration (for future use)
    REDIS_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379'
    
    # Security Configuration
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-key-change-in-production'
    JWT_ACCESS_TOKEN_EXPIRES = 3600  # 1 hour
    
    # Performance Configuration
    MAX_WORKERS = 4
    QUEUE_SIZE = 100
    
    # Monitoring Configuration
    ENABLE_METRICS = True
    METRICS_PORT = 9090
    
    @staticmethod
    def get_signal_timing(vehicle_count):
        """Calculate signal timing based on vehicle count"""
        if vehicle_count <= Config.DENSITY_THRESHOLDS['low']:
            return Config.BASE_GREEN_TIME
        elif vehicle_count <= Config.DENSITY_THRESHOLDS['medium']:
            return 20
        elif vehicle_count <= Config.DENSITY_THRESHOLDS['high']:
            return 25
        else:
            return Config.MAX_GREEN_TIME
    
    @staticmethod
    def get_lane_from_coordinates(x, frame_width):
        """Determine lane from x-coordinate"""
        lane_width = frame_width // Config.LANE_COUNT
        
        if x < lane_width:
            return 'A'
        elif x < lane_width * 2:
            return 'B'
        elif x < lane_width * 3:
            return 'C'
        else:
            return 'D'
