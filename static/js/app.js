// 실시간 데이터 업데이트
setInterval(async () => {
    try {
        const response = await fetch('/api/data');
        const data = await response.json();
        
        // 각도 업데이트
        document.getElementById('angle').textContent = data.angle.toFixed(1) + '°';
        document.getElementById('left-knee').textContent = data.left_knee.toFixed(1) + '°';
        document.getElementById('right-knee').textContent = data.right_knee.toFixed(1) + '°';
        
        // 프레임 카운트 업데이트
        document.getElementById('frame-count').textContent = `프레임: ${data.frame_count}`;
        
        // 판정 결과 업데이트
        const depthElement = document.getElementById('depth');
        depthElement.textContent = data.depth;
        
        // 판정 결과에 따라 색상 변경
        depthElement.classList.remove('shallow', 'normal');
        
        if (data.depth === 'DEEP') {
            depthElement.style.color = '#2ecc71';
        } else if (data.depth === 'NORMAL') {
            depthElement.style.color = '#f39c12';
            depthElement.classList.add('normal');
        } else if (data.depth === 'SHALLOW') {
            depthElement.style.color = '#e74c3c';
            depthElement.classList.add('shallow');
        } else {
            depthElement.style.color = '#666';
        }
    } catch (error) {
        console.error('Error fetching data:', error);
    }
}, 100); // 100ms마다 업데이트

// 페이지 로드 확인
window.addEventListener('load', () => {
    console.log('✅ HYROX System loaded');
});