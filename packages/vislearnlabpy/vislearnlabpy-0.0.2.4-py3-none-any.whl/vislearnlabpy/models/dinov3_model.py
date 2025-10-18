from transformers import pipeline
from vislearnlabpy.models.vision_model import VisionModel
from transformers import AutoImageProcessor, AutoModel
import torch

class DinoV3Generator(VisionModel):
    def __init__(self, dataloader=None, device=None, text_prompt="a photo of a "):
        self.pipe = pipeline(
            task="image-feature-extraction",
            model="facebook/dinov3-vits16-pretrain-lvd1689m",
            dtype=torch.bfloat16,
        )
        self.model, self.preprocess = self.pipe.model, self.pipe.feature_extractor
        super().__init__(self.model, self.preprocess, dataloader, device)
        self.name = "dinov3"

    def image_embeddings(self):
        # 
        return 
    