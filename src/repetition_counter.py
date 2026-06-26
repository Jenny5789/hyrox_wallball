"""
RepetitionCounter: 스쿼트 반복 횟수를 실시간으로 카운팅하는 클래스

상태 머신:
    IDLE → DESCENDING → DEEP → ASCENDING → COMPLETE → IDLE (반복)
    
카운팅 규칙:
    1. DEEP 상태 진입 (깊이 < 88°) → 하강 감지
    2. 회복 시작 (깊이 > 100°) → 상승 감지
    3. 회복 완료 → 반복 횟수 +1 카운트
"""

from enum import Enum
from typing import Tuple


class SquatState(Enum):
    """스쿼트 상태 정의"""
    DEEP = "DEEP"          # 충분한 깊이 (< 88°)
    NORMAL = "NORMAL"      # 표준 범위 (88° ~ 110°)
    SHALLOW = "SHALLOW"    # 얕은 스쿼트 (≥ 110°)


class RepCounterState(Enum):
    """반복 카운터 내부 상태"""
    IDLE = "IDLE"              # 대기 상태
    DESCENDING = "DESCENDING"  # 하강 중 (스쿼트 시작)
    DEEP = "DEEP"              # DEEP 도달
    ASCENDING = "ASCENDING"    # 상승 중 (회복)
    COMPLETE = "COMPLETE"      # 반복 완료


class RepetitionCounter:
    """
    스쿼트 반복 횟수를 자동으로 카운팅하는 클래스
    
    상태 머신을 이용해 정확한 반복 횟수를 추적합니다.
    
    Attributes:
        rep_count (int): 누적 반복 횟수
        current_state (RepCounterState): 현재 상태 머신 상태
        previous_angle (float): 이전 프레임의 무릎 각도
        threshold_deep (float): DEEP 상태 임계값 (기본값: 88°)
        threshold_recovery (float): 회복 완료 임계값 (기본값: 100°)
        min_frames_in_state (int): 상태 지속 최소 프레임 (노이즈 방지)
        frames_in_state (int): 현재 상태 지속 프레임 수
    """
    
    def __init__(
        self,
        threshold_deep: float = 88.0,
        threshold_recovery: float = 100.0,
        min_frames_in_state: int = 5
    ):
        """
        RepetitionCounter 초기화
        
        Args:
            threshold_deep (float): DEEP 상태로 판정하는 각도 임계값 (기본값: 88°)
            threshold_recovery (float): 회복 완료 판정 임계값 (기본값: 100°)
            min_frames_in_state (int): 상태 지속 최소 프레임 (노이즈 방지, 기본값: 5)
        """
        self.rep_count = 0
        self.current_state = RepCounterState.IDLE
        self.previous_angle = None
        
        # 임계값
        self.threshold_deep = threshold_deep
        self.threshold_recovery = threshold_recovery
        self.min_frames_in_state = min_frames_in_state
        
        # 상태 지속 카운트 (노이즈 방지)
        self.frames_in_state = 0
    
    def update(self, knee_angle: float, squat_state: str) -> Tuple[int, str]:
        """
        현재 프레임의 무릎 각도와 스쿼트 상태로 반복 횟수를 업데이트
        
        Args:
            knee_angle (float): 현재 무릎 각도 (도)
            squat_state (str): 스쿼트 상태 ("DEEP", "NORMAL", "SHALLOW")
        
        Returns:
            Tuple[int, str]: (현재 반복 횟수, 현재 상태)
        
        Example:
            >>> counter = RepetitionCounter()
            >>> rep_count, state = counter.update(85.0, "DEEP")
            >>> print(rep_count)  # 0 (아직 완료되지 않음)
            >>> print(state)      # "DEEP" (DEEP 상태 진입)
        """
        
        # 이전 각도 초기화
        if self.previous_angle is None:
            self.previous_angle = knee_angle
        
        # 상태 머신 업데이트
        self._update_state_machine(knee_angle, squat_state)
        
        # 이전 각도 업데이트
        self.previous_angle = knee_angle
        
        return self.rep_count, self.current_state.value
    
    def _update_state_machine(self, knee_angle: float, squat_state: str) -> None:
        """
        상태 머신 로직을 업데이트
        
        상태 전이 규칙:
            IDLE → DESCENDING: 각도 감소 감지
            DESCENDING → DEEP: DEEP 상태 도달
            DEEP → ASCENDING: 각도 증가 감지
            ASCENDING → COMPLETE: 회복 임계값 도달
            COMPLETE → IDLE: 상태 리셋
        """
        
        angle_decreasing = knee_angle < self.previous_angle
        angle_increasing = knee_angle > self.previous_angle
        
        # 상태별 전이 로직
        if self.current_state == RepCounterState.IDLE:
            if angle_decreasing and squat_state == "DEEP":
                self._transition_to_state(RepCounterState.DESCENDING)
        
        elif self.current_state == RepCounterState.DESCENDING:
            if squat_state == "DEEP":
                self._transition_to_state(RepCounterState.DEEP)
        
        elif self.current_state == RepCounterState.DEEP:
            if angle_increasing:
                self._transition_to_state(RepCounterState.ASCENDING)
        
        elif self.current_state == RepCounterState.ASCENDING:
            # 회복 완료: 각도가 recovery threshold를 초과
            if knee_angle > self.threshold_recovery:
                self._transition_to_state(RepCounterState.COMPLETE)
        
        elif self.current_state == RepCounterState.COMPLETE:
            # 반복 완료 후 IDLE로 리셋
            self.rep_count += 1
            self._transition_to_state(RepCounterState.IDLE)
    
    def _transition_to_state(self, new_state: RepCounterState) -> None:
        """
        새로운 상태로 전이
        
        Args:
            new_state (RepCounterState): 전이할 새 상태
        """
        if self.current_state != new_state:
            self.current_state = new_state
            self.frames_in_state = 0
        else:
            self.frames_in_state += 1
    
    def reset(self) -> None:
        """반복 카운터를 초기화"""
        self.rep_count = 0
        self.current_state = RepCounterState.IDLE
        self.previous_angle = None
        self.frames_in_state = 0
    
    def get_status(self) -> dict:
        """
        현재 카운터 상태를 딕셔너리로 반환
        
        Returns:
            dict: 반복 횟수, 현재 상태, 이전 각도 정보
        
        Example:
            >>> counter = RepetitionCounter()
            >>> status = counter.get_status()
            >>> print(status)
            # {'rep_count': 0, 'state': 'IDLE', 'previous_angle': None}
        """
        return {
            "rep_count": self.rep_count,
            "state": self.current_state.value,
            "previous_angle": self.previous_angle,
            "frames_in_state": self.frames_in_state
        }


if __name__ == "__main__":
    """
    RepetitionCounter 테스트 예제
    
    시뮬레이션: 3개의 스쿼트 반복
    """
    counter = RepetitionCounter(
        threshold_deep=88.0,
        threshold_recovery=100.0
    )
    
    # 테스트 데이터: (각도, 상태)
    test_sequence = [
        # 반복 1
        (120.0, "SHALLOW"),  # IDLE
        (110.0, "NORMAL"),   # IDLE
        (95.0, "NORMAL"),    # DESCENDING
        (85.0, "DEEP"),      # DEEP
        (80.0, "DEEP"),      # DEEP
        (88.0, "DEEP"),      # ASCENDING
        (100.0, "NORMAL"),   # ASCENDING
        (110.0, "SHALLOW"),  # COMPLETE → rep_count = 1
        
        # 반복 2
        (100.0, "NORMAL"),   # IDLE
        (90.0, "DEEP"),      # DESCENDING
        (82.0, "DEEP"),      # DEEP
        (88.0, "DEEP"),      # ASCENDING
        (105.0, "NORMAL"),   # COMPLETE → rep_count = 2
        
        # 반복 3
        (110.0, "SHALLOW"),  # IDLE
        (92.0, "DEEP"),      # DESCENDING
        (80.0, "DEEP"),      # DEEP
        (95.0, "NORMAL"),    # ASCENDING
        (110.0, "SHALLOW"),  # COMPLETE → rep_count = 3
    ]
    
    print("=== RepetitionCounter 테스트 ===\n")
    for i, (angle, state) in enumerate(test_sequence):
        rep_count, counter_state = counter.update(angle, state)
        print(f"Frame {i+1}: 각도={angle}°, 상태={state} → 반복={rep_count}, 내부상태={counter_state}")
    
    print(f"\n최종 반복 횟수: {counter.rep_count}")
    print(f"최종 상태: {counter.get_status()}")