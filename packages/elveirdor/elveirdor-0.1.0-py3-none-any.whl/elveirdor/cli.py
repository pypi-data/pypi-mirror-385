# Simple CLI entry point
import argparse
from .pipeline import run_pipeline
import json

def build_parser():
    p = argparse.ArgumentParser(prog='elveirdor', description='Elveirdor unified pipeline')
    p.add_argument('--text', type=str, default='ELVEIRDOR')
    p.add_argument('--grid', type=int, default=10)
    p.add_argument('--seed', type=int, default=12345)
    p.add_argument('--export', type=str, default='output.png')
    p.add_argument('--export_json', type=str, default='metadata.json')
    p.add_argument('--export_html', type=str, default='preview.html')
    p.add_argument('--sequence', type=str, default='')
    return p

def main():
    parser = build_parser()
    args = parser.parse_args()
    seq = args.sequence if args.sequence else None
    metadata, _ = run_pipeline(text=args.text, grid_size=max(3,int(args.grid)), seed=int(args.seed),
                               export_png_path=args.export, export_json_path=args.export_json,
                               export_html_path=args.export_html, sequence=seq)
    print('Pipeline complete. Summary:')
    print(json.dumps({k: metadata.get(k) for k in ['text','grid_size','seed','png','json','html','steps']}, indent=2))

if __name__ == '__main__':
    main()
