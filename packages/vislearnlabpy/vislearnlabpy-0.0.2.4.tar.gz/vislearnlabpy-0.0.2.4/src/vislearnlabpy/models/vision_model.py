import itertools
from vislearnlabpy.models.feature_generator import FeatureGenerator
from vislearnlabpy.embeddings import utils
from torchvision import transforms
import torch

class VisionModel(FeatureGenerator):
    """Abstract base class for multimodal models like CLIP and CVCL that extends FeatureGenerator"""
    
    def __init__(self, model, preprocess, dataloader=None, device=None):
        super().__init__(model, preprocess, dataloader, device)
        self.image_word_alignment = lambda **x: self.model(**x).logits_per_image.softmax(dim=-1).detach().cpu().numpy()

    # Load and preprocess images
    def preprocess_image(self, image):
        if isinstance(image, torch.Tensor):  
            transform = transforms.ToPILImage()
            image = transform(image)
        return self.preprocess(image).unsqueeze(0).to(self.device)

    def encode_image(self, image):
        return self.model.encode_image(image)

    def image_embeddings(self, images, normalize_embeddings=False):
        """Get image embeddings (batched for speed)"""
        # Handle single image case
        if not isinstance(images, list):
            return self.image_embeddings([images], normalize_embeddings)[0]
        # Preprocess all images → batch
        preprocessed_images = [self.preprocess_image(image) for image in images]
        preprocessed_images = [image.squeeze(0) if image.dim() == 4 else image for image in preprocessed_images]
        # Stack into a single tensor batch (assuming tensors are returned)
        image_batch = torch.stack(preprocessed_images).to(self.device)
        with torch.no_grad():
            embeddings = self.encode_image(image_batch)  # model handles batch
        if normalize_embeddings:
            embeddings = utils.normalize_embeddings(embeddings)
        return embeddings
        
    # TODO: probably move this to the dataloader row level instead of to a pair of words within a dataloader row
    # TODO: words or texts? what is my parameter
    def embeddings(self, word1, word2, dataloader_row):
        valid_images = [img for img in dataloader_row['images'] if img is not None]
        output_embeddings = []
        for image1, image2 in itertools.combinations(valid_images, 2):
            curr_image_embeddings = self.image_embeddings([image1, image2])
            curr_text_embeddings = self.text_embeddings([word1, word2])
            output_embeddings.append({
                'image_embeddings': curr_image_embeddings,
                'text_embeddings': curr_text_embeddings,
                'multimodal_embeddings': self.multimodal_embeddings(curr_image_embeddings, curr_text_embeddings)
            })
        return output_embeddings
    
