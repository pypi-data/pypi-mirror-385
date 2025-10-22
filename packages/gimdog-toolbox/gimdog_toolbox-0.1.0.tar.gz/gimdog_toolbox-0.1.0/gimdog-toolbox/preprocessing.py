"""
Created in 2025 July

@author: Aron Gimesi (https://github.com/gimesia)
@contact: gimesiaron@gmail.com
"""

import albumentations as A
import cv2
import numpy as np
import torch
import torch.nn.functional as F
import torchvision.transforms.v2 as transforms


def tensor2image(tensor: torch.Tensor) -> np.ndarray:
    if tensor.ndim == 2:
        return tensor.cpu().numpy()
    elif tensor.ndim == 3:
        return tensor.permute(1, 2, 0).cpu().numpy()
    elif tensor.ndim == 4:
        return tensor.squeeze(0).permute(1, 2, 0).cpu().numpy()
    else:
        raise ValueError("Invalid tensor shape")


def image2tensor(image: np.ndarray) -> torch.Tensor:
    if image.ndim == 2:
        return torch.from_numpy(image).unsqueeze(0)
    elif image.ndim == 3:
        return torch.from_numpy(image).permute(2, 0, 1)
    elif image.ndim == 4:
        return torch.from_numpy(image).permute(0, 3, 1, 2)
    else:
        raise ValueError("Invalid image shape")


def normalize2uint8(image: np.ndarray | torch.Tensor) -> np.ndarray | torch.Tensor:
    is_tensor = isinstance(image, torch.Tensor)
    if is_tensor:
        image = tensor2image(image)
    normalized_image = cv2.normalize(
        image,
        None,
        alpha=0,
        beta=255,
        norm_type=cv2.NORM_MINMAX,
        dtype=cv2.CV_8U,
    )
    if is_tensor:
        normalized_image = image2tensor(normalized_image)
    return normalized_image


def normalize2int8(image: np.ndarray | torch.Tensor) -> np.ndarray | torch.Tensor:
    is_tensor = isinstance(image, torch.Tensor)
    if is_tensor:
        image = tensor2image(image)
    normalized_image = cv2.normalize(
        image,
        None,
        alpha=-128,
        beta=127,
        norm_type=cv2.NORM_MINMAX,
        dtype=cv2.CV_8S,
    )
    if is_tensor:
        normalized_image = image2tensor(normalized_image)
    return normalized_image


def normalize2float32(image: np.ndarray | torch.Tensor) -> np.ndarray | torch.Tensor:
    is_tensor = isinstance(image, torch.Tensor)
    if is_tensor:
        image = tensor2image(image)
    normalized_image = cv2.normalize(
        image,
        None,
        alpha=0,
        beta=1,
        norm_type=cv2.NORM_MINMAX,
        dtype=cv2.CV_32F,
    )
    if is_tensor:
        normalized_image = image2tensor(normalized_image)
    return normalized_image


def normalize2float64(image: np.ndarray | torch.Tensor) -> np.ndarray | torch.Tensor:
    is_tensor = isinstance(image, torch.Tensor)
    if is_tensor:
        image = tensor2image(image)
    normalized_image = cv2.normalize(
        image,
        None,
        alpha=0,
        beta=1,
        norm_type=cv2.NORM_MINMAX,
        dtype=cv2.CV_64F,
    )
    if is_tensor:
        normalized_image = image2tensor(normalized_image)
    return normalized_image


def normalize2uint16(image: np.ndarray | torch.Tensor) -> np.ndarray | torch.Tensor:
    is_tensor = isinstance(image, torch.Tensor)
    if is_tensor:
        image = tensor2image(image)
    normalized_image = cv2.normalize(
        image,
        None,
        alpha=0,
        beta=65535,
        norm_type=cv2.NORM_MINMAX,
        dtype=cv2.CV_16U,
    )
    if is_tensor:
        normalized_image = image2tensor(normalized_image)
    return normalized_image


def normalize2int16(image: np.ndarray | torch.Tensor) -> np.ndarray | torch.Tensor:
    is_tensor = isinstance(image, torch.Tensor)
    if is_tensor:
        image = tensor2image(image)
    normalized_image = cv2.normalize(
        image,
        None,
        alpha=-32768,
        beta=32767,
        norm_type=cv2.NORM_MINMAX,
        dtype=cv2.CV_16S,
    )
    if is_tensor:
        normalized_image = image2tensor(normalized_image)
    return normalized_image


def rgb2gray(image: np.ndarray | torch.Tensor) -> np.ndarray | torch.Tensor:
    is_tensor = isinstance(image, torch.Tensor)
    if is_tensor:
        image = tensor2image(image)

    # Check if all channels are the same
    if image.ndim == 3 and np.all(image[:, :, 0] == image[:, :, 1]) and np.all(image[:, :, 1] == image[:, :, 2]):
        gray_image = image[:, :, 0]
    else:
        gray_image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)

    if is_tensor:
        gray_image = image2tensor(gray_image)
    return gray_image


def gray2rgb(image: np.ndarray | torch.Tensor) -> np.ndarray | torch.Tensor:
    is_tensor = isinstance(image, torch.Tensor)
    if is_tensor:
        if image.shape[0] == 1:
            image = image.squeeze(0)
        image = tensor2image(image)

    if image.ndim == 2:  # Grayscale image
        rgb_image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
    else:
        raise ValueError("Input image is not a grayscale image")

    if is_tensor:
        rgb_image = image2tensor(rgb_image)
    return rgb_image


def resize_image(image, size, binary=False):
    is_tensor = isinstance(image, torch.Tensor)
    original_dtype = image.dtype  # Store the original data type

    if not is_tensor:
        image = image2tensor(image)  # Convert to tensor if it's not already

    # Convert the tensor to float32 for interpolation
    image = image.to(dtype=torch.float32)

    image = image.unsqueeze(0)  # Add batch dimension
    resized_image = F.interpolate(image, size=size, mode="nearest" if binary else "bilinear", align_corners=False)  # Resize

    # Convert back to the original data type
    resized_image = resized_image.to(dtype=original_dtype)

    if not is_tensor:
        return tensor2image(resized_image.squeeze(0))  # Convert back to image if needed
    return resized_image.squeeze(0)


def normalize4imagenet(array: torch.tensor) -> torch.tensor:
    """
    Normalize image tensor to ImageNet intensity distribution.

    Args:
        array (torch.tensor): Input tensor.

    Returns:
        torch.tensor: Normalized tensor.

    TODO: make the usage more clear!
    """
    assert array.shape[0] == 3, f"{array.shape}"
    # ImageNet normalization
    # Array to be assumed in range [0,1]
    # assert (array.min() >= 0) and (array.max() <= 1)
    array = normalize2float32(array)

    array = (array - torch.tensor([0.485, 0.456, 0.406]).view(-1, 1, 1)) / (torch.tensor([0.229, 0.224, 0.225]).view(-1, 1, 1))
    return array


def preprocess_masks(masks: torch.Tensor | np.ndarray) -> torch.Tensor | np.ndarray:
    """
    Preprocess masks to ensure they are in the correct form.

    Args:
        masks (torch.Tensor | np.ndarray): Input mask tensor or array.

    Returns:
        torch.Tensor | np.ndarray: Preprocessed mask tensor or array.
    """
    is_tensor = isinstance(masks, torch.Tensor)
    if is_tensor:
        masks = masks.clone()  # Avoid modifying the original tensor
    else:
        masks = masks.copy()  # Avoid modifying the original array

    # Diaphragm cut
    masks[0] = masks[0] - masks[6]
    masks[0] = torch.clamp(masks[0], 0, 1) if is_tensor else np.clip(masks[0], 0, 1)

    masks[1] = masks[1] - masks[6]
    masks[1] = torch.clamp(masks[1], 0, 1) if is_tensor else np.clip(masks[1], 0, 1)

    # Heart cut
    masks[0] = masks[0] - masks[2]
    masks[0] = torch.clamp(masks[0], 0, 1) if is_tensor else np.clip(masks[0], 0, 1)

    masks[1] = masks[1] - masks[2]
    masks[1] = torch.clamp(masks[1], 0, 1) if is_tensor else np.clip(masks[1], 0, 1)

    # # Spine cut (commented out)
    # masks[0] = masks[0] - masks[8]
    # masks[0] = torch.clamp(masks[0], 0, 1) if is_tensor else np.clip(masks[0], 0, 1)

    # masks[1] = masks[1] - masks[8]
    # masks[1] = torch.clamp(masks[1], 0, 1) if is_tensor else np.clip(masks[1], 0, 1)

    # Rib occlusion cut
    for i in range(17, 10, -1):
        masks[i] = masks[i] - masks[i - 1]
        masks[i] = torch.clamp(masks[i], 0, 1) if is_tensor else np.clip(masks[i], 0, 1)

    return masks


# PYTORCH TRANSFORMS
class NormalizeToFloat:
    def __init__(self, dtype=np.float64):
        self.dtype = dtype

    def __call__(self, img):
        if self.dtype == np.float32:
            return normalize2float32(img)
        elif self.dtype == np.float64:
            return normalize2float64(img)
        else:
            raise ValueError("Invalid dtype")

    def __repr__(self):
        return self.__class__.__name__ + "()"


class NormalizeTensorToXrayRange:
    def __call__(self, img):
        img = img * 2048 - 1024  # Scale to [-1024, 1024]
        return img

    def __repr__(self):
        return self.__class__.__name__ + "()"


class GrayToRGB:
    def __call__(self, img):
        return gray2rgb(img)

    def __repr__(self):
        return self.__class__.__name__ + "()"


class GrayTo3Channel:
    def __call__(self, img):
        if isinstance(img, torch.Tensor) and img.shape[0] == 1:
            return img.repeat(3, 1, 1)
        elif isinstance(img, torch.Tensor) or isinstance(img, np.ndarray) and img.shape[2] != 1:
            return img
        elif isinstance(img, np.ndarray):
            return np.repeat(img[:, :, np.newaxis], 3, axis=2)
        else:
            raise TypeError("Input should be a torch.Tensor or a numpy.ndarray")

    def __repr__(self):
        return self.__class__.__name__ + "()"


class ResizeImage:
    def __init__(self, size, binary=False):
        self.size = size
        self.binary = binary

    def __call__(self, img):
        return resize_image(img, self.size, binary=self.binary)

    def __repr__(self):
        return self.__class__.__name__ + "()"


class Pad2Square:
    def __init__(self, fill=0):
        self.fill = fill

    def __call__(self, image):
        is_tensor = isinstance(image, torch.Tensor)

        if is_tensor:
            image = tensor2image(image)  # Convert tensor to numpy array with shape (H, W, C)

        height, width = image.shape[:2]
        if height == width:
            if is_tensor:
                return image2tensor(image)  # Convert back to tensor
            return image  # Image is already square, no need to pad

        size = max(height, width)
        delta_w = size - width
        delta_h = size - height
        top, bottom = delta_h // 2, delta_h - (delta_h // 2)
        left, right = delta_w // 2, delta_w - (delta_w // 2)

        color = [self.fill] * 3  # Assuming image has 3 channels (RGB)
        padded_image = cv2.copyMakeBorder(image, top, bottom, left, right, cv2.BORDER_CONSTANT, value=color)

        if is_tensor:
            if len(padded_image.shape) == 2:
                return torch.from_numpy(padded_image).unsqueeze(0)  # Convert back to tensor
            return torch.from_numpy(padded_image).permute(2, 0, 1)  # Convert back to tensor
        return padded_image

    def __repr__(self):
        return self.__class__.__name__ + "()"


class ImageNetNormalize:
    def __call__(self, image):
        return normalize4imagenet(image)

    def __repr__(self):
        return self.__class__.__name__ + "()"


class RandomErasingWithMinValue:
    def __init__(self, scale=(0.02, 0.06), ratio=(0.5, 0.6), p=0.2):
        self.scale = scale
        self.ratio = ratio
        self.p = p

    def __call__(self, img):
        # Compute the minimum value of the image tensor
        min_value = img.min().item()
        # Set the value for erasing to the minimum value (scalar for single-channel images)
        t = transforms.RandomErasing(scale=self.scale, ratio=self.ratio, p=self.p, value=min_value)
        return t(img)

    def __repr__(self):
        return self.__class__.__name__ + "()"

class ZScoreConditional:
    def __init__(self):
        pass

    def __call__(self, image, **kwargs):  # Accept **kwargs to avoid errors
        unique_vals = np.unique(image)
        if len(unique_vals) == 2:
            return image
        else:
            image = image.astype(np.float32)
            mean = image.mean()
            std = image.std()
            image = (image - mean) / (std + 1e-8)
            return image

    def __repr__(self):
        return self.__class__.__name__ + "()"


class Gray2RGB(A.ImageOnlyTransform):
    def apply(self, img, **params):
        if len(img.shape) != 3 or img.shape[2] != 3:  # Check if the image is grayscale
            img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
        return img


class Norm2Float(A.ImageOnlyTransform):
    def apply(self, img, **params):
        # print(f"Normalizing image to uint8 with shape: {img.shape}")
        if isinstance(img, torch.Tensor):
            img = tensor2image(img)
            img = cv2.normalize(img, None, 0, 1, cv2.NORM_MINMAX).astype(np.float32)
            return image2tensor(img).float()
        elif not isinstance(img, np.ndarray):
            raise TypeError(f"Expected image to be a numpy array or torch tensor, got {type(img)}")
        return cv2.normalize(img, None, 0, 1, cv2.NORM_MINMAX).astype(np.float32)


class Checkpoint:
    def __call__(self, image):
        print(f"Array shape after converting to tensor: {image.shape}")
        print(f"Array dtype after converting to tensor: {image.dtype}")
        print(f"Array min after converting to tensor: {image.min()}")
        print(f"Array max after converting to tensor: {image.max()}\n")

        return image

    def __repr__(self):
        return self.__class__.__name__ + "()"


xrv_transform = transforms.Compose(
    [
        NormalizeToFloat(),  # Convert from uint16 to float32 and normalize to [0, 1] for PIL and resizing
        Pad2Square(0),
        ResizeImage((512, 512)),  # Resize to 512x512 for XRV segmentation model
        transforms.ToTensor(),
        NormalizeTensorToXrayRange(),  # Normalize to [-1024, 1024] for XRV segmentation model
    ]
)

cxas_transform_Padding = transforms.Compose(
    [
        NormalizeToFloat(),
        GrayToRGB(),
        transforms.ToTensor(),
        Pad2Square(0),
        ImageNetNormalize(),
        ResizeImage((512, 512)),
    ]
)


cxas_mask_transform_Padding = transforms.Compose(
    [
        NormalizeToFloat(),
        transforms.ToTensor(),
        Pad2Square(0),
        ResizeImage((512, 512)),
    ]
)

hybridgnet_transform = transforms.Compose(
    [
        NormalizeToFloat(),
        Pad2Square(),
        ResizeImage((1024, 1024)),
        transforms.ToTensor(),
    ]
)


def process_batch_maskrcnn(targets, num_classes):
    masks, labels = targets["masks"], targets["labels"]

    msks = np.zeros((num_classes, masks.shape[-2], masks.shape[-1]), float)

    for label, mask in zip(labels, masks):
        msks[label - 1] = np.clip((mask.cpu().float().detach().numpy() > 0.5) + msks[label - 1], 0, 1, dtype=float)

    return torch.as_tensor((msks > 0.5).astype(np.uint8)) if isinstance(msks, np.ndarray) else (msks > 0.5).int()


def format_maskrcnn_targets(maskrcnn_targets, num_classes):
    if isinstance(maskrcnn_targets, dict):
        return torch.stack([process_batch_maskrcnn({k: v[i] for k, v in maskrcnn_targets.items()}, num_classes) for i in range(len(maskrcnn_targets["masks"]))])

    elif isinstance(maskrcnn_targets, list):
        return torch.stack([process_batch_maskrcnn(targets, num_classes) for targets in maskrcnn_targets])
