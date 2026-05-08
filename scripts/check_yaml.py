import yaml, sys, os

openapi_dir = "/app/docs/openapi"
for f in sorted(os.listdir(openapi_dir)):
    if not f.endswith(".yml"):
        continue
    path = os.path.join(openapi_dir, f)
    try:
        with open(path) as fh:
            yaml.safe_load(fh)
        print("OK: " + f)
    except yaml.YAMLError as e:
        print("ERR: " + f)
        print("  " + str(e))
