import json, base64, os
from PIL import Image

def export_png(grid, filename):
    img = Image.fromarray(grid)
    img.save(filename)

def export_json(metadata, filename):
    with open(filename,'w',encoding='utf-8') as f:
        json.dump(metadata,f,indent=2)

def make_html_preview(png_file, json_file, html_file):
    try:
        with open(json_file,'r',encoding='utf-8') as f:
            meta = json.load(f)
    except Exception:
        meta = {"error":"missing metadata"}
    try:
        with open(png_file,'rb') as f:
            img_data = base64.b64encode(f.read()).decode('ascii')
    except Exception:
        img_data = ''
    html = f"""<!doctype html><html><head><meta charset='utf-8'><title>Elveirdor</title></head><body>\n"
    html += f"<h1>Elveirdor Preview</h1>\n"
    if img_data:
        html += f"<img src=\"data:image/png;base64,{img_data}\" alt=\"output\">\n"
    else:
        html += "<p>No image available.</p>\n"
    html += f"<pre>{json.dumps(meta,indent=2)}</pre></body></html>"
    with open(html_file,'w',encoding='utf-8') as f:
        f.write(html)
