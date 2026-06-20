const API_BASE = window.location.origin;

const uploadForm = document.getElementById('uploadForm');
const imageInput = document.getElementById('imageInput');
const uploadMessage = document.getElementById('uploadMessage');
const gallery = document.getElementById('gallery');
const cacheStatus = document.getElementById('cacheStatus');
const cfRay = document.getElementById('cfRay');
const requestTime = document.getElementById('requestTime');

function init() {
    uploadForm.addEventListener('submit', handleUpload);
    loadImages();
}

async function handleUpload(event) {
    event.preventDefault();
    
    if (!imageInput.files.length) {
        showMessage('Please select an image file first.', 'error');
        return;
    }

    const file = imageInput.files[0];
    const formData = new FormData();
    formData.append('image', file);

    try {
        showMessage('Uploading...', 'info');
        
        const response = await fetch(`${API_BASE}/upload`, {
            method: 'POST',
            body: formData,
        });

        const data = await response.json();

        if (!response.ok) {
            showMessage(data.detail || 'Upload failed', 'error');
            return;
        }

        showMessage(`✓ Uploaded: ${data.filename}`, 'success');
        imageInput.value = '';
        
        setTimeout(loadImages, 500);
    } catch (error) {
        console.error('Upload error:', error);
        showMessage(`Error: ${error.message}`, 'error');
    }
}

async function loadImages() {
    try {
        const response = await fetch(`${API_BASE}/images`);
        const data = await response.json();
        
        updateCacheInfo(response);

        gallery.innerHTML = '';

        if (!data.images || data.images.length === 0) {
            gallery.innerHTML = '<p class="loading">No images uploaded yet. Upload one to get started!</p>';
            return;
        }

        data.images.forEach((image) => {
            const item = createGalleryItem(image);
            gallery.appendChild(item);
        });
    } catch (error) {
        console.error('Load images error:', error);
        gallery.innerHTML = `<p class="loading" style="color: #d9534f;">Error loading images: ${error.message}</p>`;
    }
}

function createGalleryItem(image) {
    const div = document.createElement('div');
    div.className = 'gallery-item';
    
    const img = document.createElement('img');
    img.src = image.url;
    img.alt = image.filename;
    img.addEventListener('click', () => viewImage(image));
    
    const info = document.createElement('div');
    info.className = 'gallery-item-info';
    info.textContent = image.filename;
    
    div.appendChild(img);
    div.appendChild(info);
    
    return div;
}

async function viewImage(image) {
    try {
        const response = await fetch(image.url);
        updateCacheInfo(response);
        window.open(image.url, '_blank');
    } catch (error) {
        console.error('View image error:', error);
    }
}

function updateCacheInfo(response) {
    const cacheStatusValue = response.headers.get('CF-Cache-Status') || 'MISS';
    const cfRayValue = response.headers.get('CF-Ray') || 'N/A';
    const now = new Date().toLocaleTimeString();

    cacheStatus.textContent = cacheStatusValue;
    cfRay.textContent = cfRayValue;
    requestTime.textContent = now;

    if (cacheStatusValue === 'HIT') {
        cacheStatus.style.color = '#28a745';
        cacheStatus.textContent = `✓ ${cacheStatusValue}`;
    } else if (cacheStatusValue === 'MISS') {
        cacheStatus.style.color = '#ffc107';
        cacheStatus.textContent = `⟳ ${cacheStatusValue}`;
    } else {
        cacheStatus.style.color = '#667eea';
    }
}

function showMessage(text, type) {
    uploadMessage.textContent = text;
    uploadMessage.className = `message ${type}`;
    
    if (type !== 'error') {
        setTimeout(() => {
            uploadMessage.className = 'message';
            uploadMessage.textContent = '';
        }, 5000);
    }
}

document.addEventListener('DOMContentLoaded', init);
