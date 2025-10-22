import re
from .grid import COLOR_MAP

_number_regex = re.compile(r'\d+')

def robust_tokenize_sequence(sequence: str):
    if not sequence:
        return []
    tokens = []
    if any(c.isspace() for c in sequence):
        for part in sequence.split():
            m = _number_regex.fullmatch(part.strip())
            if m:
                tokens.append(m.group(0))
            else:
                tokens.extend(_number_regex.findall(part))
    else:
        tokens = _number_regex.findall(sequence)
    return tokens

def decode_sequence(sequence: str, cipher: str = 'standard'):
    tokens = robust_tokenize_sequence(sequence)
    if cipher == 'standard':
        mapping = {i: chr(ord('A')+i-1) for i in range(1,27)}
        return ''.join(mapping.get(int(t),'?') if t.isdigit() else '?' for t in tokens)
    else:
        keys = list(COLOR_MAP.keys())
        mapping = {i+1: keys[i] for i in range(len(keys))}
        return ''.join(mapping.get(int(t),'?') if t.isdigit() else '?' for t in tokens)
