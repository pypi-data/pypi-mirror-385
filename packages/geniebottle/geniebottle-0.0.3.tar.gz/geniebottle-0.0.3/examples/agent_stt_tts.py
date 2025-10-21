from geniebottle import Magic
from geniebottle.spellbooks import Agent, OpenAI, StabilityAI, Local
import sounddevice as sd
import soundfile as sf
from io import BytesIO
from pydub import AudioSegment
from pydub.playback import play
import numpy as np
import webrtcvad
from rich.prompt import Prompt
from rich.live import Live
from rich import print


# Step 1: Record the audio
def record_until_silence(vad_aggressiveness=3, timeout=1):
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


def chat(text, context=None, system='You are a helpful assistant'):
    magic = Magic()
    openai_spellbook = OpenAI()
    magic.add(openai_spellbook.get('chatgpt'))
    return magic.cast(input=text, context=context, system=system)



magic = Magic(max_cost_per_cast=0.55)

spellbook = Agent()

magic.add(spellbook.get('LLMAgent'))

role = (
    "You are Jarvis, created by Tony Stark"
)
print(f'My role is: {role}. Chat with me to get started!')


def callback(text, agent_json=False, save=False):
    ''' Callback function to update the live display of the response '''
    if isinstance(text, str):
        live.update(text)


memory = None
results = None
while True:
    live = Live("")
    with live:
        live.start()

        input("Press Enter to start recording...\n")
        recording = record_until_silence()
        if recording is None:
            continue

        # Convert speech to text
        text = speech_to_text(recording)
        print(f"Transcribed text: {text}")

        out = magic.cast(
            input=text[-1],
            memory=memory,
            results=results,
            spells_at_disposal=[
                Local().get('text_response'),
                Local().get('save_content'),
                Local().get('random_number'),
                StabilityAI().get('stable_diffusion'),
                OpenAI().get('chatgpt'),
                StabilityAI().get('stable_video_diffusion')
            ],
            role=role,
            brain=OpenAI().get('chatgpt', model='gpt-4-1106-preview', max_input_tokens=5000),
            callback=callback
        )

        # Convert text back to speech and save to a file
        tts_file_path = text_to_speech(out[-1]['new_results'][-1])

        # Play back the generated speech (replace this with actual playback logic)
        audio = AudioSegment.from_file(tts_file_path[-1], format="mp3")
        play(audio)

        live.stop()
        memory = out[-1]['memory']
        results = out[-1]['results']

