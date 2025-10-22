import os
import json

# Load the dictionary at import time for better performance
_dict = None

def _load_dict():
    global _dict
    if _dict is None:
        dict_path = os.path.join(os.path.dirname(__file__), 'dictionary.json')
        with open(dict_path, 'r', encoding='utf-8') as f:
            _dict = json.load(f)
    return _dict

# Load dictionary immediately
_DICT = _load_dict()

def cn2vn(text):
    """
    Convert Chinese text to Vietnamese using Sino-Vietnamese readings.
    
    Args:
        text (str): Chinese text to convert
        
    Returns:
        str: Vietnamese text with each character converted
    """
    result = []
    for char in text:
        if char in _DICT:
            result.append(_DICT[char])
        else:
            result.append(char)
    return ' '.join(result)