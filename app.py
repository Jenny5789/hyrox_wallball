from flask import Flask, render_template, Response, jsonify
import cv2
import threading
import time
from dotenv import load_dotenv
import os
from src.pose_detector import PoseDetector
from src.squat_analyzer import SquatAnalyzer

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev')

# 웹캠 객체
camera = cv2.VideoCapture(0)

# 포즈 감지 및 분석 (무릎 각도는 화면 표시용 참고 지표로만 사용)
detector = PoseDetector()
analyzer = SquatAnalyzer()

# 실시간 데이터 저장 (script.js가 기대하는 필드명에 맞춤)
current_data = {
    'status': 'ok',
    'knee_angle': 0,
    'left_knee': 0,
    'right_knee': 0,
    'depth_state': 'READY',
    'confidence': 0,
    'rep_count': 0,
    'rep_target': 100,
    'counter_state': 'IDLE',
    'frame_count': 0
}

# 실제 카운트(하이록스 월볼 규정)는 무릎 각도가 아니라 "골반이 무릎보다 아래로
# 내려갔는지"로 센다. 무릎 각도/판정은 위 화면 표시용으로만 계속 쓰고, 최종
# 카운트는 이 상태로 별도 관리한다.
wb_rep_count = 0
wb_is_down = False

# 캡처+추론은 이 스레드 하나에서만 수행하고 결과(최신 JPEG)를 여기 저장한다.
# 요청 스레드(/video_feed, /api/data)마다 캡처+추론을 반복하면 GIL/CPU/GPU를
# 독점해서 새 연결조차 못 받을 정도로 서버가 막히므로, 무거운 작업과 요청 처리를
# 분리한다.
latest_jpeg = None
frame_lock = threading.Lock()
capture_running = True

def update_wallball_count(landmarks):
    """골반(hip)이 무릎(knee)보다 아래로 내려갔다가 다시 올라오면 1회로 카운트.
    화면 좌표는 아래로 갈수록 y가 커지므로, 골반 y가 무릎 y 이상이면 무릎보다
    아래로 내려간 것으로 본다."""
    global wb_rep_count, wb_is_down

    hip_ys = [landmarks[i]['y'] for i in (analyzer.LEFT_HIP, analyzer.RIGHT_HIP)
              if landmarks[i]['confidence'] >= analyzer.confidence_threshold]
    knee_ys = [landmarks[i]['y'] for i in (analyzer.LEFT_KNEE, analyzer.RIGHT_KNEE)
               if landmarks[i]['confidence'] >= analyzer.confidence_threshold]

    if not hip_ys or not knee_ys:
        current_data['counter_state'] = 'UNKNOWN'
        return

    hip_y = sum(hip_ys) / len(hip_ys)
    knee_y = sum(knee_ys) / len(knee_ys)
    is_down = hip_y >= knee_y

    if is_down:
        wb_is_down = True
        current_data['counter_state'] = 'DOWN'
    else:
        if wb_is_down:
            wb_rep_count += 1
            current_data['rep_count'] = wb_rep_count
        wb_is_down = False
        current_data['counter_state'] = 'UP'

def capture_loop():
    """웹캠 캡처 + 포즈 추정 + 분석을 반복하는 백그라운드 스레드"""
    global latest_jpeg, current_data

    frame_count = 0

    while capture_running:
        success, frame = camera.read()
        if not success:
            time.sleep(0.05)
            continue

        # 포즈 추정
        annotated_frame, results = detector.detect(frame)

        # 랜드마크 추출
        landmarks = detector.get_landmarks(results)

        # 분석 (무릎 각도/판정은 화면 표시용 참고 지표)
        if landmarks:
            analysis = analyzer.analyze(landmarks)
            knee_angles = analysis['knee_angles']
            verdict = analysis['verdict']

            average_angle = knee_angles['average_knee_angle'] if knee_angles else None

            current_data['knee_angle'] = average_angle if average_angle else 0
            current_data['left_knee'] = (knee_angles['left_knee_angle'] if knee_angles and knee_angles['left_knee_angle'] else 0)
            current_data['right_knee'] = (knee_angles['right_knee_angle'] if knee_angles and knee_angles['right_knee_angle'] else 0)
            current_data['depth_state'] = verdict['depth']
            current_data['confidence'] = verdict['confidence']

            # 실제 카운트: 골반-무릎 높이 비교 (하이록스 월볼 규정)
            update_wallball_count(landmarks)
        else:
            current_data['knee_angle'] = 0
            current_data['depth_state'] = 'UNKNOWN'
            current_data['confidence'] = 0

        current_data['frame_count'] = frame_count
        frame_count += 1

        # 화면에 정보 표시
        if landmarks:
            # 각도 표시
            angle_text = f"Angle: {current_data['knee_angle']:.1f}°"
            cv2.putText(annotated_frame, angle_text, (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            # 판정 결과 표시
            verdict_text = current_data['depth_state']
            color = (0, 255, 0) if current_data['depth_state'] == 'DEEP' else (0, 165, 255) if current_data['depth_state'] == 'NORMAL' else (0, 0, 255)
            cv2.putText(annotated_frame, verdict_text, (10, 70),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)

            # 반복 횟수 표시
            rep_text = f"Reps: {current_data['rep_count']}"
            cv2.putText(annotated_frame, rep_text, (10, 110),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)

        # 프레임을 JPEG로 인코딩해서 공유 변수에 저장
        ret, buffer = cv2.imencode('.jpg', annotated_frame)
        if ret:
            with frame_lock:
                latest_jpeg = buffer.tobytes()

def generate_frames():
    """저장된 최신 JPEG을 그대로 스트리밍 (여기서는 캡처/추론을 하지 않음)"""
    while True:
        with frame_lock:
            frame = latest_jpeg

        if frame is not None:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

        time.sleep(0.03)  # 약 30fps로 클라이언트에 전송

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

@app.route('/api/reset-counter', methods=['POST'])
def reset_counter():
    """반복 횟수 카운터 리셋"""
    global wb_rep_count, wb_is_down
    wb_rep_count = 0
    wb_is_down = False
    current_data['rep_count'] = 0
    current_data['counter_state'] = 'IDLE'
    return jsonify({'status': 'ok', 'rep_count': wb_rep_count})

@app.route('/api/no-rep', methods=['POST'])
def no_rep():
    """심판 오버라이드: 방금 카운트된 반복 1회만 무효 처리 (전체 리셋 아님)"""
    global wb_rep_count
    wb_rep_count = max(0, wb_rep_count - 1)
    current_data['rep_count'] = wb_rep_count
    return jsonify({'status': 'ok', 'rep_count': wb_rep_count})

@app.route('/api/status')
def status():
    return jsonify({
        'status': 'ABSC System Running',
        'message': 'Pose detection and squat analysis active'
    })

if __name__ == '__main__':
    capture_thread = threading.Thread(target=capture_loop, daemon=True)
    capture_thread.start()

    # debug=True는 리로더가 프로세스를 두 번 띄워서 웹캠을 중복으로 열려다 오류/지연이 날 수 있어 끔
    app.run(debug=False, threaded=True, port=5000)
