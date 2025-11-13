// TezzaWorks AI Marketing Content Generator - Main JavaScript

// API base URL
const API_BASE = '/api';

// Current active tab
let activeTab = 'upload';

// Initialize the application
document.addEventListener('DOMContentLoaded', () => {
    initializeTabs();
    initializeFileUpload();
    loadScripts();
    loadJobs();
    loadVideos();
    loadConfig();

    // Set up auto-refresh for jobs
    setInterval(() => {
        if (activeTab === 'jobs') {
            loadJobs();
        }
    }, 5000);
});

// Tab Management
function initializeTabs() {
    const tabButtons = document.querySelectorAll('.tab-button');

    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            const tabName = button.getAttribute('data-tab');
            switchTab(tabName);
        });
    });
}

function switchTab(tabName) {
    // Update active tab
    activeTab = tabName;

    // Update tab buttons
    document.querySelectorAll('.tab-button').forEach(btn => {
        btn.classList.remove('active');
        if (btn.getAttribute('data-tab') === tabName) {
            btn.classList.add('active');
        }
    });

    // Update tab content
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });
    document.getElementById(`${tabName}-tab`).classList.add('active');

    // Reload data when switching to certain tabs
    if (tabName === 'scripts') {
        loadScripts();
    } else if (tabName === 'jobs') {
        loadJobs();
    } else if (tabName === 'videos') {
        loadVideos();
    } else if (tabName === 'config') {
        loadConfig();
    }
}

// File Upload
function initializeFileUpload() {
    const uploadArea = document.getElementById('upload-area');
    const fileInput = document.getElementById('file-input');
    const selectFileBtn = document.getElementById('select-file-btn');

    // Click to select file
    selectFileBtn.addEventListener('click', () => {
        fileInput.click();
    });

    uploadArea.addEventListener('click', (e) => {
        if (e.target === uploadArea || e.target.classList.contains('upload-icon')) {
            fileInput.click();
        }
    });

    // File selected
    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            uploadFile(e.target.files[0]);
        }
    });

    // Drag and drop
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.classList.add('drag-over');
    });

    uploadArea.addEventListener('dragleave', () => {
        uploadArea.classList.remove('drag-over');
    });

    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.classList.remove('drag-over');

        if (e.dataTransfer.files.length > 0) {
            uploadFile(e.dataTransfer.files[0]);
        }
    });
}

async function uploadFile(file) {
    const statusDiv = document.getElementById('upload-status');

    // Validate file type
    const allowedTypes = ['text/markdown', 'text/plain'];
    const allowedExtensions = ['.md', '.txt'];
    const fileExtension = '.' + file.name.split('.').pop().toLowerCase();

    if (!allowedExtensions.includes(fileExtension)) {
        showStatus(statusDiv, 'error', 'Invalid file type. Please upload a .md or .txt file.');
        return;
    }

    // Validate file size (5MB max)
    if (file.size > 5 * 1024 * 1024) {
        showStatus(statusDiv, 'error', 'File too large. Maximum size is 5MB.');
        return;
    }

    showStatus(statusDiv, 'info', 'Uploading file...');

    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch(`${API_BASE}/scripts/upload`, {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (data.success) {
            showStatus(statusDiv, 'success', `File uploaded successfully: ${data.filename}`);
            loadScripts();
        } else {
            showStatus(statusDiv, 'error', `Upload failed: ${data.error}`);
        }
    } catch (error) {
        showStatus(statusDiv, 'error', `Upload error: ${error.message}`);
    }
}

// Scripts Management
async function loadScripts() {
    const container = document.getElementById('scripts-list');
    container.innerHTML = '<div class="loading">Loading scripts...</div>';

    try {
        const response = await fetch(`${API_BASE}/scripts`);
        const data = await response.json();

        if (data.success && data.scripts.length > 0) {
            container.innerHTML = '';
            data.scripts.forEach(script => {
                container.appendChild(createScriptItem(script));
            });
        } else {
            container.innerHTML = '<p>No scripts uploaded yet.</p>';
        }
    } catch (error) {
        container.innerHTML = `<p class="error">Error loading scripts: ${error.message}</p>`;
    }
}

function createScriptItem(script) {
    const item = document.createElement('div');
    item.className = 'list-item';

    const sizeKB = (script.size / 1024).toFixed(2);
    const date = new Date(script.modified).toLocaleString();

    item.innerHTML = `
        <div class="list-item-header">
            <div class="list-item-title">${script.filename}</div>
        </div>
        <div class="list-item-meta">
            Size: ${sizeKB} KB | Modified: ${date}
        </div>
        <div class="list-item-actions">
            <button class="btn btn-primary btn-small" onclick="viewScript('${script.filename}')">
                View Details
            </button>
            <button class="btn btn-success btn-small" onclick="generateVideo('${script.filename}')">
                Generate Video
            </button>
            <button class="btn btn-danger btn-small" onclick="deleteScript('${script.filename}')">
                Delete
            </button>
        </div>
    `;

    return item;
}

async function viewScript(filename) {
    try {
        const response = await fetch(`${API_BASE}/scripts/${filename}`);
        const data = await response.json();

        if (data.success) {
            showScriptModal(data);
        }
    } catch (error) {
        alert(`Error loading script: ${error.message}`);
    }
}

function showScriptModal(data) {
    const modal = document.getElementById('script-modal');
    const modalTitle = document.getElementById('modal-title');
    const modalBody = document.getElementById('modal-body');

    modalTitle.textContent = data.filename;

    let html = '';

    data.scripts.forEach(script => {
        html += `
            <div class="script-info">
                <h3>${script.title}</h3>
                <p><strong>Concept:</strong> ${script.concept}</p>
                <p><strong>Style:</strong> ${script.style}</p>

                <div class="script-stats">
                    <div class="stat-item">
                        <div class="stat-value">${script.statistics.narrations}</div>
                        <div class="stat-label">Narrations</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-value">${script.statistics.audio_cues}</div>
                        <div class="stat-label">Audio Cues</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-value">${script.statistics.scenes}</div>
                        <div class="stat-label">Scenes</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-value">${script.statistics.text_overlays}</div>
                        <div class="stat-label">Text Overlays</div>
                    </div>
                </div>

                <button class="btn btn-success" onclick="generateVideoFromScript('${data.filename}', '${script.title}')">
                    Generate Video for This Script
                </button>
            </div>
        `;
    });

    modalBody.innerHTML = html;
    modal.classList.add('show');

    // Close modal
    const closeBtn = modal.querySelector('.close');
    closeBtn.onclick = () => {
        modal.classList.remove('show');
    };

    window.onclick = (event) => {
        if (event.target === modal) {
            modal.classList.remove('show');
        }
    };
}

async function generateVideo(filename) {
    if (!confirm(`Generate video from ${filename}?`)) {
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/generate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ filename })
        });

        const data = await response.json();

        if (data.success) {
            alert(`Video generation started!\nJob ID: ${data.job_id}`);
            switchTab('jobs');
        } else {
            alert(`Error: ${data.error}`);
        }
    } catch (error) {
        alert(`Error: ${error.message}`);
    }
}

async function generateVideoFromScript(filename, scriptTitle) {
    // Close modal
    document.getElementById('script-modal').classList.remove('show');

    try {
        const response = await fetch(`${API_BASE}/generate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                filename,
                script_title: scriptTitle
            })
        });

        const data = await response.json();

        if (data.success) {
            alert(`Video generation started for "${scriptTitle}"!\nJob ID: ${data.job_id}`);
            switchTab('jobs');
        } else {
            alert(`Error: ${data.error}`);
        }
    } catch (error) {
        alert(`Error: ${error.message}`);
    }
}

async function deleteScript(filename) {
    if (!confirm(`Delete ${filename}?`)) {
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/scripts/${filename}`, {
            method: 'DELETE'
        });

        const data = await response.json();

        if (data.success) {
            loadScripts();
        } else {
            alert(`Error: ${data.error}`);
        }
    } catch (error) {
        alert(`Error: ${error.message}`);
    }
}

// Jobs Management
async function loadJobs() {
    const container = document.getElementById('jobs-list');

    try {
        const response = await fetch(`${API_BASE}/jobs`);
        const data = await response.json();

        if (data.success && data.jobs.length > 0) {
            container.innerHTML = '';
            data.jobs.forEach(job => {
                container.appendChild(createJobItem(job));
            });
        } else {
            container.innerHTML = '<p>No jobs yet.</p>';
        }
    } catch (error) {
        container.innerHTML = `<p class="error">Error loading jobs: ${error.message}</p>`;
    }
}

document.getElementById('refresh-jobs-btn').addEventListener('click', loadJobs);

function createJobItem(job) {
    const item = document.createElement('div');
    item.className = 'list-item';

    const date = new Date(job.created).toLocaleString();

    item.innerHTML = `
        <div class="list-item-header">
            <div class="list-item-title">${job.script_title || job.filename}</div>
            <span class="status-badge ${job.status}">${job.status.toUpperCase()}</span>
        </div>
        <div class="list-item-meta">
            Job ID: ${job.id} | Created: ${date}
        </div>
        <div class="progress-bar">
            <div class="progress-fill" style="width: ${job.progress}%">
                ${job.progress}%
            </div>
        </div>
        <div class="list-item-meta">
            ${job.message}
        </div>
        ${job.video_path ? `
            <div class="list-item-actions">
                <a href="${API_BASE}/videos/${job.video_path}" class="btn btn-success btn-small" download>
                    Download Video
                </a>
            </div>
        ` : ''}
    `;

    return item;
}

// Videos Management
async function loadVideos() {
    const container = document.getElementById('videos-list');
    container.innerHTML = '<div class="loading">Loading videos...</div>';

    try {
        const response = await fetch(`${API_BASE}/videos`);
        const data = await response.json();

        if (data.success && data.videos.length > 0) {
            container.innerHTML = '';
            data.videos.forEach(video => {
                container.appendChild(createVideoItem(video));
            });
        } else {
            container.innerHTML = '<p>No videos generated yet.</p>';
        }
    } catch (error) {
        container.innerHTML = `<p class="error">Error loading videos: ${error.message}</p>`;
    }
}

function createVideoItem(video) {
    const item = document.createElement('div');
    item.className = 'list-item';

    const sizeMB = (video.size / (1024 * 1024)).toFixed(2);
    const date = new Date(video.modified).toLocaleString();

    item.innerHTML = `
        <div class="list-item-header">
            <div class="list-item-title">${video.filename}</div>
        </div>
        <div class="list-item-meta">
            Size: ${sizeMB} MB | Created: ${date}
        </div>
        <div class="list-item-actions">
            <a href="${API_BASE}/videos/${video.filename}" class="btn btn-primary btn-small" download>
                Download Video
            </a>
        </div>
    `;

    return item;
}

// Configuration
async function loadConfig() {
    const container = document.getElementById('config-info');
    container.innerHTML = '<div class="loading">Loading configuration...</div>';

    try {
        const response = await fetch(`${API_BASE}/config`);
        const data = await response.json();

        if (data.success) {
            container.innerHTML = createConfigDisplay(data.config);
        }
    } catch (error) {
        container.innerHTML = `<p class="error">Error loading config: ${error.message}</p>`;
    }
}

function createConfigDisplay(config) {
    return `
        <div class="config-section">
            <h3>API Configuration</h3>
            <div class="config-item">
                <span class="config-label">
                    <span class="config-status ${config.elevenlabs_configured ? 'active' : 'inactive'}"></span>
                    ElevenLabs API
                </span>
                <span class="config-value">${config.elevenlabs_configured ? 'Configured' : 'Not Configured'}</span>
            </div>
            <div class="config-item">
                <span class="config-label">
                    <span class="config-status ${config.suno_configured ? 'active' : 'inactive'}"></span>
                    Suno AI API
                </span>
                <span class="config-value">${config.suno_configured ? 'Configured' : 'Not Configured'}</span>
            </div>
        </div>

        <div class="config-section">
            <h3>Video Settings</h3>
            <div class="config-item">
                <span class="config-label">Resolution</span>
                <span class="config-value">${config.video_settings.resolution}</span>
            </div>
            <div class="config-item">
                <span class="config-label">Frame Rate</span>
                <span class="config-value">${config.video_settings.framerate} fps</span>
            </div>
            <div class="config-item">
                <span class="config-label">Output Format</span>
                <span class="config-value">${config.video_settings.output_format.toUpperCase()}</span>
            </div>
            <div class="config-item">
                <span class="config-label">Video Codec</span>
                <span class="config-value">${config.video_settings.video_codec}</span>
            </div>
        </div>

        <div class="config-section">
            <h3>Available Voice Profiles</h3>
            ${Object.entries(config.available_voices).map(([key, value]) => `
                <div class="config-item">
                    <span class="config-label">${key}</span>
                    <span class="config-value">${value}</span>
                </div>
            `).join('')}
        </div>

        <div class="config-section">
            <h3>Music Styles</h3>
            ${config.music_styles.map(style => `
                <div class="config-item">
                    <span class="config-value">${style}</span>
                </div>
            `).join('')}
        </div>
    `;
}

// Utility Functions
function showStatus(element, type, message) {
    element.className = `status-message show ${type}`;
    element.textContent = message;

    setTimeout(() => {
        element.classList.remove('show');
    }, 5000);
}

// Format file size
function formatFileSize(bytes) {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(2) + ' MB';
}
