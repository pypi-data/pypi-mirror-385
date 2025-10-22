import unittest

import numpy as np
import torch

from gimdog_toolbox.preprocessing import (
    image2tensor,
    normalize2float,
    normalize2int8,
    normalize2int16,
    normalize2uint8,
    normalize2uint16,
    tensor2image,
)


class TestPreprocessing(unittest.TestCase):

    def setUp(self):
        self.tensor_2d = torch.tensor([[1, 2], [3, 4]], dtype=torch.float32)
        self.tensor_3d = torch.rand((3, 64, 64), dtype=torch.float32)
        self.tensor_4d = torch.rand((1, 3, 64, 64), dtype=torch.float32)
        self.image_2d = np.array([[1, 2], [3, 4]], dtype=np.float32)
        self.image_3d = np.random.rand(64, 64, 3).astype(np.float32)
        self.image_4d = np.random.rand(1, 64, 64, 3).astype(np.float32)

    def test_tensor2image(self):
        self.assertEqual(tensor2image(self.tensor_2d).shape, (2, 2))
        self.assertEqual(tensor2image(self.tensor_3d).shape, (64, 64, 3))
        self.assertEqual(tensor2image(self.tensor_4d).shape, (64, 64, 3))

    def test_image2tensor(self):
        self.assertEqual(image2tensor(self.image_2d).shape, (1, 2, 2))
        self.assertEqual(image2tensor(self.image_3d).shape, (3, 64, 64))
        self.assertEqual(image2tensor(self.image_4d).shape, (1, 3, 64, 64))

    def test_normalize2uint8(self):
        normalized_image = normalize2uint8(self.image_2d)
        self.assertEqual(normalized_image.dtype, np.uint8)
        self.assertTrue(
            (normalized_image >= 0).all() and (normalized_image <= 255).all()
        )

    def test_normalize2int8(self):
        normalized_image = normalize2int8(self.image_2d)
        self.assertEqual(normalized_image.dtype, np.int8)
        self.assertTrue(
            (normalized_image >= -128).all() and (normalized_image <= 127).all()
        )

    def test_normalize2float(self):
        normalized_image = normalize2float(self.image_2d)
        self.assertEqual(normalized_image.dtype, np.float32)
        self.assertTrue((normalized_image >= 0).all() and (normalized_image <= 1).all())

    def test_normalize2uint16(self):
        normalized_image = normalize2uint16(self.image_2d)
        self.assertEqual(normalized_image.dtype, np.uint16)
        self.assertTrue(
            (normalized_image >= 0).all() and (normalized_image <= 65535).all()
        )

    def test_normalize2int16(self):
        normalized_image = normalize2int16(self.image_2d)
        self.assertEqual(normalized_image.dtype, np.int16)
        self.assertTrue(
            (normalized_image >= -32768).all() and (normalized_image <= 32767).all()
        )


if __name__ == "__main__":
    unittest.main()
