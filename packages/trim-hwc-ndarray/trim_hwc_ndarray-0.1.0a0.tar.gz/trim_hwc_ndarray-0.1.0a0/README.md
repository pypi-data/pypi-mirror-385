# `trim-hwc-ndarray`

A simple utility for trimming borders from images represented as HWC ndarrays, based on the color value of a specified
corner.

## Features

- **Trim uniform borders** from an HWC ndarray in which the border pixels match the color of a specified corner.
- Flexible selection of **which corner to use as the background color**.
- Preserves image channels and returns a trimmed copy.

## Installation

```bash
pip install trim-hwc-ndarray
```

## Usage

```python
# coding=utf-8
from __future__ import print_function
from trim_hwc_ndarray import trim_hwc_ndarray, Corner
import numpy as np

# Example: Trim a border from a 3x3 RGB image
img = np.array([
    [[255, 255, 255], [255, 255, 255], [255, 255, 255]],
    [[255, 255, 255], [0, 0, 0], [255, 255, 255]],
    [[255, 255, 255], [255, 255, 255], [255, 255, 255]]
])
trimmed_img = trim_hwc_ndarray(img, Corner.TOP_LEFT)
print(trimmed_img.shape)  # Output: (1, 1, 3)
```

## Contributing

Contributions are welcome! Please submit pull requests or open issues on the GitHub repository.

## License

This project is licensed under the [MIT License](LICENSE).