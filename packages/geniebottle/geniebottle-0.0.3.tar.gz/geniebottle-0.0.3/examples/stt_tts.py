from geniebottle import Magic
from geniebottle.spellbooks import OpenAI
import sounddevice as sd
import soundfile as sf
from io import BytesIO
from pydub import AudioSegment
from pydub.playback import play
import numpy as np
import webrtcvad


# Step 1: Record the audio
def record_until_silence(vad_aggressiveness=2, timeout=1):
    """
    Records audio from the microphone until silence is detected.

    Args:
        vad_aggressiveness (int): VAD aggressiveness. Higher values are more aggressive.
        timeout (float): Amount of silence (in seconds) to consider as end of speech.

    Returns:
        np.ndarray: Recorded audio data.
    """
    vad = webrtcvad.Vad(vad_aggressiveness)
    device_info = sd.query_devices(sd.default.device, 'input')
    print(f'Device info: {device_info}')
    dtype = np.int16
    samplerate = int(device_info['default_samplerate'])

    frame_duration = 30
    samples_per_frame = int(samplerate * frame_duration / 1000)
    num_silent_frames_to_end = int(timeout / (frame_duration / 1000))

    frames_buffer = []
    is_speech_frames = []
    recording_stopped = [False]  # Use a mutable object so it can be modified inside the callback

    def callback(indata, frame_count, time, status):
        if status:
            print(status)

        is_speech = vad.is_speech(indata.tobytes(), samplerate)
        is_speech_frames.append(is_speech)
        frames_buffer.append(indata.copy())

        if len(is_speech_frames) > num_silent_frames_to_end:
            is_speech_frames.pop(0)

        if len(is_speech_frames) == num_silent_frames_to_end and not any(is_speech_frames):
            print("Detected continuous silence, stopping...")
            recording_stopped[0] = True  # Signal to stop recording

    print("Speak into your microphone...")

    with sd.InputStream(callback=callback, dtype=dtype, channels=device_info['max_input_channels'], samplerate=samplerate, blocksize=samples_per_frame):
        while True:
            if recording_stopped[0]:
                break  # Exit the loop when silence is detected
            sd.sleep(1)

    print("Recording stopped, processing the audio...")

    final_recording = np.concatenate(frames_buffer)
    bytes_io = BytesIO()
    bytes_io.name = 'temp_audio.wav'
    sf.write(bytes_io, final_recording, samplerate, format='WAV')
    bytes_io.seek(0)

    return bytes_io


# Step 2: Convert Speech to Text
def speech_to_text(audio_bytes_io):
    magic = Magic()
    openai_spellbook = OpenAI()
    magic.add(openai_spellbook.get('whisper_speech_to_text'))
    return magic.cast(input=audio_bytes_io)


# Step 3: Text to Speech
def text_to_speech(text):
    magic = Magic()
    openai_spellbook = OpenAI()
    magic.add(openai_spellbook.get('tts_text_to_speech'))
    return magic.cast(input=text)


# Example usage
if __name__ == "__main__":
    # Record audio to a file (replace this with actual recording logic)

    while True:
        input("Press Enter to start recording...\n")
        recording = record_until_silence()
        if recording is None:
            continue

        # Convert speech to text
        text = speech_to_text(recording)
        print(f"Transcribed text: {text}")

        # Convert text back to speech and save to a file
        tts_file_path = text_to_speech(text[-1])
        print(f"Generated speech saved to: {tts_file_path}")

        # Play back the generated speech (replace this with actual playback logic)
        audio = AudioSegment.from_file(tts_file_path[-1], format="mp3")
        play(audio)
