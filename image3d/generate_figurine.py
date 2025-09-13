# image3d/generate_figurine.py
import os
import torch
from diffusers import StableDiffusionPipeline, DPMSolverMultistepScheduler
import random
from datetime import datetime

# DEFAULT CONFIG (tweak for web use to be lighter)
MODEL_ID = "runwayml/stable-diffusion-v1-5"
STEPS = 28
GUIDANCE = 7.5
DEFAULT_HEIGHT = 768
DEFAULT_WIDTH = 768
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

PROMPT_DEFAULT = (
    "ultra-detailed photorealistic 3D figurine collectible toy, glossy ceramic finish with metallic gold accents, "
    "stylized character pose, dramatic rim lighting, shallow depth of field, 50mm lens bokeh, octane/unreal engine render look, cinematic composition, ultra-detailed textures"
)

NEGATIVE_PROMPT_DEFAULT = "lowres, deformed, watermark, text, signature, extra fingers, malformed, blurry"

def load_pipeline(model_id=MODEL_ID, device=DEVICE):
    pipe = StableDiffusionPipeline.from_pretrained(
        model_id,
        torch_dtype=torch.float16 if device.startswith("cuda") else torch.float32,
        safety_checker=None,
        requires_safety_checker=False
    )
    try:
        pipe.scheduler = DPMSolverMultistepScheduler.from_config(pipe.scheduler.config)
    except Exception:
        pass
    pipe = pipe.to(device)
    try:
        pipe.enable_xformers_memory_efficient_attention()
    except Exception:
        pass
    return pipe

def generate_images(
    pipe,
    prompt=PROMPT_DEFAULT,
    negative_prompt=NEGATIVE_PROMPT_DEFAULT,
    out_dir="outputs_figurine",
    num_images=1,
    steps=STEPS,
    guidance_scale=GUIDANCE,
    height=DEFAULT_HEIGHT,
    width=DEFAULT_WIDTH,
    seed_start=None
):
    os.makedirs(out_dir, exist_ok=True)
    results = []
    for i in range(num_images):
        seed = (seed_start + i) if isinstance(seed_start, int) else random.randint(1, 2**31-1)
        generator = torch.Generator(device=pipe.device).manual_seed(seed)
        out = pipe(
            prompt,
            height=height,
            width=width,
            num_inference_steps=steps,
            guidance_scale=guidance_scale,
            negative_prompt=negative_prompt,
            generator=generator
        )
        img = out.images[0]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"figurine_seed{seed}_{timestamp}_{i+1}.png"
        path = os.path.join(out_dir, filename)
        img.save(path)
        results.append((path, seed))
    return results
