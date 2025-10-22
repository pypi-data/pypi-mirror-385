from .grid import initialize_grid, draw_m, draw_y, transition_to_black, combustion_invert
from .mosaic import create_mosaic, RNG
from .export import export_png, export_json, make_html_preview
from .decode import decode_sequence
import os

def run_pipeline(text='ELVEIRDOR', grid_size=10, seed=12345,
                 export_png_path='output.png', export_json_path='metadata.json', export_html_path='preview.html',
                 sequence=None):
    rng = RNG(seed)
    metadata = {'text': text, 'grid_size': grid_size, 'seed': int(seed), 'steps': []}
    if sequence:
        metadata['sequence_raw'] = sequence
        metadata['decoded_standard'] = decode_sequence(sequence,'standard')
        metadata['decoded_elveirdor'] = decode_sequence(sequence,'elveirdor')
    grid = initialize_grid(grid_size, seed=seed, white=True)
    metadata['steps'].append('initialized')
    try:
        grid = draw_m(grid, max(0, min(grid_size-1, grid_size//4)), max(0, min(grid_size-1, grid_size//4)), scale=max(1, grid_size//24 or 1))
        metadata['steps'].append('draw_m')
    except Exception as e:
        metadata['draw_m_error'] = str(e)
    try:
        grid = transition_to_black(grid)
        metadata['steps'].append('transition_to_black')
    except Exception as e:
        metadata['transition_error'] = str(e)
    try:
        pieces = 4 if grid_size>=8 else 2
        grid = create_mosaic(grid, num_pieces=pieces, rng=rng)
        metadata['steps'].append('create_mosaic')
    except Exception as e:
        metadata['mosaic_error'] = str(e)
    try:
        grid = draw_y(grid, grid_size//2, grid_size//2)
        metadata['steps'].append('draw_y')
    except Exception as e:
        metadata['draw_y_error'] = str(e)
    try:
        grid = combustion_invert(grid)
        metadata['steps'].append('combustion_invert')
    except Exception as e:
        metadata['combustion_error'] = str(e)
    try:
        export_png(grid, export_png_path)
        metadata['png'] = os.path.abspath(export_png_path)
    except Exception as e:
        metadata['export_png_error'] = str(e)
    try:
        export_json(metadata, export_json_path)
        metadata['json'] = os.path.abspath(export_json_path)
    except Exception as e:
        metadata['export_json_error'] = str(e)
    try:
        make_html_preview(export_png_path, export_json_path, export_html_path)
        metadata['html'] = os.path.abspath(export_html_path)
    except Exception as e:
        metadata['export_html_error'] = str(e)
    return metadata, grid
