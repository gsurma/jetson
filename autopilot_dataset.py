import torch
import os
import glob
import PIL.Image
from PIL import ImageFilter
import torch.utils.data
import cv2
import numpy as np

from autopilot_utils import center_crop_square

class AutopilotDataset(torch.utils.data.Dataset):
    
    def __init__(self, directory, frame_size, transform=None, random_noise=False, random_blur=False, random_horizontal_flip=False):
        super(AutopilotDataset, self).__init__()
        
        self.frame_size = frame_size
        self.transform = transform
        self.random_noise = random_noise
        self.random_blur = random_blur
        self.random_horizontal_flip = random_horizontal_flip
        
        self.data = []

        with open(directory + "annotations.csv", 'r') as annotations:
            for line in annotations:
                timestamp, steering, throttle = line.split(",")
                image = directory+timestamp+'.jpg'
                if os.path.isfile(image) and os.stat(image).st_size > 0:
                    self.data.append((image, steering, throttle))
                    
            annotations.close()
        print("Generated dataset of " + str(len(self.data)) + " items")
          
    def __len__(self):
        return len(self.data)
    
    def __getitem__(self, idx):
        item = self.data[idx]
        
        image, steering, throttle = item
        image = cv2.imread(image, cv2.IMREAD_COLOR)
        image = center_crop_square(image)
        image = cv2.resize(image, (self.frame_size, self.frame_size))
        image = PIL.Image.fromarray(image)
        
        steering = float(steering)
        throttle = float(throttle)
        
        if self.random_blur and float(np.random.random(1)) > 0.5:
            image = image.filter(ImageFilter.BLUR)
            
        if self.random_noise and float(np.random.random(1)) > 0.5:
            output = np.copy(np.array(image))
    
            amount = 0.1
        
            nb_salt = np.ceil(amount * output.size * 0.5)
            coords = [np.random.randint(0, i - 1, int(nb_salt)) for i in output.shape]
            output[tuple(coords)] = 1.0

            nb_pepper = np.ceil(amount* output.size * 0.5)
            coords = [np.random.randint(0, i - 1, int(nb_pepper)) for i in output.shape]
            output[tuple(coords)] = 0.0
            
            image = PIL.Image.fromarray(output)
        
        if self.random_horizontal_flip and float(np.random.random(1)) > 0.5:
            image = image.transpose(PIL.Image.FLIP_LEFT_RIGHT)
            steering = -steering
            
        if self.transform is not None:
            image = self.transform(image)
            
        return image, torch.Tensor([steering, throttle])
