import torch
import torchvision
import numpy as np
import time
import cv2
import os
from jetracer.nvidia_racecar import NvidiaRacecar
from jetcam.csi_camera import CSICamera
from torch2trt import torch2trt
from torch2trt import TRTModule

from autopilot_utils import preprocess_image, center_crop_square
from autopilot_model import AutopilotModel

# TODO: set your paths
MODELS_DIR = ""
NAME = ""
MODEL_PATH = MODELS_DIR + NAME + ".pth"
MODEL_PATH_TRT = MODELS_DIR + NAME + "_trt.pth"

STEERING_OFFSET = 0.035
THROTTLE_GAIN = 0.8

CAMERA_WIDTH = 448
CAMERA_HEIGHT = 336

FRAME_SIZE = 224
FRAME_CHANNELS = 3

SHOW_LOGS = False

# Model
if os.path.isfile(MODEL_PATH_TRT):
	model_trt = TRTModule()
	model_trt.load_state_dict(torch.load(MODEL_PATH_TRT))
else:
	model = AutopilotModel(pretrained=False)
	model.load_from_path(MODEL_PATH)
	model.eval()

	x = torch.ones((1, FRAME_CHANNELS, FRAME_SIZE, FRAME_SIZE)).cuda()
	model_trt = torch2trt(model, [x], fp16_mode=True)
	torch.save(model_trt.state_dict(), MODEL_PATH_TRT)

try:
	# Car
	car = NvidiaRacecar()
	car.throttle_gain = THROTTLE_GAIN
	car.steering_offset = STEERING_OFFSET

	# Camera
	camera = CSICamera(width=CAMERA_WIDTH, height=CAMERA_HEIGHT)

	# Control Loop
	while True:
		if SHOW_LOGS:
			start_time = time.time()
		
		camera_frame = camera.read()
		cropped_frame = center_crop_square(camera_frame)
		resized_frame = cv2.resize(cropped_frame, (FRAME_SIZE, FRAME_SIZE))
		preprocessed_frame = preprocess_image(resized_frame)
		output = model_trt(preprocessed_frame).detach().clamp(-1.0, 1.0).cpu().numpy().flatten()

		steering = float(output[0])
		car.steering = steering

		throttle = float(output[1])
		car.throttle = throttle
		
		if SHOW_LOGS:
			fps = int(1/(time.time()-start_time))
			print("fps: " + str(int(fps)) + ", steering: " + str(steering) + ", throttle: " + str(throttle), end="\r")
   
except KeyboardInterrupt:
	car.throttle = 0.0
	car.steering = 0.0
	raise SystemExit

	
