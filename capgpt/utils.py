# capgpt/utils.py
import torch, os
from diffusers import StableDiffusionImg2ImgPipeline, DPMSolverMultistepScheduler
from PIL import Image
from datetime import datetime

MODEL_ID = "runwayml/stable-diffusion-v1-5"   # swap with SDXL if available
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

PROMPT = (
    "Capgemini-inspired futuristic 3D figurine, glossy ceramic finish, "
    "cyan-blue highlights (#17ABDA), ultra-detailed photoreal collectible toy, "
    "studio rim lighting, cinematic render"
)
NEG_PROMPT = "lowres, blurry, distorted, extra limbs, watermark, text"

def load_img2img_pipeline():
    pipe = StableDiffusionImg2ImgPipeline.from_pretrained(
        MODEL_ID,
        torch_dtype=torch.float16 if DEVICE=="cuda" else torch.float32,
        safety_checker=None,
        requires_safety_checker=False
    )
    pipe.scheduler = DPMSolverMultistepScheduler.from_config(pipe.scheduler.config)
    return pipe.to(DEVICE)

pipe = load_img2img_pipeline()

def generate_3d_image(upload_path, out_dir="media/generated", strength=0.65):
    os.makedirs(out_dir, exist_ok=True)
    init_img = Image.open(upload_path).convert("RGB").resize((768,768))

    result = pipe(
        prompt=PROMPT,
        negative_prompt=NEG_PROMPT,
        image=init_img,
        strength=strength,
        guidance_scale=7.5,
        num_inference_steps=28,
    ).images[0]

    filename = f"capgpt_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    out_path = os.path.join(out_dir, filename)
    result.save(out_path)
    return out_path
