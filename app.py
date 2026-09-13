from flask import Flask, render_template, Response, jsonify, request
import cv2
import numpy as np
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
    'rep_target': 20,
    'counter_state': 'IDLE',
    'frame_count': 0,
    'camera_connected': True,
    'guidance': '',
    'athlete_name': 'GUEST'
}

# 반복 횟수는 무릎 각도 기준으로 센다 (카메라 거리/각도에 안 흔들리고, 몇 도인지로
# 바로 조절 가능해서 직관적임). REP_ANGLE_DOWN 이하로 내려갔다가 REP_ANGLE_UP
# 이상으로 다시 올라오면 1회로 카운트. 두 값 사이에 간격(히스테리시스)을 둬서
# 경계값 근처에서 흔들려도 중복 카운트되지 않게 함.
REP_ANGLE_DOWN = 120.0  # 이 각도 이하면 DOWN (낮을수록 더 깊이 앉아야 인정)
REP_ANGLE_UP = 130.0    # 이 각도 이상 올라와야 UP으로 확정

rep_state = 'UP'  # UP -> DESCENDING -> DOWN -> ASCENDING -> UP
wb_rep_count = 0

# 얕은 시도/덜 일어선 시도처럼 "지금 이 순간" 발생한 문제는 몇 초간만 안내
# 문구로 보여주고 사라지게 한다 (카메라/자세 문제처럼 계속되는 상황이 아니라서).
TRANSIENT_GUIDANCE_SECONDS = 3.0
transient_guidance = ''
transient_guidance_until = 0.0

# 카메라 read() 실패가 이 횟수만큼 연속되면 "연결 안 됨"으로 판단
CAMERA_FAIL_THRESHOLD = 10
camera_fail_count = 0

# 화면에 keypoint 스켈레톤을 그릴지 여부 (프론트 토글 버튼으로 전환)
show_keypoints = False

# 캡처+추론은 이 스레드 하나에서만 수행하고 결과(최신 JPEG)를 여기 저장한다.
# 요청 스레드(/video_feed, /api/data)마다 캡처+추론을 반복하면 GIL/CPU/GPU를
# 독점해서 새 연결조차 못 받을 정도로 서버가 막히므로, 무거운 작업과 요청 처리를
# 분리한다.
latest_jpeg = None
frame_lock = threading.Lock()
capture_running = True

def build_no_camera_frame():
    """카메라를 읽지 못할 때 빈 화면 대신 보여줄 안내 프레임을 만든다."""
    frame = np.zeros((720, 1280, 3), dtype=np.uint8)
    text = "NO CAMERA SIGNAL"
    font = cv2.FONT_HERSHEY_SIMPLEX
    scale, thickness = 1.8, 3
    (text_w, text_h), _ = cv2.getTextSize(text, font, scale, thickness)
    x = (frame.shape[1] - text_w) // 2
    y = (frame.shape[0] + text_h) // 2
    cv2.putText(frame, text, (x, y), font, scale, (0, 0, 255), thickness)
    ret, buffer = cv2.imencode('.jpg', frame)
    return buffer.tobytes() if ret else None

NO_CAMERA_JPEG = build_no_camera_frame()

def set_transient_guidance(message):
    """얕은 시도/덜 일어선 시도 같은 순간적인 문제를 몇 초간 안내 문구로 띄운다."""
    global transient_guidance, transient_guidance_until
    transient_guidance = message
    transient_guidance_until = time.time() + TRANSIENT_GUIDANCE_SECONDS

def get_active_transient_guidance():
    """아직 유효 시간이 지나지 않은 순간 안내 문구를 반환 (지났으면 빈 문자열)"""
    if transient_guidance and time.time() < transient_guidance_until:
        return transient_guidance
    return ''

def update_rep_state(angle):
    """4단계 상태 머신(UP -> DESCENDING -> DOWN -> ASCENDING -> UP)으로 반복을
    카운트한다. 내려가다가 깊이를 못 채우고 다시 올라오면 "얕음"으로, 다 올라오지
    않고 다시 내려가면 "덜 일어섬"으로 안내 문구를 띄운다."""
    global rep_state, wb_rep_count

    if not angle:
        current_data['counter_state'] = 'UNKNOWN'
        return

    if rep_state == 'UP':
        if angle < REP_ANGLE_UP:
            rep_state = 'DESCENDING'
    elif rep_state == 'DESCENDING':
        if angle <= REP_ANGLE_DOWN:
            rep_state = 'DOWN'
        elif angle >= REP_ANGLE_UP:
            set_transient_guidance('더 깊이 앉으세요')
            rep_state = 'UP'
    elif rep_state == 'DOWN':
        if angle > REP_ANGLE_DOWN:
            rep_state = 'ASCENDING'
    elif rep_state == 'ASCENDING':
        if angle >= REP_ANGLE_UP:
            wb_rep_count += 1
            current_data['rep_count'] = wb_rep_count
            rep_state = 'UP'
        elif angle <= REP_ANGLE_DOWN:
            set_transient_guidance('완전히 일어선 후 다시 앉으세요')
            rep_state = 'DOWN'

    current_data['counter_state'] = rep_state

def capture_loop():
    """웹캠 캡처 + 포즈 추정 + 분석을 반복하는 백그라운드 스레드"""
    global latest_jpeg, current_data, camera_fail_count

    frame_count = 0

    while capture_running:
        success, frame = camera.read()
        if not success:
            camera_fail_count += 1
            if camera_fail_count >= CAMERA_FAIL_THRESHOLD:
                current_data['camera_connected'] = False
                current_data['guidance'] = '카메라 신호 없음'
                if NO_CAMERA_JPEG is not None:
                    with frame_lock:
                        latest_jpeg = NO_CAMERA_JPEG
            time.sleep(0.05)
            continue

        camera_fail_count = 0
        current_data['camera_connected'] = True

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
            current_data['confidence'] = verdict['confidence']

            # 판정은 실제 카운트와 같은 기준(REP_ANGLE_DOWN)으로 둘로만 나눔.
            # (예전엔 SquatAnalyzer의 88/110도 기준으로 DEEP/NORMAL/SHALLOW를
            # 따로 보여줘서 실제 카운트 기준과 안 맞아 헷갈렸음)
            if average_angle:
                current_data['depth_state'] = 'DEEP' if average_angle <= REP_ANGLE_DOWN else 'SHALLOW'
            else:
                current_data['depth_state'] = 'UNKNOWN'

            # 실제 카운트: 무릎 각도 기준
            update_rep_state(average_angle)

            if average_angle:
                # 골반/무릎이 잘 보여서 각도 계산이 되는 정상 상태.
                # 얕은 시도/덜 일어선 시도가 방금 있었으면 그 안내만 잠깐 보여줌
                current_data['guidance'] = get_active_transient_guidance()
            else:
                current_data['guidance'] = '몸 전체(엉덩이~발목)가 보이도록 카메라에서 물러나 주세요'
        else:
            current_data['knee_angle'] = 0
            current_data['depth_state'] = 'UNKNOWN'
            current_data['confidence'] = 0
            current_data['counter_state'] = 'UNKNOWN'
            current_data['guidance'] = '카메라 앞에 서주세요'

        current_data['frame_count'] = frame_count
        frame_count += 1

        # 각도/판정/반복 횟수는 화면 쪽 HTML 오버레이(텔레메트리 패널)에서 이미
        # 표시하므로, 영상 픽셀에 직접 텍스트를 굽던 예전 코드는 제거함
        # (해상도에 따라 잘려 보이고 중복이었음)

        # 스켈레톤 표시가 꺼져 있으면 원본 프레임을, 켜져 있으면 keypoint가
        # 그려진 프레임을 스트리밍용으로 사용 (감지/카운팅 자체는 항상 수행됨)
        output_frame = annotated_frame if show_keypoints else frame

        # 프레임을 JPEG로 인코딩해서 공유 변수에 저장
        ret, buffer = cv2.imencode('.jpg', output_frame)
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
    data = dict(current_data)
    data['show_keypoints'] = show_keypoints
    return jsonify(data)

@app.route('/api/toggle-keypoints', methods=['POST'])
def toggle_keypoints():
    """영상에 keypoint 스켈레톤을 그릴지 켜고 끔"""
    global show_keypoints
    show_keypoints = not show_keypoints
    return jsonify({'status': 'ok', 'show_keypoints': show_keypoints})

@app.route('/api/reset-counter', methods=['POST'])
def reset_counter():
    """반복 횟수 카운터 리셋"""
    global wb_rep_count, rep_state
    wb_rep_count = 0
    rep_state = 'UP'
    current_data['rep_count'] = 0
    current_data['counter_state'] = 'IDLE'
    return jsonify({'status': 'ok', 'rep_count': wb_rep_count})

@app.route('/api/set-goal', methods=['POST'])
def set_goal():
    """목표 반복 횟수 변경"""
    body = request.get_json(silent=True) or {}
    try:
        goal = int(body.get('goal'))
    except (TypeError, ValueError):
        return jsonify({'status': 'error', 'message': 'invalid goal'}), 400

    if goal <= 0:
        return jsonify({'status': 'error', 'message': 'goal must be positive'}), 400

    current_data['rep_target'] = goal
    return jsonify({'status': 'ok', 'rep_target': goal})

@app.route('/api/set-athlete', methods=['POST'])
def set_athlete():
    """선수 이름 변경"""
    body = request.get_json(silent=True) or {}
    name = str(body.get('name', '')).strip()[:20]

    if not name:
        return jsonify({'status': 'error', 'message': 'name must not be empty'}), 400

    current_data['athlete_name'] = name
    return jsonify({'status': 'ok', 'athlete_name': name})

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
