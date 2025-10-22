import copy

import cv2
import numpy as np
import skimage
import torch
from matplotlib import pyplot as plt
from matplotlib.colors import to_hex, to_rgb

from .preprocessing import normalize2uint8, tensor2image, gray2rgb


hex_to_rgb = lambda hex_code: tuple(int(hex_code[i : i + 2], 16) for i in (1, 3, 5))
grad_colors = lambda n: [tuple(normalize2uint8(plt.cm.rainbow(i / 17)[:3]).ravel()) for i in range(n)]


def generate_gradient(base_color_hex, num_colors):
    """
    Generates a list of hex color codes forming a gradient based on a base color.
    The gradient is created by adjusting the brightness of the base color, producing
    a symmetrical gradient with the base color at the center.
    Parameters
    ----------
    base_color_hex : str
        Hex code of the base color (e.g., '#FF5733').
    num_colors : int
        Number of colors to generate in the gradient.
    Returns
    -------
    list of str
        List of hex color codes representing the gradient.
    Notes
    -----
    Requires `numpy` and `matplotlib.colors` (`to_rgb`, `to_hex`) for color conversions.
    """
    base_rgb = np.array(to_rgb(base_color_hex))
    gradient = []

    for i in range(num_colors):
        if i < num_colors // 2:
            factor = 1 + (num_colors // 2 - i) / (num_colors // 2)
        elif i > num_colors // 2:
            factor = 1 - (i - num_colors // 2) / (num_colors // 2)
        else:
            factor = 1  # Middle color remains the same

        gradient_color = np.clip(base_rgb * factor, 0, 1)
        gradient.append(to_hex(gradient_color))

    return gradient


def show_image(image, title=None, cmap=None, figsize=None):
    """
    Display a single image using matplotlib.

    Parameters
    ----------
    image : ndarray
        Image to display.
    title : str, optional
        Title for the image. Default is None.
    cmap : str, optional
        Colormap to use for displaying the image. Default is None, which uses the default colormap.
    """
    # Create a deep copy of the image to avoid modifying the original
    image_copy = copy.deepcopy(image)

    # Convert torch.Tensor to numpy array if necessary
    if isinstance(image_copy, torch.Tensor):
        image_copy = tensor2image(image_copy)

    # Ensure the image is in uint8 format
    if image_copy.dtype != np.uint8:
        image_copy = normalize2uint8(image_copy)

    # Display the image using matplotlib
    plt.figure()
    plt.imshow(image_copy, cmap=cmap)
    plt.title(title)
    if figsize is not None:
        plt.figure(figsize=figsize)
    plt.tight_layout()
    plt.axis("off")
    plt.show()


def show_images(images, num_cols=4, titles=None, cmap=None, figsize=None):
    """
    Display a list of images in a grid format using matplotlib.

    Parameters
    ----------
    images : list of ndarray
        List of images to display.
    num_cols : int, optional
        Number of columns in the grid. Default is 4.
    titles : list of str, optional
        List of titles for each image. Default is None.
    cmap : str, optional
        Colormap to use for displaying the images. Default is None.
    """
    # Create a deep copy of the images to avoid modifying the originals
    images_copy = copy.deepcopy(images)
    num_images = max(len(images_copy), num_cols)
    num_rows = (num_images + num_cols - 1) // num_cols

    # Create a grid of subplots
    fig, axes = plt.subplots(num_rows, num_cols, figsize=(15, num_rows * 3))
    axes = axes.flatten()

    for i in range(num_images):
        try:
            image = images_copy[i]

            # Convert torch.Tensor to numpy array if necessary
            if isinstance(image, torch.Tensor):
                image = tensor2image(image)

            # Ensure the image is in uint8 format
            if image.dtype != np.uint8:
                image = normalize2uint8(image)

            # Display the image in the subplot
            axes[i].imshow(image, cmap=cmap)

            # Set the title if provided
            if titles is not None and i < len(titles):
                axes[i].set_title(titles[i])

            axes[i].axis("off")
        except Exception as e:
            print(f"Error displaying image {i}: {e}")

    # Turn off any unused subplots
    for i in range(num_images, len(axes)):
        axes[i].axis("off")

    if figsize is not None:
        plt.figure(figsize=figsize)
    plt.tight_layout()
    plt.show()


def show_images_with_row_titles(images, num_cols, row_titles, col_titles=None, titles=None, cmap=None, figsize=None):
    """
    Displays a grid of images with row and column titles using matplotlib.
    The grid includes an extra row for column titles and an extra column for row titles.
    Each image can optionally have its own title. Images can be numpy arrays or torch.Tensors.
    Args:
        images (list): List of images to display. Each image should be a numpy array or torch.Tensor.
        num_cols (int): Number of columns in the grid (excluding the extra column for row titles).
        row_titles (list): List of titles for each row.
        col_titles (list, optional): List of titles for each column. Defaults to None.
        titles (list, optional): List of titles for each image. Defaults to None.
        cmap (str or matplotlib.colors.Colormap, optional): Colormap to use for displaying images. Defaults to None.
        figsize (tuple, optional): Size of the figure (width, height). Defaults to None.
    Notes:
        - Images are deep-copied to avoid modifying the originals.
        - torch.Tensor images are converted to numpy arrays.
        - Images are normalized to uint8 if necessary.
        - Empty cells in the grid are left blank.
        - Any errors during image display are printed to the console.
    Raises:
        Exception: If an error occurs while displaying an image.
    """
    # Create a deep copy of the images to avoid modifying the originals
    images_copy = copy.deepcopy(images)
    num_images = max(len(images_copy), num_cols)
    num_rows = (num_images + num_cols - 1) // num_cols

    # Create a grid of subplots, add an extra row for column titles and an extra column for row titles
    fig, axes = plt.subplots(num_rows + 1, num_cols + 1, figsize=(15, (num_rows + 1) * 3) if figsize is None else figsize)
    axes = axes.reshape(num_rows + 1, num_cols + 1)

    # Set column titles
    for col in range(num_cols):
        if col_titles is not None and col < len(col_titles):
            axes[0, col + 1].text(0.5, 0.5, col_titles[col], fontsize=12, ha="center", va="center")
        axes[0, col + 1].axis("off")
    axes[0, 0].axis("off")  # Top-left corner

    # Fill in images and row titles
    for row in range(num_rows):
        # Add row title if provided
        if row_titles is not None and row < len(row_titles):
            axes[row + 1, 0].text(0.5, 0.5, row_titles[row], fontsize=12, ha="center", va="center")
            axes[row + 1, 0].axis("off")
        else:
            axes[row + 1, 0].axis("off")

        for col in range(num_cols):
            idx = row * num_cols + col
            if idx < len(images_copy):
                try:
                    image = images_copy[idx]

                    # Convert torch.Tensor to numpy array if necessary
                    if isinstance(image, torch.Tensor):
                        image = tensor2image(image)

                    # Ensure the image is in uint8 format
                    if image.dtype != np.uint8:
                        image = normalize2uint8(image)

                    # Display the image in the subplot
                    axes[row + 1, col + 1].imshow(image, cmap=cmap)

                    # Set the title if provided
                    if titles is not None and idx < len(titles):
                        axes[row + 1, col + 1].set_title(titles[idx])

                    axes[row + 1, col + 1].axis("off")
                except Exception as e:
                    print(f"Error displaying image {idx}: {e}")
            else:
                axes[row + 1, col + 1].axis("off")

    plt.tight_layout()
    plt.show()


def show_images_with_reference(images, single_image=None, num_cols=4, titles=None, figsize=None):
    """
    Display a grid of images with an optional reference image in each row.

    Parameters
    ----------
    images : list of ndarray
        List of images to display.
    single_image : ndarray, optional
        A single reference image to display in the first column of each row. Defaults to None.
    num_cols : int, optional
        Number of columns of images to display (excluding the reference image column). Defaults to 4.
    titles : list of str, optional
        List of titles for each image. Defaults to None.
    """
    # Create deep copies of the images to avoid modifying the originals
    images_copy = copy.deepcopy(images)
    single_image_copy = copy.deepcopy(single_image) if single_image is not None else None

    num_images = len(images_copy)
    num_rows = (num_images + num_cols - 1) // num_cols

    # Create a grid of subplots with an extra column for the reference image
    fig, axes = plt.subplots(num_rows, num_cols + 1, figsize=(15 + 5, num_rows * 3))
    axes = axes.flatten()

    for row in range(num_rows):
        if single_image_copy is not None:
            # Convert torch.Tensor to numpy array if necessary
            if isinstance(single_image_copy, torch.Tensor):
                single_image_copy = tensor2image(single_image_copy)

            # Ensure the image is in uint8 format
            if single_image_copy.dtype != np.uint8:
                single_image_copy = normalize2uint8(single_image_copy)

            # Display the reference image in the first column of the row
            axes[row * (num_cols + 1)].imshow(single_image_copy)
            axes[row * (num_cols + 1)].set_title("Ref Image")
            axes[row * (num_cols + 1)].axis("off")
        else:
            axes[row * (num_cols + 1)].axis("off")

        for col in range(num_cols):
            idx = row * num_cols + col
            if idx < num_images:
                image = images_copy[idx]

                # Convert torch.Tensor to numpy array if necessary
                if isinstance(image, torch.Tensor):
                    image = tensor2image(image)

                # Ensure the image is in uint8 format
                if image.dtype != np.uint8:
                    image = normalize2uint8(image)

                # Display the image in the subplot
                axes[row * (num_cols + 1) + col + 1].imshow(image)

                # Set the title if provided
                if titles is not None and idx < len(titles):
                    axes[row * (num_cols + 1) + col + 1].set_title(titles[idx])

                axes[row * (num_cols + 1) + col + 1].axis("off")
            else:
                axes[row * (num_cols + 1) + col + 1].axis("off")

    if figsize is not None:
        plt.figure(figsize=figsize)
    plt.tight_layout()
    plt.show()


def draw_mask_outlines(image, mask, color=(0, 255, 0), thickness=2):
    """
    Draws the outlines of a mask on an image.
    Parameters:
    image (numpy.ndarray or torch.Tensor): The input image on which to draw the mask outlines.
                                            If a torch.Tensor is provided, it will be converted to a numpy array.
    mask (numpy.ndarray or torch.Tensor): The binary mask indicating the regions to outline.
                                            If a torch.Tensor is provided, it will be converted to a numpy array.
    color (tuple): A tuple representing the RGB color of the mask outlines. Default is green (0, 255, 0).
    Returns:
    numpy.ndarray: The image with the mask outlines drawn on it.
    """
    # Convert torch.Tensor to numpy array if necessary
    if isinstance(image, torch.Tensor):
        outlined_image = tensor2image(image)
    else:
        outlined_image = image.copy()

    # Ensure the image is in uint8 format for matplotlib
    if outlined_image.dtype != np.uint8:
        outlined_image = normalize2uint8(outlined_image)

    # Ensure the outlined image is 3-channel
    if outlined_image.ndim == 2:
        outlined_image = skimage.color.gray2rgb(outlined_image)

    # Convert torch.Tensor to numpy array if necessary
    if isinstance(mask, torch.Tensor):
        mask_copy = tensor2image(mask)
    else:
        if mask.ndim == 3 and mask.shape[0] == 1:
            mask_copy = mask[0].copy()
        else:
            mask_copy = mask.copy()

    # Ensure the mask copy is not of boolean type
    if mask_copy.dtype == bool:
        mask_copy = mask_copy.astype(np.uint8)

    # Find contours of the mask
    contours, _ = cv2.findContours(normalize2uint8(mask_copy), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Convert color to integers if necessary
    color = tuple(int(c) for c in color)

    cv2.drawContours(outlined_image, contours, -1, color, thickness)

    return outlined_image


def draw_multiple_masks(image, masks, colors=None, thickness=2):
    """
    Draw multiple masks on an image.

    Parameters
    ----------
    image : ndarray
        The image on which to draw the masks.
    masks : list of ndarray
        A list of binary masks to draw on the image.
    colors : list of tuple
        A list of colors corresponding to each mask.
    thickness : int, optional
        Thickness of the mask outlines. Default is 3.

    Returns
    -------
    ndarray
        The image with the masks drawn on it.
    """
    # Convert torch.Tensor to numpy array if necessary
    if isinstance(image, torch.Tensor):
        outlined_image = tensor2image(image)
    else:
        outlined_image = image.copy()

    # Ensure the outlined image is 3-channel
    if image.ndim == 2 or image.shape[0] == 1:
        outlined_image = gray2rgb(outlined_image.squeeze())

    # Ensure the colors are provided
    if colors is None:
        colors = grad_colors(min(masks.shape))

    # Ensure the image is in uint8 format for matplotlib
    if outlined_image.dtype != np.uint8:
        outlined_image = normalize2uint8(outlined_image)

    # Draw each mask on the image
    for i, mask in enumerate(masks):
        outlined_image = draw_mask_outlines(outlined_image, mask, colors[i], thickness)

    return outlined_image


def show_image_with_mask_outlines(image, masks, mask_colors=organ_colors, thickness=2, figsize=None):
    """
    Draw mask outlines on an image.

    Parameters
    ----------
    image : ndarray
        The image on which to draw the mask outlines.
    masks : ndarray
        A 3D array where each slice along the third axis is a binary mask.
    mask_colors : list
        A list of colors corresponding to each mask.
    """

    # Convert torch.Tensor to numpy array if necessary
    if isinstance(image, torch.Tensor):
        outlined_image = tensor2image(image)
    else:
        outlined_image = image.copy()

    # Ensure the colors are provided
    if mask_colors is None:
        mask_colors = grad_colors(masks.shape[2])

    # Ensure the image is in uint8 format for matplotlib
    if outlined_image.dtype != np.uint8:
        outlined_image = normalize2uint8(outlined_image)

    # Draw the mask outlines on the image
    for i, mask in enumerate(masks):
        outlined_image = draw_mask_outlines(outlined_image, mask, mask_colors[i], thickness)

    # Display the image with mask outlines
    plt.imshow(outlined_image)
    plt.axis("off")
    if figsize is not None:
        plt.figure(figsize=figsize)
    plt.tight_layout()
    plt.show()


def compare_predicted2gt(input_img: np.ndarray, predicted_masks: np.ndarray, gt_masks: torch.Tensor, name: str, predicted_colors: list, gt_colors: list):
    gt_image = input_img.copy()
    predicted_image = input_img.copy()
    for k in range(gt_masks.shape[2]):
        gt_image = draw_mask_outlines(gt_image, gt_masks[:, :, k], gt_colors[k])
    for k in range(predicted_masks.shape[0]):
        predicted_image = draw_mask_outlines(predicted_image, predicted_masks[k], predicted_colors[k])

    show_images([predicted_image, gt_image], 2, [name, "ground-truth"])
