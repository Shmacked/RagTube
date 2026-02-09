from yt_dlp import YoutubeDL
from io import BytesIO
from faster_whisper import WhisperModel
import subprocess
from io import BytesIO

def _get_audio_buffer(url):
    command = [
        'yt-dlp',
        '-f', 'bestaudio',
        '--quiet',
        '--no-warnings',
        '-o', '-',  # Stream to stdout
        url
    ]
    
    # We open the process and read the stream
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # communicate() returns (stdout_data, stderr_data)
    stdout_data, stderr_data = process.communicate()
    
    if process.returncode != 0:
        raise Exception(f"yt-dlp error: {stderr_data.decode()}")

    return BytesIO(stdout_data)


# This library handles decoding via PyAV (no system ffmpeg needed)
model = WhisperModel("small", device="cpu", compute_type="int8")

def _transcribe_audio(audio_buffer):
    # faster-whisper can take the buffer directly if it's formatted correctly
    # or you can pass the raw binary stream
    audio_buffer.seek(0)
    segments, info = model.transcribe(audio_buffer)
    return segments


def transcribe(url):
    audio_buffer = _get_audio_buffer(url)
    return _transcribe_audio(audio_buffer)

