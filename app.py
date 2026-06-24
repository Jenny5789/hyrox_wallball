from flask import Flask, render_template, Response
import cv2
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev')

# 웹캠 객체
camera = cv2.VideoCapture(0)

def generate_frames():
    """웹캠 프레임 생성"""
    while True:
        success, frame = camera.read()
        if not success:
            break
        
        # 프레임을 JPEG로 인코딩
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        
        # Motion JPEG 스트리밍 포맷
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/api/status')
def status():
    return {'status': 'HYROX System Running', 'message': 'Ready for squat detection'}

if __name__ == '__main__':
    app.run(debug=True, port=5000)