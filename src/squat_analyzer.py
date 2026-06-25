import numpy as np
import math

class SquatAnalyzer:
    """스쿼트 깊이 판정 클래스"""
    
    # COCO 형식 관절점 인덱스
    NOSE = 0
    LEFT_SHOULDER = 5
    RIGHT_SHOULDER = 6
    LEFT_HIP = 11
    RIGHT_HIP = 12
    LEFT_KNEE = 13
    RIGHT_KNEE = 14
    LEFT_ANKLE = 15
    RIGHT_ANKLE = 16
    
    def __init__(self):
        """초기화"""
        self.confidence_threshold = 0.5  # 신뢰도 임계값
    
    def calculate_angle(self, point_a, point_b, point_c):
        """
        3개의 점으로 각도 계산
        
        Args:
            point_a: 첫 번째 점 {'x': ..., 'y': ...}
            point_b: 중간 점 (꼭짓점)
            point_c: 세 번째 점
        
        Returns:
            angle: 각도 (0-180도)
        """
        # 벡터 계산
        vector_ba = np.array([
            point_a['x'] - point_b['x'],
            point_a['y'] - point_b['y']
        ])
        
        vector_bc = np.array([
            point_c['x'] - point_b['x'],
            point_c['y'] - point_b['y']
        ])
        
        # 내적 계산
        dot_product = np.dot(vector_ba, vector_bc)
        
        # 크기 계산
        magnitude_ba = np.linalg.norm(vector_ba)
        magnitude_bc = np.linalg.norm(vector_bc)
        
        # 각도 계산 (라디안 → 도)
        if magnitude_ba == 0 or magnitude_bc == 0:
            return 0
        
        cos_angle = dot_product / (magnitude_ba * magnitude_bc)
        # cos 값을 -1~1 범위로 제한
        cos_angle = np.clip(cos_angle, -1.0, 1.0)
        
        angle = math.degrees(math.acos(cos_angle))
        
        return angle
    
    def calculate_knee_angle(self, landmarks):
        """
        무릎 각도 계산 (좌측, 우측)
        
        Args:
            landmarks: 17개 관절점 리스트
        
        Returns:
            {
                'left_knee_angle': 각도,
                'right_knee_angle': 각도,
                'average_knee_angle': 평균 각도
            }
        """
        if not landmarks or len(landmarks) < 17:
            return None
        
        # 신뢰도 확인
        left_hip = landmarks[self.LEFT_HIP]
        left_knee = landmarks[self.LEFT_KNEE]
        left_ankle = landmarks[self.LEFT_ANKLE]
        
        right_hip = landmarks[self.RIGHT_HIP]
        right_knee = landmarks[self.RIGHT_KNEE]
        right_ankle = landmarks[self.RIGHT_ANKLE]
        
        # 신뢰도 체크
        if (left_hip['confidence'] < self.confidence_threshold or
            left_knee['confidence'] < self.confidence_threshold or
            left_ankle['confidence'] < self.confidence_threshold):
            left_knee_angle = None
        else:
            left_knee_angle = self.calculate_angle(left_hip, left_knee, left_ankle)
        
        if (right_hip['confidence'] < self.confidence_threshold or
            right_knee['confidence'] < self.confidence_threshold or
            right_ankle['confidence'] < self.confidence_threshold):
            right_knee_angle = None
        else:
            right_knee_angle = self.calculate_angle(right_hip, right_knee, right_ankle)
        
        # 평균 각도
        if left_knee_angle is not None and right_knee_angle is not None:
            average_angle = (left_knee_angle + right_knee_angle) / 2
        elif left_knee_angle is not None:
            average_angle = left_knee_angle
        elif right_knee_angle is not None:
            average_angle = right_knee_angle
        else:
            average_angle = None
        
        return {
            'left_knee_angle': left_knee_angle,
            'right_knee_angle': right_knee_angle,
            'average_knee_angle': average_angle
        }
    
    def judge_squat_depth(self, average_angle):
        """
        스쿼트 깊이 판정
        
        Args:
            average_angle: 평균 무릎 각도
        
        Returns:
            {
                'depth': 'DEEP' | 'NORMAL' | 'SHALLOW',
                'confidence': 신뢰도 (0-1),
                'description': 설명
            }
        """
        if average_angle is None:
            return {
                'depth': 'UNKNOWN',
                'confidence': 0,
                'description': '포즈를 감지할 수 없습니다'
            }
        
        # 판정 기준
        if average_angle < 88:
            return {
                'depth': 'DEEP',
                'confidence': 0.95,
                'description': f'✅ 좋은 깊이! ({average_angle:.1f}°)'
            }
        elif average_angle < 110:
            return {
                'depth': 'NORMAL',
                'confidence': 0.80,
                'description': f'⚠️  중간 깊이 ({average_angle:.1f}°)'
            }
        else:
            return {
                'depth': 'SHALLOW',
                'confidence': 0.60,
                'description': f'❌ 얕은 깊이 ({average_angle:.1f}°)'
            }
    
    def analyze(self, landmarks):
        """
        전체 분석 (각도 계산 + 판정)
        
        Returns:
            {
                'knee_angles': {...},
                'verdict': {...}
            }
        """
        knee_angles = self.calculate_knee_angle(landmarks)
        
        if knee_angles is None:
            return {
                'knee_angles': None,
                'verdict': {
                    'depth': 'UNKNOWN',
                    'confidence': 0,
                    'description': '포즈를 감지할 수 없습니다'
                }
            }
        
        average_angle = knee_angles['average_knee_angle']
        verdict = self.judge_squat_depth(average_angle)
        
        return {
            'knee_angles': knee_angles,
            'verdict': verdict
        }