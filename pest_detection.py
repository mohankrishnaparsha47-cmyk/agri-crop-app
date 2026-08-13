"""
Pest & Disease Detection module.

IMPORTANT (for your project report):
This ships with a DEMO classifier that uses basic image color/texture
heuristics to simulate detection - it is NOT a trained deep learning model,
because training a real CNN needs a large labeled leaf-disease image dataset
and GPU time that isn't available in this environment.

TO GO LIVE with a real model:
1. Download the free "PlantVillage" dataset (~54,000 labeled leaf images,
   38 classes) from Kaggle: https://www.kaggle.com/datasets/emmarex/plantdisease
2. Train a CNN (e.g. MobileNetV2 transfer learning) using TensorFlow/Keras
   or PyTorch - typically 85-95% accuracy achievable in a few hours on a
   free Google Colab GPU.
3. Export the trained model (e.g. `model.h5` or `model.tflite`) and replace
   the `detect_pest_disease()` function below to load and run inference on
   the uploaded image instead of the heuristic logic.

This demo version is still useful to *demonstrate the feature/UI flow* in
your presentation and viva - just be transparent that it's a placeholder
pending real model training when asked.
"""

import random
from PIL import Image
import colorsys

DISEASE_LIBRARY = {
    "healthy": {
        "name": "Healthy Leaf",
        "severity": "None",
        "advice": "No action needed. Continue regular monitoring and balanced fertilization."
    },
    "leaf_blight": {
        "name": "Leaf Blight",
        "severity": "Moderate",
        "advice": "Remove affected leaves. Apply copper-based fungicide (e.g. Copper Oxychloride) every 10-14 days. Avoid overhead irrigation."
    },
    "leaf_spot": {
        "name": "Leaf Spot Disease",
        "severity": "Mild",
        "advice": "Apply Mancozeb or Chlorothalonil fungicide spray. Improve field drainage and spacing for airflow."
    },
    "powdery_mildew": {
        "name": "Powdery Mildew",
        "severity": "Moderate",
        "advice": "Spray sulfur-based fungicide. Reduce humidity around plants, avoid excess nitrogen fertilizer."
    },
    "pest_infestation": {
        "name": "Pest Infestation (Aphids/Whitefly)",
        "severity": "Moderate to Severe",
        "advice": "Use Neem oil spray for organic control, or Imidacloprid for chemical control. Introduce natural predators like ladybirds where possible."
    },
    "nutrient_deficiency": {
        "name": "Nutrient Deficiency (likely Nitrogen/Iron)",
        "severity": "Mild",
        "advice": "Apply balanced NPK fertilizer or foliar spray. Get a soil test done via the Soil Health Card scheme for precise diagnosis."
    },
}


def _analyze_image_heuristic(image_path):
    """
    Very basic demo heuristic: looks at average color tone of the image to
    pick a plausible-sounding category. This is NOT real disease detection -
    it's a stand-in so the upload -> result UI flow can be demonstrated.
    """
    try:
        img = Image.open(image_path).convert("RGB")
        img = img.resize((100, 100))
        pixels = list(img.getdata())
        avg_r = sum(p[0] for p in pixels) / len(pixels)
        avg_g = sum(p[1] for p in pixels) / len(pixels)
        avg_b = sum(p[2] for p in pixels) / len(pixels)

        h, s, v = colorsys.rgb_to_hsv(avg_r / 255, avg_g / 255, avg_b / 255)

        # crude bucket logic based on hue/saturation/brightness
        if s < 0.15 and v > 0.6:
            return "nutrient_deficiency", round(random.uniform(60, 75), 1)
        if 0.20 <= h <= 0.42 and s > 0.35 and v > 0.35:
            return "healthy", round(random.uniform(80, 95), 1)
        if v < 0.35:
            return "leaf_blight", round(random.uniform(65, 85), 1)
        if s > 0.5 and h < 0.15:
            return "pest_infestation", round(random.uniform(60, 80), 1)
        if 0.08 <= h < 0.20:
            return "leaf_spot", round(random.uniform(55, 78), 1)
        return "powdery_mildew", round(random.uniform(55, 72), 1)

    except Exception:
        return "healthy", 50.0


def detect_pest_disease(image_path):
    key, confidence = _analyze_image_heuristic(image_path)
    info = DISEASE_LIBRARY[key]
    return {
        "condition": info["name"],
        "severity": info["severity"],
        "advice": info["advice"],
        "confidence": confidence,
        "is_demo": True
    }
