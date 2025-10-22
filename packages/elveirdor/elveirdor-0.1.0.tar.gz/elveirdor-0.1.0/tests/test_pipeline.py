import os
from elveirdor.pipeline import run_pipeline

def test_pipeline_runs_tmp(tmp_path):
    out_png = str(tmp_path / 'out.png')
    out_json = str(tmp_path / 'meta.json')
    out_html = str(tmp_path / 'preview.html')
    metadata, grid = run_pipeline(text='TEST', grid_size=10, seed=42,
                                  export_png_path=out_png, export_json_path=out_json, export_html_path=out_html)
    assert 'steps' in metadata
    assert metadata.get('png') is not None or os.path.exists(out_png)
    assert os.path.exists(out_json)
    assert os.path.exists(out_html)
