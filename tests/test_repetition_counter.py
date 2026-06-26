"""
test_repetition_counter.py - RepetitionCounter 클래스의 유닛 테스트

TDD 기반으로 작성된 테스트 스위트
pytest로 실행: pytest test_repetition_counter.py -v
"""

import pytest
from src.repetition_counter import RepetitionCounter, RepCounterState


class TestRepetitionCounterInitialization:
    """초기화 관련 테스트"""
    
    def test_initialization_default_values(self):
        """기본값으로 초기화"""
        counter = RepetitionCounter()
        
        assert counter.rep_count == 0
        assert counter.current_state == RepCounterState.IDLE
        assert counter.previous_angle is None
        assert counter.threshold_deep == 88.0
        assert counter.threshold_recovery == 100.0
    
    def test_initialization_custom_values(self):
        """커스텀값으로 초기화"""
        counter = RepetitionCounter(
            threshold_deep=90.0,
            threshold_recovery=105.0,
            min_frames_in_state=10
        )
        
        assert counter.threshold_deep == 90.0
        assert counter.threshold_recovery == 105.0
        assert counter.min_frames_in_state == 10


class TestRepetitionCounterStateTransition:
    """상태 머신 전이 테스트"""
    
    def test_idle_to_descending(self):
        """IDLE → DESCENDING 전이"""
        counter = RepetitionCounter()
        
        # 첫 번째 프레임: 상태 설정
        counter.update(120.0, "SHALLOW")
        assert counter.current_state == RepCounterState.IDLE
        
        # 두 번째 프레임: 각도 감소 + DEEP 진입
        rep_count, state = counter.update(85.0, "DEEP")
        assert counter.current_state == RepCounterState.DESCENDING
        assert rep_count == 0  # 아직 완료되지 않음
    
    def test_descending_to_deep(self):
        """DESCENDING → DEEP 전이"""
        counter = RepetitionCounter()
        
        counter.update(120.0, "SHALLOW")  # IDLE
        counter.update(85.0, "DEEP")      # DESCENDING
        rep_count, state = counter.update(80.0, "DEEP")
        
        assert counter.current_state == RepCounterState.DEEP
        assert rep_count == 0
    
    def test_deep_to_ascending(self):
        """DEEP → ASCENDING 전이"""
        counter = RepetitionCounter()
        
        counter.update(120.0, "SHALLOW")  # IDLE
        counter.update(85.0, "DEEP")      # DESCENDING
        counter.update(80.0, "DEEP")      # DEEP
        rep_count, state = counter.update(85.0, "DEEP")
        
        assert counter.current_state == RepCounterState.ASCENDING
        assert rep_count == 0
    
    def test_ascending_to_complete(self):
        """ASCENDING → COMPLETE 전이"""
        counter = RepetitionCounter()
        
        counter.update(120.0, "SHALLOW")  # IDLE
        counter.update(85.0, "DEEP")      # DESCENDING
        counter.update(80.0, "DEEP")      # DEEP
        counter.update(85.0, "DEEP")      # ASCENDING
        rep_count, state = counter.update(105.0, "NORMAL")
        
        assert counter.current_state == RepCounterState.COMPLETE
        assert rep_count == 1  # 반복 카운트 증가!


class TestRepetitionCountingAccuracy:
    """반복 카운팅 정확도 테스트"""
    
    def test_single_squat_repetition(self):
        """싱글 스쿼트 반복"""
        counter = RepetitionCounter()
        
        # 완전한 스쿼트: 120° → 80° → 120°
        angles = [120.0, 110.0, 95.0, 85.0, 80.0, 85.0, 100.0, 110.0, 120.0]
        states = ["SHALLOW", "NORMAL", "NORMAL", "DEEP", "DEEP", "DEEP", "NORMAL", "SHALLOW", "SHALLOW"]
        
        for angle, state in zip(angles, states):
            rep_count, _ = counter.update(angle, state)
        
        assert counter.rep_count == 1
    
    def test_multiple_squat_repetitions(self):
        """여러 번의 스쿼트 반복"""
        counter = RepetitionCounter()
        
        # 3개의 완전한 스쿼트
        test_sequence = [
            # Squat 1
            (120.0, "SHALLOW"),
            (110.0, "NORMAL"),
            (85.0, "DEEP"),
            (80.0, "DEEP"),
            (85.0, "DEEP"),
            (105.0, "NORMAL"),
            (120.0, "SHALLOW"),
            
            # Squat 2
            (110.0, "NORMAL"),
            (90.0, "DEEP"),
            (82.0, "DEEP"),
            (90.0, "DEEP"),
            (105.0, "NORMAL"),
            (120.0, "SHALLOW"),
            
            # Squat 3
            (115.0, "NORMAL"),
            (92.0, "DEEP"),
            (80.0, "DEEP"),
            (88.0, "DEEP"),
            (105.0, "NORMAL"),
            (120.0, "SHALLOW"),
        ]
        
        for angle, state in test_sequence:
            rep_count, _ = counter.update(angle, state)
        
        assert counter.rep_count == 3
    
    def test_shallow_squat_not_counted(self):
        """얕은 스쿼트는 카운팅되지 않음"""
        counter = RepetitionCounter()
        
        # 얕은 스쿼트: 120° → 110° → 120° (DEEP 미달)
        test_sequence = [
            (120.0, "SHALLOW"),
            (110.0, "NORMAL"),
            (105.0, "NORMAL"),
            (110.0, "NORMAL"),
            (120.0, "SHALLOW"),
            (115.0, "NORMAL"),
        ]
        
        for angle, state in test_sequence:
            rep_count, _ = counter.update(angle, state)
        
        assert counter.rep_count == 0  # 얕아서 카운팅 안 됨


class TestRepetitionCounterReset:
    """리셋 기능 테스트"""
    
    def test_reset_clears_counter(self):
        """리셋 후 카운터가 0으로 초기화"""
        counter = RepetitionCounter()
        
        # 한 번의 반복 완료
        test_sequence = [
            (120.0, "SHALLOW"),
            (85.0, "DEEP"),
            (80.0, "DEEP"),
            (85.0, "DEEP"),
            (105.0, "NORMAL"),
            (120.0, "SHALLOW"),
        ]
        
        for angle, state in test_sequence:
            counter.update(angle, state)
        
        assert counter.rep_count == 1
        
        # 리셋
        counter.reset()
        
        assert counter.rep_count == 0
        assert counter.current_state == RepCounterState.IDLE
        assert counter.previous_angle is None


class TestRepetitionCounterStatus:
    """상태 조회 테스트"""
    
    def test_get_status(self):
        """상태 정보 조회"""
        counter = RepetitionCounter()
        counter.update(120.0, "SHALLOW")
        
        status = counter.get_status()
        
        assert "rep_count" in status
        assert "state" in status
        assert "previous_angle" in status
        assert "frames_in_state" in status
        
        assert status["rep_count"] == 0
        assert status["state"] == "IDLE"
        assert status["previous_angle"] == 120.0


class TestRepetitionCounterEdgeCases:
    """엣지 케이스 테스트"""
    
    def test_rapid_state_changes(self):
        """빠른 상태 변화"""
        counter = RepetitionCounter()
        
        # 많은 상태 변화를 빠르게 처리
        test_sequence = [
            (120.0, "SHALLOW"),
            (85.0, "DEEP"),
            (82.0, "DEEP"),
            (84.0, "DEEP"),
            (87.0, "DEEP"),
            (90.0, "DEEP"),
            (95.0, "NORMAL"),
            (105.0, "NORMAL"),
            (115.0, "SHALLOW"),
        ]
        
        for angle, state in test_sequence:
            rep_count, _ = counter.update(angle, state)
        
        assert counter.rep_count == 1
    
    def test_incomplete_squat_followed_by_complete(self):
        """불완전한 스쿼트 후 완전한 스쿼트"""
        counter = RepetitionCounter()
        
        # 첫 번째: 불완전 (회복 안 함)
        counter.update(120.0, "SHALLOW")
        counter.update(90.0, "DEEP")
        counter.update(85.0, "DEEP")
        counter.update(120.0, "SHALLOW")  # 빠르게 올림
        
        # 두 번째: 완전한 스쿼트
        counter.update(85.0, "DEEP")
        counter.update(80.0, "DEEP")
        counter.update(85.0, "DEEP")
        counter.update(105.0, "NORMAL")
        counter.update(120.0, "SHALLOW")
        
        assert counter.rep_count == 1
    
    def test_threshold_boundary_conditions(self):
        """임계값 경계 조건"""
        counter = RepetitionCounter(
            threshold_deep=88.0,
            threshold_recovery=100.0
        )
        
        # 정확히 임계값에서의 동작
        test_sequence = [
            (120.0, "SHALLOW"),
            (88.0, "DEEP"),      # 정확히 DEEP 임계값
            (80.0, "DEEP"),
            (90.0, "DEEP"),
            (100.0, "NORMAL"),   # 정확히 RECOVERY 임계값
            (120.0, "SHALLOW"),
        ]
        
        for angle, state in test_sequence:
            counter.update(angle, state)
        
        assert counter.rep_count == 1


class TestRepetitionCounterIntegration:
    """통합 테스트"""
    
    def test_realistic_workout_session(self):
        """현실적인 운동 세션"""
        counter = RepetitionCounter()
        
        # 10개의 스쿼트 시뮬레이션
        for rep in range(10):
            # 시작 자세
            counter.update(120.0, "SHALLOW")
            # 하강
            counter.update(95.0, "NORMAL")
            # DEEP 도달
            counter.update(85.0, "DEEP")
            counter.update(80.0, "DEEP")
            # 상승
            counter.update(90.0, "DEEP")
            counter.update(105.0, "NORMAL")
            # 최종
            counter.update(120.0, "SHALLOW")
        
        assert counter.rep_count == 10
    
    def test_counter_state_consistency(self):
        """카운터 상태 일관성"""
        counter = RepetitionCounter()
        
        # 여러 반복 후에도 상태가 항상 IDLE
        for _ in range(5):
            counter.update(120.0, "SHALLOW")
            counter.update(85.0, "DEEP")
            counter.update(80.0, "DEEP")
            counter.update(85.0, "DEEP")
            counter.update(105.0, "NORMAL")
            counter.update(120.0, "SHALLOW")
        
        # 마지막 상태는 IDLE로 돌아와야 함
        assert counter.current_state == RepCounterState.IDLE


if __name__ == "__main__":
    """pytest 또는 직접 실행"""
    pytest.main([__file__, "-v"])