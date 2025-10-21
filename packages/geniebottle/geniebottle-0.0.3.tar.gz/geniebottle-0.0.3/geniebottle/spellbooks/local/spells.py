from geniebottle.decorators import agent_hint, limit_cost
import pyttsx3
from PIL.Image import Image
from typing import Union, Any
import random


@agent_hint(
    """ Respond to the the user with text. This must be used with "done": true in your
    response to allow the user to respond afterwards.

    Use this for quick replies, if the user only requires a text response or if you
    require further information to assist with the request from the user.

    Args:
        text (str): The text to send to the user.
    """
)
@limit_cost(max_cost=0)
def text_response(text: str, **kwargs):
    """ A spell that returns text provided in the input.

    It is used by an agent to respond to the the user with text. This must be used with
    "done": true in the response to allow the user to respond.

    It should be used if the user only requires a text response or if an agent requires
    further information to assist with the request

    Args:
        text (str): The text to send to the user.
    """
    return text


@agent_hint(
    """ Respond to the the user with text to speech. This must be used with "done": true
    in your response to allow the user to respond afterwards.

    Use this for quick replies, if the user only requires a spoken response or if you
    require further information to assist with the request from the user.

    Args:
        text (str): The text to turn into speech and send to the user.
    """
)
@limit_cost(max_cost=0)
def speech_response(text: str, **kwargs):
    """ A spell that returns speech from text provided in the input.

    Uses the pyttsx3 library to convert text to speech.
    See https://github.com/nateshmbhat/pyttsx3. It is used by an agent to respond to the
    the user with text/speech. This must be used with "done": true in the response to
    allow the user to respond.

    It should be used if the user only requires a speech response or if an agent requires
    further information to assist with the request.

    Args:
        text (str): The text to turn into speech and send to the user.
    """
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()
    return text


@agent_hint(
    """Save text, images, or videos to a file. The format for images should be either
    PNG or JPG, and for videos, it should be MP4. The text will be saved as a .txt file.
    If a file with the same name exists, it will automatically append a number to avoid overwriting.

    Args:
        content (str): The content to save. Specify this by using "results", e.g.
        "results[-1]" for the last "available_results".
        content_type (str): The type of content ('text', 'image', or 'video').
        file_name (str): The name of the file to save the content in. The file extension
        will be added automatically. If file exists, a number will be appended.

    Returns:
        str: Just the absolute file path where the content was saved (no extra text).
    """
)
@limit_cost(max_cost=0)
def save_content(
    content: Any,
    content_type: str,
    file_name: str,
    **kwargs
):
    """ A spell that saves the given content to a file.

    The content can be text, a Bytes base64 encoded image, or a
    Bytes base64 encoded video.

    Args:
        content (Any): The content to save (str, Image, or bytes).
        content_type (str): The type of content ('text', 'image', 'video').
        file_name (str): The file name to save the content as.
    """
    if isinstance(content, str) and not content_type == 'text':
        raise ValueError(
            f"Content {content} is a string. Please use 'text' as the content type."
        )
    import os

    # Determine extension
    if content_type == 'text':
        ext = '.txt'
    elif content_type == 'image':
        ext = '.png'
    elif content_type == 'video':
        ext = '.mp4'
    else:
        raise ValueError(
            "Unsupported content type. Please use 'text', 'image', or 'video'."
        )

    # Handle file name conflicts
    file_path = f'{file_name}{ext}'
    if os.path.exists(file_path):
        counter = 1
        while os.path.exists(f'{file_name}_{counter}{ext}'):
            counter += 1
        file_path = f'{file_name}_{counter}{ext}'

    # Save the content
    if content_type == 'text':
        with open(file_path, 'w') as file:
            file.write(content)
    elif content_type == 'image':
        content.save(file_path)
    elif content_type == 'video':
        with open(file_path, 'wb') as file:
            file.write(content)

    abs_path = os.path.abspath(file_path)
    return abs_path


@agent_hint(
    """ Provide a random number. Can be useful when you need to randomly select or
    decide something. For example, rolling a dice.

    Args:
        min (int): The minimum value to generate.
        max (str): The maximum value to generate.
    """
)
@limit_cost(max_cost=0)
def random_number(min: int, max: int, **kwargs):
    """ Provide a random number. Can be useful when you need to randomly select or
    decide something. For example, rolling a dice.

    Args:
        min (int): The minimum value to generate.
        max (str): The maximum value to generate.
    """
    return random.randint(min, max)


@agent_hint(
    """ Open and display an image file in the default image viewer.

    Args:
        file_path (str): The path to the image file to open.
    """
)
@limit_cost(max_cost=0)
def open_image(file_path: str, **kwargs):
    """ Open and display an image file in the default image viewer.

    Args:
        file_path (str): The path to the image file to open.
    """
    import os
    import subprocess
    import platform

    if not os.path.exists(file_path):
        return f"Error: File not found at {file_path}"

    system = platform.system()
    try:
        if system == "Darwin":  # macOS
            subprocess.run(["open", file_path], check=True)
        elif system == "Windows":
            os.startfile(file_path)
        elif system == "Linux":
            subprocess.run(["xdg-open", file_path], check=True)
        else:
            return f"Unsupported platform: {system}"

        return f"Opened {file_path} in default image viewer"
    except Exception as e:
        return f"Error opening image: {e}"


spells = (text_response, speech_response, save_content, random_number, open_image) 