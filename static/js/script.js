/**
 * script.js - Angle-Based Squat Counter
 * 실시간 데이터 수신 및 UI 업데이트
 */

// ============================================================================
// 1. 상태 관리
// ============================================================================

const state = {
    angle: 0,
    depth: 'READY',
    confidence: 0,
    repCount: 0,
    repTarget: 100,
    counterState: 'IDLE',
    isPaused: false,
    frameCount: 0,
    unbrokenShownFor: 0, // 이 rep_count 값에 대해 이미 배너를 띄웠는지 기록 (중복 표시 방지)
    minAngle: null,
    maxAngle: null,
    sessionStart: Date.now(),
    showKeypoints: true,
    guidance: '',
    athleteName: 'GUEST',
};

// ============================================================================
// 2. API 통신
// ============================================================================

/**
 * 서버에서 현재 데이터 가져오기
 */
async function fetchData() {
    try {
        const response = await fetch('/api/data');
        if (!response.ok) throw new Error('API 에러');

        const data = await response.json();

        if (data.status === 'ok') {
            state.angle = data.knee_angle || 0;
            state.depth = data.depth_state || 'UNKNOWN';
            state.confidence = data.confidence || 0;
            state.repCount = data.rep_count || 0;
            state.repTarget = data.rep_target || 100;
            state.counterState = data.counter_state || 'IDLE';
            state.showKeypoints = data.show_keypoints !== undefined ? data.show_keypoints : state.showKeypoints;
            state.guidance = data.guidance || '';
            state.athleteName = data.athlete_name || 'GUEST';
            state.frameCount++;

            trackAngleExtremes();
            updateUI();
            checkUnbroken();
            updateKeypointsButton();
            updateGuidance();

            const statusEl = document.getElementById('status');
            if (statusEl) statusEl.textContent = 'CONNECTED';
            return true;
        }
    } catch (error) {
        console.error('데이터 가져오기 실패:', error);
        const statusEl = document.getElementById('status');
        if (statusEl) statusEl.textContent = 'DISCONNECTED';
        return false;
    }
}

/**
 * 반복 카운터 리셋
 */
async function resetCounter() {
    if (!confirm('반복 횟수를 리셋하시겠습니까?')) return;

    try {
        const response = await fetch('/api/reset-counter', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });

        if (response.ok) {
            state.repCount = 0;
            state.frameCount = 0;
            state.unbrokenShownFor = 0;
            state.minAngle = null;
            state.maxAngle = null;
            state.sessionStart = Date.now();
            clearTimeline();
            console.log('반복 카운터 리셋됨');
        }
    } catch (error) {
        console.error('리셋 실패:', error);
    }
}

/**
 * 영상에 keypoint 스켈레톤 표시 켜기/끄기
 */
async function toggleKeypoints() {
    try {
        const response = await fetch('/api/toggle-keypoints', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });

        if (response.ok) {
            const data = await response.json();
            state.showKeypoints = data.show_keypoints;
            updateKeypointsButton();
        }
    } catch (error) {
        console.error('POSE 토글 실패:', error);
    }
}

function updateKeypointsButton() {
    const btn = document.getElementById('keypoints-btn');
    if (btn) {
        btn.textContent = state.showKeypoints ? 'POSE: ON' : 'POSE: OFF';
    }
}

/**
 * 카메라/자세 안내 문구를 영상 위에 표시 (없으면 숨김)
 */
function updateGuidance() {
    const banner = document.getElementById('guidance-banner');
    if (!banner) return;

    if (state.guidance) {
        banner.textContent = state.guidance;
        banner.hidden = false;
    } else {
        banner.hidden = true;
    }
}

/**
 * 목표 반복 횟수(GOAL) 변경
 */
async function updateGoal(newGoal) {
    const goal = parseInt(newGoal, 10);
    if (!goal || goal <= 0) return;

    try {
        const response = await fetch('/api/set-goal', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ goal })
        });

        if (response.ok) {
            const data = await response.json();
            state.repTarget = data.rep_target;
            state.unbrokenShownFor = 0;
            updateRepPercentAndGoal();
        }
    } catch (error) {
        console.error('목표 횟수 변경 실패:', error);
    }
}

/**
 * NO-REP: 방금 카운트된 반복 1회만 무효 처리 (전체 리셋 아님)
 */
async function noRep() {
    try {
        const response = await fetch('/api/no-rep', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });

        if (response.ok) {
            const data = await response.json();
            state.repCount = data.rep_count;
            updateRepCount();
            logNoRep();
            console.log('NO-REP 처리됨, 현재 카운트:', data.rep_count);
        }
    } catch (error) {
        console.error('NO-REP 처리 실패:', error);
    }
}

// ============================================================================
// 3. UI 업데이트
// ============================================================================

function updateUI() {
    updateAngle();
    updateDepth();
    updateConfidence();
    updateRepCount();
    updateRepPercentAndGoal();
    updateMinMaxAngle();
    updateCounterStatus();
    updateFrameCount();
    updateSessionClock();
    updateAthleteName();
}

/**
 * 선수 이름 입력창 동기화 (입력 중이면 서버 값으로 덮어쓰지 않음)
 */
function updateAthleteName() {
    const nameEl = document.getElementById('athlete-name-input');
    if (nameEl && document.activeElement !== nameEl) {
        nameEl.value = state.athleteName;
    }
}

/**
 * 선수 이름 변경 저장
 */
async function updateAthleteNameOnServer(newName) {
    const name = newName.trim();
    if (!name) return;

    try {
        const response = await fetch('/api/set-athlete', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name })
        });

        if (response.ok) {
            const data = await response.json();
            state.athleteName = data.athlete_name;
        }
    } catch (error) {
        console.error('선수 이름 변경 실패:', error);
    }
}

/**
 * 각도 업데이트
 */
function updateAngle() {
    const angleEl = document.getElementById('angle');
    if (angleEl) {
        angleEl.textContent = state.angle.toFixed(1) + '°';
    }
}

/**
 * 깊이 상태 업데이트 (판정 칩 자체에 색상 클래스를 붙임)
 */
const DEPTH_LABELS = {
    DEEP: '깊음',
    SHALLOW: '얕음',
    UNKNOWN: '확인 불가',
    READY: 'READY',
};

function updateDepth() {
    const depthEl = document.getElementById('depth');
    if (depthEl) {
        depthEl.textContent = DEPTH_LABELS[state.depth] || state.depth;

        depthEl.classList.remove('deep', 'shallow');

        if (state.depth === 'DEEP') {
            depthEl.classList.add('deep');
        } else if (state.depth === 'SHALLOW') {
            depthEl.classList.add('shallow');
        }
    }
}

/**
 * 신뢰도 업데이트
 */
function updateConfidence() {
    const confidenceEl = document.getElementById('confidence');
    if (confidenceEl) {
        confidenceEl.textContent = (state.confidence * 100).toFixed(1) + '%';
    }
}

/**
 * 반복 횟수 업데이트
 */
function updateRepCount() {
    const repEl = document.getElementById('rep-count');
    if (repEl) {
        const oldValue = parseInt(repEl.textContent) || 0;

        if (state.repCount > oldValue) {
            repEl.classList.remove('pulse');
            void repEl.offsetWidth; // 리플로우 강제
            repEl.classList.add('pulse');
        }

        repEl.textContent = state.repCount;
    }
}

/**
 * 반복 퍼센트 / 목표치 업데이트
 */
function updateRepPercentAndGoal() {
    const percentEl = document.getElementById('rep-percent');
    const goalEl = document.getElementById('rep-goal-input');
    const fillEl = document.getElementById('rep-progress-fill');

    // 입력창에 포커스가 가 있으면(입력 중) 서버 값으로 덮어쓰지 않음
    if (goalEl && document.activeElement !== goalEl) {
        goalEl.value = state.repTarget;
    }

    const pct = state.repTarget > 0
        ? Math.min(100, Math.round((state.repCount / state.repTarget) * 100))
        : 0;

    if (percentEl) percentEl.textContent = pct + '%';
    if (fillEl) fillEl.style.width = pct + '%';
}

/**
 * 최소/최대 무릎 각도 기록
 */
function trackAngleExtremes() {
    if (!state.angle) return;

    if (state.minAngle === null || state.angle < state.minAngle) {
        state.minAngle = state.angle;
    }
    if (state.maxAngle === null || state.angle > state.maxAngle) {
        state.maxAngle = state.angle;
    }
}

function updateMinMaxAngle() {
    const minEl = document.getElementById('min-angle');
    const maxEl = document.getElementById('max-angle');

    if (minEl) minEl.textContent = state.minAngle !== null ? state.minAngle.toFixed(1) + '°' : '--°';
    if (maxEl) maxEl.textContent = state.maxAngle !== null ? state.maxAngle.toFixed(1) + '°' : '--°';
}

/**
 * 카운터 상태 업데이트 (숨김 디버그용)
 */
const COUNTER_STATE_LABELS = {
    UP: 'STAND',
    DOWN: 'SQUAT',
};

function updateCounterStatus() {
    const statusEl = document.getElementById('counter-state');
    if (statusEl) {
        statusEl.textContent = COUNTER_STATE_LABELS[state.counterState] || state.counterState;
    }
}

/**
 * 프레임 카운트 업데이트
 */
function updateFrameCount() {
    const frameEl = document.getElementById('frame-count');
    if (frameEl) {
        frameEl.textContent = state.frameCount;
    }
}

/**
 * 세션 시작 후 경과 시간을 "mm:ss.s" 문자열로 반환
 */
function getElapsedTimeString() {
    const elapsed = (Date.now() - state.sessionStart) / 1000;
    const minutes = Math.floor(elapsed / 60);
    const seconds = (elapsed % 60).toFixed(1).padStart(4, '0');
    return `${String(minutes).padStart(2, '0')}:${seconds}`;
}

/**
 * 세션 경과 시간 표시 (mm:ss.s)
 */
function updateSessionClock() {
    const clockEl = document.getElementById('session-clock');
    if (!clockEl) return;

    clockEl.textContent = getElapsedTimeString();
}

/**
 * 목표 횟수(UNBROKEN)에 도달했는지 확인하고, 도달했으면 축하 배너를 띄움.
 * 같은 rep_count에 대해 중복으로 뜨지 않도록 unbrokenShownFor로 기록.
 */
function checkUnbroken() {
    if (state.repCount >= state.repTarget &&
        state.repTarget > 0 &&
        state.unbrokenShownFor !== state.repCount) {
        state.unbrokenShownFor = state.repCount;
        showUnbrokenBanner();
    }
}

/**
 * UNBROKEN 배너를 2초간 표시했다가 숨김
 */
function showUnbrokenBanner() {
    const banner = document.getElementById('unbroken-banner');
    if (!banner) return;

    const subEl = document.getElementById('unbroken-sub');
    if (subEl) subEl.textContent = `목표 ${state.repTarget}개 달성! 🎉`;

    banner.hidden = false;
    setTimeout(() => {
        banner.hidden = true;
    }, 2000);
}

/**
 * NO-REP 발생 시각을 타임라인에 기록
 */
function logNoRep() {
    addTimelineTick(getElapsedTimeString(), true);
}

/**
 * 타임라인에 이벤트 틱 추가
 */
function addTimelineTick(label, isNoRep) {
    const track = document.getElementById('timeline-track');
    if (!track) return;

    const tick = document.createElement('span');
    tick.className = 'timeline-tick';
    tick.textContent = label;
    if (!isNoRep) {
        tick.style.color = 'var(--accent-green)';
        tick.style.borderColor = 'var(--accent-green)';
    }
    track.appendChild(tick);
    track.scrollLeft = track.scrollWidth;
}

function clearTimeline() {
    const track = document.getElementById('timeline-track');
    if (track) track.innerHTML = '';
}

// ============================================================================
// 4. 이벤트 핸들러
// ============================================================================

document.getElementById('no-rep-btn')?.addEventListener('click', noRep);

document.getElementById('keypoints-btn')?.addEventListener('click', toggleKeypoints);

document.getElementById('reset-btn')?.addEventListener('click', resetCounter);

document.getElementById('rep-goal-input')?.addEventListener('change', (e) => {
    updateGoal(e.target.value);
});

document.getElementById('athlete-name-input')?.addEventListener('change', (e) => {
    updateAthleteNameOnServer(e.target.value);
});

/**
 * 영상 일시정지/재생 토글 (PAUSE 버튼, 영상 클릭 둘 다 이걸 호출함)
 */
function togglePause() {
    state.isPaused = !state.isPaused;

    const btn = document.getElementById('pause-btn');
    const img = document.getElementById('video-feed');
    const canvas = document.getElementById('video-freeze-frame');
    const pauseOverlay = document.getElementById('pause-overlay');

    if (state.isPaused) {
        // 현재 화면을 캔버스에 그대로 그려서 정지 화면처럼 보이게 함
        // (영상 img 자체는 계속 수신 중이지만 화면에는 안 보이게 숨김)
        if (img && canvas && img.naturalWidth) {
            canvas.width = img.naturalWidth;
            canvas.height = img.naturalHeight;
            canvas.getContext('2d').drawImage(img, 0, 0, canvas.width, canvas.height);
            img.hidden = true;
            canvas.hidden = false;
        }
        if (pauseOverlay) pauseOverlay.hidden = false;
    } else {
        if (img && canvas) {
            canvas.hidden = true;
            img.hidden = false;
        }
        if (pauseOverlay) pauseOverlay.hidden = true;
    }

    if (btn) {
        btn.textContent = state.isPaused ? '▶ RESUME STREAM' : '⏸ PAUSE STREAM';
    }
}

document.getElementById('pause-btn')?.addEventListener('click', (e) => {
    e.stopPropagation(); // 영상 클릭 토글과 중복 실행 방지
    togglePause();
});

document.getElementById('video-frame')?.addEventListener('click', togglePause);

// ============================================================================
// 5. 초기화 및 메인 루프
// ============================================================================

function initialize() {
    console.log('Angle-Based Squat Counter 시작...');

    fetchData();

    // 메인 루프: 100ms마다 데이터 업데이트
    setInterval(() => {
        if (!state.isPaused) {
            fetchData();
        }
    }, 100);

    // 세션 시계는 데이터 폴링과 별개로 매초 갱신
    setInterval(updateSessionClock, 1000);

    console.log('초기화 완료');
}

document.addEventListener('DOMContentLoaded', initialize);
