import torch
import torchvision

OUTPUT_SIZE = 2

class AutopilotModel(torch.nn.Module):
    
    def __init__(self, pretrained):
        super(AutopilotModel, self).__init__()
        
        self.network = torchvision.models.resnet18(pretrained=pretrained)
        self.network.fc = torch.nn.Linear(512, OUTPUT_SIZE)
        self.network.cuda()

    def forward(self, x):
        x = self.network(x)
        return x
    
    def save_to_path(self, path):
        torch.save(self.state_dict(), path)
        
    def load_from_path(self, path):
        self.load_state_dict(torch.load(path))
        
