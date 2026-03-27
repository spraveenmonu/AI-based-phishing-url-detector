document.addEventListener('DOMContentLoaded', () => {
    const urlInput = document.getElementById('urlInput');
    const scanBtn = document.getElementById('scanBtn');
    const resultSection = document.getElementById('resultSection');
    const singleResult = document.getElementById('singleResult');
    const batchResults = document.getElementById('batchResults');
    const statusIndicator = document.getElementById('statusIndicator');
    const resultTitle = document.getElementById('resultTitle');
    const probabilityFill = document.getElementById('probabilityFill');
    const probabilityText = document.getElementById('probabilityText');
    const urlDisplay = document.getElementById('urlDisplay');
    const featuresList = document.getElementById('featuresList');
    const recommendationText = document.getElementById('recommendationText');
    const btnText = scanBtn.querySelector('.btn-text');
    const loader = scanBtn.querySelector('.loader');

    // Tabs
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');

    // File Upload
    const dropZone = document.getElementById('dropZone');
    const fileInput = document.getElementById('fileInput');
    const fileInfoDisplay = document.getElementById('fileInfoDisplay');
    const fileName = document.getElementById('fileName');
    const scanFileBtn = document.getElementById('scanFileBtn');

    // Batch result elements
    const totalScanned = document.getElementById('totalScanned');
    const totalPhishing = document.getElementById('totalPhishing');
    const totalSafe = document.getElementById('totalSafe');
    const batchResultsList = document.getElementById('batchResultsList');

    // Static API URL for local project execution
    const API_URL = 'http://127.0.0.1:8000';
    let selectedFile = null;

    // Surprise: Resilient Connection Health Check with Retry
    async function checkHealth(retries = 3) {
        const statusEl = document.getElementById('connectionStatus');
        for (let i = 0; i < retries; i++) {
            try {
                const res = await fetch(`${API_URL}/api/health`, { cache: 'no-store' });
                if (res.ok) {
                    statusEl.className = 'status-badge online';
                    statusEl.innerHTML = '<i class="fas fa-satellite-dish"></i> <span>SYSTEM ONLINE</span>';
                    return;
                }
            } catch (e) {
                console.log(`Health check attempt ${i + 1} failed...`);
                if (i < retries - 1) await new Promise(r => setTimeout(r, 1000));
            }
        }
        statusEl.className = 'status-badge offline';
        statusEl.innerHTML = '<i class="fas fa-times-circle"></i> <span>SYSTEM OFFLINE</span>';
    }
    checkHealth();

    // Tab Switching with Animation
    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const target = btn.dataset.tab;

            // Revert active states
            tabBtns.forEach(b => b.classList.remove('active'));
            tabContents.forEach(c => {
                c.classList.remove('active');
                c.style.animation = 'none'; // Reset animation
            });

            btn.classList.add('active');
            const targetContent = document.getElementById(`${target}Tab`);
            targetContent.classList.add('active');

            // Surprise: Slide-up animation
            targetContent.style.animation = 'slideUp 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards';

            resultSection.classList.add('hidden');
        });
    });

    // Surprise: Paste Animation for Input
    urlInput.addEventListener('paste', () => {
        urlInput.classList.add('pasting');
        setTimeout(() => urlInput.classList.remove('pasting'), 600);
    });

    // File Upload Logic
    dropZone.addEventListener('click', () => fileInput.click());

    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('dragover');
    });

    dropZone.addEventListener('dragleave', () => dropZone.classList.remove('dragover'));

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('dragover');
        if (e.dataTransfer.files.length) {
            handleFileSelect(e.dataTransfer.files[0]);
        }
    });

    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length) {
            handleFileSelect(e.target.files[0]);
        }
    });

    function handleFileSelect(file) {
        selectedFile = file;
        fileName.textContent = file.name;
        fileInfoDisplay.classList.remove('hidden');
    }

    async function checkPhishing(url) {
        if (!url) {
            alert('Please enter a URL to scan.');
            return;
        }

        btnText.classList.add('hidden');
        loader.classList.remove('hidden');
        scanBtn.disabled = true;
        resultSection.classList.add('hidden');

        // Surprise: Add holographic scanning bar
        const scanCard = document.querySelector('.input-card');
        const scanner = document.createElement('div');
        scanner.className = 'scanning-bar';
        scanCard.appendChild(scanner);

        try {
            const response = await fetch(`${API_URL}/predict`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ url: url }),
            });

            if (!response.ok) throw new Error('API request failed');
            const data = await response.json();

            setTimeout(() => {
                scanner.remove();
                singleResult.classList.remove('hidden');
                batchResults.classList.add('hidden');
                displayResult(data);
            }, 800); // Small delay to enjoy the animation
        } catch (error) {
            scanner.remove();
            console.error('Fetch error:', error);
            const errorMsg = error.name === 'TypeError' ? 'Network Error: Backend is unreachable.' : error.message;
            alert(`Connection Error: ${errorMsg}\n\n1. Check if the terminal running 'run.py' is still open.\n2. Ensure no firewall is blocking port 8000.\n3. Refresh this page and try again.`);
        } finally {
            btnText.classList.remove('hidden');
            loader.classList.add('hidden');
            scanBtn.disabled = false;
        }
    }

    async function scanFile() {
        const file = selectedFile;
        if (!file) return;

        scanFileBtn.disabled = true;
        scanFileBtn.textContent = 'Scanning...';
        resultSection.classList.add('hidden');

        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch(`${API_URL}/predict-file`, {
                method: 'POST',
                body: formData
            });

            if (!response.ok) throw new Error('File scan failed');
            const data = await response.json();

            singleResult.classList.add('hidden');
            batchResults.classList.remove('hidden');
            displayBatchResults(data);
        } catch (error) {
            alert('Error scanning file.');
        } finally {
            scanFileBtn.disabled = false;
            scanFileBtn.textContent = 'Scan File';
        }
    }

    function displayBatchResults(data) {
        totalScanned.textContent = data.summary.total;
        totalPhishing.textContent = data.summary.phishing;
        totalSafe.textContent = data.summary.safe;

        batchResultsList.innerHTML = '';
        data.results.forEach(res => {
            const isPhish = res.prediction === 'Phishing';
            const row = document.createElement('tr');
            row.innerHTML = `
                <td class="truncate" style="max-width: 300px;">${res.url}</td>
                <td><span class="status-badge ${isPhish ? 'phishing' : 'safe'}">${res.prediction}</span></td>
                <td>${res.probability}%</td>
            `;
            batchResultsList.appendChild(row);
        });

        resultSection.classList.remove('hidden');
        resultSection.scrollIntoView({ behavior: 'smooth' });
    }

    scanFileBtn.addEventListener('click', scanFile);

    function displayResult(data) {
        const isPhishing = data.prediction === 'Phishing';
        const mainCard = document.querySelector('.main-result-card');

        // Reset classes
        mainCard.classList.remove('phishing', 'legitimate');
        mainCard.classList.add(isPhishing ? 'phishing' : 'legitimate');

        // Upgraded: HUD Typing Animation for Title
        const fullText = isPhishing ? '⚡ WARNING: PHISHING DETECTED ⚡' : '🛡️ LINK ANALYSIS: SAFE 🛡️';
        resultTitle.textContent = '';
        let i = 0;
        const typeEffect = setInterval(() => {
            if (i < fullText.length) {
                resultTitle.textContent += fullText.charAt(i);
                i++;
            } else {
                clearInterval(typeEffect);
            }
        }, 50);

        statusIndicator.innerHTML = isPhishing ? '<i class="fas fa-exclamation-triangle"></i>' : '<i class="fas fa-check-circle"></i>';

        // Update probability gauge
        setTimeout(() => {
            probabilityFill.style.width = `${data.probability}%`;
            probabilityText.textContent = `${data.probability}% Confidence`;
        }, 100);

        // Update URL display
        urlDisplay.textContent = `Analyzed: ${data.url}`;

        // Staggered Reveal Analysis with Animation
        featuresList.innerHTML = '';
        Object.entries(data.features).forEach(([key, value], index) => {
            setTimeout(() => {
                const li = document.createElement('li');
                li.className = 'feature-item';
                li.style.animationDelay = `${index * 0.1}s`;
                li.innerHTML = `<span>${key}</span><span>${value}</span>`;
                featuresList.appendChild(li);
            }, index * 100);
        });

        // Update recommendation
        if (isPhishing) {
            recommendationText.textContent = 'WARNING: This URL exhibits strong characteristics of phishing. DO NOT enter any credentials or personal information on this site. Close the tab immediately.';
            recommendationText.style.color = '#ff416c';
        } else {
            recommendationText.textContent = 'This URL appears to be legitimate based on our AI analysis. However, always be cautious and check for suspicious elements before interacting.';
            recommendationText.style.color = '#00b09b';
        }

        // Show results with animation
        resultSection.classList.remove('hidden');
        resultSection.scrollIntoView({ behavior: 'smooth' });
    }

    scanBtn.addEventListener('click', () => {
        const url = urlInput.value.trim();
        checkPhishing(url);
    });

    document.querySelectorAll('.example-link').forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const url = link.textContent;
            urlInput.value = url;
            checkPhishing(url);
        });
    });

    urlInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            const url = urlInput.value.trim();
            checkPhishing(url);
        }
    });
});
