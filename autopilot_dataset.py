import torch
import torchvision
import os
import glob
import PIL.Image
from PIL import ImageFilter
import torch.utils.data
import cv2
import numpy as np

from autopilot_utils import center_crop_square

class AutopilotDataset(torch.utils.data.Dataset):
    
    def __init__(self, directory,
                 frame_size, 
                 transform=None,
                 random_noise=False,
                 random_blur=False,
                 random_horizontal_flip=False,
                 random_color_jitter=False,
                 keep_images_in_ram=False): # requires lots of RAM but significantly speeds up IO, otherwise stores image paths
        super(AutopilotDataset, self).__init__()
        
        self.frame_size = frame_size
        self.transform = transform
        self.random_noise = random_noise
        self.random_blur = random_blur
        self.random_horizontal_flip = random_horizontal_flip
        self.random_color_jitter = random_color_jitter
        self.keep_images_in_ram = keep_images_in_ram
        
        self.data = []

        with open(directory + "annotations.csv", 'r') as annotations:
            for line in annotations:
                name, steering, throttle = line.split(",")
                image = directory+name+'.jpg'
                if os.path.isfile(image) and os.stat(image).st_size > 0:
                    if self.keep_images_in_ram:
                        image = self.load_and_prepare_image_from_path(image)
                    self.data.append((name, image, steering, throttle))
                    
            annotations.close()
        print("Generated dataset of " + str(len(self.data)) + " items")
          
    def __len__(self):
        return len(self.data)
    
    def __getitem__(self, idx):
        item = self.data[idx]
        
        name, image, steering, throttle = item
        if not self.keep_images_in_ram:
            image = self.load_and_prepare_image_from_path(image)
        
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
            
        transforms = []
        if self.random_color_jitter:
            transforms = [torchvision.transforms.ColorJitter(brightness=0.25, contrast=0.25, hue=0.25, saturation=0.25)]
            
        transforms += [
            torchvision.transforms.ToTensor(),
            torchvision.transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])]
                                             
        composed_transforms = torchvision.transforms.Compose(transforms)
        image = composed_transforms(image)
        
        return name, image, torch.Tensor([steering, throttle])

    def load_and_prepare_image_from_path(self, path):
        image = cv2.imread(path, cv2.IMREAD_COLOR)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = center_crop_square(image)
        image = cv2.resize(image, (self.frame_size, self.frame_size))
        image = PIL.Image.fromarray(image)
        return image