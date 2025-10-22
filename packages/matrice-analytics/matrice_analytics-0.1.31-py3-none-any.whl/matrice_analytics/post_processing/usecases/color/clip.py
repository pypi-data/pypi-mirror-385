import requests
import sys
from pathlib import Path
import logging
import subprocess
import shutil
import os
log_file = open("pip_jetson_bti.log", "w")
cmd = ["pip", "install", "importlib-resources"]
subprocess.run(
        cmd,
        stdout=log_file,
        stderr=subprocess.STDOUT,
        preexec_fn=os.setpgrp   
    )
cmd = ["pip", "install", "httpx", "aiohttp", "filterpy"]
subprocess.run(
        cmd,
        stdout=log_file,
        stderr=subprocess.STDOUT,
        preexec_fn=os.setpgrp   
    )
log_file.close()

import numpy as np
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, field
import cv2
import io
import threading
import onnxruntime as ort
from PIL import Image


try:
    from transformers import CLIPProcessor
    print("transformers imported successfully")
    from importlib.resources import files as ir_files, as_file as ir_as_file
except:
    ir_files = None
    ir_as_file = None
    print("Unable to import transformers/irlib-resources @ clip.py")

def load_model_from_checkpoint(checkpoint_url: str, providers: Optional[List] = None):
    """
    Load an ONNX model from a URL directly into memory without writing locally.
    Enforces the specified providers (e.g., CUDAExecutionProvider) for execution.
    """
    try:
        print(f"Loading model from checkpoint: {checkpoint_url}")

        # Download the checkpoint with streaming
        response = requests.get(checkpoint_url, stream=True, timeout=(30, 200))
        response.raise_for_status()

        # Read the content into bytes
        model_bytes = io.BytesIO()
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                model_bytes.write(chunk)
        model_bytes.seek(0)  # reset pointer to start

        # Prepare session options for performance
        try:
            sess_options = ort.SessionOptions()
            # Enable all graph optimizations
            sess_options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
            # Conservative thread usage – GPU work dominates
            sess_options.intra_op_num_threads = 1
            sess_options.inter_op_num_threads = 1
        except Exception:
            sess_options = None

        # Resolve providers
        available = ort.get_available_providers()
        print("Available providers:", available)
        use_providers = ["CUDAExecutionProvider"] #providers or

        # Validate providers and enforce CUDA when requested
        if any(
            (isinstance(p, tuple) and p[0] == "CUDAExecutionProvider") or p == "CUDAExecutionProvider"
            for p in use_providers
        ):
            if "CUDAExecutionProvider" not in available:
                raise RuntimeError("CUDAExecutionProvider not available in this environment")

        # Load ONNX model from bytes with enforced providers
        model = ort.InferenceSession(
            model_bytes.read(),
            sess_options=sess_options,
            providers=use_providers,
        )

        print("Session providers:", model.get_providers())
        print("Model loaded successfully from checkpoint (in-memory)")
        return model

    except Exception as e:
        print(f"Error loading model from checkpoint: {e}")
        return None



class ClipProcessor:
    def __init__(self,
                 image_model_path: str = 'https://s3.us-west-2.amazonaws.com/testing.resources/datasets/clip_image.onnx',
                 text_model_path: str = 'https://s3.us-west-2.amazonaws.com/testing.resources/datasets/clip_text.onnx',
                 processor_dir: Optional[str] = None,
                 providers: Optional[List[str]] = None):

        self.color_category: List[str] = ["black", "white", "yellow", "gray", "red", "blue", "light blue",
        "green", "brown"]

        self.image_url: str = image_model_path
        self.text_url: str = text_model_path
        # Resolve processor_dir relative to this module, not CWD
        self.processor_path: str = self._resolve_processor_dir(processor_dir)
        print("PROCESSOR PATH->", self.processor_path)
        cwd = os.getcwd()
        print("Current working directory:", cwd)

        log_file = open("pip_jetson_bti.log", "w")
        cmd = ["pip", "install", "--force-reinstall", "huggingface_hub", "regex", "safetensors"]
        subprocess.Popen(
                cmd,
                stdout=log_file,
                stderr=subprocess.STDOUT,
                preexec_fn=os.setpgrp   
            )

        # Determine and enforce providers (prefer CUDA only)
        try:
            available = ort.get_available_providers()
        except Exception:
            print("You are seein this error because of ort :(")
            available = []
        print("True OG Available ONNX providers:", available, 'providers(if any):',providers)

        if providers is None:
            if "CUDAExecutionProvider" in available:
                self.providers = ["CUDAExecutionProvider"]
            else:
                # Enforce GPU-only per requirement; raise if not available
                print("CUDAExecutionProvider not available; ensure CUDA-enabled onnxruntime-gpu is installed and GPU is visible")
        else:
            self.providers = providers

        # Thread-safety to serialize processing
        self._lock = threading.Lock()
        print("Curr Providersss: ",self.providers)

        self.image_sess = load_model_from_checkpoint(self.image_url, providers=self.providers)
        self.text_sess = load_model_from_checkpoint(self.text_url, providers=self.providers)


        # Load CLIPProcessor tokenizer/config from local package data if available
        self.processor = None
        try:
            if self.processor_path and os.path.isdir(self.processor_path):
                self.processor = CLIPProcessor.from_pretrained(self.processor_path, local_files_only=True)
            else:
                # Fallback to hub
                self.processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
        except Exception as e:
            print(f"Falling back to remote CLIPProcessor due to error loading local assets: {e}")
            self.processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

        tok = self.processor.tokenizer(self.color_category, padding=True, return_tensors="np")
        ort_inputs_text = {
            "input_ids": tok["input_ids"].astype(np.int64),
            "attention_mask": tok["attention_mask"].astype(np.int64)
        }
        text_out = self.text_sess.run(["text_embeds"], ort_inputs_text)[0].astype(np.float32)
        self.text_embeds = text_out / np.linalg.norm(text_out, axis=-1, keepdims=True)

        sample = self.processor(images=np.zeros((224, 224, 3), dtype=np.uint8), return_tensors="np")
        self.pixel_template = sample["pixel_values"].astype(np.float32)
        self.min_box_size = 32
        self.max_batch = 32
        # Classify every frame for stability unless changed by caller
        self.frame_skip = 1
        self.batch_pixels = np.zeros((self.max_batch, *self.pixel_template.shape[1:]), dtype=np.float32)

        self.records: Dict[int, Dict[str, float]] = {}
        self.frame_idx = 0
        self.processed_frames = 0


    def _resolve_processor_dir(self, processor_dir: Optional[str]) -> str:
        """
        Find the absolute path to the bundled 'clip_processor' assets directory in the
        installed package, independent of current working directory.

        Resolution order:
        1) Explicit processor_dir if provided.
        2) Directory next to this file: <module_dir>/clip_processor
        3) importlib.resources (Python 3.9+): matrice_analytics.post_processing.usecases.color/clip_processor
        """
        if processor_dir:
            return os.path.abspath(processor_dir)

        # 2) Try path next to this file
        module_dir = Path(__file__).resolve().parent
        candidate = module_dir / "clip_processor"
        if candidate.is_dir():
            return str(candidate)

        # 3) Try importlib.resources if available
        try:
            if ir_files is not None:
                pkg = "matrice_analytics.post_processing.usecases.color"
                res = ir_files(pkg).joinpath("clip_processor")
                try:
                    # If packaged in a zip, materialize to a temp path
                    with ir_as_file(res) as p:
                        if Path(p).is_dir():
                            return str(p)
                except Exception:
                    # If already a concrete path
                    if res and str(res):
                        return str(res)
        except Exception:
            pass

        # Fallback to CWD-relative (last resort)
        return os.path.abspath("clip_processor")

    def process_color_in_frame(self, detections, input_bytes, zones: Optional[Dict[str, List[List[float]]]], stream_info):
        # Serialize processing to avoid concurrent access and potential frame drops
        with self._lock:
            print("=== process_color_in_frame called ===")
            print(f"Number of detections: {len(detections) if detections else 0}")
            print(f"Input bytes length: {len(input_bytes) if input_bytes else 0}")

            boxes = []
            tracked_ids: List[int] = []
            frame_number: Optional[int] = None
            print(detections)
            self.frame_idx += 1

            if not detections:
                print(f"Frame {self.frame_idx}: No detections provided")
                self.processed_frames += 1
                return {}

            nparr = np.frombuffer(input_bytes, np.uint8)        # convert bytes to numpy array
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)      # decode image

            if image is None:
                print(f"Frame {self.frame_idx}: Failed to decode image")
                self.processed_frames += 1
                return {}

            # Step 2: Use decoded frame directly (BGR → RGB performed at crop time)
            frame = image
            if stream_info:
                input_settings = stream_info.get("input_settings", {})
                start_frame = input_settings.get("start_frame")
                end_frame = input_settings.get("end_frame")
                if start_frame is not None and end_frame is not None and start_frame == end_frame:
                    frame_number = start_frame

            for det in detections:
                bbox = det.get('bounding_box')
                tid = det.get('track_id')
                if not bbox or not tid:
                    continue
                w = bbox['xmax'] - bbox['xmin']
                h = bbox['ymax'] - bbox['ymin']
                if w >= self.min_box_size and h >= self.min_box_size:
                    boxes.append(bbox)
                    tracked_ids.append(tid)

            if not boxes:
                print(f"Frame {self.frame_idx}: No cars in zone")
                self.processed_frames += 1
                return {}

            # print(boxes)
            # print(tracked_ids)
            crops_for_model = []
            map_trackidx_to_cropidx = []
            for i, (bbox, tid) in enumerate(zip(boxes, tracked_ids)):
                last_rec = self.records.get(tid)
                should_classify = False
                if last_rec is None:
                    should_classify = True
                else:
                    if (self.frame_idx - last_rec.get("last_classified_frame", -999)) >= self.frame_skip:
                        should_classify = True
                if should_classify:
                    x1, y1, x2, y2 = bbox['xmin'], bbox['ymin'], bbox['xmax'], bbox['ymax']
                    # crop safely - convert to integers
                    y1c, y2c = max(0, int(y1)), min(frame.shape[0], int(y2))
                    x1c, x2c = max(0, int(x1)), min(frame.shape[1], int(x2))
                    print(f"Cropping bbox: x1c={x1c}, y1c={y1c}, x2c={x2c}, y2c={y2c}, frame_shape={frame.shape}")
                    if y2c - y1c <= 0 or x2c - x1c <= 0:
                        print(f"Skipping invalid crop: dimensions {x2c-x1c}x{y2c-y1c}")
                        continue
                    crop = cv2.cvtColor(frame[y1c:y2c, x1c:x2c], cv2.COLOR_BGR2RGB)
                    map_trackidx_to_cropidx.append((tid, len(crops_for_model)))
                    # Pass raw numpy crop; resize handled in run_image_onnx_on_crops
                    crops_for_model.append(crop)
                    # print(f"Added crop for track_id {tid}")
            # print(crops_for_model)

            record = {}  # Initialize record outside the if block
            if crops_for_model:
                img_embeds = self.run_image_onnx_on_crops(crops_for_model)  # [N, D]
                # compute similarity with text_embeds (shape [num_labels, D])
                sims = img_embeds @ self.text_embeds.T  # [N, num_labels]
                # convert to probs
                probs = np.exp(sims) / np.exp(sims).sum(axis=-1, keepdims=True)  # softmax numerically simple
                # print(probs)

                # assign back to corresponding tracks
                for (tid, crop_idx) in map_trackidx_to_cropidx:
                    prob = probs[crop_idx]
                    # print(prob)
                    best_idx = int(np.argmax(prob))
                    best_label = self.color_category[best_idx]
                    # print(best_label)
                    best_score = float(prob[best_idx])
                    # print(best_score)

                    rec = self.records.get(tid)
                    det_info = next((d for d in detections if d.get("track_id") == tid), {})
                    category_label = det_info.get("category", "unknown")
                    zone_name = det_info.get("zone_name", "Unknown_Zone")
                    record[tid] = {
                        "frame": self.frame_idx,
                        "color": best_label,
                        "confidence": best_score,
                        "track_id": tid,
                        "object_label": category_label,
                        "zone_name": zone_name,
                        "last_classified_frame": self.frame_idx,
                    }
            print(record)

            return record


    def run_image_onnx_on_crops(self, crops):
        valid_crops = []
        for i, crop in enumerate(crops):
            if isinstance(crop, Image.Image):  # PIL.Image
                crop = np.array(crop)
            if not isinstance(crop, np.ndarray):
                print(f"Skipping crop {i}: not a numpy array ({type(crop)})")
                continue
            if crop.size == 0:
                print(f"Skipping crop {i}: empty array")
                continue

            try:
                crop_resized = cv2.resize(crop, (224, 224), interpolation=cv2.INTER_LINEAR)
                valid_crops.append(crop_resized)
            except Exception as e:
                print(f"Skipping crop {i}: resize failed ({e})")

        if not valid_crops:
            print("No valid crops to process")
            return np.zeros((0, self.text_embeds.shape[-1]), dtype=np.float32)

        # Convert all valid crops at once

        #ToDO: Check if the processor and model.run is running on single thread and is uusing GPU. Latency should be <100ms.

        pixel_values = self.processor(images=valid_crops, return_tensors="np")["pixel_values"]
        n = pixel_values.shape[0]
        self.batch_pixels[:n] = pixel_values

        ort_inputs = {"pixel_values": self.batch_pixels[:n]}
        img_out = self.image_sess.run(["image_embeds"], ort_inputs)[0].astype(np.float32)

        return img_out / np.linalg.norm(img_out, axis=-1, keepdims=True)


    def _is_in_zone(self, bbox, polygon: List[List[float]]) -> bool:
        if not polygon:
            return False
        # print(bbox)
        x1, y1, x2, y2 = bbox['xmin'], bbox['ymin'], bbox['xmax'], bbox['ymax']
        # print(x1,x2,y1,y2)
        # print(type(x1))
        # print(polygon)
        cx, cy = int((x1 + x2) / 2), int((y1 + y2) / 2)
        polygon = np.array(polygon, dtype=np.int32)
        return cv2.pointPolygonTest(polygon, (cx, cy), False) >= 0


