# 🏋️ Angle-Based Squat Counter

**AI 기반 실시간 스쿼트 깊이 판정 및 반복 횟수 자동 카운팅 시스템**

[![Python](https://img.shields.io/badge/Python-3.10-blue)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0-green)](https://flask.palletsprojects.com/)
[![YOLOv8](https://img.shields.io/badge/YOLOv8-Pose-red)](https://github.com/ultralytics/ultralytics)
[![License](https://img.shields.io/badge/License-MIT-yellow)](#license)

---

## 📋 목차

- [개요](#개요)
- [주요 기능](#주요-기능)
- [기술 스택](#기술-스택)
- [설치 방법](#설치-방법)
- [사용 방법](#사용-방법)
- [프로젝트 구조](#프로젝트-구조)
- [개발 진행 상황](#개발-진행-상황)
- [라이선스](#라이선스)

---

## 🎯 개요

**Angle-Based Squat Counter**는 웹캠을 통해 사용자의 스쿼트 자세를 실시간으로 분석하고, 
깊이를 자동으로 판정하며, 반복 횟수를 카운팅하는 AI 기반 포트폴리오 프로젝트입니다.

### 목표
- ✅ 실시간 포즈 감지 (YOLOv8)
- ✅ 스쿼트 깊이 정확한 판정 (벡터 기하학)
- ✅ 반복 횟수 자동 카운팅 (상태 머신)
- ✅ 웹 기반 사용자 인터페이스
- ✅ 포트폴리오 프로젝트로 배포 가능

---

## ✨ 주요 기능

### 1. 실시간 포즈 감지
- YOLOv8 포즈 감지 모델 사용
- 웹캠 입력 처리 (30+ FPS)
- 17개 키포인트 추출

### 2. 스쿼트 깊이 분석
- 벡터 기하학 기반 각도 계산
- 좌/우 무릎 각도 독립 측정
- 3단계 판정 (DEEP / NORMAL / SHALLOW)

```
DEEP:    < 88°   ✅ 충분한 깊이
NORMAL:  88-110° ✓  표준 범위
SHALLOW: ≥ 110°  ⚠️  얕은 스쿼트
```

### 3. 반복 횟수 자동 카운팅
- 상태 머신 기반 정확한 카운팅
- 상태 전이: IDLE → DESCENDING → DEEP → ASCENDING → COMPLETE
- 노이즈 방지 필터링

### 4. 웹 인터페이스
- 실시간 비디오 스트리밍
- 각도 / 깊이 / 신뢰도 표시
- 반복 횟수 실시간 업데이트
- 반응형 디자인 (모바일 호환)

---

## 🛠️ 기술 스택

| 항목 | 기술 | 버전 |
|------|------|------|
| **언어** | Python | 3.10 |
| **웹 프레임워크** | Flask | 3.0+ |
| **포즈 감지** | YOLOv8 (ultralytics) | Latest |
| **컴퓨터 비전** | OpenCV | 4.x |
| **딥러닝** | PyTorch | 2.6+ |
| **프론트엔드** | HTML5 / CSS3 / JavaScript | Vanilla |
| **배포 대상** | Hugging Face Spaces | - |

---

## 📦 설치 방법

### 필수 요구사항
- Python 3.10 (필수)
- 웹캠 (또는 카메라)
- Windows 10 / macOS / Linux

### 설치 단계

#### 1️⃣ 저장소 복제
```bash
git clone https://github.com/Jenny5789/angle-based-squat-counter.git
cd angle-based-squat-counter
```

#### 2️⃣ 가상환경 생성 (Python 3.10)
```bash
# Windows
py -3.10 -m venv venv
venv\Scripts\activate.bat

# macOS / Linux
python3.10 -m venv venv
source venv/bin/activate
```

#### 3️⃣ 의존성 설치
```bash
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

#### 4️⃣ 환경 변수 설정
```bash
# .env 파일 생성
echo SECRET_KEY=your-secret-key > .env
```

#### 5️⃣ 앱 실행
```bash
python app.py
```

브라우저에서 `http://localhost:5000` 열기

---

## 🚀 사용 방법

### 기본 사용법
1. 애플리케이션 실행 (`python app.py`)
2. 웹브라우저에서 `http://localhost:5000` 접속
3. 웹캠 앞에서 스쿼트 수행
4. 실시간으로 깊이 판정 및 반복 횟수 확인

### API 엔드포인트

#### 비디오 스트리밍
```
GET /video_feed
→ Motion JPEG 스트림
```

#### 실시간 데이터
```bash
GET /api/data

응답:
{
    "angle": 85.5,
    "depth": "DEEP",
    "confidence": 0.95,
    "left_knee": 85.0,
    "right_knee": 86.0,
    "frame_count": 150
}
```

#### 상태 확인
```bash
GET /api/status

응답:
{
    "status": "ABSC System Running",
    "message": "Pose detection and squat analysis active"
}
```

---

## 📁 프로젝트 구조

```
ANGLE-BASED-SQUAT-COUNTER/
├── src/                          # 소스 코드
│   ├── pose_detector.py          # YOLOv8 포즈 감지
│   ├── squat_analyzer.py         # 깊이 분석
│   └── repetition_counter.py     # 반복 카운팅
│
├── tests/                        # 유닛 테스트
│   ├── test_pose_detector.py
│   ├── test_squat_analyzer.py
│   └── test_repetition_counter.py
│
├── templates/                    # HTML 템플릿
│   └── index.html                # 웹 UI
│
├── static/                       # 정적 파일
│   ├── css/
│   │   └── style.css             # 스타일시트
│   └── js/
│       └── script.js             # 클라이언트 로직
│
├── docs/                         # 프로젝트 문서
│   ├── SCRUM_PROJECT_PLAN.md
│   └── SPRINT_2_REPORT.md
│
├── data/                         # 데이터 (테스트 비디오 등)
├── venv/                         # 가상환경
├── app.py                        # Flask 메인 앱
├── requirements.txt              # Python 의존성
├── .env                          # 환경 변수
├── .gitignore                    # Git 제외 파일
└── README.md                     # 이 파일
```

---

## 📊 개발 진행 상황

### Sprint 1: Foundation (✅ 완료)
- [x] 프로젝트 구조 설정
- [x] YOLOv8 포즈 모델 통합
- [x] 초기 테스트 코드 작성
- [ ] 테스트 비디오 수집 (이월)

### Sprint 2: Core Features (✅ 완료)
- [x] Flask 앱 구축
- [x] Motion JPEG 스트리밍
- [x] 스쿼트 깊이 분석
- [x] 웹 UI 구현
- [x] 실시간 데이터 API

### Sprint 3: Rep Counting (⏳ 진행 중)
- [x] RepetitionCounter 클래스 (상태 머신)
- [x] 유닛 테스트 (14개 테스트 케이스)
- [ ] app.py 통합
- [ ] 깊이 인식 정확도 개선

### Sprint 4: Deployment (📅 예정)
- [ ] 성능 최적화
- [ ] UI 폴리시
- [ ] Hugging Face Spaces 배포
- [ ] 최종 문서화

---

## 🧪 테스트 실행

```bash
# 전체 테스트
pytest tests/ -v

# RepetitionCounter 테스트만
pytest tests/test_repetition_counter.py -v
```

**테스트 커버리지:** 14개 유닛 테스트 (상태 머신, 카운팅 정확도, 엣지 케이스)

---

## 📝 주요 학습 및 해결한 문제

### 1. MediaPipe → YOLOv8 마이그레이션
- **문제:** MediaPipe 0.10.35에서 `mp.solutions` API 완전 폐기
- **해결:** YOLOv8 포즈 감지 모델로 전환
- **결과:** 더 빠르고 안정적 (30+ FPS)

### 2. Python 버전 호환성
- **원칙:** Python 3.10 필수 (3.14+는 OpenCV/NumPy 미지원)
- **설정:** `py -3.10 -m venv venv`로 명시적 버전 지정

### 3. 상태 머신 기반 반복 카운팅
- **설계:** IDLE → DESCENDING → DEEP → ASCENDING → COMPLETE
- **장점:** 정확한 반복 인식, 노이즈 필터링, 테스트 용이

### 4. Git 모범 사례
- `.pt` 모델 파일은 `.gitignore`에 제외
- 작은 단위의 커밋 (기능별)
- 명확한 커밋 메시지

---

## 🎓 기술 스택 선택 이유

| 기술 | 선택 이유 |
|------|---------|
| **YOLOv8** | 최신 포즈 감지, 빠른 추론 속도 |
| **Flask** | 가볍고 빠른 웹 프레임워크 |
| **OpenCV** | 실시간 비디오 처리 표준 |
| **상태 머신** | 정확한 반복 카운팅, 테스트 용이 |
| **Vanilla JS** | 외부 라이브러리 없이 가볍게 구현 |

---

## 🚀 배포 (예정)

### Hugging Face Spaces 배포
```bash
# 환경 변수 설정
# requirements.txt에서 불필요한 패키지 제거
# Dockerfile 작성
# HF Spaces에 연결
```

---

## 📚 참고 자료

- [YOLOv8 공식 문서](https://docs.ultralytics.com/)
- [Flask 공식 문서](https://flask.palletsprojects.com/)
- [OpenCV 튜토리얼](https://docs.opencv.org/)
- [상태 머신 패턴](https://refactoring.guru/design-patterns/state)

---

## 💡 향후 개선 사항

- [ ] 깊이 인식 정확도 향상 (calibration)
- [ ] 실시간 운동 피드백 (음성/텍스트)
- [ ] 운동 데이터 저장 및 분석
- [ ] 모바일 앱 개발
- [ ] 다중 사용자 지원
- [ ] 다양한 운동 동작 인식 (벤치프레스, 데드리프트 등)

---

## 👤 저자

**EJ (이재)** - GitHub: [@Jenny5789](https://github.com/Jenny5789)

---

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

자세한 내용은 [LICENSE](LICENSE) 파일을 참고하세요.

---

**마지막 업데이트:** 2026년 6월 26일  
**프로젝트 상태:** Sprint 3 진행 중 🚀


---

## 👩‍💻 개발자

- GitHub: [@Jenny5789](https://github.com/Jenny5789)
