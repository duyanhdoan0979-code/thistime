import os
import requests
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

HTML_TEMPLATE = r"""
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HUST Weather Data System</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <script>
        tailwind.config = {
            theme: {
                extend: {
                    fontFamily: { sans: ['Inter', 'sans-serif'] },
                    colors: {
                        hustRed: '#a31720',
                        hustDarkRed: '#7a1318',
                        hustYellow: '#f2a900'
                    }
                }
            }
        }
    </script>
    <style>
        body { background-color: #f8fafc; }
        .custom-scrollbar::-webkit-scrollbar { height: 6px; width: 6px; }
        .custom-scrollbar::-webkit-scrollbar-track { background: #f1f5f9; }
        .custom-scrollbar::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 4px; }
        .custom-scrollbar::-webkit-scrollbar-thumb:hover { background: #94a3b8; }
        
        #customCoords { transition: max-height 0.3s ease-in-out, opacity 0.3s ease-in-out; overflow: hidden; }
        .hidden-coords { max-height: 0; opacity: 0; margin-top: 0; }
        .visible-coords { max-height: 100px; opacity: 1; margin-top: 1.5rem; }
    </style>
</head>
<body class="font-sans text-slate-800 antialiased min-h-screen flex flex-col">

    <header class="bg-white border-b-4 border-hustYellow py-4 px-6 lg:px-12 flex flex-col md:flex-row justify-between items-center gap-4 relative z-30">
        <div class="flex items-center gap-4">
            <img src="logo-HD-bach-khoa-ha-noi-hust.jpg" class="h-12 object-contain" alt="HUST Logo" onerror="this.src='https://placehold.co/120x48/ffffff/a31720?text=HUST'">
            <div>
                <h1 class="text-hustRed font-extrabold text-lg md:text-xl uppercase tracking-wide leading-tight">Đại học Bách Khoa Hà Nội</h1>
                <p class="text-gray-500 text-sm font-medium">Ứng dụng Python trong thu thập và hiển thị dữ liệu</p>
            </div>
        </div>
        
        <div class="flex items-center gap-6 text-sm">
            <div class="text-right">
                <p class="text-xs text-gray-500 font-bold uppercase tracking-wider mb-0.5">Họ và tên</p>
                <p class="text-hustDarkRed font-bold text-base">Đoàn Duy Anh</p>
            </div>
            <div class="h-10 w-[2px] bg-gray-200"></div>
            <div class="text-left">
                <p class="text-xs text-gray-500 font-bold uppercase tracking-wider mb-0.5">Mã số sinh viên</p>
                <p class="text-hustDarkRed font-bold text-base">20222727</p>
            </div>
        </div>
    </header>

    <section class="bg-hustRed text-white overflow-hidden relative">
        <div class="max-w-7xl mx-auto px-6 lg:px-12 pt-16 pb-36 flex justify-between items-center relative z-10">
            <div class="max-w-2xl relative z-20">
                <span class="inline-block bg-hustYellow text-hustDarkRed font-extrabold text-[11px] px-4 py-1.5 rounded-full mb-6 tracking-wide shadow-sm">WEATHER DATA SYSTEM</span>
                <h2 class="text-4xl md:text-5xl font-extrabold mb-5 leading-[1.2]">
                    Thu thập và hiển thị <span class="text-hustYellow">dữ liệu<br>thời tiết</span>
                </h2>
                <p class="text-lg text-red-100 font-medium max-w-lg">
                    Tra cứu nhiệt độ, độ ẩm tương đối và cường độ bức xạ mặt trời theo từng ngày.
                </p>
            </div>
            
            <div class="absolute right-0 top-1/2 -translate-y-1/2 translate-x-1/4 hidden md:block">
                <div class="w-[450px] h-[450px] bg-[#8f141c] rounded-full absolute top-1/2 right-10 -translate-y-1/2 opacity-80"></div>
                <div class="w-56 h-56 bg-hustYellow rounded-full absolute top-1/2 right-40 -translate-y-1/2 flex items-center justify-center shadow-xl">
                    <svg class="w-24 h-24 text-hustDarkRed" fill="currentColor" viewBox="0 0 24 24">
                        <path d="M12 7c-2.76 0-5 2.24-5 5s2.24 5 5 5 5-2.24 5-5-2.24-5-5-5zM2 13h2c.55 0 1-.45 1-1s-.45-1-1-1H2c-.55 0-1 .45-1 1s.45 1 1 1zm18 0h2c.55 0 1-.45 1-1s-.45-1-1-1h-2c-.55 0-1 .45-1 1s.45 1 1 1zM11 2v2c0 .55.45 1 1 1s1-.45 1-1V2c0-.55-.45-1-1-1s-1 .45-1 1zm0 18v2c0 .55.45 1 1 1s1-.45 1-1v-2c0-.55-.45-1-1-1s-1 .45-1 1zM5.99 4.58c-.39-.39-1.03-.39-1.41 0-.39.39-.39 1.03 0 1.41l1.06 1.06c.39.39 1.03.39 1.41 0 .39-.39.39-1.03 0-1.41L5.99 4.58zm12.37 12.37c-.39-.39-1.03-.39-1.41 0-.39.39-.39 1.03 0 1.41l1.06 1.06c.39.39 1.03.39 1.41 0 .39-.39.39-1.03 0-1.41l-1.06-1.06zm1.06-10.96c.39-.39.39-1.03 0-1.41-.39-.39-1.03-.39-1.41 0l-1.06 1.06c-.39.39-.39 1.03 0 1.41.39.39 1.03.39 1.41 0l1.06-1.06zM7.05 18.36c.39-.39.39-1.03 0-1.41-.39-.39-1.03-.39-1.41 0l-1.06 1.06c-.39.39-.39 1.03 0 1.41.39.39 1.03.39 1.41 0l1.06-1.06z"></path>
                    </svg>
                </div>
            </div>
        </div>
    </section>

    <section class="max-w-6xl mx-auto px-4 lg:px-12 w-full relative z-20 -mt-24 mb-10">
        <div class="bg-white rounded-2xl shadow-[0_8px_30px_rgb(0,0,0,0.12)] p-6 md:p-10 border border-gray-100">
            <h3 class="text-hustRed text-xs font-bold tracking-[0.2em] uppercase mb-1">Tra cứu</h3>
            <h4 class="text-hustDarkRed text-2xl font-bold mb-8">Chọn khu vực và khoảng thời gian</h4>
            
            <form id="weatherForm">
                <div class="grid grid-cols-1 md:grid-cols-4 gap-6 items-end">
                    <div>
                        <label class="block text-sm font-bold text-gray-800 mb-2">Địa điểm</label>
                        <select id="location" class="w-full bg-white border border-gray-300 rounded-lg px-4 py-3 text-sm focus:ring-2 focus:ring-hustRed outline-none font-medium">
                            <option value="hanoi" selected>Hà Nội (Ví dụ)</option>
                            <option value="danang">Đà Nẵng</option>
                            <option value="hcm">Hồ Chí Minh</option>
                            <option value="custom">Tọa độ tùy chỉnh...</option>
                        </select>
                    </div>
                    <div>
                        <label class="block text-sm font-bold text-gray-800 mb-2">Ngày quá khứ</label>
                        <input type="number" id="past" value="1" min="0" max="90" class="w-full bg-white border border-gray-300 rounded-lg px-4 py-3 text-sm focus:ring-2 focus:ring-hustRed outline-none font-medium">
                    </div>
                    <div>
                        <label class="block text-sm font-bold text-gray-800 mb-2">Ngày dự báo</label>
                        <input type="number" id="forecast" value="3" min="0" max="14" class="w-full bg-white border border-gray-300 rounded-lg px-4 py-3 text-sm focus:ring-2 focus:ring-hustRed outline-none font-medium">
                    </div>
                    <div>
                        <button type="submit" id="submitBtn" class="w-full bg-hustRed hover:bg-hustDarkRed text-white font-bold py-3 px-4 rounded-lg shadow-md transition-colors duration-200 flex justify-center items-center gap-2">
                            <span id="btnText">Lấy dữ liệu</span>
                            <svg id="btnSpinner" class="animate-spin hidden h-5 w-5 text-white" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
                        </button>
                    </div>
                </div>
                
                <div id="customCoords" class="hidden-coords grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                        <label class="block text-sm font-bold text-gray-700 mb-2">Vĩ độ (Latitude)</label>
                        <input type="number" step="any" id="lat" placeholder="VD: 21.0285" class="w-full border border-gray-300 rounded-lg px-4 py-2.5 outline-none focus:ring-2 focus:ring-hustRed text-sm">
                    </div>
                    <div>
                        <label class="block text-sm font-bold text-gray-700 mb-2">Kinh độ (Longitude)</label>
                        <input type="number" step="any" id="lon" placeholder="VD: 105.8542" class="w-full border border-gray-300 rounded-lg px-4 py-2.5 outline-none focus:ring-2 focus:ring-hustRed text-sm">
                    </div>
                </div>
            </form>
        </div>
    </section>

    <main id="dashboard" class="max-w-6xl mx-auto px-4 lg:px-12 w-full hidden flex-col gap-8 pb-16 flex-1">
        
        <div id="errorState" class="hidden bg-red-50 border-l-4 border-red-500 p-4 rounded shadow-sm">
            <p id="errorMessage" class="text-red-700 font-medium">Đã xảy ra lỗi khi lấy dữ liệu.</p>
        </div>

        <div id="chartsContainer" class="space-y-6">
            <div class="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
                <h4 class="text-lg font-bold text-gray-800 mb-4 flex items-center gap-2">
                    <span class="text-hustYellow">☀️</span> Cường độ bức xạ mặt trời (GHI)
                </h4>
                <div class="w-full h-[350px]"><canvas id="ghiChart"></canvas></div>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div class="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
                    <h4 class="text-lg font-bold text-gray-800 mb-4 flex items-center gap-2">
                        <span class="text-hustRed">🌡️</span> Nhiệt độ (°C)
                    </h4>
                    <div class="w-full h-[300px]"><canvas id="tempChart"></canvas></div>
                </div>
                
                <div class="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
                    <h4 class="text-lg font-bold text-gray-800 mb-4 flex items-center gap-2">
                        <span class="text-blue-500">💧</span> Độ ẩm tương đối (%)
                    </h4>
                    <div class="w-full h-[300px]"><canvas id="humChart"></canvas></div>
                </div>
            </div>
        </div>

        <div id="tableContainer" class="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
            <div class="flex justify-between items-center mb-6">
                <h4 class="text-lg font-bold text-gray-800 flex items-center gap-2">
                    <span>📋</span> Bảng dữ liệu chi tiết
                </h4>
                <button id="downloadBtn" class="bg-white border border-gray-300 hover:bg-gray-50 text-gray-700 font-bold py-2 px-4 rounded-lg shadow-sm transition flex items-center gap-2 text-sm">
                    Tải xuống CSV
                </button>
            </div>
            
            <div class="border border-gray-200 rounded-lg overflow-hidden">
                <div class="overflow-x-auto custom-scrollbar max-h-[400px]">
                    <table class="w-full text-left border-collapse whitespace-nowrap">
                        <thead class="sticky top-0 bg-gray-50 z-10 text-xs font-bold text-gray-600 uppercase">
                            <tr>
                                <th class="px-4 py-3 border-b border-gray-200">Thời gian (Giờ VN)</th>
                                <th class="px-4 py-3 border-b border-gray-200 text-right">Nhiệt độ (°C)</th>
                                <th class="px-4 py-3 border-b border-gray-200 text-right">Độ ẩm (%)</th>
                                <th class="px-4 py-3 border-b border-gray-200 text-right">Bức xạ GHI (W/m²)</th>
                            </tr>
                        </thead>
                        <tbody id="dataTableBody" class="text-sm text-gray-700 divide-y divide-gray-100"></tbody>
                    </table>
                </div>
            </div>
        </div>
    </main>

    <footer class="w-full bg-white border-t border-gray-200 mt-12 py-8 relative z-20 flex-shrink-0">
        <div class="max-w-6xl mx-auto px-4 flex flex-col items-center justify-center gap-3">
            <img src="logo-dai-hoc-bach-khoa-ha-noi_2.jpg" alt="HUST Logo Secondary" class="h-14 md:h-20 object-contain" onerror="this.src='https://placehold.co/400x120/ffffff/a31720?text=HUST'">
            <p class="text-xs text-gray-400 font-medium tracking-wide">© 2026 Open Web Weather Data Collection</p>
        </div>
    </footer>

    <script>
        const cityData = {
            hanoi: { lat: 21.0285, lon: 105.8542 },
            danang: { lat: 16.0678, lon: 108.2208 },
            hcm: { lat: 10.8231, lon: 106.6297 }
        };

        const locationSelect = document.getElementById('location');
        const customCoords = document.getElementById('customCoords');
        const latInput = document.getElementById('lat');
        const lonInput = document.getElementById('lon');
        const form = document.getElementById('weatherForm');
        const submitBtn = document.getElementById('submitBtn');
        const btnText = document.getElementById('btnText');
        const btnSpinner = document.getElementById('btnSpinner');
        const dashboard = document.getElementById('dashboard');
        const errorState = document.getElementById('errorState');
        const errorMessage = document.getElementById('errorMessage');
        const tableBody = document.getElementById('dataTableBody');
        const downloadBtn = document.getElementById('downloadBtn');

        let chartInstances = {};
        let currentData = null;

        locationSelect.addEventListener('change', (e) => {
            if (e.target.value === 'custom') {
                customCoords.classList.remove('hidden-coords');
                customCoords.classList.add('visible-coords');
                latInput.required = true;
                lonInput.required = true;
            } else {
                customCoords.classList.add('hidden-coords');
                customCoords.classList.remove('visible-coords');
                latInput.required = false;
                lonInput.required = false;
            }
        });

        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            btnText.textContent = "Đang xử lý...";
            btnSpinner.classList.remove('hidden');
            submitBtn.disabled = true;
            errorState.classList.add('hidden');
            dashboard.classList.remove('hidden');
            dashboard.classList.add('flex');

            let lat, lon;
            const selectedLocation = locationSelect.value;
            if (selectedLocation === 'custom') {
                lat = parseFloat(latInput.value).toFixed(4);
                lon = parseFloat(lonInput.value).toFixed(4);
            } else {
                lat = cityData[selectedLocation].lat;
                lon = cityData[selectedLocation].lon;
            }

            const pastDays = document.getElementById('past').value;
            const forecastDays = document.getElementById('forecast').value;

            try {
                // Call the Python API Backend instead of Open-Meteo directly
                const url = `/api/weather?lat=${lat}&lon=${lon}&past=${pastDays}&forecast=${forecastDays}`;
                
                const locationSelect = document.getElementById('location').value;
const locationSelect = document.getElementById('location').value;
const past = document.getElementById('pastDays').value;
const forecast = document.getElementById('forecastDays').value;

const coordinates = {
    'Hà Nội': { lat: 21.0285, lon: 105.8542 },
    'Đà Nẵng': { lat: 16.0678, lon: 108.2208 },
    'Hồ Chí Minh': { lat: 10.8231, lon: 106.6297 }
};

// Renamed to avoid clashing with any existing 'lat' or 'lon' variables
const reqLat = coordinates[locationSelect].lat;
const reqLon = coordinates[locationSelect].lon;

fetch('/api/weather', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        lat: reqLat,
        lon: reqLon,
        past: parseInt(past),
        forecast: parseInt(forecast)
    })
})
.then(response => {
    if (!response.ok) {
        throw new Error('Máy chủ Python không phản hồi.');
    }
    return response.json();
})
.then(data => {
    console.log("Data received:", data);
    
    // Hide the error message if successful
    document.getElementById('error-message').style.display = 'none';
    
    // YOUR CHART DRAWING CODE GOES HERE
})
.catch(error => {
    console.error("Lỗi kết nối:", error);
    const errorDiv = document.getElementById('error-message');
    errorDiv.style.display = 'block';
    errorDiv.innerText = error.message; 
});

        function renderCharts(hourly) {
            const labels = hourly.time.map(t => {
                const date = new Date(t);
                return `${date.getHours().toString().padStart(2, '0')}:00, ${date.getDate()} Th${date.getMonth()+1}`;
            });

            const pointConfig = labels.length > 72 ? 0 : 2; 
            const commonOptions = {
                responsive: true, maintainAspectRatio: false,
                interaction: { mode: 'index', intersect: false },
                plugins: { legend: { display: false } },
                scales: {
                    x: { grid: { display: false }, ticks: { maxTicksLimit: 10, font: {family: 'Inter'} } },
                    y: { border: { display: false }, grid: { color: '#f1f5f9' }, ticks: { font: {family: 'Inter'} } }
                }
            };

            const createOrUpdateChart = (id, label, data, color, bg) => {
                const ctx = document.getElementById(id).getContext('2d');
                if (chartInstances[id]) chartInstances[id].destroy();
                chartInstances[id] = new Chart(ctx, {
                    type: 'line',
                    data: { labels: labels, datasets: [{ label: label, data: data, borderColor: color, backgroundColor: bg, borderWidth: 2, fill: !!bg, pointRadius: pointConfig, tension: 0.2 }] },
                    options: commonOptions
                });
            };

            createOrUpdateChart('ghiChart', 'Bức xạ GHI (W/m²)', hourly.shortwave_radiation, '#f2a900', 'rgba(242, 169, 0, 0.15)');
            createOrUpdateChart('tempChart', 'Nhiệt độ (°C)', hourly.temperature_2m, '#a31720', null);
            createOrUpdateChart('humChart', 'Độ ẩm (%)', hourly.relative_humidity_2m, '#3b82f6', null);
        }

        function renderTable(hourly) {
            tableBody.innerHTML = '';
            const frag = document.createDocumentFragment();
            for (let i = 0; i < hourly.time.length; i++) {
                const d = new Date(hourly.time[i]);
                const timeStr = `${d.getHours().toString().padStart(2, '0')}:00 - ${d.getDate()}/${d.getMonth()+1}/${d.getFullYear()}`;
                const tr = document.createElement('tr');
                tr.className = "hover:bg-slate-50 transition-colors";
                tr.innerHTML = `
                    <td class="px-4 py-2 border-b border-gray-100 font-medium">${timeStr}</td>
                    <td class="px-4 py-2 text-right border-b border-gray-100 text-hustDarkRed font-semibold">${hourly.temperature_2m[i] ?? '-'}</td>
                    <td class="px-4 py-2 text-right border-b border-gray-100 text-blue-600">${hourly.relative_humidity_2m[i] ?? '-'}</td>
                    <td class="px-4 py-2 text-right border-b border-gray-100 text-yellow-600">${hourly.shortwave_radiation[i] ?? '-'}</td>
                `;
                frag.appendChild(tr);
            }
            tableBody.appendChild(frag);
        }

        downloadBtn.addEventListener('click', () => {
            if (!currentData) return;
            let csv = "\uFEFFThoi gian,Nhiet do (C),Do am (%),Buc xa GHI (W/m2)\n";
            for (let i = 0; i < currentData.time.length; i++) {
                csv += `${currentData.time[i]},${currentData.temperature_2m[i]},${currentData.relative_humidity_2m[i]},${currentData.shortwave_radiation[i]}\n`;
            }
            const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
            const link = document.createElement('a');
            link.href = URL.createObjectURL(blob);
            link.download = `DuLieuThoiTiet_HUST.csv`;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        });
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    """Serves the main frontend UI."""
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/weather')
def weather_api():
    """
    Python backend proxy route: Takes coordinates from the frontend,
    requests data securely from Open-Meteo, and returns it to the client.
    """
    lat = request.args.get('lat', type=float)
    lon = request.args.get('lon', type=float)
    past = request.args.get('past', type=int)
    forecast = request.args.get('forecast', type=int)

    # If parameters are missing, return a bad request error
    if None in (lat, lon, past, forecast):
        return jsonify({"error": "Missing required coordinate or day parameters."}), 400

    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "past_days": past,
        "forecast_days": forecast,
        "hourly": "temperature_2m,relative_humidity_2m,shortwave_radiation",
        "timezone": "Asia/Bangkok"
    }

    try:
        # Use Python to fetch the data
        response = requests.get(url, params=params)
        response.raise_for_status() 
        return jsonify(response.json())
        
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Failed to fetch data from weather provider: {str(e)}"}), 502

if __name__ == '__main__':
    # Render assigns a dynamic port via environment variable. 
    # Defaults to 5000 for local testing if the PORT variable isn't set.
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
