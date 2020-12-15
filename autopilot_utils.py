import cv2
import torch
import torchvision.transforms as transforms
import torch.nn.functional as F
import PIL.Image
import numpy as np

mean = torch.Tensor([0.485, 0.456, 0.406]).cuda()
std = torch.Tensor([0.229, 0.224, 0.225]).cuda()

def preprocess_image(image):
    image = PIL.Image.fromarray(image)
    image = transforms.functional.to_tensor(image).cuda()
    image.sub_(mean[:, None, None]).div_(std[:, None, None])
    return image[None, ...]

def center_crop_square(frame):
    src_height, src_width, _ = frame.shape
    src_aspect_ratio = src_width/src_height
    vertical_padding = 0
    horizontal_padding = 0

    if src_aspect_ratio > 1.0:
        square_size = src_height
        horizontal_padding = int((src_width-square_size)/2)
    else:
        square_size = src_width
        vertical_padding = int((src_height-square_size)/2)

    cropped = frame[vertical_padding:vertical_padding+square_size,
                    horizontal_padding:horizontal_padding+square_size]
    return cropped
