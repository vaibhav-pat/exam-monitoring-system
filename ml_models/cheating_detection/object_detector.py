import torch
import cv2
import numpy as np
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class ObjectDetector:
    def __init__(self, model_path='ml_models/yolov5/yolov5s.pt'):
        """Initialize YOLOv5 object detector"""
        try:
            # Load YOLOv5 model
            self.model = torch.hub.load('ultralytics/yolov5', 'custom', 
                                       path=model_path, force_reload=False)
            self.model.conf = 0.45  # Confidence threshold
            self.model.iou = 0.45   # IOU threshold for NMS
            
            # Classes we're interested in detecting
            self.target_classes = ['cell phone', 'laptop', 'book', 'person']
            
        except Exception as e:
            logger.error(f"Failed to load object detection model: {str(e)}")
            self.model = None
    
    def detect_objects(self, frame):
        """Detect objects in frame"""
        if self.model is None:
            return []
        
        try:
            # Run inference
            results = self.model(frame)
            
            # Parse results
            detections = []
            for *box, conf, cls in results.xyxy[0]:  # xyxy format
                class_name = self.model.names[int(cls)]
                if class_name in self.target_classes:
                    detections.append({
                        'class': class_name,
                        'confidence': float(conf),
                        'bbox': [int(x) for x in box]
                    })
            
            return detections
        
        except Exception as e:
            logger.error(f"Object detection error: {str(e)}")
            return []
    
    def detect_phone(self, frame):
        """Specifically detect cell phones in frame"""
        detections = self.detect_objects(frame)
        phones = [d for d in detections if d['class'] == 'cell phone']
        return phones
    
    def detect_multiple_persons(self, frame):
        """Detect if multiple persons are in frame"""
        detections = self.detect_objects(frame)
        persons = [d for d in detections if d['class'] == 'person']
        return len(persons), persons
