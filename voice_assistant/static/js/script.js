const startBtn = document.getElementById('start-btn');
const stopBtn = document.getElementById('stop-btn');
const status = document.getElementById('status');
const commandLog = document.getElementById('command-log');

let recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
recognition.lang = 'en-US';
recognition.interimResults = false;

startBtn.addEventListener('click', () => {
    recognition.start();
    status.textContent = 'Status: Listening...';
    startBtn.disabled = true;
    stopBtn.disabled = false;
});

stopBtn.addEventListener('click', () => {
    recognition.stop();
    status.textContent = 'Status: Idle';
    startBtn.disabled = false;
    stopBtn.disabled = true;
});

recognition.onresult = (event) => {
    const command = event.results[0][0].transcript;
    commandLog.innerHTML += `<p>Command: ${command}</p>`;
    
    fetch('/process-voice/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({ command: command })
    })
    .then(response => response.json())
    .then(data => {
        commandLog.innerHTML += `<p>Response: ${data.response}</p>`;
        commandLog.scrollTop = commandLog.scrollHeight;
    });
};

recognition.onend = () => {
    status.textContent = 'Status: Idle';
    startBtn.disabled = false;
    stopBtn.disabled = true;
};

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

