// Configuration
const API_ENDPOINT = 'https://8ocspcig82.execute-api.us-west-2.amazonaws.com/prod';

// DOM Elements
const accessCodesTextarea = document.getElementById('accessCodes');
const uploadBtn = document.getElementById('uploadBtn');
const uploadMessage = document.getElementById('uploadMessage');
const refreshBtn = document.getElementById('refreshBtn');
const resetBtn = document.getElementById('resetBtn');
const availableCount = document.getElementById('availableCount');
const usedCount = document.getElementById('usedCount');
const availableCodes = document.getElementById('availableCodes');
const usedCodes = document.getElementById('usedCodes');

// Event Listeners
uploadBtn.addEventListener('click', uploadAccessCodes);
refreshBtn.addEventListener('click', refreshStatus);
resetBtn.addEventListener('click', resetAllCodes);

// Initialize
document.addEventListener('DOMContentLoaded', refreshStatus);

// Functions
async function uploadAccessCodes() {
    const codes = accessCodesTextarea.value
        .split('\n')
        .map(code => code.trim())
        .filter(code => code !== '');
    
    if (codes.length === 0) {
        showMessage('Please enter at least one access code', 'error');
        return;
    }
    
    try {
        uploadBtn.disabled = true;
        uploadBtn.textContent = 'Uploading...';
        
        const response = await fetch(`${API_ENDPOINT}/admin/upload`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ access_codes: codes })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showMessage(`Successfully uploaded ${data.count} access codes`, 'success');
            accessCodesTextarea.value = '';
            refreshStatus();
        } else {
            showMessage(`Error: ${data.message}`, 'error');
        }
    } catch (error) {
        showMessage(`Error: ${error.message}`, 'error');
    } finally {
        uploadBtn.disabled = false;
        uploadBtn.textContent = 'Upload Access Codes';
    }
}

async function refreshStatus() {
    try {
        refreshBtn.disabled = true;
        refreshBtn.textContent = 'Loading...';
        
        const response = await fetch(`${API_ENDPOINT}/admin/list`, {
            method: 'GET'
        });
        
        const data = await response.json();
        
        if (response.ok) {
            // Update counts
            availableCount.textContent = data.available_count;
            usedCount.textContent = data.used_count;
            
            // Update available codes list
            availableCodes.innerHTML = '';
            data.available_codes.forEach(code => {
                const codeItem = document.createElement('div');
                codeItem.className = 'code-item';
                codeItem.textContent = code;
                availableCodes.appendChild(codeItem);
            });
            
            // Update used codes list
            usedCodes.innerHTML = '';
            Object.entries(data.used_codes).forEach(([userId, code]) => {
                const codeItem = document.createElement('div');
                codeItem.className = 'code-item';
                codeItem.textContent = `${userId}: ${code}`;
                usedCodes.appendChild(codeItem);
            });
        } else {
            showMessage(`Error: ${data.message}`, 'error');
        }
    } catch (error) {
        showMessage(`Error: ${error.message}`, 'error');
    } finally {
        refreshBtn.disabled = false;
        refreshBtn.textContent = 'Refresh Status';
    }
}

function showMessage(message, type) {
    uploadMessage.textContent = message;
    uploadMessage.className = `message ${type}`;
    
    // Clear message after 5 seconds
    setTimeout(() => {
        uploadMessage.textContent = '';
        uploadMessage.className = 'message';
    }, 5000);
}

async function resetAllCodes() {
    if (!confirm('Are you sure you want to reset all access codes? This action cannot be undone.')) {
        return;
    }
    
    try {
        resetBtn.disabled = true;
        resetBtn.textContent = 'Resetting...';
        
        const response = await fetch(`${API_ENDPOINT}/admin/reset`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({})
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showMessage('All access codes have been reset successfully', 'success');
            refreshStatus();
        } else {
            showMessage(`Error: ${data.message}`, 'error');
        }
    } catch (error) {
        showMessage(`Error: ${error.message}`, 'error');
    } finally {
        resetBtn.disabled = false;
        resetBtn.textContent = 'Reset All Codes';
    }
}
