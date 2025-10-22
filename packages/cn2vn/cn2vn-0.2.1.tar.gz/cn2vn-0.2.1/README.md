# Cn2vn

A Python library to convert Chinese text to Vietnamese using Sino-Vietnamese readings.

## Installation

```bash
pip install cn2vn
```

## Usage

```python
from cn2vn import cn2vn

chinese_text = "王小明"
vietnamese = cn2vn(chinese_text)
print(vietnamese)  # Output: Vương Tiểu Minh (example)
```

## Features

- Converts Chinese characters to their Vietnamese equivalents based on Sino-Vietnamese pronunciation.
- Handles unknown characters by leaving them unchanged.

## Requirements

- Python 3.6+

## License

MIT