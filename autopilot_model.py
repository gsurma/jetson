import torch
import torchvision
from efficientnet_pytorch import EfficientNet
from torch2trt import TRTModule
from torch2trt import torch2trt

OUTPUT_SIZE = 2
DROPOUT_PROB = 0.5

class AutopilotModel(torch.nn.Module):
    
    def __init__(self, pretrained):
        super(AutopilotModel, self).__init__()

        self.network = torchvision.models.resnet18(pretrained=pretrained)
        self.network.fc = torch.nn.Sequential(
            torch.nn.Dropout(p=DROPOUT_PROB),
            torch.nn.Linear(in_features=self.network.fc.in_features, out_features=1024),
            torch.nn.Dropout(p=DROPOUT_PROB),
            torch.nn.Linear(in_features=1024, out_features=512),
            torch.nn.Dropout(p=DROPOUT_PROB),
            torch.nn.Linear(in_features=512, out_features=256),
            torch.nn.Dropout(p=DROPOUT_PROB),
            torch.nn.Linear(in_features=256, out_features=128),
            torch.nn.Dropout(p=DROPOUT_PROB),
            torch.nn.Linear(in_features=128, out_features=64),
            torch.nn.Dropout(p=DROPOUT_PROB),
            torch.nn.Linear(in_features=64, out_features=OUTPUT_SIZE)
        )
        self.network.cuda()

    def forward(self, x):
        y = self.network(x)
        return y
    
    def save_to_path(self, path):
        torch.save(self.state_dict(), path)
        
    def load_from_path(self, path):
        self.load_state_dict(torch.load(path))
        
