import numpy as np

COLOR_MAP = {
    'A': (255,0,0), 'B': (0,0,255), 'C': (255,165,0), 'Ch': (0,0,0), 'Ck': (0,255,0),
    'D': (255,255,0), 'E': (0,128,128), 'F': (128,128,128), 'G': (128,0,128),
    'H': (0,255,255), 'I': (46,139,87), 'J': (173,216,230), 'K': (0,100,0),
    'L': (255,255,255), 'LL': (255,215,0), 'M': (0,0,0), 'N': (220,20,60),
    'O': (165,42,42), 'P': (0,0,128), 'Ph': (75,83,32), 'Q': (255,182,193),
    'R': (255,255,255), 'S': (192,192,192), 'T': (255,165,0), 'Th': (255,165,0),
    'U': (200,162,200), 'V': (143,0,255), 'W': (70,130,180), 'Wh': (160,82,45),
    'X': (65,105,225), 'Y': (154,205,50), 'Z': (255,69,0)
}

def initialize_grid(size, seed=12345, white=True):
    import numpy as _np
    _np.random.seed(int(seed))
    if white:
        return _np.ones((size,size,3), dtype=_np.uint8)*255
    return _np.zeros((size,size,3), dtype=_np.uint8)

def draw_m(grid, x, y, scale=1):
    m_coords = [(0,0),(0,1),(0,2),(1,2),(1,1),(2,0),(3,1),(4,2),(4,1),(4,0)]
    h,w = grid.shape[:2]
    for dx,dy in m_coords:
        cx,cy = x+dx*scale, y+dy*scale
        if 0<=cx<h and 0<=cy<w:
            grid[cx,cy] = COLOR_MAP.get('M',(0,0,0))
    return grid

def draw_y(grid, x, y):
    y_coords = [(2,0),(2,1),(2,2),(3,2),(4,3),(3,3)]
    h,w = grid.shape[:2]
    for dx,dy in y_coords:
        cx,cy = x+dx, y+dy
        if 0<=cx<h and 0<=cy<w:
            grid[cx,cy] = COLOR_MAP.get('Y',(154,205,50))
    return grid

def transition_to_black(grid):
    h,w = grid.shape[:2]
    mcol = COLOR_MAP.get('M',(0,0,0))
    import numpy as _np
    for i in range(h):
        for j in range(w):
            if not _np.array_equal(grid[i,j], mcol):
                grid[i,j] = (0,0,0)
    for i in range(1,h):
        grid[i,:,1] = 255
    return grid

def combustion_invert(grid):
    import numpy as _np
    return (255 - grid).astype(_np.uint8)
