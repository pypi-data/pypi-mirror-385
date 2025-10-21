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
# Initialize a global buffer
audio_buffer = bytes()


def play_audio_chunk(audio_chunk: bytes, threshold_bytes=129540, is_final=False):
    """
    Buffers and plays audio data chunks smoothly by accumulating enough data before playback.

    Args:
        audio_chunk (bytes): A chunk of MP3 audio data.
        threshold_bytes (int): The minimum buffer size to trigger playback.
    """
    global audio_buffer

    # Append the new audio chunk to the buffer
    audio_buffer += audio_chunk

    def play_buffer():
        global audio_buffer
        try:
            audio_segment = AudioSegment.from_file(BytesIO(audio_buffer), format="mp3")
            samples = np.array(audio_segment.get_array_of_samples())
            if audio_segment.channels == 2:
                samples = samples.reshape((-1, 2))

            sd.play(samples, audio_segment.frame_rate)
            sd.wait()  # Ensure playback finishes

            audio_buffer = bytes()  # Clear the buffer after playback
        except Exception as e:
            print(f"Error processing audio chunk: {e}")

    # Play if buffer reaches threshold or if this is the final chunk of audio
    if len(audio_buffer) >= threshold_bytes or is_final:
        if not is_final:
            print("Playing buffered audio...")
        else:
            print("Playing final audio...")
        play_buffer()


# Example usage
def main():
    magic = Magic()
    openai_spellbook = OpenAI()
    magic.add(openai_spellbook.get('chatgpt_tts_stream'))

    texts = []

    while True:
        input("Press Enter to start recording...\n")
        recording = record_until_silence()
        if recording is None:
            continue

        # Convert speech to text
        text_gen = speech_to_text(recording)
        text = list(text_gen)[-1]  # Get the last item from the generator
        print(f"Transcribed text: {text}")

        # Process chat and get TTS streamed back, playing it live
        response_gen = magic.cast(
            input=text,
            system='You are C-3PO, Human-Cyborg Relations.',
            context=texts,
            callback=play_audio_chunk,
        )

        # Consume the generator to get the response
        response = list(response_gen)[-1]  # Get the last item (the full text)

        # add using chatml
        texts.append({'role': 'user', 'content': text})
        texts.append({'role': 'assistant', 'content': response})


if __name__ == "__main__":
    main()
