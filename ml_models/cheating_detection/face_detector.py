import cv2
import numpy as np
import dlib
from mtcnn import MTCNN
import logging

logger = logging.getLogger(__name__)

class FaceDetector:
    def __init__(self, method='mtcnn'):
        """
        Initialize face detector with specified method.
        Methods: 'mtcnn', 'dlib', 'opencv_dnn', 'haar'
        """
        self.method = method
        
        if method == 'mtcnn':
            self.detector = MTCNN()
        elif method == 'dlib':
            self.detector = dlib.get_frontal_face_detector()
            self.predictor = dlib.shape_predictor('ml_models/weights/shape_predictor_68_face_landmarks.dat')
        elif method == 'opencv_dnn':
            self.net = cv2.dnn.readNetFromCaffe(
                'ml_models/weights/deploy.prototxt',
                'ml_models/weights/res10_300x300_ssd_iter_140000.caffemodel'
            )
        elif method == 'haar':
            self.detector = cv2.CascadeClassifier(
                cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            )
    
    def detect_faces(self, frame):
        """Detect faces in a frame and return bounding boxes"""
        faces = []
        
        try:
            if self.method == 'mtcnn':
                detections = self.detector.detect_faces(frame)
                faces = [(d['box'][0], d['box'][1], 
                         d['box'][0] + d['box'][2], 
                         d['box'][1] + d['box'][3], 
                         d['confidence']) for d in detections]
            
            elif self.method == 'dlib':
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                dets = self.detector(gray, 1)
                faces = [(d.left(), d.top(), d.right(), d.bottom(), 1.0) for d in dets]
            
            elif self.method == 'opencv_dnn':
                h, w = frame.shape[:2]
                blob = cv2.dnn.blobFromImage(frame, 1.0, (300, 300), (104.0, 177.0, 123.0))
                self.net.setInput(blob)
                detections = self.net.forward()
                
                for i in range(detections.shape[2]):
                    confidence = detections[0, 0, i, 2]
                    if confidence > 0.5:
                        box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                        faces.append((*box.astype(int), confidence))
            
            elif self.method == 'haar':
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                dets = self.detector.detectMultiScale(gray, 1.3, 5)
                faces = [(x, y, x+w, y+h, 1.0) for (x, y, w, h) in dets]
        
        except Exception as e:
            logger.error(f"Face detection error: {str(e)}")
        
        return faces
    
    def get_face_landmarks(self, frame, face_box):
        """Get facial landmarks for gaze estimation"""
        if self.method != 'dlib':
            logger.warning("Landmarks only available with dlib detector")
            return None
        
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        x1, y1, x2, y2, _ = face_box
        rect = dlib.rectangle(x1, y1, x2, y2)
        
        landmarks = self.predictor(gray, rect)
        points = [(p.x, p.y) for p in landmarks.parts()]
        
        return points
