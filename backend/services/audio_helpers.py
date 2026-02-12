from yt_dlp import YoutubeDL
from io import BytesIO
from faster_whisper import WhisperModel
import subprocess
from io import BytesIO
from fastapi import HTTPException

def _get_audio_buffer(url, task_id: str = None, task_memory: dict = None, tasks_results: dict = None):
    if task_id and task_memory is None:
        raise HTTPException(status_code=400, detail="Task memory is required")
    if task_id and tasks_results is None:
        raise HTTPException(status_code=400, detail="Tasks results is required")
    task_memory[task_id]["progress"] = 0
    task_memory[task_id]["message"] = "Downloading audio"
    task_memory[task_id]["status"] = "processing"
    command = [
        'yt-dlp',
        '-f', 'bestaudio',
        '--quiet',
        '--no-warnings',
        '-o', '-',  # Stream to stdout
        url
    ]
    try:
        # We open the process and read the stream
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout_data, stderr_data = process.communicate()
    except Exception as e:
        task_memory[task_id]["status"] = "failed"
        task_memory[task_id]["message"] = f"Error downloading audio: {e}"
        raise HTTPException(status_code=500, detail=f"Error downloading audio: {e}") from e
    task_memory[task_id]["progress"] = 25
    task_memory[task_id]["message"] = "Audio downloaded"
    task_memory[task_id]["status"] = "processing"

    return BytesIO(stdout_data)


# This library handles decoding via PyAV (no system ffmpeg needed)
model = WhisperModel("small", device="cpu", compute_type="int8")

def _transcribe_audio(audio_buffer, task_id: str = None, task_memory: dict = None, tasks_results: dict = None):
    if task_id and task_memory is None:
        raise HTTPException(status_code=400, detail="Task memory is required")
    if task_id and tasks_results is None:
        raise HTTPException(status_code=400, detail="Tasks results is required")
    task_memory[task_id]["progress"] = 25
    task_memory[task_id]["message"] = "Transcribing audio"
    task_memory[task_id]["status"] = "processing"
    # faster-whisper can take the buffer directly if it's formatted correctly
    # or you can pass the raw binary stream
    try:
        audio_buffer.seek(0)
        segments, info = model.transcribe(audio_buffer)
    except Exception as e:
        task_memory[task_id]["status"] = "failed"
        task_memory[task_id]["message"] = f"Error transcribing audio: {e}"
        raise HTTPException(status_code=500, detail=f"Error transcribing audio: {e}") from e
    task_memory[task_id]["progress"] = 50
    task_memory[task_id]["message"] = "Audio transcribed"
    task_memory[task_id]["status"] = "processing"
    return segments


def transcribe(url, task_id: str = None, task_memory: dict = None, tasks_results: dict = None):
    if task_id and task_memory is None:
        raise HTTPException(status_code=400, detail="Task memory is required")
    if task_id and tasks_results is None:
        raise HTTPException(status_code=400, detail="Tasks results is required")
    audio_buffer = _get_audio_buffer(url, task_id=task_id, task_memory=task_memory, tasks_results=tasks_results)
    return _transcribe_audio(audio_buffer, task_id=task_id, task_memory=task_memory, tasks_results=tasks_results)

