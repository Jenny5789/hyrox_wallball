import cv2
from src.pose_detector import PoseDetector

def main():
    """웹캠에서 포즈 추정 테스트"""
    
    # PoseDetector 초기화
    detector = PoseDetector()
    
    # 웹캠 열기
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("❌ 웹캠을 열 수 없습니다")
        return
    
    print("✅ 포즈 추정 시작!")
    print("ESC를 눌러서 종료하세요")
    
    while True:
        ret, frame = cap.read()
        
        if not ret:
            break
        
        # 포즈 추정
        frame, results = detector.detect(frame)
        
        # 랜드마크 추출
        landmarks = detector.get_landmarks(results)
        
        # 정보 표시
        if landmarks:
            print(f"✅ {len(landmarks)}개 관절점 감지됨")
        else:
            print("⚠️ 포즈를 감지할 수 없습니다")
        
        # 화면 표시
        cv2.imshow('Pose Detection', frame)
        
        # ESC 눌러서 종료
        if cv2.waitKey(1) & 0xFF == 27:
            break
    
    # 리소스 해제
    cap.release()
    cv2.destroyAllWindows()
    detector.close()
    
    print("✅ 종료됨")

if __name__ == '__main__':
    main()