import cv2
from src.pose_detector import PoseDetector

def main():
    """웹캠에서 YOLOv8 포즈 추정 테스트"""
    
    print("🚀 YOLOv8 Pose 초기화 중...")
    detector = PoseDetector()
    keypoint_names = detector.get_keypoint_names()
    
    # 웹캠 열기
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("❌ 웹캠을 열 수 없습니다")
        return
    
    print("✅ 포즈 추정 시작!")
    print("ESC를 눌러서 종료하세요")
    
    frame_count = 0
    
    while True:
        ret, frame = cap.read()
        
        if not ret:
            break
        
        # 포즈 추정
        annotated_frame, results = detector.detect(frame)
        
        # 랜드마크 추출
        landmarks = detector.get_landmarks(results)
        
        # 정보 표시
        if landmarks:
            print(f"✅ Frame {frame_count}: {len(landmarks)}개 관절점 감지됨")
            
            # 감지된 관절점 출력 (첫 5개만)
            for i, (name, landmark) in enumerate(zip(keypoint_names[:5], landmarks[:5])):
                print(f"   {name}: ({landmark['x']:.1f}, {landmark['y']:.1f}) - 신뢰도: {landmark['confidence']:.2f}")
        else:
            print(f"⚠️  Frame {frame_count}: 포즈를 감지할 수 없습니다")
        
        frame_count += 1
        
        # 화면 표시
        cv2.imshow('YOLOv8 Pose Detection', annotated_frame)
        
        # ESC 눌러서 종료
        if cv2.waitKey(1) & 0xFF == 27:
            break
    
    # 리소스 해제
    cap.release()
    cv2.destroyAllWindows()
    detector.close()
    
    print(f"✅ 종료됨 (총 {frame_count}프레임 처리)")

if __name__ == '__main__':
    main()