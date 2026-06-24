// 페이지 로드 시 상태 확인
window.addEventListener('load', () => {
    console.log('✅ HYROX System loaded');
    document.getElementById('status-text').textContent = '✅ 카메라 실시간 스트리밍 중...';
});