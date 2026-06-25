import cv2
from ultralytics import YOLO
import numpy as np

class PoseDetector:
    def __init__(self):
        """YOLOv8 Pose 초기화"""
        # YOLOv8 Pose 모델 로드 (자동으로 다운로드됨)
        self.model = YOLO('yolov8m-pose.pt')
        self.conf = 0.5  # 신뢰도 임계값
    
    def detect(self, frame):
        """
        프레임에서 포즈 추정
        
        Args:
            frame: OpenCV 프레임 (BGR)
        
        Returns:
            frame: 포즈가 그려진 프레임
            results: YOLOv8 결과
        """
        # YOLOv8으로 추정
        results = self.model(frame, conf=self.conf)
        
        # 결과 그리기
        annotated_frame = results[0].plot()
        
        return annotated_frame, results
    
    def get_landmarks(self, results):
        """
        포즈 랜드마크(관절점) 추출
        
        Returns:
            landmarks: 17개의 관절점 좌표 (COCO 형식)
        """
        landmarks = []
        
        if results and len(results) > 0:
            keypoints = results[0].keypoints.data  # (1, 17, 3) 형태
            
            if keypoints is not None and len(keypoints) > 0:
                for point in keypoints[0]:
                    landmarks.append({
                        'x': float(point[0].item()) if hasattr(point[0], 'item') else float(point[0]),
                        'y': float(point[1].item()) if hasattr(point[1], 'item') else float(point[1]),
                        'confidence': float(point[2].item()) if hasattr(point[2], 'item') else float(point[2])
                    })
        
        return landmarks if landmarks else None
    
    def get_keypoint_names(self):
        """COCO 형식의 17개 관절점 이름"""
        return [
            'nose', 'left_eye', 'right_eye', 'left_ear', 'right_ear',
            'left_shoulder', 'right_shoulder', 'left_elbow', 'right_elbow',
            'left_wrist', 'right_wrist', 'left_hip', 'right_hip',
            'left_knee', 'right_knee', 'left_ankle', 'right_ankle'
        ]
    
    def close(self):
        """리소스 해제"""
        pass  # YOLOv8은 특별한 정리 불필요