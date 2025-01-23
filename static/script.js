let mediaRecorder;
let audioChunks = [];

const recordButton = document.getElementById('recordButton');
const stopButton = document.getElementById('stopButton');
const status = document.getElementById('status');
const transcription = document.getElementById('transcription');

recordButton.addEventListener('click', async () => {
  const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
  mediaRecorder = new MediaRecorder(stream);
  audioChunks = [];

  mediaRecorder.ondataavailable = (event) => {
    console.log('Audio data available:', event.data);
    audioChunks.push(event.data);
  };

  mediaRecorder.onstop = async () => {
    console.log("Recording stopped.");
    const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
    console.log("Audio blob size:", audioBlob.size);
    const formData = new FormData();
    formData.append('audio', audioBlob, 'audio.webm');

    console.log("FormData contents before sending:");
    formData.forEach((value, key) => {
        console.log(key, value);
    });

    status.textContent = 'Processing transcription...';
    const response = await fetch('/transcribe', {
      method: 'POST',
      body: formData,
    });

    if (response.ok) {
      const data = await response.json();
      transcription.textContent = data.transcription;
    } else {
      const error = await response.json();
      transcription.textContent = `Error: ${error.error}`;
    }
    status.textContent = 'Transcription completed.';
  };

  if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
    alert("Your browser doesn't support audio recording.");
    return;
  }  

  mediaRecorder.start();
  status.textContent = 'Recording...';
  recordButton.disabled = true;
  stopButton.disabled = false;
});

stopButton.addEventListener('click', () => {
  mediaRecorder.stop();
  recordButton.disabled = false;
  stopButton.disabled = true;
});
