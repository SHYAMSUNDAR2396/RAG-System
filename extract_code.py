import json
import sys

def extract_code(notebook_path):
    with open(notebook_path, 'r') as f:
        data = json.load(f)
    
    for cell in data.get('cells', []):
        if cell.get('cell_type') == 'code':
            source = ''.join(cell.get('source', []))
            print(source)
            print('\n# --- CELL BOUNDARY ---\n')

if __name__ == '__main__':
    extract_code(sys.argv[1])
