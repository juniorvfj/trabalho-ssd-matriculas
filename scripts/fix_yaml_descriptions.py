"""
Script para corrigir valores YAML que contêm ':' sem aspas nas descriptions.
Problema: 'description: Código da disciplina (Ex: CIC0001)' não é YAML válido
porque o parser interpreta 'Ex:' como uma chave de mapeamento.
Solução: Envolver o valor com aspas duplas.
"""
import os
import re

openapi_dir = "/app/docs/openapi"
total_fixes = 0

for f in sorted(os.listdir(openapi_dir)):
    if not f.endswith(".yml"):
        continue
    path = os.path.join(openapi_dir, f)
    with open(path, "r", encoding="utf-8") as fh:
        lines = fh.readlines()

    fixed_lines = []
    fixes = 0
    for line in lines:
        stripped = line.strip()
        # Check if it's a description line with unquoted colons in value
        if stripped.startswith("description:") and not stripped.startswith("description: |"):
            # Get everything after 'description:'
            parts = line.split("description:", 1)
            if len(parts) == 2:
                indent_part = parts[0]
                value = parts[1].strip().rstrip("\n")
                # Check if value contains ':' and is NOT already quoted
                if ":" in value and not value.startswith('"') and not value.startswith("'"):
                    new_value = '"' + value.replace('"', '\\"') + '"'
                    fixed_line = indent_part + "description: " + new_value + "\n"
                    fixed_lines.append(fixed_line)
                    fixes += 1
                    continue
        fixed_lines.append(line)

    if fixes > 0:
        with open(path, "w", encoding="utf-8") as fh:
            fh.writelines(fixed_lines)
        total_fixes += fixes
        print(f"FIXED {fixes} lines in {f}")
    else:
        print(f"OK (no fixes needed): {f}")

print(f"\nTotal fixes: {total_fixes}")
