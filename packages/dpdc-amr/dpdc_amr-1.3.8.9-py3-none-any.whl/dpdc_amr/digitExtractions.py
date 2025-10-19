from ultralytics import YOLO
import cv2
import base64
import numpy as np
from ultralytics.utils.plotting import Annotator
import os
import torch
import time

os.environ["CUDA_LAUNCH_BLOCKING"] = "1"
try:
    torch.cuda.set_per_process_memory_fraction(0.6, 0)
except Exception as e:
    print(e)

current_dir = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(current_dir, 'weights/best.pt')

def getYoloModel():
    """
    Load YOLO model for inference only.
    Uses FP16 on GPU for faster predictions.
    """
    model = YOLO(model_path)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(device)

    # Optional fuse (skip if triggers dataset loading)
    try:
        model.fuse()
    except Exception as e:
        print(f"[WARN] fuse() skipped: {e}")

    model.to(device)
    # Use FP16 on GPU
    if device.type == "cuda":
        try:
            model.model.half()
            print("[INFO] Model using FP16 for faster GPU inference.")
        except Exception as e:
            print(f"[WARN] FP16 failed: {e}")

    return model


def extract_digits(test_model, bigfile, conf, imgflg=False, cropped=False):
    """
    Detect digits/objects from an image using YOLOv8.
    Returns: (digits_str, optional base64 annotated image, optional base64 crop)
    """
    t0 = time.time()
    img = cv2.imread(bigfile, cv2.IMREAD_COLOR)
    if img is None:
        print(f"[ERROR] Failed to read image: {bigfile}")
        return '', '', ''

    annotator = Annotator(img) if imgflg else None
    test_model.conf = conf

    device_str = "cuda" if torch.cuda.is_available() else "cpu"

    try:
        with torch.no_grad():
            r = test_model.predict(
                source=img,
                device=device_str,
                show_conf=True,
                save=False,
                save_crop=False,
                exist_ok=True,
                verbose=False,
                iou=0.4,
                agnostic_nms=True
            )[0]

        if device_str.startswith("cuda"):
            torch.cuda.synchronize()

        boxes = r.boxes
        if boxes is None or len(boxes) == 0:
            print("[WARNING] No boxes found.")
            return '', '', ''

        # --- vectorized processing ----------------------------------
        xywh = boxes.xywh.cpu().numpy()
        confs = boxes.conf.cpu().numpy()
        clses = boxes.cls.cpu().numpy().astype(int)

        avg_y = xywh[:, 1].mean()
        ymask = (xywh[:, 1] >= avg_y - 20.0) & (xywh[:, 1] <= avg_y + 20.0)

        xs_int = xywh[:, 0].astype(int)
        order = np.lexsort((-confs, xs_int))
        xs_sorted = xs_int[order]
        conf_sorted = confs[order]
        cls_sorted = clses[order]

        _, keep_idx = np.unique(xs_sorted, return_index=True)
        keep = order[keep_idx]
        keep = keep[ymask[keep]]

        if keep.size == 0:
            return '', '', ''

        # Build digit string in x order
        digits_str = ''.join(test_model.names[c] for c in cls_sorted[np.isin(order, keep)][np.argsort(xs_sorted[keep_idx])])

        # --- optional annotated image --------------------------------
        base64_image = ''
        if imgflg and annotator is not None:
            for b in boxes[keep]:
                annotator.box_label(b.xyxy[0], test_model.names[int(b.cls)])
            _, buf = cv2.imencode('.jpg', annotator.result())
            base64_image = base64.b64encode(buf).decode()

        # --- optional crop ------------------------------------------
        cb64 = ''
        if cropped:
            xyxy = boxes.xyxy.cpu().numpy()
            x_min, y_min = xyxy[:, 0].min(), xyxy[:, 1].min()
            x_max, y_max = xyxy[:, 2].max(), xyxy[:, 3].max()
            y_min = 0 if y_min < 20 else y_min - 20

            crop = img[int(y_min):int(y_max), int(x_min):int(x_max)]
            if crop.size:
                _, buf = cv2.imencode('.jpg', crop)
                cb64 = base64.b64encode(buf).decode()

        print(f'Extraction in: {(time.time() - t0) * 1000:.2f} ms')
        return digits_str, base64_image, cb64

    except Exception as e:
        print(f"[ERROR] Prediction failed: {e}")
        import traceback
        print(traceback.format_exc())
        try:
            torch.cuda.empty_cache()
        except Exception:
            pass
        return '', '', ''
