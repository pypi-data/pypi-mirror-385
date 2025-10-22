import cv2
import os
import numpy as np
from deepface import DeepFace
from idvpackage.spoof_resources.generate_patches import CropImage
import torch
import torch.nn.functional as F
from idvpackage.spoof_resources.MiniFASNet import MiniFASNetV1SE, MiniFASNetV2
from idvpackage.spoof_resources import transform as trans
import pkg_resources
from concurrent.futures import ThreadPoolExecutor
import gc
import torch.cuda

MODEL_MAPPING = {
    'MiniFASNetV1SE': MiniFASNetV1SE,
    'MiniFASNetV2': MiniFASNetV2
}

# Global variables for model caching
_models = {}
_image_cropper = None
_device = 'cpu'

def _initialize_resources():
    global _models, _image_cropper, _device
    if not _models:
        # Force garbage collection before loading models
        gc.collect()
        torch.cuda.empty_cache() if torch.cuda.is_available() else None
        
        _models = {
            '2.7_80x80_MiniFASNetV2.pth': load_model(pkg_resources.resource_filename('idvpackage', 'spoof_resources/2.7_80x80_MiniFASNetV2.pth')),
            '4_0_0_80x80_MiniFASNetV1SE.pth': load_model(pkg_resources.resource_filename('idvpackage', 'spoof_resources/4_0_0_80x80_MiniFASNetV1SE.pth'))
        }
    if not _image_cropper:
        _image_cropper = CropImage()

def get_bbox(frame):
    try:
        face_objs = DeepFace.extract_faces(frame, detector_backend='fastmtcnn')
        if face_objs:
            biggest_face = max(face_objs, key=lambda face: face['facial_area']['w'] * face['facial_area']['h'])
            facial_area = biggest_face['facial_area']
            x, y, w, h = facial_area['x'], facial_area['y'], facial_area['w'], facial_area['h']
            bbox = [x, y, w, h]
            return bbox
        else:
            return None
    except Exception as e:
        print(f"Error in face detection: {e}")
        return None

def parse_model_name(model_name):
    info = model_name.split('_')[0:-1]
    h_input, w_input = info[-1].split('x')
    model_type = model_name.split('.pth')[0].split('_')[-1]
    scale = None if info[0] == "org" else float(info[0])
    return int(h_input), int(w_input), model_type, scale

def get_kernel(height, width):
    return ((height + 15) // 16, (width + 15) // 16)

def load_model(model_path):
    model_name = os.path.basename(model_path)
    h_input, w_input, model_type, _ = parse_model_name(model_name)
    kernel_size = get_kernel(h_input, w_input)
    
    # Initialize model on CPU to save memory
    model = MODEL_MAPPING[model_type](conv6_kernel=kernel_size).to(_device)
    
    # Load state dict with memory optimization
    state_dict = torch.load(model_path, map_location=_device)
    if next(iter(state_dict)).startswith('module.'):
        state_dict = {k[7:]: v for k, v in state_dict.items()}
    
    model.load_state_dict(state_dict)
    del state_dict
    gc.collect()
    
    model.eval()
    return model

def predict(img, model):
    test_transform = trans.Compose([trans.ToTensor()])
    img = test_transform(img).unsqueeze(0).to(_device)
    
    with torch.no_grad():
        result = model.forward(img)
        result = F.softmax(result).cpu().numpy()
    
    # Clear GPU memory if available
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
    
    return result

def check_image(image):
    height, width, _ = image.shape
    
    # Only check for minimum size, remove strict aspect ratio check
    if height < 240 or width < 320:  # minimum 240p
        print("Image resolution too low. Minimum 320x240 required.")
        return False
    
    return True

def frame_count_and_save(cap):
    frames = []
    frame_skip = 8
    frame_index = 1
    
    while True:
        status, frame = cap.read()
        if not status:
            break
            
        if frame_index % frame_skip == 0:
            # Resize frame immediately to reduce memory
            target_height = 640
            aspect_ratio = frame.shape[1] / frame.shape[0]
            target_width = int(target_height * aspect_ratio)
            
            if target_width > 1280:
                target_width = 1280
                target_height = int(target_width / aspect_ratio)
                
            frame = cv2.resize(frame, (target_width, target_height))
            frames.append(frame)
            
        frame_index += 1
        
        # Clear memory if too many frames
        if len(frames) > 10:
            frames = frames[-10:]
            
    cap.release()
    return frames

def process_frame(frame, image_cropper):
    if frame is None:
        return None
    
    if not check_image(frame):
        return None
        
    bbox = get_bbox(frame)
    if not bbox:
        return "SPOOF"
        
    prediction = np.zeros((1, 3))
    
    try:
        for model_name, model in _models.items():
            h_input, w_input, model_type, scale = parse_model_name(model_name)
            param = {
                "org_img": frame,
                "bbox": bbox,
                "scale": scale,
                "out_w": w_input,
                "out_h": h_input,
                "crop": True if scale is not None else False,
            }
            img = image_cropper.crop(**param)
            prediction += predict(img, model)
            
            # Clear memory
            del img
            gc.collect()
            
        label = np.argmax(prediction)
        value = prediction[0][label] / 2
        
        label_text = "LIVE" if (label == 1 and value > 0.55) or (label == 2 and value < 0.45) else "SPOOF"
        return label_text
    finally:
        # Ensure memory is cleared even if there's an error
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

def test(video_path):
    # Initialize resources only once
    _initialize_resources()
    
    try:
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            print("Error: Could not open video")
            return 'consider'
            
        frames = frame_count_and_save(cap)
        if len(frames) < 3:
            print("Error: Video too short")
            return 'consider'
            
        frames_to_process = [frames[0], frames[3], frames[6], frames[-7], frames[-4], frames[-1]] if len(frames) > 6 else frames[:]
        
        # Clear full frames list to save memory
        del frames
        gc.collect()
        
        all_predictions = []
        with ThreadPoolExecutor(max_workers=2) as executor:  # Reduced max workers
            futures = [executor.submit(process_frame, frame, _image_cropper) for frame in frames_to_process]
            for future in futures:
                result = future.result()
                if result:
                    all_predictions.append(result)
                gc.collect()  # Clear memory after each frame
        
        # Clear processed frames
        del frames_to_process
        gc.collect()
        
        if not all_predictions:
            return 'consider'

        spoof_count = all_predictions.count('SPOOF')
        total_frames = len(all_predictions)
        
        return 'consider' if spoof_count / total_frames >= 0.4 else 'clear'
    finally:
        # Ensure cleanup
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

