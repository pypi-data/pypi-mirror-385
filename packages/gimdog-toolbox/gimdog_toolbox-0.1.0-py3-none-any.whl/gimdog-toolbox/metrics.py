"""
Created in 2025 July

@author: Aron Gimesi (https://github.com/gimesia)
@contact: gimesiaron@gmail.com
"""

import numpy as np
import pandas as pd
import torch
from scipy.spatial.distance import directed_hausdorff


def dice_score(mask1, mask2):
    """
    Calculate the Dice score between two binary masks.

    Parameters:
    mask1 (np.array or torch.Tensor): First binary mask.
    mask2 (np.array or torch.Tensor): Second binary mask.

    Returns:
    float: Dice score between the two masks.
    """
    if isinstance(mask1, np.ndarray) and isinstance(mask2, np.ndarray):
        intersection = np.sum(mask1 * mask2)
        total = np.sum(mask1) + np.sum(mask2)
    elif isinstance(mask1, torch.Tensor) and isinstance(mask2, torch.Tensor):
        intersection = torch.sum(mask1 * mask2).item()
        total = torch.sum(mask1).item() + torch.sum(mask2).item()
    else:
        raise TypeError("Both masks must be of the same type (np.array or torch.Tensor).")

    return (2.0 * intersection) / total if total > 0 else 0.0


def iou_score(mask1, mask2):
    """
    Calculate the Intersection over Union (IoU) score between two binary masks.

    Parameters:
    mask1 (np.array or torch.Tensor): First binary mask.
    mask2 (np.array or torch.Tensor): Second binary mask.

    Returns:
    float: IoU score between the two masks.
    """
    if isinstance(mask1, np.ndarray) and isinstance(mask2, np.ndarray):
        intersection = np.sum(mask1 * mask2)
        union = np.sum(mask1) + np.sum(mask2) - intersection
    elif isinstance(mask1, torch.Tensor) and isinstance(mask2, torch.Tensor):
        intersection = torch.sum(mask1 * mask2).item()
        union = torch.sum(mask1).item() + torch.sum(mask2).item() - intersection
    else:
        raise TypeError("Both masks must be of the same type (np.array or torch.Tensor).")

    return intersection / union if union > 0 else 0.0


def compare_masks(masks, metric_fn, model_names=None):
    """
    Compare all masks with each other and calculate Dice scores.

    Parameters:
    masks (list of np.array): List of binary masks (0 or 1) from different models.
    model_names (list of str): List of model names corresponding to the masks.

    Returns:
    pd.DataFrame: DataFrame with mask indices as rows and columns, and Dice scores as values.
    """
    num_masks = len(masks)
    dice_scores = np.zeros((num_masks, num_masks))

    for i in range(num_masks):
        for j in range(num_masks):
            if i != j:
                dice_scores[i, j] = metric_fn(masks[i], masks[j])

    if model_names is None:
        model_names = [f"Mask_{i}" for i in range(num_masks)]

    df = pd.DataFrame(dice_scores, columns=model_names, index=model_names)
    return df


def hausdorff_distance(mask1, mask2):
    """Compute the symmetric Hausdorff distance between two binary masks."""
    # Get coordinates of foreground (nonzero) pixels
    coords1 = np.column_stack(np.nonzero(mask1))
    coords2 = np.column_stack(np.nonzero(mask2))

    if coords1.size == 0 or coords2.size == 0:
        # If either mask is empty, define HD as np.inf
        return np.inf

    # Compute directed HD in both directions
    hd_forward = directed_hausdorff(coords1, coords2)[0]
    hd_backward = directed_hausdorff(coords2, coords1)[0]
    return max(hd_forward, hd_backward)


def hausdorff_distance_batch(pred_masks, gt_masks):
    """
    Compute the Hausdorff Distance for a batch of masks.

    Args:
        pred_masks (np.ndarray): Predicted masks of shape (nMasks, H, W)
        gt_masks (np.ndarray): Ground truth masks of shape (nMasks, H, W)

    Returns:
        hd_per_mask (np.ndarray): Array of Hausdorff distances per mask
        hd_average (float): Average Hausdorff distance over all masks
    """
    assert pred_masks.shape == gt_masks.shape, "Shape mismatch between prediction and ground truth masks."

    n_masks = pred_masks.shape[0]
    hd_per_mask = np.zeros(n_masks)

    for i in range(n_masks):
        hd_per_mask[i] = hausdorff_distance(pred_masks[i], gt_masks[i])

    hd_average = np.mean(hd_per_mask[np.isfinite(hd_per_mask)])  # Ignore infinite values in average
    return hd_per_mask, hd_average
