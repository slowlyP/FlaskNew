document.addEventListener('DOMContentLoaded', function() {
    const dataElement = document.getElementById('score-data');
    
    // 데이터 추출
    const pythonScore = dataElement.dataset.python;
    const dbScore = dataElement.dataset.db;
    const frontendScore = dataElement.dataset.frontend;
    const historyAvgs = JSON.parse(dataElement.dataset.historyAvgs || '[]');
    const historyDates = JSON.parse(dataElement.dataset.historyDates || '[]');

    // 1. 레이더 차트 (과목 성취도)
    const ctxRadar = document.getElementById('myScoreChart').getContext('2d');
    new Chart(ctxRadar, {
        type: 'radar',
        data: {
            labels: ['Python', 'Database', 'Frontend'],
            datasets: [{
                data: [pythonScore, dbScore, frontendScore],
                backgroundColor: 'rgba(0, 234, 255, 0.2)',
                borderColor: 'rgba(0, 234, 255, 1)',
                borderWidth: 2,
                pointBackgroundColor: '#00eaff'
            }]
        },
        options: {
            responsive: true,
            scales: {
                r: {
                    angleLines: { color: 'rgba(255, 255, 255, 0.1)' },
                    grid: { color: 'rgba(255, 255, 255, 0.1)' },
                    suggestedMin: 0, suggestedMax: 100,
                    ticks: { display: false },
                    pointLabels: { color: '#00eaff', font: { size: 12 } }
                }
            },
            plugins: { legend: { display: false } }
        }
    });

    // 2. 꺾은선 그래프 (성적 추이)
    const ctxLine = document.getElementById('lineChart').getContext('2d');
    new Chart(ctxLine, {
        type: 'line',
        data: {
            labels: historyDates,
            datasets: [{
                label: '평균 점수',
                data: historyAvgs,
                borderColor: '#00eaff',
                backgroundColor: 'rgba(0, 234, 255, 0.1)',
                fill: true,
                tension: 0.4,
                borderWidth: 2,
                pointRadius: 4,
                pointBackgroundColor: '#fff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false, // HTML에서 설정한 높이(220px)를 고수함
            scales: {
                y: { 
                    min: 0, max: 100, 
                    ticks: { color: '#888', font: { size: 10 } },
                    grid: { color: 'rgba(255, 255, 255, 0.05)' }
                },
                x: { 
                    ticks: { color: '#888', font: { size: 10 } },
                    grid: { display: false }
                }
            },
            plugins: {
                legend: { display: false }
            }
        }
    });
});