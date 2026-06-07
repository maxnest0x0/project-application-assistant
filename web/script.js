const inputField = document.querySelector('#idea-input');
const continueButton = document.querySelector('#continue-btn');
const micButton = document.querySelector('#mic-btn');

async function api(url, idea) {
    inputField.disabled = continueButton.disabled = micButton.disabled = true;
    continueButton.classList.add('loading');

    const data = new FormData();
    data.append('idea', idea);

    const response = await fetch(url, { body: data, method: 'POST' });
    const text = await response.text();

    if (response.ok) {
        sessionStorage.application = text;
        window.location.href = 'page2.html';
        return;
    }

    try {
        alert(JSON.parse(text).detail);
    } catch {
        alert('Произошла неизвестная ошибка');
    }

    inputField.disabled = continueButton.disabled = micButton.disabled = false;
    continueButton.classList.remove('loading');
}

async function submitText() {
    const idea = inputField.value.trim();
    if (!idea) return;

    await api('/api/generate', idea);
}

inputField.addEventListener('keydown', event => {
    if (event.key === 'Enter') submitText();
});
continueButton.addEventListener('click', submitText);

let mediaRecorder = null;
micButton.addEventListener('click', async () => {
    if (mediaRecorder && mediaRecorder.state === 'recording') {
        mediaRecorder.stop();
        return;
    }

    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaRecorder = new MediaRecorder(stream);

        const chunks = [];
        mediaRecorder.addEventListener('dataavailable', event => chunks.push(event.data));

        mediaRecorder.addEventListener('stop', async () => {
            micButton.classList.remove('recording');
            await api('/api/generate/from_audio', new Blob(chunks));
        });

        mediaRecorder.start();
        micButton.classList.add('recording');
        inputField.disabled = continueButton.disabled = true;
    } catch {
        alert('Не удалось записать аудио');
        inputField.disabled = continueButton.disabled = micButton.disabled = false;
    }
});
