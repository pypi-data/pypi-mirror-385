from geniebottle.decorators import agent_hint, limit_cost
from PIL import Image
from diffusers import (
    AutoPipelineForText2Image, 
    StableDiffusionXLPipeline, 
    TextToVideoZeroPipeline,
    TextToVideoZeroSDXLPipeline,
)
import torch
from diffusers import AnimateDiffPipeline, MotionAdapter, EulerDiscreteScheduler
from diffusers.utils import export_to_gif
from diffusers import StableDiffusionXLPipeline, UNet2DConditionModel, EulerDiscreteScheduler
from huggingface_hub import hf_hub_download
from safetensors.torch import load_file
import torch
from pathlib import Path
import numpy as np
import imageio
import tomesd
import warnings


@agent_hint(
    """ Generate an image from text with a local model using the diffusers library.
    This spell is compatible with different hardware including cpu, cuda gpus and mps
    (Apple M1/M2 chips).

    Args:
        input (str): A prompt describing the desired image.
    """
)
@limit_cost(max_cost=0)
def text2image(
    input: str,
    negative_prompt: str = None,
    model_name: str = 'stabilityai/stable-diffusion-xl-base-1.0',
    bits: int = 16,
    width: int = 512,
    height: int = 512,
    steps: int = 50,
    guidance_scale: float = 7.5,
    num_images_per_prompt: int = 1,
    use_safety_checker: bool = True,
    lora_safetensors_path=None,
    local_file_model=None,
    **kwargs
) -> Image:
    """ Generate an image from text with a local model using the diffusers library.
    This spell is compatible with different hardware including cpu, cuda gpus and mps
    (Apple M1/M2 chips).

    Models downloaded by the diffusers library will be stored in the cache at the
    magic/spells/diffusers/hf_cache_dir directory.

    See https://huggingface.co/docs/diffusers/v0.26.1/en/api/pipelines/stable_diffusion/text2img#diffusers.StableDiffusionPipeline.__call__

    Args:
        input (str): The prompt to provide to the model.
        model_name (str): Name of the model to use on Hugging Face's model hub or a
        local file. If a local file is provided, the local_file_model argument must be
        set, providing the name of the base model.
        local_file_model argument must be set, providing the name of the base model.
        bits (int): Number of bits to use for the model.
        width (int): Width of the generated image.
        height (int): Height of the generated image.
        steps (int): Number of steps to use for the model.
        use_safety_checker (bool): Whether to use the safety checker.
        lora_safetensors_path (str): Path to a LoRA safetensors file. If provided, the
        model will use the LoRA safetensors file.
        local_file_model (str): Name of the base model to use if a local file is
        provided to the model_name argument. Currently, only 'StableDiffusionXL' is
        supported.

    Returns:
        A list of PIL.Image objects
    """
    print("Determining the best device for inference...")

    assert bits in (16, 32), "bits must be either 16 or 32"

    # check system hardware and select the appropriate device
    # see https://huggingface.co/docs/diffusers/optimization/mps
    if torch.backends.mps.is_available():
        device = "mps"
    elif torch.cuda.is_available():
        device = "cuda"
    else:
        device = "cpu"

    # define the cache directory relative to the script's directory
    script_dir = Path(__file__).parent.resolve()
    cache_dir = script_dir / 'hf_cache_dir'

    additional_kwargs = {}

    additional_kwargs['use_safetensors'] = True
    additional_kwargs['cache_dir'] = str(cache_dir)

    if bits == 16:
        additional_kwargs["torch_dtype"] = torch.float16
        additional_kwargs["variant"] = "fp16"

    if not use_safety_checker:
        additional_kwargs["safety_checker"] = None
        additional_kwargs["requires_safety_checker"] = False

    print('Creating the pipeline')
    if local_file_model:
        if local_file_model == 'StableDiffusionXL':
            pipeline = StableDiffusionXLPipeline.from_single_file(
                model_name,
                local_files_only=True,
                **additional_kwargs
            ).to(device)
        else:
            raise NotImplementedError('Only StableDiffusionXL has been implemented for local_file_model selection')
    else:
        # load the pipeline (this will download and cache the model the first time)
        pipeline = AutoPipelineForText2Image.from_pretrained(
            model_name,
            **additional_kwargs
        ).to(device)

    if lora_safetensors_path:
        pipeline.load_lora_weights(lora_safetensors_path)

    # enable attention slicing for systems with less than 64 GB of RAM
    # see https://huggingface.co/docs/diffusers/optimization/mps
    # if psutil.virtual_memory().total < 64 * 1024**3:  # 64 GB in bytes
    #     pipeline.enable_attention_slicing()

    # warm-up pass for PyTorch 1.13 on M1/M2 Macs
    # see https://huggingface.co/docs/diffusers/optimization/mps
    # if device == "mps" and torch.__version__.startswith("1.13"):
    #     _ = pipeline(input, num_inference_steps=1)

    print("Generating images...")
    return pipeline(
        input,
        width=width,
        height=height,
        negative_prompt=negative_prompt,
        num_inference_steps=steps,
        guidance_scale=guidance_scale,
        num_images_per_prompt=num_images_per_prompt,
    ).images

def text2video_zero_generator(
    input: str,
    model_name: str = 'runwayml/stable-diffusion-v1-5',
    # model_name: str = "SDXL-Lightning",
    # model_name: str = 'stabilityai/sdxl-turbo',
    bits: int = 16,
    width: int = 512,
    height: int = 512,
    steps: int = 50,
    guidance_scale: float = 7.5,
    motion_field_strength_x: int = 2,
    motion_field_strength_y: int = 2,
    t0: int | None = None,
    t1: int | None = None,
    use_cpu_offloading: bool = False,
    **kwargs
):
    """
    Generate a single frame from text with a local model using the diffusers library.
    Uses the previous frame for context if provided.

    Args:
        input (str): The prompt to provide to the model.
        pipeline (TextToVideoZeroPipeline): Existing pipeline object to avoid recreation.
        model_name (str): Name of the model to use on Hugging Face's model hub or a local file.
        bits (int): Number of bits to use for the model.
        width (int): Width of the generated video.
        height (int): Height of the generated video.
        steps (int): Number of steps to use for the model.
        guidance_scale (float): The scale for classifier-free guidance.
        previous_frame (PIL.Image): Previous frame to be used for context.
        motion_field_strength_x (int): Strength of motion along x-axis.
        motion_field_strength_y (int): Strength of motion along y-axis.
        t0 (int): Starting timestep for motion control.
        t1 (int): Ending timestep for motion control.
        use_cpu_offloading (bool): Whether to use CPU offloading to reduce memory usage.

    Returns:
        Tuple[TextToVideoZeroPipeline, PIL.Image]: The pipeline object and the generated frame.
    """
    device = 'mps'
    script_dir = Path(__file__).parent.resolve()
    cache_dir = script_dir / 'hf_cache_dir'
    # model_name = "runwayml/stable-diffusion-v1-5"
    prompt = input

    compression = 0.6

    if t0 is None:
        t0 = int(0.88 * steps)

    if t1 is None:
        t1 = steps - 1
        if t1 <= t0:
            t1 = t0 + 1

    # if the word stable-diffusion-xl is in the model_name, we use the SDXL pipeline
    if "stable-diffusion-xl" in model_name or "SDXL-Lightning" == model_name or 'stabilityai/sdxl-turbo' == model_name:
        if model_name == 'SDXL-Lightning':
            if width != 1024 or height != 1024:
                warnings.warn("SDXL-Lightning model is best used with 1024x1024 resolution.")
            base = "stabilityai/stable-diffusion-xl-base-1.0"
            repo = "ByteDance/SDXL-Lightning"
            ckpt = "sdxl_lightning_4step_unet.safetensors" # Use the correct ckpt for your step setting!
            unet = UNet2DConditionModel.from_config(base, subfolder="unet").to(device, torch.float16)
            unet.load_state_dict(load_file(hf_hub_download(repo, ckpt), device=device))
            pipe = TextToVideoZeroSDXLPipeline.from_pretrained(base, unet=unet, torch_dtype=torch.float16, variant='fp16', use_safetensors=True, cache_dir=cache_dir).to(device)
            # Ensure sampler uses "trailing" timesteps.
            pipe.scheduler = EulerDiscreteScheduler.from_config(pipe.scheduler.config, timestep_spacing="trailing")
        else:
            pipe = TextToVideoZeroSDXLPipeline.from_pretrained(model_name, torch_dtype=torch.float16, variant='fp16', use_safetensors=True, cache_dir=cache_dir).to(device)
    else:
        pipe = TextToVideoZeroPipeline.from_pretrained(model_name, torch_dtype=torch.float16, cache_dir=cache_dir, variant='fp16').to(device)

    pipe.enable_attention_slicing()

    if compression > 0:
        tomesd.apply_patch(pipe, ratio=compression)

    seed = 0
    video_length = 12 
    chunk_size = 4
    # prompt = "A panda is playing guitar on times square"
    # pipe.scheduler.num_inference_steps = steps

    # Generate the video chunk-by-chunk
    results = []
    chunk_ids = np.arange(0, video_length, chunk_size - 1)
    generator = torch.Generator(device=device)
    for i in range(len(chunk_ids)):
        print(f"Processing chunk {i + 1} / {len(chunk_ids)}")
        ch_start = chunk_ids[i]
        ch_end = video_length if i == len(chunk_ids) - 1 else chunk_ids[i + 1]
        # Attach the first frame for Cross Frame Attention
        frame_ids = [0] + list(range(ch_start, ch_end))
        # Fix the seed for the temporal consistency
        generator.manual_seed(seed)
        output = pipe(
            prompt=prompt, 
            width=width, 
            height=height, 
            video_length=len(frame_ids), 
            generator=generator, 
            frame_ids=frame_ids, 
            num_inference_steps=steps, 
            t0=t0, 
            t1=t1,
            motion_field_strength_x=motion_field_strength_x,
            motion_field_strength_y=motion_field_strength_y,
        )

        result = [Image.fromarray((r * 255).astype("uint8")) for r in output.images[1:]] # skip the cross frame attention frame
        yield result
        results += result

    imageio.mimsave("video.mp4", results, fps=4)

    return result
    # result = [(r * 255).astype("uint8") for r in result]

    # current_frame = (output.images[0] * 255).astype("uint8")
    # pil_frame = Image.fromarray(current_frame)
    
    # return pipeline, pil_frame
    for frame in result:
        current_frame = (frame * 255).astype("uint8")
        pil_frame = Image.fromarray(current_frame)

        yield pil_frame


def animate_diff(
    input: str,
    width: int = 512,
    height: int = 512,
    steps: int = 2,
    **kwargs
):
    """
    """
    device = 'mps'
    script_dir = Path(__file__).parent.resolve()
    cache_dir = script_dir / 'hf_cache_dir'

    dtype = torch.float16

    # steps  # Options: [1,2,4,8]
    repo = "ByteDance/AnimateDiff-Lightning"
    ckpt = f"animatediff_lightning_{steps}step_diffusers.safetensors"
    base = "emilianJR/epiCRealism"  # Choose to your favorite base model.

    adapter = MotionAdapter().to(device, dtype)
    adapter.load_state_dict(load_file(hf_hub_download(repo ,ckpt), device=device))
    pipe = AnimateDiffPipeline.from_pretrained(base, motion_adapter=adapter, torch_dtype=dtype, cache_dir=cache_dir).to(device)
    pipe.scheduler = EulerDiscreteScheduler.from_config(pipe.scheduler.config, timestep_spacing="trailing", beta_schedule="linear", cache_dir=cache_dir)

    output = pipe(prompt=input, guidance_scale=1.0, num_inference_steps=steps, width=width, height=height, num_frames=8)

    export_to_gif(output.frames[0], "animation.gif")

    return output.frames[0]


spells = (text2image, animate_diff, text2video_zero_generator)
