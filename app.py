from flask import Flask, render_template, Response, jsonify
import cv2
from dotenv import load_dotenv
import os
from src.pose_detector import PoseDetector
from src.squat_analyzer import SquatAnalyzer

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev')

# 웹캠 객체
camera = cv2.VideoCapture(0)

# 포즈 감지 및 분석
detector = PoseDetector()
analyzer = SquatAnalyzer()

# 실시간 데이터 저장
current_data = {
    'angle': 0,
    'depth': 'READY',
    'confidence': 0,
    'left_knee': 0,
    'right_knee': 0,
    'frame_count': 0
}

def generate_frames():
    """웹캠 프레임 생성 + 포즈 추정 + 분석"""
    global current_data
    
    frame_count = 0
    
    while True:
        success, frame = camera.read()
        if not success:
            break
        
        # 포즈 추정
        annotated_frame, results = detector.detect(frame)
        
        # 랜드마크 추출
        landmarks = detector.get_landmarks(results)
        
        # 분석
        if landmarks:
            analysis = analyzer.analyze(landmarks)
            knee_angles = analysis['knee_angles']
            verdict = analysis['verdict']
            
            # 데이터 저장
            current_data['angle'] = knee_angles['average_knee_angle'] if knee_angles['average_knee_angle'] else 0
            current_data['left_knee'] = knee_angles['left_knee_angle'] if knee_angles['left_knee_angle'] else 0
            current_data['right_knee'] = knee_angles['right_knee_angle'] if knee_angles['right_knee_angle'] else 0
            current_data['depth'] = verdict['depth']
            current_data['confidence'] = verdict['confidence']
        else:
            current_data['angle'] = 0
            current_data['depth'] = 'UNKNOWN'
            current_data['confidence'] = 0
        
        current_data['frame_count'] = frame_count
        frame_count += 1
        
        # 화면에 정보 표시
        if landmarks:
            # 각도 표시
            angle_text = f"Angle: {current_data['angle']:.1f}°"
            cv2.putText(annotated_frame, angle_text, (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
            # 판정 결과 표시
            verdict_text = current_data['depth']
            color = (0, 255, 0) if current_data['depth'] == 'DEEP' else (0, 165, 255) if current_data['depth'] == 'NORMAL' else (0, 0, 255)
            cv2.putText(annotated_frame, verdict_text, (10, 70),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
        
        # 프레임을 JPEG로 인코딩
        ret, buffer = cv2.imencode('.jpg', annotated_frame)
        frame = buffer.tobytes()
        
        # Motion JPEG 스트리밍
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/api/data')
def get_data():
    """실시간 데이터 API"""
    return jsonify(current_data)

@app.route('/api/status')
def status():
    return jsonify({
        'status': 'HYROX System Running',
        'message': 'Pose detection and squat analysis active'
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)