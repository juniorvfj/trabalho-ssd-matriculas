import os
import glob
from ruamel.yaml import YAML

base_dir = r"c:\Users\junio\OneDrive\AAMestrado\2026.1\Segurança de Sistemas Distribuidos\TrabalhoSSD\docs\openapi"
yaml = YAML(typ='safe')

errors = []
for filepath in glob.glob(os.path.join(base_dir, "*.yml")):
    filename = os.path.basename(filepath)
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = yaml.load(f)
            # basic check
            if 'paths' not in data:
                errors.append(f"{filename}: 'paths' missing")
                
            # check for duplicate keys
    except Exception as e:
        errors.append(f"{filename} is invalid: {str(e)}")

if errors:
    print("Errors found:")
    for e in errors:
        print(e)
else:
    print("All YAMLs are syntactically valid!")
