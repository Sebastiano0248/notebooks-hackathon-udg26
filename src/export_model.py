import argparse
import os
import pickle
import shutil
import sys
import time


def ensure_dummy_artifacts_exist(source_model_path, source_logic_path):
    """
    Generates fake model and logic files to test the pipeline.
    """
    print("🚧 DUMMY MODE ACTIVE: Checking for fake artifacts...")

    # 1. Create a Dummy Model
    if not os.path.exists(source_model_path):
        print(f"   ⚠️ Creating dummy model at {source_model_path}...")
        dummy_model = {
            "name": "Test Model",
            "accuracy": 0.99,
            "timestamp": time.time(),
            "note": "Placeholder model for CI/CD testing.",
        }
        os.makedirs(os.path.dirname(source_model_path), exist_ok=True)
        with open(source_model_path, "wb") as f:
            pickle.dump(dummy_model, f)
    else:
        print("   ✅ Dummy model already exists.")

    # 2. Create Dummy Logic
    if not os.path.exists(source_logic_path):
        print(f"   ⚠️ Creating dummy logic at {source_logic_path}...")
        dummy_code = """
def preprocess(data):
    # Dummy function for CI/CD testing
    return data
"""
        os.makedirs(os.path.dirname(source_logic_path), exist_ok=True)
        with open(source_logic_path, "w") as f:
            f.write(dummy_code)
    else:
        print("   ✅ Dummy logic already exists.")


def export(output_dir, is_dummy=False):
    base_dir = os.getcwd()

    # Define expected locations of source files
    source_model = os.path.join(base_dir, "models", "latest_model.pkl")
    source_logic = os.path.join(base_dir, "src", "transformers.py")

    # LOGIC SWITCH:
    if is_dummy:
        ensure_dummy_artifacts_exist(source_model, source_logic)

    # Validation: If we are NOT in dummy mode, files MUST exist
    if not os.path.exists(source_model):
        print(f"❌ ERROR: Model file missing at {source_model}")
        sys.exit(1)

    if not os.path.exists(source_logic):
        print(f"❌ ERROR: Transformer logic missing at {source_logic}")
        sys.exit(1)

    # Proceed with Export
    os.makedirs(output_dir, exist_ok=True)

    dst_model = os.path.join(output_dir, "model.pkl")
    dst_logic = os.path.join(output_dir, "transformers.py")

    shutil.copy2(source_model, dst_model)
    shutil.copy2(source_logic, dst_logic)

    print("-" * 30)
    print(f"🚀 EXPORT SUCCESSFUL (Dummy Mode: {is_dummy})")
    print(f"📂 Output Dir: {output_dir}")
    print("-" * 30)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output_dir", required=True, help="Destination folder")
    # The flag that triggers dummy mode
    parser.add_argument(
        "--is_dummy", action="store_true", help="Generate fake files if missing"
    )

    args = parser.parse_args()

    export(args.output_dir, is_dummy=args.is_dummy)
