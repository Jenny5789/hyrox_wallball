import cv2

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("❌ 웹캠을 열 수 없습니다")
    exit()

print("✅ 웹캠 정상!")
print("ESC를 눌러서 종료하세요")

while True:
    ret, frame = cap.read()
    
    if not ret:
        break
    
    cv2.imshow('Webcam Test', frame)
    
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()