import os
import json

# Load the dictionary
_dict = None

def _load_dict():
    global _dict
    if _dict is None:
        dict_path = os.path.join(os.path.dirname(__file__), 'dictionary.json')
        with open(dict_path, 'r', encoding='utf-8') as f:
            _dict = json.load(f)
    return _dict

def cn2vn(text):
    """
    Convert Chinese text to Vietnamese using Sino-Vietnamese readings.
    
    Args:
        text (str): Chinese text to convert
        
    Returns:
        str: Vietnamese text with each character converted
    """
    d = _load_dict()
    result = []
    for char in text:
        if char in d:
            result.append(d[char])
        else:
            result.append(char)
    return ' '.join(result)