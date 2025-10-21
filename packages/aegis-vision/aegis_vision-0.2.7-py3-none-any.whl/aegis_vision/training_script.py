"""
YOLO Training Script for Kaggle and Training Agents (Simplified with aegis-vision)

This script uses the aegis-vision package for simplified training.
Includes automatic dataset discovery, merging, and Wandb integration.

Works on:
- Kaggle notebooks
- Training agents (local/remote machines)
"""

import sys
import json
import subprocess
import os
from pathlib import Path

# Detect environment
IS_KAGGLE = Path("/kaggle").exists()
IS_AGENT = os.environ.get("AEGIS_AGENT_MODE") == "1"

if IS_KAGGLE:
    # CRITICAL: Fix NumPy compatibility BEFORE any other imports (Kaggle only)
    print("📦 Checking NumPy compatibility...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "--force-reinstall", "numpy<2.0"])
        print("✅ NumPy 1.x installed")
        
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "--force-reinstall", "--no-deps", "matplotlib"])
        print("✅ Matplotlib reinstalled for NumPy 1.x")
    except subprocess.CalledProcessError as e:
        print(f"⚠️  Warning: Failed to reinstall packages: {e}")

# Install aegis-vision if not already installed (Kaggle only)
if IS_KAGGLE:
    try:
        import aegis_vision
        print(f"✅ aegis-vision {aegis_vision.__version__} already installed")
    except ImportError:
        print("📦 Installing aegis-vision...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--quiet", "aegis-vision>=0.2.3"])
        import aegis_vision
        print(f"✅ aegis-vision {aegis_vision.__version__} installed")
else:
    import aegis_vision

from aegis_vision import (
    YOLOTrainer,
    AdvancedCOCOtoYOLOMerger,
    discover_datasets,
    preprocess_datasets,
    setup_logging,
    detect_environment
)

# Environment-specific paths
if IS_KAGGLE:
    INPUT_DIR = Path("/kaggle/input")
    WORKING_DIR = Path("/kaggle/working")
else:
    # For agents, paths will be passed via config
    INPUT_DIR = Path(os.environ.get("AEGIS_INPUT_DIR", "."))
    WORKING_DIR = Path(os.environ.get("AEGIS_WORKING_DIR", "."))

# Output directory for models (consistent storage location)
if IS_KAGGLE:
    OUTPUT_DIR = Path("/kaggle/working")
else:
    # For agent mode, use working directory; otherwise use ~/.aegis-vision
    if os.environ.get("AEGIS_AGENT_MODE"):
        OUTPUT_DIR = WORKING_DIR / "trained_models"
    else:
        OUTPUT_DIR = Path.home() / ".aegis-vision" / "models"
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# EMBEDDED_CONFIG_PLACEHOLDER
EMBEDDED_CONFIG = """{{TRAINING_CONFIG_JSON}}"""

# Setup logging
setup_logging(level="INFO")

import logging
logger = logging.getLogger(__name__)


def log_progress(message: str, **kwargs):
    """Log training progress directly for real-time visibility"""
    print(message)
    logger.info(message)


def main():
    """Main training function"""
    try:
        env_name = "Kaggle" if IS_KAGGLE else "Training Agent"
        log_progress(f"🚀 Starting Aegis Vision training on {env_name}")
        log_progress(f"📦 aegis-vision version: {aegis_vision.__version__}")
        log_progress(f"📂 Input directory: {INPUT_DIR}")
        log_progress(f"📂 Working directory: {WORKING_DIR}")
        
        # Detect environment
        env = detect_environment()
        log_progress(f"🌍 Environment detected: {env}")
        
        # Load configuration
        log_progress("📋 Loading training configuration...")
        
        config = {}
        config_source = None
        
        # Priority 1: Environment variable (for remote agents)
        env_config = os.environ.get('AEGIS_TRAINING_CONFIG')
        if env_config:
            try:
                config = json.loads(env_config)
                config_source = "environment variable (AEGIS_TRAINING_CONFIG)"
                log_progress("✅ Loaded training config from environment variable")
            except json.JSONDecodeError as e:
                log_progress(f"⚠️  Failed to parse config from environment: {e}", status="warning")
        
        # Priority 2: Embedded config (for Kaggle notebooks)
        if not config:
            try:
                if EMBEDDED_CONFIG and not EMBEDDED_CONFIG.startswith("{{"):
                    config = json.loads(EMBEDDED_CONFIG)
                    config_source = "embedded"
                    log_progress("✅ Loaded training config from embedded source")
            except json.JSONDecodeError as e:
                log_progress(f"⚠️  Failed to parse embedded config: {e}", status="warning")
        
        # Priority 3: File-based config (fallback for local agents)
        if not config:
            # First, try the input directory root (agent training)
            config_file = INPUT_DIR / "training_config.json"
            if config_file.exists():
                with open(config_file, 'r') as f:
                    config = json.load(f)
                    config_source = f"file ({config_file})"
                    log_progress("✅ Loaded training config from file")
            else:
                # Then try inside dataset subdirectories (Kaggle)
                for dataset_dir in INPUT_DIR.iterdir():
                    if dataset_dir.is_dir():
                        config_file = dataset_dir / "training_config.json"
                        if config_file.exists():
                            with open(config_file, 'r') as f:
                                config = json.load(f)
                                config_source = f"file ({config_file})"
                                log_progress("✅ Loaded training config from file")
                            break
        
        # Use defaults if no config found
        if not config:
            log_progress("⚠️  No config found, using defaults", status="warning")
            config = {
                "model_variant": "yolov8n",
                "epochs": 10,
                "batch_size": 16,
                "img_size": 640,
                "output_formats": ["onnx"],
            }
        
        log_progress(f"📋 Config loaded from: {config_source}")
        
        # DEBUG: Log the raw config to see what we received
        log_progress(f"🔍 DEBUG: Raw config keys: {list(config.keys())}")
        log_progress(f"🔍 DEBUG: epochs in config = {config.get('epochs', 'NOT FOUND')}")
        
        # Extract config parameters
        model_variant = config.get('model_variant', 'yolov8n')
        epochs = config.get('epochs', 10)
        batch_size = config.get('batch_size', 16)
        img_size = config.get('img_size', 640)
        output_formats = config.get('output_formats', ['onnx'])
        
        log_progress(f"🔍 DEBUG: After extraction, epochs = {epochs}")
        
        # Wandb configuration
        wandb_enabled = config.get('wandb_enabled', False)
        wandb_project = config.get('wandb_project', '')
        wandb_entity = config.get('wandb_entity', None)
        
        # Extract all training hyperparameters from config
        learning_rate = config.get('learning_rate', 0.01)
        momentum = config.get('momentum', 0.937)
        weight_decay = config.get('weight_decay', 0.0005)
        warmup_epochs = config.get('warmup_epochs', 3)
        
        # Early stopping configuration
        early_stopping_config = config.get('early_stopping', {})
        patience = early_stopping_config.get('patience', 50) if isinstance(early_stopping_config, dict) else 50
        
        # Additional hyperparameters
        hsv_h = config.get('hsv_h', 0.015)  # HSV-Hue augmentation
        hsv_s = config.get('hsv_s', 0.7)    # HSV-Saturation augmentation
        hsv_v = config.get('hsv_v', 0.4)    # HSV-Value augmentation
        degrees = config.get('degrees', 0.0)  # Rotation degrees
        translate = config.get('translate', 0.1)  # Translation
        scale = config.get('scale', 0.5)  # Scale augmentation
        flipud = config.get('flipud', 0.0)  # Flip up-down
        fliplr = config.get('fliplr', 0.5)  # Flip left-right
        mosaic = config.get('mosaic', 1.0)  # Mosaic augmentation
        mixup = config.get('mixup', 0.0)  # Mixup augmentation
        
        log_progress("📊 Training configuration summary",
                    model=model_variant,
                    epochs=epochs,
                    batch_size=batch_size,
                    img_size=img_size,
                    learning_rate=learning_rate,
                    patience=patience,
                    wandb_enabled=wandb_enabled)
        
        # Discover datasets using aegis-vision
        log_progress("🔍 Discovering datasets...")
        datasets_found = discover_datasets(INPUT_DIR)
        
        if not datasets_found:
            log_progress(f"❌ No datasets found in {INPUT_DIR}", status="error")
            sys.exit(1)
        
        log_progress(f"📊 Found {len(datasets_found)} dataset(s)")
        
        if len(datasets_found) == 1:
            log_progress("🎯 Single dataset detected - will convert if needed")
        else:
            log_progress(f"🔀 Multiple datasets detected ({len(datasets_found)}) - will merge")
        
        # Preprocess datasets (convert COCO standard to flat format)
        preprocessed_datasets = preprocess_datasets(datasets_found, WORKING_DIR)
        
        # Merge and convert datasets to YOLO format
        log_progress("⚡ Merging datasets and converting to YOLO format...")
        output_dir = WORKING_DIR / "yolo_dataset"
        merger = AdvancedCOCOtoYOLOMerger(output_dir=output_dir)
        merge_result = merger.merge_and_convert(preprocessed_datasets)
        
        dataset_yaml = merge_result['dataset_yaml']
        log_progress(f"✅ Dataset ready: {dataset_yaml}")
        log_progress(f"   • Train: {merge_result['train_images']} images, {merge_result['train_labels']} labels")
        log_progress(f"   • Val: {merge_result['val_images']} images, {merge_result['val_labels']} labels")
        log_progress(f"   • Classes: {merge_result['classes']}")
        
        # Setup Wandb if enabled
        wandb_api_key = None
        if wandb_enabled:
            log_progress("🔧 Setting up Wandb integration...")
            
            wandb_api_key = os.environ.get('WANDB_API_KEY')
            
            if not wandb_api_key:
                log_progress("⚠️  WANDB_API_KEY not found in environment", status="warning")
                log_progress("    Wandb tracking disabled. Set WANDB_API_KEY env var to enable.", status="warning")
                wandb_enabled = False
            else:
                log_progress(f"✅ Found WANDB_API_KEY in environment")
                log_progress(f"📊 Wandb Project: {wandb_project}")
                if wandb_entity:
                    log_progress(f"📊 Wandb Entity: {wandb_entity}")
        
        # Initialize trainer
        log_progress(f"🤖 Initializing YOLOTrainer with {model_variant}...")
        
        trainer = YOLOTrainer(
            model_variant=model_variant,
            dataset_path=str(dataset_yaml),
            epochs=epochs,
            batch_size=batch_size,
            img_size=img_size,
            output_formats=output_formats,
            learning_rate=learning_rate,
            momentum=momentum,
            weight_decay=weight_decay,
            warmup_epochs=warmup_epochs,
            patience=patience,
            hsv_h=hsv_h,
            hsv_s=hsv_s,
            hsv_v=hsv_v,
            degrees=degrees,
            translate=translate,
            scale=scale,
            flipud=flipud,
            fliplr=fliplr,
            mosaic=mosaic,
            mixup=mixup,
            output_dir=str(OUTPUT_DIR),  # Pass the configured output directory
        )
        
        # Setup Wandb with API key and config
        if wandb_enabled and wandb_api_key:
            log_progress("📊 Configuring Wandb tracking...")
            primary_dataset_name = datasets_found[0]["name"] if datasets_found else "merged"
            run_name = f"{model_variant}_{primary_dataset_name}"
            if len(datasets_found) > 1:
                run_name += f"_plus{len(datasets_found)-1}"
            
            try:
                trainer.setup_wandb(
                    project=wandb_project or 'aegis-ai',
                    entity=wandb_entity,
                    api_key=wandb_api_key,
                    run_name=run_name
                )
                log_progress(f"✅ Wandb run initialized: {run_name}")
            except Exception as e:
                log_progress(f"⚠️  Failed to setup Wandb: {str(e)}", status="warning")
                log_progress("   Training will continue without Wandb tracking", status="warning")
        elif not wandb_enabled:
            log_progress("📊 Wandb tracking disabled for this training run")
        
        # Train
        log_progress(f"🚀 Starting training for {epochs} epochs...")
        results = trainer.train()
        
        log_progress("✅ Training completed successfully!")
        log_progress(f"📊 Results saved to: {WORKING_DIR / 'runs'}")
        
        # Finish Wandb run (sync all metrics)
        if wandb_enabled:
            log_progress("📊 Finishing Wandb run and syncing metrics...")
            trainer.finish_wandb()
        
        # Export models
        if output_formats:
            log_progress(f"📤 Exporting model to {len(output_formats)} formats...")
            export_results = trainer.export(formats=output_formats)
            log_progress("✅ Model export complete!", **export_results)
        
        # Copy models to output directory
        log_progress("📦 Preparing models for download...")
        trainer.prepare_kaggle_output(output_dir=OUTPUT_DIR)
        
        # Upload to Kaggle Model Hub if enabled
        kaggle_upload_enabled = config.get('kaggle_upload_enabled', False)
        
        # DEBUG: Log Kaggle upload configuration
        log_progress(f"🔍 DEBUG: Kaggle upload enabled: {kaggle_upload_enabled}")
        log_progress(f"🔍 DEBUG: Config keys: {list(config.keys())}")
        
        if kaggle_upload_enabled:
            log_progress("🚀 Uploading model to Kaggle Model Hub...")
            
            kaggle_username = os.environ.get('KAGGLE_USERNAME')
            kaggle_api_key = os.environ.get('KAGGLE_KEY')
            kaggle_model_slug = config.get('kaggle_model_slug')
            
            log_progress(f"🔍 DEBUG: Kaggle username from env: {'SET' if kaggle_username else 'NOT SET'}")
            log_progress(f"🔍 DEBUG: Kaggle API key from env: {'SET' if kaggle_api_key else 'NOT SET'}")
            log_progress(f"🔍 DEBUG: Kaggle model slug from config: {kaggle_model_slug}")
            
            if kaggle_username and kaggle_api_key and kaggle_model_slug:
                try:
                    from aegis_vision.kaggle_uploader import upload_trained_model
                    
                    log_progress(f"📦 Uploading from directory: {OUTPUT_DIR}")
                    log_progress(f"📦 Model slug: {kaggle_model_slug}")
                    log_progress(f"📦 Model variant: {model_variant}")
                    
                    # Prepare dataset info
                    dataset_info = {
                        'name': datasets_found[0]['name'] if datasets_found else 'Custom Dataset',
                        'num_classes': merge_result.get('classes', 'N/A'),
                        'train_images': merge_result.get('train_images', 'N/A'),
                        'val_images': merge_result.get('val_images', 'N/A')
                    }
                    
                    # Upload model
                    upload_result = upload_trained_model(
                        model_dir=str(OUTPUT_DIR),
                        model_slug=kaggle_model_slug,
                        model_variant=model_variant,
                        training_config=config,
                        kaggle_username=kaggle_username,
                        kaggle_api_key=kaggle_api_key,
                        metrics=None,  # Could extract from trainer.model.metrics if available
                        dataset_info=dataset_info
                    )
                    
                    if upload_result.get('success'):
                        log_progress(f"✅ Model uploaded successfully!")
                        log_progress(f"   URL: {upload_result.get('model_url')}")
                        log_progress(f"   Files: {upload_result.get('files_uploaded')} uploaded")
                    else:
                        log_progress(f"⚠️  Model upload failed: {upload_result.get('error')}", status="warning")
                        log_progress(f"   Help: {upload_result.get('help', 'N/A')}", status="warning")
                        log_progress("   Training completed successfully, but upload failed", status="warning")
                        
                except Exception as e:
                    log_progress(f"⚠️  Failed to upload model to Kaggle: {str(e)}", status="warning")
                    import traceback
                    log_progress(f"   Traceback: {traceback.format_exc()}", status="warning")
                    log_progress("   Training completed successfully, but upload failed", status="warning")
            else:
                missing = []
                if not kaggle_username:
                    missing.append("KAGGLE_USERNAME environment variable")
                if not kaggle_api_key:
                    missing.append("KAGGLE_KEY environment variable")
                if not kaggle_model_slug:
                    missing.append("kaggle_model_slug in config")
                
                log_progress(f"⚠️  Kaggle upload skipped - missing: {', '.join(missing)}", status="warning")
                log_progress("   To enable Kaggle upload:", status="warning")
                log_progress("   1. Set kaggleUploadEnabled=true in training config", status="warning")
                log_progress("   2. Provide Kaggle username and API key", status="warning")
                log_progress("   3. Provide kaggle_model_slug", status="warning")
        else:
            log_progress("ℹ️  Kaggle upload disabled in configuration")
        
        log_progress("🎉 All tasks completed successfully!")
        
    except Exception as e:
        log_progress(f"❌ Training failed: {str(e)}", status="error")
        import traceback
        log_progress(f"Traceback: {traceback.format_exc()}", status="error")
        sys.exit(1)


if __name__ == "__main__":
    main()

