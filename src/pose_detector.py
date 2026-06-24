import cv2
import numpy as np

try:
    # 먼저 새 API 시도
    from mediapipe.tasks import vision
    from mediapipe.framework.formats import landmark_pb2
    import mediapipe as mp
    USE_NEW_API = True
except:
    # 구 API 사용
    import mediapipe as mp
    USE_NEW_API = False

class PoseDetector:
    def __init__(self):
        """MediaPipe Pose 초기화"""
        if USE_NEW_API:
            self.pose = None
        else:
            self.pose = mp.solutions.pose.Pose()
            self.mp_drawing = mp.solutions.drawing_utils
            self.mp_pose = mp.solutions.pose
    
    def detect(self, frame):
        """포즈 추정"""
        # BGR을 RGB로 변환
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # 포즈 추정
        results = self.pose.process(rgb_frame)
        
        # 결과 그리기
        if results.pose_landmarks:
            self.mp_drawing.draw_landmarks(
                frame,
                results.pose_landmarks,
                self.mp_pose.POSE_CONNECTIONS
            )
        
        return frame, results
    
    def get_landmarks(self, results):
        """관절점 추출"""
        if results and results.pose_landmarks:
            landmarks = []
            for landmark in results.pose_landmarks.landmark:
                landmarks.append({
                    'x': landmark.x,
                    'y': landmark.y,
                    'z': landmark.z,
                    'visibility': landmark.visibility
                })
            return landmarks
        return None
    
    def close(self):
        """리소스 해제"""
        if self.pose:
            self.pose.close()