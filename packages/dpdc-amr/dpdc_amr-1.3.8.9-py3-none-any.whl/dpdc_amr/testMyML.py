from PIL import Image
import os
from ultralytics import YOLO
import torch
import time
import cv2
import numpy as np

os.environ["CUDA_LAUNCH_BLOCKING"] = "1"
try:
    torch.cuda.set_per_process_memory_fraction(0.6, 0)
except Exception as e:
    print(e)

current_dir = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(current_dir, 'weights/best_cls.pt')

# Module-level warmup flag
_warmup_done = False

def getModel():
    """
    Load YOLO model strictly for inference (classification only).
    Returns: model
    """
    model = YOLO(model_path, task="classify")  # strict inference
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(device)
    model.to(device)

    # Optional fuse, skip if triggers dataset loading
    try:
        model.fuse()
    except Exception as e:
        print(f"[WARN] fuse() skipped: {e}")

    # Try FP16 on GPU for speed
    if device.type == "cuda":
        try:
            model.model.half()
            print("[INFO] Model converted to FP16 for faster inference.")
        except Exception as e:
            print(f"[WARN] FP16 conversion failed: {e}")

    # Light warmup (small dummy image)
    global _warmup_done
    if not _warmup_done:
        try:
            dummy = np.zeros((64, 64, 3), dtype=np.uint8)
            with torch.no_grad():
                _ = model(dummy, device=str(device), imgsz=64, verbose=False)
            if device.type == "cuda":
                torch.cuda.synchronize()
            _warmup_done = True
            print("[INFO] Model warmup complete.")
        except Exception as e:
            print(f"[WARN] Warmup failed: {e}")

    return model

def _read_image_fast(path):
    """
    Fast image reader returning RGB uint8 numpy array.
    Falls back to PIL if cv2 cannot read.
    """
    img_bgr = cv2.imread(str(path), cv2.IMREAD_COLOR)
    if img_bgr is None:
        try:
            pil = Image.open(path).convert('RGB')
            arr = np.asarray(pil, dtype=np.uint8)
            return arr
        except Exception as e:
            print(f"[ERROR] cannot read image {path}: {e}")
            return None
    # BGR -> RGB
    img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
    return img_rgb

def examine(model, imgFile):
    """
    Fast single-image classification using the provided model.
    Returns: label string (same style as original).
    """
    start = time.time()
    class_names = ['IllegibleMeter', 'Calculator', 'Meter', 'Non-Meter']
    device_str = "cuda" if torch.cuda.is_available() else "cpu"

    try:
        img = _read_image_fast(imgFile)
        if img is None:
            return "Unknown"

        with torch.no_grad():
            results = model(img, device=device_str, verbose=False)
            if device_str.startswith("cuda"):
                torch.cuda.synchronize()

        # parse classification result
        pred_idx = None
        try:
            pred_idx = int(results[0].probs.top1)
        except Exception:
            # fallback for detection-like parsing
            try:
                res0 = results[0]
                if hasattr(res0, "boxes") and res0.boxes is not None and len(res0.boxes) > 0:
                    pred_idx = int(res0.boxes.cls[0].item())
            except Exception:
                pred_idx = None

        elapsed_ms = round((time.time() - start) * 1000, 2)
        print('Classified in: ' + str(elapsed_ms) + ' ms')

        if pred_idx is None:
            return "Unknown"
        return class_names[pred_idx]

    except Exception as e:
        print(f"[ERROR] Prediction failed: {e}")
        import traceback
        print(traceback.format_exc())

        try:
            torch.cuda.empty_cache()
        except Exception:
            pass

        return "Unknown"
