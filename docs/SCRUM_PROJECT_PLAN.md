# Angle-Based Squat Counter
## Master Scrum Project Plan

**Project:** Real-time Squat Depth Analysis System using Webcam  
**Duration:** ~2 months (4 Sprints)  
**Methodology:** Scrum + TDD + Kanban Hybrid  
**Repository:** https://github.com/Jenny5789/angle-based-squat-counter (Private)  
**Deployment Target:** Hugging Face Spaces  

---

## 📋 Project Overview

### Goal
포트폴리오 프로젝트로서 **작동 가능한 실시간 스쿼트 깊이 판별 시스템**을 구축.
웹캠을 통해 사용자의 스쿼트 자세를 분석하고, 깊이를 실시간으로 피드백하며, 반복 횟수를 자동으로 카운팅.

### Tech Stack
- **Python:** 3.10 (필수)
- **Pose Detection:** YOLOv8 (ultralytics)
- **Web Framework:** Flask
- **Computer Vision:** OpenCV
- **Deep Learning:** PyTorch 2.6+
- **Environment:** Windows 10, cmd.exe, venv
- **Testing:** TDD (pytest)

### Key Constraints
- Python 3.10 필수 (3.14+는 OpenCV/NumPy 미지원)
- 모든 `.pt` 모델 파일은 `.gitignore`에 제외
- cmd.exe 사용 (PowerShell의 한글 경로 문제 회피)
- 메모리 최적화 필수 (리소스 제한 환경 고려)

---

## 🎯 4-Sprint Roadmap

### **SPRINT 1: Foundation & Initial Setup**
**Duration:** Week 1-2  
**Goal:** 프로젝트 기초 구축 및 포즈 감지 모델 통합

#### Tasks

| Task ID | Task Name | Status | Assignee | Notes |
|---------|-----------|--------|----------|-------|
| 1.1 | 프로젝트 구조 설정 (src/, tests/, docs/) | ✅ | EJ | 완료 |
| 1.2 | 테스트 비디오 수집 (스쿼트 데이터셋) | ⏳ | EJ | **이월됨** |
| 1.3 | YOLOv8 포즈 모델 통합 (`pose_detector.py`) | ✅ | EJ | 완료 |
| 1.4 | 초기 테스트 코드 작성 (TDD) | ✅ | EJ | 진행 중 |
| 1.5 | GitHub 저장소 초기화 & .gitignore 설정 | ✅ | EJ | 완료 |

#### Deliverables
- ✅ `src/pose_detector.py` (17 keypoint 추출)
- ✅ `docs/` 폴더 구조
- ✅ `.gitignore` (*.pt, venv 포함)
- ✅ Initial README draft
- ⏳ Test video dataset (이월)

---

### **SPRINT 2: Core Feature Development**
**Duration:** Week 3-4  
**Goal:** 실시간 포즈 감지 + 스쿼트 깊이 분석 구현

#### Tasks

| Task ID | Task Name | Status | Assignee | Notes |
|---------|-----------|--------|----------|-------|
| 2.1 | Flask 앱 구축 + Motion JPEG 스트리밍 | ✅ | EJ | 완료 |
| 2.2 | REST API 엔드포인트 구현 (/api/data) | ✅ | EJ | 완료 |
| 2.3 | 스쿼트 깊이 분석 엔진 (벡터 기하학) | ✅ | EJ | 완료 |
| 2.4 | 깊이 분류 시스템 (DEEP/NORMAL/SHALLOW) | ✅ | EJ | 완료 |
| 2.5 | 반응형 웹 UI (HTML/CSS/JS) | ✅ | EJ | 완료 |
| 2.6 | 실시간 포즈 키포인트 시각화 | ✅ | EJ | 완료 |
| 2.7 | Sprint 2 보고서 작성 | ✅ | EJ | 완료 |

#### Deliverables
- ✅ `app.py` (Flask 애플리케이션)
- ✅ `src/squat_analyzer.py` (깊이 계산)
- ✅ `templates/index.html` + `static/style.css` + `static/script.js`
- ✅ `SPRINT_2_REPORT.md`
- ✅ 2x GitHub commits

#### Key Achievements
- 실시간 포즈 감지: 30+ FPS
- 깊이 분류 정확도: 신뢰도 기반 (conf > 0.5)
- MediaPipe → YOLOv8 마이그레이션 성공
- `.pt` 모델 파일 관리 자동화

---

### **SPRINT 3: Rep Counting & Performance Optimization**
**Duration:** Week 5-6  
**Goal:** 반복 횟수 카운팅 + 성능 최적화

#### Tasks

| Task ID | Task Name | Status | Assignee | Notes |
|---------|-----------|--------|----------|-------|
| 3.1 | RepetitionCounter 클래스 구현 | ⏳ | EJ | 다음 세션 시작 |
| 3.2 | 반복 횟수 카운팅 로직 (상태 머신) | ⏳ | EJ | DEEP 상태 진입 감지 |
| 3.3 | 유효한 반복 기준 정의 (깊이 + 회복) | ⏳ | EJ | 비즈니스 로직 |
| 3.4 | UI에 반복 횟수 표시 | ⏳ | EJ | 실시간 카운터 |
| 3.5 | 모델 추론 속도 최적화 | ⏳ | EJ | GPU 메모리 관리 |
| 3.6 | 웹캠 지연 시간 최소화 | ⏳ | EJ | 버퍼링 최적화 |
| 3.7 | Sprint 3 보고서 작성 | ⏳ | EJ | |

#### Deliverables
- `src/repetition_counter.py` (Rep counting logic)
- Updated UI with live counter display
- Performance benchmark report
- `SPRINT_3_REPORT.md`

#### Success Criteria
- Rep counting accuracy ≥ 95%
- 추론 지연 시간 < 100ms
- 웹캠 프레임율 유지: 30+ FPS

---

### **SPRINT 4: Polish & Deployment**
**Duration:** Week 7-8  
**Goal:** UI 완성 + 배포 준비 + 최종 문서화

#### Tasks

| Task ID | Task Name | Status | Assignee | Notes |
|---------|-----------|--------|----------|-------|
| 4.1 | 운동 완료 요약 화면 (대시보드) | ⏳ | EJ | 최종 리포트 UI |
| 4.2 | 깊이 추이 차트 구현 | ⏳ | EJ | 시각화 |
| 4.3 | 설정 및 튜닝 페이지 추가 | ⏳ | EJ | 깊이 임계값 조정 |
| 4.4 | Hugging Face Spaces 배포 준비 | ⏳ | EJ | 환경 변수, requirements.txt |
| 4.5 | 사용 설명서 작성 | ⏳ | EJ | README 최종 버전 |
| 4.6 | 배포 및 테스트 | ⏳ | EJ | HF Spaces에 배포 |
| 4.7 | 포트폴리오 프레젠테이션 준비 | ⏳ | EJ | 데모 영상, 설명 |
| 4.8 | Sprint 4 최종 보고서 | ⏳ | EJ | Project retrospective |

#### Deliverables
- Enhanced UI with dashboard
- `requirements.txt` (production)
- `README.md` (최종 버전)
- Deployment guide
- `SPRINT_4_REPORT.md` (프로젝트 완료 보고서)
- Demo video or presentation materials

#### Success Criteria
- HF Spaces에서 정상 작동
- 배포 후 실제 사용 환경에서 테스트 완료
- 포트폴리오 항목으로 즉시 사용 가능

---

## 📊 Project Timeline

```
Week 1-2  │ Sprint 1: Foundation      │ ✅ (진행 중, Task 1.2 이월)
Week 3-4  │ Sprint 2: Core Features   │ ✅ (완료)
Week 5-6  │ Sprint 3: Rep Counting    │ ⏳ (예정)
Week 7-8  │ Sprint 4: Deployment      │ ⏳ (예정)
          │ TOTAL: ~2 months          │
```

---

## 🔄 Methodology: Scrum + TDD + Kanban Hybrid

### Scrum Elements
- **Sprint Duration:** 2주 (2 sprints)
- **Sprint Review:** 각 Sprint 끝에 보고서 작성
- **Daily Standup:** 문제 발생 시 즉시 해결

### TDD Elements
- 모든 새로운 기능은 **테스트 먼저 작성**
- `test_*.py` 파일로 기능 검증
- pytest를 통한 자동화 테스트

### Kanban Elements
- Task 상태: TODO → In Progress → Review → Done
- 우선순위 기반 작업 순서 조정
- 이월 Task는 다음 Sprint에서 우선 처리

---

## 📁 Project Structure

```
ANGLE-BASED-SQUAT-COUNTER/
├── venv/                      # Python 3.10 가상환경
├── src/
│   ├── pose_detector.py       # YOLOv8 포즈 감지
│   ├── squat_analyzer.py      # 스쿼트 깊이 분석 (완료)
│   └── repetition_counter.py  # 반복 횟수 카운팅 (예정)
├── templates/
│   └── index.html             # 웹 UI (완료)
├── static/
│   ├── style.css              # 스타일 (완료)
│   └── script.js              # 클라이언트 로직 (완료)
├── app.py                     # Flask 메인 앱 (완료)
├── test_pose_detector.py      # 포즈 감지 테스트
├── test_squat_analyzer.py     # 깊이 분석 테스트
├── test_repetition_counter.py # 반복 카운팅 테스트 (예정)
├── .gitignore                 # (*.pt, venv 포함) ✅
├── requirements.txt           # Python 의존성
├── README.md                  # 프로젝트 설명 (초안 완료)
└── docs/
    ├── SCRUM_PROJECT_PLAN.md          # 이 파일
    ├── SPRINT_1_REPORT.md             # (작성 필요)
    └── SPRINT_2_REPORT.md             # ✅ 완료
```

---

## ⚙️ Development Rules

### Environment Setup
```bash
# 프로젝트 폴더로 이동
cd D:\JEN\VISION_AI\ANGLE-BASED-SQUAT-COUNTER

# Python 3.10 venv 생성
py -3.10 -m venv venv

# 활성화 (cmd.exe 사용!)
venv\Scripts\activate.bat

# 의존성 설치
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

### Git Workflow
- 각 Sprint 완료 후 GitHub에 commit
- Commit 메시지: `Sprint N - [주요 기능] 구현` 형식
- 모든 `.pt` 파일은 자동으로 제외

### Testing & Documentation
- 모든 함수는 docstring 포함
- 각 Sprint 끝에 `SPRINT_N_REPORT.md` 작성
- 테스트 커버리지 목표: > 80%

---

## 🎓 Key Learnings & Principles

1. **Python 3.10은 필수**
   - 3.14+는 OpenCV/NumPy 미지원
   - venv 생성 시 `py -3.10 -m venv venv` 명시 필수

2. **MediaPipe → YOLOv8 마이그레이션**
   - MediaPipe 0.10.35에서 `mp.solutions` API 완전 폐기
   - YOLOv8이 더 빠르고 안정적

3. **PyTorch 2.6 보안 변경**
   - ultralytics와 torch는 동시 업그레이드 필요
   - 버전 호환성 항상 확인

4. **모델 파일 관리**
   - `.pt` 파일은 절대 GitHub에 커밋하지 말 것
   - 처음부터 `.gitignore`에 포함

5. **Miniforge/Conda와 venv 충돌**
   - Conda base 환경 비활성화
   - standalone Python 3.10 venv 사용

---

## 📋 Current Status

**Completed:**
- ✅ Sprint 1 기초 (Task 1.2 이월)
- ✅ Sprint 2 완료 (포즈 감지 + 깊이 분석)
- ✅ `SPRINT_2_REPORT.md` 작성

**In Progress:**
- ⏳ Sprint 3 준비 (RepetitionCounter 구현 대기)

**Upcoming:**
- ⏳ Sprint 3: Rep counting & optimization
- ⏳ Sprint 4: Deployment & polish

---

## 🚀 Next Session Trigger

**명령어:** `반복 횟수 카운팅 시작하자!`  
→ Sprint 3 시작: RepetitionCounter 구현 시작

---

**문서 작성:** 2026년 6월 26일  
**마지막 업데이트:** 2026년 6월 26일  
**프로젝트 상태:** On Track ✅