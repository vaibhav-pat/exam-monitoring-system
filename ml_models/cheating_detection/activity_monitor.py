import cv2
import numpy as np
from datetime import datetime, timedelta
import json
import logging
from collections import deque

logger = logging.getLogger(__name__)

class ActivityMonitor:
    def __init__(self, config):
        """Initialize activity monitor with configuration"""
        self.config = config
        
        # Initialize detectors
        from .face_detector import FaceDetector
        from .object_detector import ObjectDetector
        from .audio_analyzer import AudioAnalyzer
        
        self.face_detector = FaceDetector(method='mtcnn')
        self.object_detector = ObjectDetector()
        self.audio_analyzer = AudioAnalyzer()
        
        # Activity tracking
        self.activity_history = deque(maxlen=100)
        self.last_face_count = 0
        self.absence_start_time = None
        self.suspicious_activities = []
        
        # Frame buffer for saving evidence
        self.frame_buffer = deque(maxlen=10)
    
    def analyze_frame(self, frame, audio_data=None):
        """Analyze a single frame for suspicious activities"""
        timestamp = datetime.now()
        activities = []
        
        # Face detection
        faces = self.face_detector.detect_faces(frame)
        face_count = len(faces)
        
        # Check for multiple faces
        if face_count > 1:
            activities.append({
                'type': 'multiple_faces',
                'confidence': 0.9,
                'details': f'{face_count} faces detected',
                'timestamp': timestamp
            })
        
        # Check for absence
        if face_count == 0:
            if self.absence_start_time is None:
                self.absence_start_time = timestamp
            elif (timestamp - self.absence_start_time).seconds > self.config['ABSENCE_DURATION_THRESHOLD']:
                activities.append({
                    'type': 'student_absent',
                    'confidence': 0.95,
                    'details': f'Absent for {(timestamp - self.absence_start_time).seconds} seconds',
                    'timestamp': timestamp
                })
        else:
            self.absence_start_time = None
        
        # Object detection
        objects = self.object_detector.detect_objects(frame)
        
        # Check for phone
        phones = [obj for obj in objects if obj['class'] == 'cell phone']
        if phones:
            activities.append({
                'type': 'phone_detected',
                'confidence': max(p['confidence'] for p in phones),
                'details': f'{len(phones)} phone(s) detected',
                'timestamp': timestamp
            })
        
        # Check for unauthorized materials
        books = [obj for obj in objects if obj['class'] == 'book']
        if books:
            activities.append({
                'type': 'unauthorized_material',
                'confidence': max(b['confidence'] for b in books),
                'details': 'Book or notes detected',
                'timestamp': timestamp
            })
        
        # Audio analysis
        if audio_data is not None:
            is_voice = self.audio_analyzer.detect_voice_activity(audio_data)
            is_anomaly, anomaly_conf = self.audio_analyzer.detect_anomaly(audio_data)
            
            if is_voice:
                activities.append({
                    'type': 'voice_detected',
                    'confidence': 0.8,
                    'details': 'Voice activity detected',
                    'timestamp': timestamp
                })
            
            if is_anomaly:
                activities.append({
                    'type': 'audio_anomaly',
                    'confidence': anomaly_conf,
                    'details': 'Unusual audio pattern detected',
                    'timestamp': timestamp
                })
        
        # Eye movement analysis (if face detected)
        if face_count == 1 and self.config.get('enable_gaze_tracking', False):
            landmarks = self.face_detector.get_face_landmarks(frame, faces[0])
            if landmarks:
                gaze_info = self._analyze_gaze(landmarks, frame.shape)
                if gaze_info['suspicious']:
                    activities.append({
                        'type': 'suspicious_gaze',
                        'confidence': gaze_info['confidence'],
                        'details': gaze_info['details'],
                        'timestamp': timestamp
                    })
        
        # Update history
        self.activity_history.append({
            'timestamp': timestamp,
            'face_count': face_count,
            'activities': activities
        })
        
        # Add frame to buffer if suspicious activity detected
        if activities:
            self.frame_buffer.append((frame, timestamp))
        
        return activities
    
    def _analyze_gaze(self, landmarks, frame_shape):
        """Analyze eye gaze from facial landmarks"""
        # Extract eye landmarks (simplified)
        left_eye = landmarks[36:42]
        right_eye = landmarks[42:48]
        
        # Calculate eye center
        left_center = np.mean(left_eye, axis=0)
        right_center = np.mean(right_eye, axis=0)
        
        # Simple gaze estimation based on position relative to frame
        h, w = frame_shape[:2]
        gaze_x = (left_center[0] + right_center[0]) / 2 / w
        gaze_y = (left_center[1] + right_center[1]) / 2 / h
        
        # Check if looking away from screen
        suspicious = False
        confidence = 0.0
        details = ""
        
        if gaze_x < 0.2 or gaze_x > 0.8:
            suspicious = True
            confidence = 0.7
            details = "Looking to the side"
        elif gaze_y < 0.2 or gaze_y > 0.8:
            suspicious = True
            confidence = 0.7
            details = "Looking up or down"
        
        return {
            'suspicious': suspicious,
            'confidence': confidence,
            'details': details
        }
    
    def get_summary(self):
        """Get summary of monitoring session"""
        if not self.activity_history:
            return {}
        
        # Count different types of activities
        activity_counts = {}
        for record in self.activity_history:
            for activity in record['activities']:
                activity_type = activity['type']
                if activity_type not in activity_counts:
                    activity_counts[activity_type] = 0
                activity_counts[activity_type] += 1
        
        # Calculate suspicion score
        weights = {
            'multiple_faces': 10,
            'phone_detected': 8,
            'student_absent': 5,
            'unauthorized_material': 7,
            'voice_detected': 4,
            'audio_anomaly': 3,
            'suspicious_gaze': 2
        }
        
        total_score = sum(
            counts * weights.get(activity, 1) 
            for activity, counts in activity_counts.items()
        )
        
        return {
            'activity_counts': activity_counts,
            'suspicion_score': total_score,
            'total_frames': len(self.activity_history),
            'high_confidence_alerts': [
                a for record in self.activity_history 
                for a in record['activities'] 
                if a['confidence'] > self.config['CHEATING_CONFIDENCE_THRESHOLD']
            ]
        }
    
    def save_evidence(self, session_id, activity):
        """Save frame as evidence for suspicious activity"""
        if not self.frame_buffer:
            return None
        
        # Get the most recent frame
        frame, timestamp = self.frame_buffer[-1]
        
        # Create filename
        filename = f"{session_id}_{activity['type']}_{timestamp.strftime('%Y%m%d_%H%M%S')}.jpg"
        filepath = f"app/static/uploads/evidence/{filename}"
        
        # Save frame
        try:
            cv2.imwrite(filepath, frame)
            return filename
        except Exception as e:
            logger.error(f"Failed to save evidence: {str(e)}")
            return None