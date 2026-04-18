import gradio as gr
import requests
import random
from PIL import Image
from io import BytesIO
import urllib.parse

# ── Models available on Pollinations.ai (no API key needed) ──────────────────
MODELS = {
    "flux": "⚡ Flux — Best Quality",
    "flux-realism": "📸 Flux Realism — Photorealistic",
    "flux-anime": "🎌 Flux Anime — Anime Style",
    "flux-3d": "🎲 Flux 3D — 3D Render",
    "turbo": "🚀 Turbo — Fastest",
}

# ── Style presets ─────────────────────────────────────────────────────────────
STYLES = {
    "None": "",
    "Photorealistic": "photorealistic, 8k ultra detailed, cinematic lighting, sharp focus",
    "Digital Art": "digital art, vibrant colors, trending on artstation, concept art",
    "Anime": "anime style, cel shaded, studio ghibli inspired, beautiful",
    "Oil Painting": "oil painting, classical art, museum quality, brush strokes, masterpiece",
    "Watercolor": "watercolor painting, soft pastel colors, artistic, beautiful",
    "Cyberpunk": "cyberpunk, neon lights, futuristic city, dark atmosphere, rain",
    "Fantasy": "fantasy art, magical, mystical, epic scene, dramatic lighting",
    "Pencil Sketch": "pencil sketch, hand drawn, detailed linework, black and white",
    "Minimalist": "minimalist, clean design, simple, white background, elegant",
    "Vintage": "vintage photography, film grain, retro aesthetic, 1970s, faded colors",
    "3D Render": "3D render, octane render, highly detailed, studio lighting, CGI",
}

# ── Aspect ratios ─────────────────────────────────────────────────────────────
RATIOS = {
    "Square (1:1) — 1024×1024": (1024, 1024),
    "Landscape (16:9) — 1280×720": (1280, 720),
    "Portrait (9:16) — 720×1280": (720, 1280),
    "Wide (4:3) — 1024×768": (1024, 768),
    "HD — 1920×1080": (1920, 1080),
}

def generate_image(prompt, style, model, ratio, neg_prompt, seed_input, num_images, progress=gr.Progress()):
    if not prompt.strip():
        raise gr.Error("⚠️ Please enter a prompt first!")

    style_suffix = STYLES.get(style, "")
    full_prompt = f"{prompt.strip()}, {style_suffix}".strip(", ") if style_suffix else prompt.strip()

    w, h = RATIOS.get(ratio, (1024, 1024))
    model_key = [k for k, v in MODELS.items() if v == model][0]

    seed = int(seed_input) if str(seed_input).strip() else random.randint(0, 999999)

    images = []
    for i in range(int(num_images)):
        progress((i / int(num_images)), desc=f"Generating image {i+1} of {int(num_images)}...")
        current_seed = seed + i
        encoded = urllib.parse.quote(full_prompt)
        url = (
            f"https://image.pollinations.ai/prompt/{encoded}"
            f"?width={w}&height={h}&seed={current_seed}"
            f"&model={model_key}&nologo=true&enhance=true"
        )
        if neg_prompt.strip():
            url += f"&negative={urllib.parse.quote(neg_prompt.strip())}"

        try:
            resp = requests.get(url, timeout=60)
            resp.raise_for_status()
            img = Image.open(BytesIO(resp.content)).convert("RGB")
            images.append(img)
        except Exception as e:
            print(f"Image {i+1} failed: {e}")
            continue

    if not images:
        raise gr.Error("❌ All images failed to generate. Please try again!")

    progress(1.0, desc="Done!")
    info = f"✅ Generated {len(images)} image(s) | Model: {model_key} | Seed: {seed} | Size: {w}×{h}"
    return images, info


# ── Gradio UI ─────────────────────────────────────────────────────────────────
with gr.Blocks(
    title="🎨 AI Image Generator — Free & Unlimited",
    theme=gr.themes.Soft(
        primary_hue="violet",
        secondary_hue="blue",
        neutral_hue="slate",
    ),
    css="""
    .gen-btn { font-size: 1.1rem !important; font-weight: 700 !important; }
    .gallery-wrap { min-height: 300px; }
    footer { display: none !important; }
    """
) as app:

    gr.Markdown("""
    # 🎨 AI Image Generator
    ### Free & Unlimited — No API Key Needed — Powered by Pollinations.ai
    ---
    """)

    with gr.Row():
        # ── LEFT COLUMN ──────────────────────────────────────────────────────
        with gr.Column(scale=1):
            prompt_input = gr.Textbox(
                label="✏️ Your Prompt",
                placeholder="e.g. A majestic lion on a mountain at golden hour, dramatic sky...",
                lines=4,
            )
            neg_input = gr.Textbox(
                label="🚫 Negative Prompt (what to avoid)",
                placeholder="e.g. blurry, ugly, bad anatomy, watermark, text...",
                lines=2,
            )

            with gr.Row():
                model_dd = gr.Dropdown(
                    label="🤖 Model",
                    choices=list(MODELS.values()),
                    value=list(MODELS.values())[0],
                )
                style_dd = gr.Dropdown(
                    label="🎨 Style Preset",
                    choices=list(STYLES.keys()),
                    value="None",
                )

            with gr.Row():
                ratio_dd = gr.Dropdown(
                    label="📐 Aspect Ratio",
                    choices=list(RATIOS.keys()),
                    value=list(RATIOS.keys())[0],
                )
                num_dd = gr.Dropdown(
                    label="🖼️ How Many",
                    choices=["1", "2", "4", "6"],
                    value="4",
                )

            seed_input = gr.Number(
                label="🎲 Seed (leave blank for random)",
                precision=0,
                value=None,
            )

            generate_btn = gr.Button(
                "✨ Generate Images!",
                variant="primary",
                elem_classes=["gen-btn"],
            )
            clear_btn = gr.Button("🗑️ Clear All", variant="secondary")

            gr.Markdown("""
            ---
            ### 💡 Tips
            - **Ctrl+Enter** to generate quickly
            - Use **Style Presets** to enhance quality
            - Add **negative prompt** to remove unwanted things
            - Same **seed** = same image (reproducible)
            - Try **Turbo** model for instant results
            ---
            ### 🤖 Models
            - ⚡ **Flux** — Best overall quality
            - 📸 **Flux Realism** — Photorealistic photos
            - 🎌 **Flux Anime** — Anime & manga style
            - 🎲 **Flux 3D** — 3D renders & CGI
            - 🚀 **Turbo** — Fastest generation
            """)

        # ── RIGHT COLUMN ─────────────────────────────────────────────────────
        with gr.Column(scale=2):
            info_box = gr.Markdown("_Enter a prompt and click Generate to create images!_")
            gallery = gr.Gallery(
                label="🖼️ Generated Images",
                columns=2,
                rows=2,
                height=600,
                object_fit="cover",
                show_download_button=True,
                elem_classes=["gallery-wrap"],
            )

    # ── Events ────────────────────────────────────────────────────────────────
    generate_btn.click(
        fn=generate_image,
        inputs=[prompt_input, style_dd, model_dd, ratio_dd, neg_input, seed_input, num_dd],
        outputs=[gallery, info_box],
    )

    clear_btn.click(
        fn=lambda: ([], "_Enter a prompt and click Generate to create images!_", None),
        outputs=[gallery, info_box, prompt_input],
    )

app.launch()
