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
            state.frameCount++;

            trackAngleExtremes();
            updateUI();
            checkUnbroken();

            const statusEl = document.getElementById('status');
            if (statusEl) statusEl.textContent = '연결됨';
            return true;
        }
    } catch (error) {
        console.error('데이터 가져오기 실패:', error);
        const statusEl = document.getElementById('status');
        if (statusEl) statusEl.textContent = '연결 끊김';
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
            clearVarLog();
            clearTimeline();
            console.log('반복 카운터 리셋됨');
        }
    } catch (error) {
        console.error('리셋 실패:', error);
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
function updateDepth() {
    const depthEl = document.getElementById('depth');
    if (depthEl) {
        depthEl.textContent = state.depth;

        depthEl.classList.remove('deep', 'normal', 'shallow');

        switch (state.depth) {
            case 'DEEP':
                depthEl.classList.add('deep');
                break;
            case 'NORMAL':
                depthEl.classList.add('normal');
                break;
            case 'SHALLOW':
                depthEl.classList.add('shallow');
                break;
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
            addTimelineTick(`REP ${state.repCount}`, false);
        }

        repEl.textContent = state.repCount;
    }
}

/**
 * 반복 퍼센트 / 목표치 업데이트
 */
function updateRepPercentAndGoal() {
    const percentEl = document.getElementById('rep-percent');
    const goalEl = document.getElementById('rep-goal');

    if (goalEl) goalEl.textContent = state.repTarget;
    if (percentEl) {
        const pct = state.repTarget > 0
            ? Math.min(100, Math.round((state.repCount / state.repTarget) * 100))
            : 0;
        percentEl.textContent = pct + '%';
    }
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
function updateCounterStatus() {
    const statusEl = document.getElementById('counter-state');
    if (statusEl) {
        statusEl.textContent = state.counterState;
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
 * 세션 경과 시간 표시 (mm:ss.s)
 */
function updateSessionClock() {
    const clockEl = document.getElementById('session-clock');
    if (!clockEl) return;

    const elapsed = (Date.now() - state.sessionStart) / 1000;
    const minutes = Math.floor(elapsed / 60);
    const seconds = (elapsed % 60).toFixed(1).padStart(4, '0');
    clockEl.textContent = `${String(minutes).padStart(2, '0')}:${seconds}`;
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

    banner.hidden = false;
    setTimeout(() => {
        banner.hidden = true;
    }, 2000);
}

/**
 * VAR 로그에 NO-REP 기록 추가
 */
function logNoRep() {
    const log = document.getElementById('var-log');
    if (!log) return;

    const empty = log.querySelector('.var-log-empty');
    if (empty) empty.remove();

    const item = document.createElement('li');
    const angleText = state.angle ? state.angle.toFixed(0) + '°' : '--';
    item.innerHTML = `<span>NO-REP (${angleText})</span><span class="var-log-replay">REPLAY</span>`;
    log.prepend(item);

    addTimelineTick('NO-REP', true);
}

function clearVarLog() {
    const log = document.getElementById('var-log');
    if (!log) return;
    log.innerHTML = '<li class="var-log-empty">NO-REP 발생 시 여기에 기록됩니다</li>';
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

document.getElementById('reset-btn')?.addEventListener('click', resetCounter);

document.getElementById('pause-btn')?.addEventListener('click', () => {
    state.isPaused = !state.isPaused;
    const btn = document.getElementById('pause-btn');
    if (btn) {
        btn.textContent = state.isPaused ? '▶ RESUME STREAM' : '⏸ PAUSE STREAM';
    }
});

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
