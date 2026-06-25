import cv2
from src.pose_detector import PoseDetector
from src.squat_analyzer import SquatAnalyzer

def main():
    """웹캠에서 포즈 추정 + 스쿼트 깊이 판정"""
    
    print("🚀 YOLOv8 Pose + Squat Analyzer 초기화 중...")
    detector = PoseDetector()
    analyzer = SquatAnalyzer()
    
    # 웹캠 열기
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("❌ 웹캠을 열 수 없습니다")
        return
    
    print("✅ 분석 시작!")
    print("ESC를 눌러서 종료하세요\n")
    
    frame_count = 0
    
    while True:
        ret, frame = cap.read()
        
        if not ret:
            break
        
        # 포즈 추정
        annotated_frame, results = detector.detect(frame)
        
        # 랜드마크 추출
        landmarks = detector.get_landmarks(results)
        
        if landmarks:
            # 스쿼트 분석
            analysis = analyzer.analyze(landmarks)
            
            knee_angles = analysis['knee_angles']
            verdict = analysis['verdict']
            
            # 정보 출력
            print(f"Frame {frame_count}:")
            print(f"  좌측 무릎: {knee_angles['left_knee_angle']:.1f}°" if knee_angles['left_knee_angle'] else "  좌측 무릎: 감지 안 됨")
            print(f"  우측 무릎: {knee_angles['right_knee_angle']:.1f}°" if knee_angles['right_knee_angle'] else "  우측 무릎: 감지 안 됨")
            print(f"  평균 각도: {knee_angles['average_knee_angle']:.1f}°" if knee_angles['average_knee_angle'] else "  평균 각도: 계산 안 됨")
            print(f"  판정: {verdict['description']}\n")
            
            # 화면에 텍스트 표시
            text = f"Knee Angle: {knee_angles['average_knee_angle']:.1f}°" if knee_angles['average_knee_angle'] else "No Detection"
            verdict_text = verdict['depth']
            
            cv2.putText(annotated_frame, text, (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(annotated_frame, verdict_text, (10, 70),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        frame_count += 1
        
        # 화면 표시
        cv2.imshow('Squat Analysis', annotated_frame)
        
        # ESC 눌러서 종료
        if cv2.waitKey(1) & 0xFF == 27:
            break
    
    # 리소스 해제
    cap.release()
    cv2.destroyAllWindows()
    
    print(f"✅ 종료됨 (총 {frame_count}프레임 처리)")

if __name__ == '__main__':
    main()