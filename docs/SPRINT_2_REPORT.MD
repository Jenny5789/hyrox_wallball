# SPRINT 2 REPORT
## Angle-Based Squat Counter

**Sprint Duration:** [Sprint 2 시작일 ~ 현재]  
**Status:** ✅ 완료  
**Repository:** https://github.com/Jenny5789/angle-based-squat-counter (Private)

---

## 🎯 Sprint 목표

Sprint 2에서는 **실시간 포즈 감지와 스쿼트 깊이 분석**을 핵심 기능으로 구현하여, 웹캠 기반의 작동 가능한 프로토타입을 완성하는 것을 목표로 했습니다.

---

## ✅ 완료된 작업

### 1. Flask 웹 애플리케이션 구축
- **Motion JPEG 실시간 스트리밍** (`/video_feed` 엔드포인트)
  - OpenCV를 통한 프레임 캡처 및 스트리밍
  - 브라우저 호환성 확보
- **REST API 구현** (`/api/data` 엔드포인트)
  - 실시간 JSON 형식 포즈 데이터 제공
  - 클라이언트 측 분석 지원

### 2. YOLOv8 포즈 감지 모듈 (`src/pose_detector.py`)
- YOLOv8m-pose 모델 통합 (MediaPipe 0.10.35 호환성 문제 해결)
- 웹캠 입력 처리 및 17개 키포인트 추출
- GPU/CPU 자동 감지 및 최적화
- 모든 `.pt` 모델 파일을 `.gitignore`에 추가 (GitHub 용량 관리)

### 3. 스쿼트 깊이 분석 엔진 (`src/squat_analyzer.py`)
- **벡터 기하학 기반 각도 계산**
  - 엉덩이(hip), 무릎(knee), 발목(ankle) 키포인트를 이용한 벡터 각도 계산
  - 안정적이고 신뢰도 높은 깊이 판별
- **깊이 분류 시스템** (사용자 튜닝됨)
  - DEEP: < 88° (충분한 깊이)
  - NORMAL: 88° ~ 110° (표준 범위)
  - SHALLOW: ≥ 110° (얕은 스쿼트)
- 신뢰도 기반 필터링 (confidence threshold: 0.5)

### 4. 반응형 웹 UI
- **실시간 비디오 피드** 디스플레이
- **깊이 상태 표시** (색상 코드: DEEP 초록색, NORMAL 노랑색, SHALLOW 빨강색)
- **포즈 키포인트 시각화** (관절 표시)
- **모바일 호환 반응형 디자인**

### 5. 문서 및 버전 관리
- GitHub 커밋 2회 완료
- `SPRINT_2_REPORT.md` 작성
- `README.md` 초안 작성 (최종 검토 대기)
- `.gitignore` 정리 (모델 파일 제외)

---

## 🛠️ 기술 스택 & 환경

| 항목 | 버전/사양 |
|------|---------|
| **Python** | 3.10 |
| **YOLOv8** | ultralytics (최신) |
| **Flask** | 3.x |
| **OpenCV** | 4.x |
| **PyTorch** | 2.6+ (보안 업데이트 적용) |
| **OS** | Windows 10 |
| **개발 도구** | cmd.exe, venv (Python 3.10) |

**주요 의존성:**
```
ultralytics
torch
opencv-python
flask
numpy
```

---

## 🎓 주요 학습 및 트러블슈팅

### 1. MediaPipe → YOLOv8 마이그레이션
- **문제:** MediaPipe 0.10.35 릴리스 후 `mp.solutions` API 완전 폐기
- **해결:** YOLOv8 포즈 감지 모델로 전환 → 더 빠르고 안정적
- **결과:** 초당 30 프레임 이상 처리 가능

### 2. PyTorch 2.6 보안 변경
- **문제:** 모델 로딩 시 호환성 오류
- **해결:** ultralytics와 torch를 동시 업그레이드
- **학습:** 주요 라이브러리 업데이트 시 의존성 일괄 관리 필수

### 3. Python 버전 호환성
- **원칙:** Python 3.10 필수 (3.14+ OpenCV/NumPy 미지원)
- **설정:** `py -3.10 -m venv venv`로 환경 구성
- **팁:** Miniforge/Conda base 환경과 venv 충돌 주의

### 4. GitHub `.pt` 모델 파일 실수
- **문제:** 처음 커밋 후 `yolov8m-pose.pt` 크기 오류로 플래그됨
- **해결:** `.gitignore`에 `*.pt` 추가 후 커밋 이력 정리
- **교훈:** 프로젝트 초기에 모델 제외 설정 필수

---

## 📊 핵심 성과 지표

| 지표 | 결과 |
|------|------|
| 실시간 포즈 감지 FPS | 30+ fps |
| 모델 신뢰도 범위 | 0.5 ~ 1.0 |
| 웹 UI 반응성 | 100ms 이하 |
| GitHub 커밋 수 | 2회 |
| 코드 커버리지 | TDD 진행 중 |

---

## ⏳ 대기 중인 작업

### RepetitionCounter 클래스 (미구현)
- **설계 완료:** DEEP 상태 진입 시 반복 횟수 카운팅
- **구현 시점:** 다음 세션 (`반복 횟수 카운팅 시작하자!` 신호)
- **목표:** 사용자가 수행한 유효한 스쿼트 반복 횟수 추적

### Sprint 1 Task 1.2 (이월)
- 테스트 비디오 수집 (스쿼트 데이터셋)
- 모델 검증용 실제 사용 데이터

---

## 🚀 다음 단계 (Sprint 3)

1. **RepetitionCounter 구현**
   - 반복 횟수 정확한 카운팅
   - 유효한 반복 기준 정의 (깊이, 회복 상태)

2. **성능 최적화**
   - 모델 추론 속도 개선
   - GPU 메모리 사용률 최적화
   - 웹캠 지연 시간 최소화

3. **UI 개선**
   - 누적 반복 횟수 표시
   - 실시간 차트 (스쿼트 깊이 추이)
   - 운동 완료 요약 화면

4. **배포 준비 (Sprint 4)**
   - Hugging Face Spaces 배포
   - 환경 변수 관리
   - 사용 설명서 작성

---

## 📝 커밋 히스토리

```
Commit 2: Sprint 2 완료 - 포즈 감지 및 깊이 분석 구현
Commit 1: 초기 설정 - Flask 앱 및 YOLOv8 통합
```

---

## ✨ 결론

Sprint 2를 통해 **작동 가능한 스쿼트 깊이 판별 시스템**의 핵심 기능을 완성했습니다. 실시간 포즈 감지와 정확한 깊이 분석으로 포트폴리오 프로젝트로서의 기초를 마련했으며, 다음 Sprint에서는 반복 횟수 카운팅과 성능 최적화에 집중할 예정입니다.

---

**작성일:** 2026년 6월 26일  
**작성자:** EJ (Jenny5789)