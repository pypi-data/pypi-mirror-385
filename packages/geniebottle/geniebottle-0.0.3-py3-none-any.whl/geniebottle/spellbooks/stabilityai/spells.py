from geniebottle.decorators import agent_hint, bind_to_spellbook
from geniebottle.models import Bytes
from geniebottle.spellbooks import StabilityAI
from stability_sdk import client
import stability_sdk.interfaces.gooseai.generation.generation_pb2 as generation
from typing import Union, Callable
from PIL import Image
import warnings
import mimetypes
import requests
import base64
import time
import json
import io


def setup(
    host: str,
    api_key: str,
    engine: str = 'stable-diffusion-xl-1024-v1-0',
    verbose: bool = True
):
    """ Set up our connection to the API. """
    stability_api = client.StabilityInference(
        host=host,
        key=api_key,
        verbose=verbose,
        engine=engine
    )
    return stability_api


@agent_hint(
    """ Generate an image with stable_diffusion

    Args:
        input (str): A stateless prompt to provide to the model. Use a detailed and
        vivid description with comma-separated details like subject, style,
        mood, color, lighting, perspective, composition, lens type, texture, background
        and fine features. Do not ask questions or refer to prior generated images as
        input is the only context provided to the model.

    Returns:
        A list of Images
    """
)
@bind_to_spellbook(StabilityAI)
def stable_diffusion(
    self,
    input: str,
    engine: str = 'stable-diffusion-xl-1024-v1-0',
    steps: int = 30,
    cfg_scale: float = 7.0,
    width: int = 1024,
    height: int = 1024,
    n: int = 1,
    sampler: int = generation.SAMPLER_K_DPMPP_2M,
    verbose: bool = True,
    seed: Union[int, None] = None,
    callback: Union[Callable, None] = None,
    *args,
    **kwargs
) -> Image:
    """ Generate an image with stable_diffusion

    Args:
        input (str): The prompt to provide to the model. It is best to use a prompt with
        clear, comma-separated details: specify subject, style, mood, color, lighting,
        perspective, composition, and minimize ambiguity.
        engine (str): The engine to use for generation. For a full list of available
        engines, see https://platform.stability.ai/docs/features/api-parameters#engine
        steps (int): Amount of inference steps performed on image generation. Defaults
        to 30.
        cfg_scale (float): Influences how strongly your generation is guided to match
        your prompt. Setting this value higher increases the strength in which it tries
        to match your prompt. Defaults to 7.0.
        width (int): Generation width. Defaults to 512.
        height (int): Generation height. Defaults to 512.
        n (int): The number of images to generate. Defaults to 1.
        sampler (int): Choose which sampler we want to denoise our generation with.
        Import sampler numbers like so:
        ```
        import stability_sdk.interfaces.gooseai.generation.generation_pb2 as generation
        sampler = generation.SAMPLER_K_DPMPP_2M
        ```
        Defaults to k_dpmpp_2m. Clip Guidance only supports ancestral samplers.
        (Available Samplers: ddim, plms, k_euler, k_euler_ancestral, k_heun, k_dpm_2,
        k_dpm_2_ancestral, k_dpmpp_2s_ancestral, k_lms, k_dpmpp_2m, k_dpmpp_sde)
        verbose (bool): Whether to print debug messages. Defaults to True.
        seed (int): Seed to use for generating images deterministically. If a seed is
        used along with all the same generation parameters, you can always recall the
        same image simply by generating it again. Note: This isn't quite the case for
        Clip Guided generations.
        callback (Optional[Callable], optional): A callback function to call with the
        response. It is used for updating the status of responses that are in progress.

    Returns:
        A list of Images
    """
    if callback:
        callback('Connecting to model...')
    stability_api = setup(
        self.host,
        self.api_key,
        engine=engine,
        verbose=verbose
    )

    if callback:
        callback('Drawing...')
    # set up our initial generation parameters
    answers = stability_api.generate(
        prompt=input,
        seed=seed,
        steps=steps,
        cfg_scale=cfg_scale,
        width=width,
        height=height,
        samples=n,
        sampler=sampler
    )

    # Warn if the adult content classifier is tripped.
    for resp in answers:
        for artifact in resp.artifacts:
            if artifact.finish_reason == generation.FILTER:
                warnings.warn(
                    "Your request activated the API's safety filters and could not be "
                    "processed. Please modify the input prompt and try again."
                )
                if callback:
                    callback('An image in your request activated safety filters and could not be processed. Try again with a different prompt.')
            if artifact.type == generation.ARTIFACT_IMAGE:
                img = Image.open(io.BytesIO(artifact.binary))
                yield img


def image_to_bytes(img: Image, format="PNG"):
    """ Convert an image to byte array. """
    im_file = io.BytesIO()
    img.save(im_file, format=format)
    img_bytes = im_file.getvalue()
    return img_bytes


def get_image_format(image_path: str):
    """ Get the format of the image. """
    image_mime_type = mimetypes.guess_type(image_path)[0]
    if image_mime_type is None:
        raise ValueError(f"Unknown image mime type for {image_path}")
    image_format = image_mime_type.split("/")[-1].upper()
    return image_format


def resize_and_crop(image: Image, width: int, height: int):
    """ Resize and crop the image to fit specified dimensions. """
    w, h = image.size
    if w < h:
        image = image.resize((width, int(h * width / w)), Image.Resampling.LANCZOS)
    else:
        image = image.resize((int(w * height / h), height), Image.Resampling.LANCZOS)

    # Center crop
    left = (image.width - width) / 2
    top = (image.height - height) / 2
    right = (image.width + width) / 2
    bottom = (image.height + height) / 2
    image = image.crop((left, top, right, bottom))
    return image


def get_closest_valid_dims(image: Image):
    """ Find the closest valid dimensions for video generation. """
    w, h = image.size
    aspect_ratio = w / h
    portrait_aspect_ratio = 9 / 16
    landscape_aspect_ratio = 16 / 9
    portrait_aspect_ratio_midpoint = (portrait_aspect_ratio + 1) / 2
    landscape_aspect_ratio_midpoint = (landscape_aspect_ratio + 1) / 2

    if aspect_ratio < 1.0:
        # Portrait
        width, height = (576, 1024) if aspect_ratio < portrait_aspect_ratio_midpoint else (768, 768)
    else:
        # Landscape
        width, height = (1024, 576) if aspect_ratio > landscape_aspect_ratio_midpoint else (768, 768)

    return width, height


def image_to_valid_bytes(image: Image):
    """ Convert an image to bytes with valid dimensions. """
    width, height = get_closest_valid_dims(image)
    if image.size != (width, height):
        print(f"Resizing image to {width}x{height}")
        image = resize_and_crop(image, width, height)
    else:
        print(f"Image already has valid dimensions: {width}x{height}")
    print('Converting image to bytes...')
    image_bytes = image_to_bytes(image)
    return image_bytes


@agent_hint(
    """ Generate a video with stable video diffusion

    Args:
        input (Image): An initial image to start the video generation process.
        This can be generated first with a image generation spell. If so specify it
        using the relevant result from `'available_results'`, e.g. `results[-1]`.

    Returns:
        A byte array representing the video.
    """
)
@bind_to_spellbook(StabilityAI)
def stable_video_diffusion(
    self,
    input: Image,
    seed: int = 0,
    cfg_scale: float = 3.0,
    motion_bucket_id: int = 150,
    *args,
    **kwargs
) -> bytes:
    """ Generate a video with stable video diffusion

    Args:
        input (Image): An initial image to start the video generation process.
        This can be generated first with a image generation spell. If so specify it
        using the relevant result from `'available_results'`, e.g. `results[-1]`.
        seed (int): Seed to use for generating images deterministically. If a seed is
        used along with all the same generation parameters, you can always recall the
        same image simply by generating it again. Note: This isn't quite the case for
        Clip Guided generations.
        cfg_scale (float): How strongly the video sticks to the original image. 
        Use lower values to allow the model more freedom to make changes and higher 
        values to correct motion distortions.
        motion_bucket_id (int): Lower values generally result in less motion in the 
        output video, while higher values generally result in more motion. This 
        parameter corresponds to the motion_bucket_id parameter from the paper.

    Returns:
        A byte array representing the video.
    """

    # Convert input image to bytes
    image_bytes = image_to_valid_bytes(input)

    # Set up credentials and headers
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {self.api_key}"
    }
    host = "https://api.stability.ai/v2beta/image-to-video"

    # Prepare request payload
    files = {
        "image": ("file", image_bytes, "image/png"),
        "seed": (None, str(seed).encode('utf-8')),
        "cfg_scale": (None, str(cfg_scale).encode('utf-8')),
        "motion_bucket_id": (None, str(motion_bucket_id).encode('utf-8'))
    }

    # Send REST request
    response = requests.post(host, headers=headers, files=files)
    if not response.ok:
        raise Exception(f"HTTP {response.status_code}: {response.text}")

    # Handle async response and loop until video result or timeout
    response_dict = json.loads(response.text)
    request_id = response_dict.get("id", None)
    if request_id is None:
        raise Exception("No request ID in response")

    timeout = 500  # Modify as needed
    start = time.time()
    while True:
        response = requests.get(f"{host}/result/{request_id}", headers=headers)
        if not response.ok:
            raise Exception(f"HTTP {response.status_code}: {response.text}")
        if response.status_code != 202 or time.time() - start > timeout:
            break
        time.sleep(2)

    # Decode and save video
    json_data = response.json()
    video = base64.b64decode(json_data["video"])
    video = Bytes(video)
    return video



@agent_hint(
    """ Generate an ultra-quality image with stable_diffusion ultra

    Args:
        input (str): A prompt describing the image to generate with high-quality details.
        aspect_ratio (str): Aspect ratio of the generated image, e.g., '16:9'.
        negative_prompt (Optional[str]): Specify elements you do not want in the image.
        seed (Optional[int]): Seed for deterministic generation.
        output_format (str): Desired output format, e.g., 'png', 'jpeg', 'webp'.
        strength (Optional[float]): When image is provided, controls influence of input image.

    Returns:
        Generated image bytes in the specified format.
    """
)
@bind_to_spellbook(StabilityAI)
def stable_image_ultra(
    self,
    input: str,
    aspect_ratio: str = "1:1",
    output_format: str = "png",
    negative_prompt: str = None,
    seed: Union[int, None] = None,
    strength: Union[float, None] = None,
    *args,
    **kwargs
) -> bytes:
    """ Generate an ultra-quality image with Stable Image Ultra

    Args:
        input (str): The descriptive prompt for image generation.
        aspect_ratio (str): Aspect ratio of the output image.
        output_format (str): Format of the output image ('jpeg', 'png', 'webp').
        negative_prompt (Optional[str]): Keywords of what to avoid in the image.
        seed (Optional[int]): A seed for deterministic image generation.
        strength (Optional[float]): Controls influence of the image parameter if image is provided.

    Returns:
        Image bytes in the specified format.
    """

    headers = {
        "Authorization": f"Bearer {self.api_key}",
        "Accept": "image/*"
    }
    files = {"none": ""}
    data = {
        "prompt": input,
        "output_format": output_format,
        "aspect_ratio": aspect_ratio,
    }

    # Include optional parameters if provided
    if negative_prompt:
        data["negative_prompt"] = negative_prompt
    if seed is not None:
        data["seed"] = seed
    if strength is not None:
        data["strength"] = strength

    response = requests.post(
        "https://api.stability.ai/v2beta/stable-image/generate/ultra",
        headers=headers,
        files=files,
        data=data
    )

    if response.status_code == 200:
        return Image.open(io.BytesIO(response.content))
    else:
        raise Exception(f"Failed with status {response.status_code}: {response.json()}")


spells = (stable_diffusion, stable_image_ultra, stable_video_diffusion)
