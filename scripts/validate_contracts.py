"""Script de validação de JSON Schemas e OpenAPI YAMLs."""
import json
import os
import sys

# === 1. Validar JSON Schemas ===
schemas_dir = "/app/docs/schemas"
errors = []
ok = []

for f in sorted(os.listdir(schemas_dir)):
    if not f.endswith(".json"):
        continue
    path = os.path.join(schemas_dir, f)
    try:
        with open(path) as fh:
            data = json.load(fh)
        if data.get("type") == "object" and "properties" not in data:
            errors.append(f"{f}: FALTA campo 'properties'")
        else:
            ok.append(f)
    except json.JSONDecodeError as e:
        errors.append(f"{f}: JSON INVALIDO - {e}")

print(f"=== JSON Schemas: {len(ok)} OK, {len(errors)} ERROS ===")
for f in ok:
    print(f"  OK  {f}")
for e in errors:
    print(f"  ERR {e}")

# === 2. Validar OpenAPI YAMLs ===
import yaml

openapi_dir = "/app/docs/openapi"
yaml_errors = []
yaml_ok = []

for f in sorted(os.listdir(openapi_dir)):
    if not f.endswith(".yml"):
        continue
    path = os.path.join(openapi_dir, f)
    try:
        with open(path) as fh:
            data = yaml.safe_load(fh)
        # Verificar campos obrigatórios de OpenAPI
        missing = []
        if "openapi" not in data:
            missing.append("openapi")
        if "info" not in data:
            missing.append("info")
        if "paths" not in data:
            missing.append("paths")
        if missing:
            yaml_errors.append(f"{f}: FALTAM campos: {', '.join(missing)}")
        else:
            # Verificar que cada path tem pelo menos um método
            for path_key, methods in data.get("paths", {}).items():
                if not isinstance(methods, dict):
                    yaml_errors.append(f"{f}: path '{path_key}' invalido")
                    break
            else:
                yaml_ok.append(f)
    except yaml.YAMLError as e:
        yaml_errors.append(f"{f}: YAML INVALIDO - {e}")

print(f"\n=== OpenAPI YAMLs: {len(yaml_ok)} OK, {len(yaml_errors)} ERROS ===")
for f in yaml_ok:
    print(f"  OK  {f}")
for e in yaml_errors:
    print(f"  ERR {e}")

# === 3. Verificar refs internas nos OpenAPI ===
ref_errors = []
for f in sorted(os.listdir(openapi_dir)):
    if not f.endswith(".yml"):
        continue
    path = os.path.join(openapi_dir, f)
    with open(path) as fh:
        data = yaml.safe_load(fh)
    
    schemas = data.get("components", {}).get("schemas", {})
    raw = open(path).read()
    
    # Encontrar todas as $ref
    import re
    refs = re.findall(r'\$ref:\s+["\']?([^"\'}\s]+)', raw)
    for ref in refs:
        if ref.startswith("#/components/schemas/"):
            schema_name = ref.split("/")[-1]
            if schema_name not in schemas:
                ref_errors.append(f"{f}: ref '{ref}' aponta para schema inexistente '{schema_name}'")

print(f"\n=== Refs Internas: {len(ref_errors)} ERROS ===")
if ref_errors:
    for e in ref_errors:
        print(f"  ERR {e}")
else:
    print("  Todas as refs internas estao corretas")

# === Resultado final ===
total_errors = len(errors) + len(yaml_errors) + len(ref_errors)
print(f"\n{'='*50}")
print(f"RESULTADO FINAL: {len(ok) + len(yaml_ok)} arquivos validos, {total_errors} erros")
if total_errors > 0:
    sys.exit(1)
else:
    print("TODOS OS CONTRATOS ESTAO VALIDOS!")
