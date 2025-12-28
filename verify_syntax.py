import os
import py_compile
import sys

def check_syntax(file_path):
    try:
        py_compile.compile(file_path, doraise=True)
        return True
    except py_compile.PyCompileError as e:
        print(f"SYNTAX ERROR in {file_path}: {e}")
        return False
    except Exception as e:
        print(f"Error checking {file_path}: {e}")
        return False

def check_file_exists(file_path):
    if os.path.exists(file_path):
        return True
    print(f"MISSING FILE: {file_path}")
    return False

def main():
    root_dir = "c:/project/satellite-ndvi-pipeline"
    
    python_files = [
        "data_ingestion/ingest.py",
        "data_ingestion/sentinel_client.py",
        "data_ingestion/__init__.py",
        "ndvi_processing/processor.py",
        "ndvi_processing/worker.py",
        "ndvi_processing/__init__.py",
        "api_gateway/main.py",
        "api_gateway/schemas.py",
        "api_gateway/routers/ndvi.py",
        "api_gateway/routers/__init__.py",
        "shared/database.py",
        "shared/models.py",
        "shared/__init__.py"
    ]
    
    infra_files = [
        "docker-compose.yml",

        "data_ingestion/Dockerfile",
        "ndvi_processing/Dockerfile",
        "api_gateway/Dockerfile",
        "kubernetes/configmap.yaml",
        "kubernetes/secret.yaml",
        "kubernetes/postgres.yaml",
        "kubernetes/ingestion.yaml",
        "kubernetes/processing.yaml",
        "kubernetes/api.yaml",
        "database/init.sql"
    ]
    
    success = True
    
    print("--- Verifying Python Syntax ---")
    for f in python_files:
        full_path = os.path.join(root_dir, f)
        if not check_file_exists(full_path):
            success = False
            continue
        if full_path.endswith(".py") and not check_syntax(full_path):
            success = False
            
    print("\n--- Verifying Infrastructure Files ---")
    for f in infra_files:
        full_path = os.path.join(root_dir, f)
        if not check_file_exists(full_path):
            success = False

    if success:
        print("\nAll checks passed successfully.")
        sys.exit(0)
    else:
        print("\nVerification FAILED.")
        sys.exit(1)

if __name__ == "__main__":
    main()
