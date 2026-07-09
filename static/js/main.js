// Socket.IO connection
const socket = io();

// Chart.js setup
let throughputChart;
let chartData = {
    labels: [],
    datasets: [{
        label: 'Throughput (Mbps)',
        data: [],
        borderColor: 'rgb(52, 152, 219)',
        tension: 0.1,
        fill: false
    }]
};

function initCharts() {
    const ctx = document.getElementById('throughputChart').getContext('2d');
    throughputChart = new Chart(ctx, {
        type: 'line',
        data: chartData,
        options: {
            responsive: true,
            maintainAspectRatio: true,
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Throughput (Mbps)'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Time'
                    }
                }
            }
        }
    });
}

function updateChart(timestamp, throughput) {
    const now = new Date(timestamp * 1000);
    const timeStr = now.toLocaleTimeString();

    chartData.labels.push(timeStr);
    chartData.datasets[0].data.push(throughput);

    // Limit to last 50 data points
    if (chartData.labels.length > 50) {
        chartData.labels.shift();
        chartData.datasets[0].data.shift();
    }

    if (throughputChart) {
        throughputChart.update();
    }
}

// Socket.IO event handlers
socket.on('connect', () => {
    console.log('Connected to server');
});

socket.on('stats_update', (data) => {
    // Update dashboard stats
    document.getElementById('srt-status').textContent = data.srt.status;
    document.getElementById('throughput').textContent = `${data.srt.throughput.toFixed(2)} Mbps`;
    document.getElementById('packet-loss').textContent = `${data.srt.packet_loss}%`;
    document.getElementById('cpu-usage').textContent = `${data.system.cpu_usage}%`;

    // Update chart
    updateChart(data.timestamp, data.srt.throughput);
});

socket.on('status_message', (message) => {
    const output = document.getElementById('srt-status-output');
    output.textContent += `\n[${new Date().toLocaleTimeString()}] ${message}`;
    output.scrollTop = output.scrollHeight;
});

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    initCharts();

    // Clear stats button
    document.getElementById('clear-stats').addEventListener('click', () => {
        if (confirm('Clear all statistics?')) {
            socket.emit('clear_stats');
        }
    });

    // Save stats button
    document.getElementById('save-stats').addEventListener('click', () => {
        socket.emit('save_stats');
        alert('Statistics saved successfully!');
    });

    // SRT config form
    const configForm = document.getElementById('srt-config-form');
    if (configForm) {
        configForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const formData = new FormData(configForm);
            const config = {};

            formData.forEach((value, key) => {
                config[key] = value;
            });

            socket.emit('apply_srt_config', config);
        });
    }
});
