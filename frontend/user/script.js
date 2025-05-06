// Configuration
const API_ENDPOINT = 'https://8ocspcig82.execute-api.us-west-2.amazonaws.com/prod';

// DOM Elements
const userIdInput = document.getElementById('userId');
const getCodeBtn = document.getElementById('getCodeBtn');
const resultContainer = document.getElementById('resultContainer');
const accessCodeElement = document.getElementById('accessCode');
const resultMessage = document.getElementById('resultMessage');
const errorMessage = document.getElementById('errorMessage');

// Event Listeners
getCodeBtn.addEventListener('click', getAccessCode);

// Functions
async function getAccessCode() {
    const userId = userIdInput.value.trim();
    
    if (!userId) {
        showError('Please enter your User ID');
        return;
    }
    
    try {
        getCodeBtn.disabled = true;
        getCodeBtn.textContent = 'Getting Code...';
        hideError();
        
        const response = await fetch(`${API_ENDPOINT}/user/code`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ user_id: userId })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            // Show the access code
            accessCodeElement.textContent = data.access_code;
            resultMessage.textContent = data.message;
            resultContainer.classList.remove('hidden');
        } else {
            showError(`Error: ${data.message}`);
            resultContainer.classList.add('hidden');
        }
    } catch (error) {
        showError(`Error: ${error.message}`);
        resultContainer.classList.add('hidden');
    } finally {
        getCodeBtn.disabled = false;
        getCodeBtn.textContent = 'Get Access Code';
    }
}

function showError(message) {
    errorMessage.textContent = message;
    errorMessage.className = 'message error';
}

function hideError() {
    errorMessage.textContent = '';
    errorMessage.className = 'message';
}
