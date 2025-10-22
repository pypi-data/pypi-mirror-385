import numpy as np
from .grid import COLOR_MAP

class RNG:
    def __init__(self, seed=12345):
        self._rng = np.random.default_rng(int(seed))
        self.seed = int(seed)
    def choice(self, seq):
        return self._rng.choice(seq)

def create_mosaic(grid, num_pieces=4, rng=None):
    if rng is None:
        rng = RNG(12345)
    h,w = grid.shape[:2]
    if h % num_pieces != 0 or w % num_pieces != 0:
        return grid
    ph, pw = h//num_pieces, w//num_pieces
    out = grid.copy()
    for i in range(num_pieces):
        for j in range(num_pieces):
            y0,y1 = i*ph, (i+1)*ph
            x0,x1 = j*pw, (j+1)*pw
            piece = grid[y0:y1, x0:x1].copy()
            angle = rng.choice([0,90,180,270])
            if angle != 0:
                k = angle // 90
                piece = np.rot90(piece, k=k)
                ph2, pw2 = piece.shape[:2]
                if ph2==ph and pw2==pw:
                    out[y0:y1, x0:x1] = piece
                else:
                    ph_min = min(ph, ph2)
                    pw_min = min(pw, pw2)
                    out[y0:y0+ph_min, x0:x0+pw_min] = piece[0:ph_min,0:pw_min]
            else:
                out[y0:y1, x0:x1] = piece
    return out
