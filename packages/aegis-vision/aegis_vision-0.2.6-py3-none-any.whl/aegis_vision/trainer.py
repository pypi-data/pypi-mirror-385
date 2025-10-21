"""
YOLO Trainer for Aegis Vision
"""

import os
import shutil
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class YOLOTrainer:
    """
    Unified YOLO trainer supporting YOLOv8-v11
    """
    
    def __init__(
        self,
        model_variant: str = "yolov8n",
        dataset_path: Optional[str] = None,
        epochs: int = 10,
        batch_size: int = 16,
        img_size: int = 640,
        output_formats: Optional[List[str]] = None,
        learning_rate: float = 0.01,
        momentum: float = 0.937,
        weight_decay: float = 0.0005,
        warmup_epochs: int = 3,
        patience: int = 50,
        # Augmentation parameters
        hsv_h: float = 0.015,
        hsv_s: float = 0.7,
        hsv_v: float = 0.4,
        degrees: float = 0.0,
        translate: float = 0.1,
        scale: float = 0.5,
        flipud: float = 0.0,
        fliplr: float = 0.5,
        mosaic: float = 1.0,
        mixup: float = 0.0,
        output_dir: Optional[str] = None,  # NEW: Allow specifying output directory
    ):
        """
        Initialize YOLO trainer
        
        Args:
            model_variant: Model variant (e.g., "yolov8n", "yolo11l")
            dataset_path: Path to dataset.yaml
            epochs: Number of training epochs
            batch_size: Batch size
            img_size: Input image size
            output_formats: List of export formats (e.g., ["onnx", "coreml"])
            learning_rate: Initial learning rate
            momentum: SGD momentum
            weight_decay: Weight decay factor
            warmup_epochs: Number of warmup epochs
            patience: Early stopping patience
            hsv_h: HSV-Hue augmentation (0-1)
            hsv_s: HSV-Saturation augmentation (0-1)
            hsv_v: HSV-Value augmentation (0-1)
            degrees: Rotation degrees (-180 to 180)
            translate: Translation fraction (0-1)
            scale: Scale augmentation (0-1)
            flipud: Flip up-down probability (0-1)
            fliplr: Flip left-right probability (0-1)
            mosaic: Mosaic augmentation (0-1)
            mixup: Mixup augmentation (0-1)
        """
        self.model_variant = model_variant
        self.dataset_path = dataset_path
        self.epochs = epochs
        self.batch_size = batch_size
        self.img_size = img_size
        self.output_formats = output_formats or []
        self.learning_rate = learning_rate
        self.momentum = momentum
        self.weight_decay = weight_decay
        self.warmup_epochs = warmup_epochs
        self.patience = patience
        
        # Augmentation parameters
        self.hsv_h = hsv_h
        self.hsv_s = hsv_s
        self.hsv_v = hsv_v
        self.degrees = degrees
        self.translate = translate
        self.scale = scale
        self.flipud = flipud
        self.fliplr = fliplr
        self.mosaic = mosaic
        self.mixup = mixup
        
        self.model = None
        self.results = None
        self.wandb_enabled = False
        self.wandb_run = None
        
        # Use ~/.aegis-vision for storage (consistent with storage manager)
        # For Kaggle: use /kaggle/working
        # For Agent/Local: use ~/.aegis-vision
        if Path("/kaggle/working").exists():
            self.working_dir = Path("/kaggle/working")
        else:
            # Use provided output_dir or default to ~/.aegis-vision/models
            if output_dir:
                self.working_dir = Path(output_dir)
            else:
                self.working_dir = Path.home() / ".aegis-vision" / "models"
            self.working_dir.mkdir(parents=True, exist_ok=True)
        
        self.output_dir = self.working_dir / "runs"
    
    def setup_wandb(
        self,
        project: str,
        entity: Optional[str] = None,
        api_key: Optional[str] = None,
        run_name: Optional[str] = None,
    ) -> None:
        """
        Setup Weights & Biases tracking
        
        Args:
            project: Wandb project name
            entity: Wandb entity/username
            api_key: Wandb API key
            run_name: Name for this run
        """
        try:
            import wandb
            from ultralytics import settings
            
            # Set environment variables BEFORE wandb.init
            if api_key:
                os.environ['WANDB_API_KEY'] = api_key
            if project:
                os.environ['WANDB_PROJECT'] = project
            if entity:
                os.environ['WANDB_ENTITY'] = entity
            if run_name:
                os.environ['WANDB_NAME'] = run_name
            
            # Prevent RANK errors (required for single-GPU training)
            if 'RANK' not in os.environ:
                os.environ['RANK'] = '-1'
            os.environ['WANDB_MODE'] = 'online'
            
            # Login to wandb (required for authentication)
            if api_key:
                wandb.login(key=api_key, relogin=True)
                logger.info("✅ Logged into Wandb")
            
            # Initialize wandb run (official Ultralytics pattern)
            self.wandb_run = wandb.init(
                project=project,
                entity=entity,
                name=run_name,
                job_type="train",
                config={
                    "model_variant": self.model_variant,
                    "epochs": self.epochs,
                    "batch_size": self.batch_size,
                    "img_size": self.img_size,
                    "learning_rate": self.learning_rate,
                    "momentum": self.momentum,
                    "weight_decay": self.weight_decay,
                },
                tags=['yolo', self.model_variant, 'aegis-vision', 'kaggle']
            )
            
            logger.info(f"✅ Wandb run initialized:")
            logger.info(f"   • Project: {project}")
            if entity:
                logger.info(f"   • Entity: {entity}")
            logger.info(f"   • Run name: {run_name}")
            
            # Enable wandb in Ultralytics settings (native integration - CRITICAL!)
            try:
                settings.update({'wandb': True})
                logger.info("✅ Enabled wandb in Ultralytics settings")
                logger.info("📊 Ultralytics will automatically log all training metrics")
            except Exception as settings_err:
                logger.warning(f"⚠️  Could not update Ultralytics settings: {settings_err}")
            
            self.wandb_enabled = True
            
        except Exception as e:
            logger.warning(f"⚠️ Failed to setup Wandb: {e}")
            self.wandb_enabled = False
            self.wandb_run = None
    
    def finish_wandb(self) -> None:
        """
        Finish and sync the Wandb run
        """
        if self.wandb_enabled and self.wandb_run is not None:
            try:
                import wandb
                wandb.finish()
                logger.info("✅ Wandb run finished and synced")
            except Exception as e:
                logger.warning(f"⚠️ Failed to finish Wandb run: {e}")
    
    def _get_optimal_workers(self) -> int:
        """
        Automatically detect optimal number of DataLoader workers based on shared memory.
        
        PyTorch DataLoader uses /dev/shm (shared memory) for inter-process communication.
        If /dev/shm is too small, reduce workers to avoid "No space left on device" errors.
        
        Returns:
            Optimal number of workers (0-8)
        """
        import os
        import shutil
        
        try:
            # Check shared memory size
            shm_stats = shutil.disk_usage('/dev/shm')
            shm_total_mb = shm_stats.total / (1024 * 1024)
            shm_free_mb = shm_stats.free / (1024 * 1024)
            
            logger.info(f"📊 Shared memory: {shm_total_mb:.0f}MB total, {shm_free_mb:.0f}MB free")
            
            # Heuristic: Need ~50-100MB per worker for typical YOLO training
            # With safety margin, use 100MB per worker
            max_workers_by_shm = max(0, int(shm_free_mb / 100))
            
            # Also consider CPU count
            cpu_count = os.cpu_count() or 4
            max_workers_by_cpu = min(8, cpu_count)
            
            # Take the minimum of the two constraints
            optimal_workers = min(max_workers_by_shm, max_workers_by_cpu)
            
            # Always allow at least 0 workers (main process only)
            optimal_workers = max(0, optimal_workers)
            
            if shm_total_mb < 512:  # Less than 512MB shared memory
                logger.warning(f"⚠️ Low shared memory ({shm_total_mb:.0f}MB). Reducing workers to {optimal_workers}")
                logger.warning(f"   Tip: Increase Docker --shm-size to 2g or more for better performance")
            
            return optimal_workers
            
        except Exception as e:
            logger.warning(f"⚠️ Could not detect shared memory: {e}. Using 0 workers (safe mode)")
            return 0  # Safe fallback: no multiprocessing
    
    def train(self) -> Dict[str, Any]:
        """
        Train the YOLO model
        
        Returns:
            Training results dictionary
        """
        from ultralytics import YOLO
        
        logger.info(f"🤖 Initializing {self.model_variant} model...")
        
        # Try different model naming conventions (yolov11l vs yolo11l)
        # YOLOv11 models use 'yolo11' not 'yolov11'
        model_variants_to_try = []
        
        # For v11 models, try yolo11 first (correct naming)
        if 'v11' in self.model_variant:
            alternative = self.model_variant.replace('yolov11', 'yolo11')
            model_variants_to_try = [alternative, self.model_variant]
        else:
            model_variants_to_try = [self.model_variant]
        
        last_error = None
        for variant in model_variants_to_try:
            try:
                model_path = f'{variant}.pt'
                logger.info(f"⬇️ Attempting to load: {model_path}")
                self.model = YOLO(model_path)
                logger.info(f"✅ Loaded model: {model_path}")
                break
            except Exception as e:
                last_error = e
                logger.warning(f"⚠️ Failed to load {variant}.pt: {str(e)}")
                continue
        
        if self.model is None:
            raise FileNotFoundError(
                f"Model not found after trying: {', '.join([f'{v}.pt' for v in model_variants_to_try])}\n"
                f"Valid models: yolov8n/s/m/l/x, yolov9t/s/m/c/e, yolov10n/s/m/b/l/x, yolo11n/s/m/l/x\n"
                f"Last error: {last_error}"
            )
        
        logger.info(f"🚀 Starting training for {self.epochs} epochs...")
        
        # Detect available device (CUDA, MPS, or CPU)
        import torch
        import os
        
        if torch.cuda.is_available():
            device = 0  # Use first CUDA GPU if available
            device_name = f"CUDA GPU (ID: 0)"
        elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
            device = "mps"  # Use MPS on Apple Silicon
            device_name = "Metal Performance Shaders (MPS)"
        else:
            device = "cpu"  # Fallback to CPU
            device_name = "CPU"
        
        logger.info(f"🖥️  Using device: {device_name}")
        
        # Auto-detect optimal worker count based on shared memory
        # PyTorch DataLoader uses /dev/shm for inter-process communication
        workers = self._get_optimal_workers()
        logger.info(f"🔧 Using {workers} DataLoader workers")
        
        # Train the model
        self.results = self.model.train(
            data=self.dataset_path,
            epochs=self.epochs,
            batch=self.batch_size,
            imgsz=self.img_size,
            lr0=self.learning_rate,
            momentum=self.momentum,
            weight_decay=self.weight_decay,
            warmup_epochs=self.warmup_epochs,
            patience=self.patience,
            project=str(self.output_dir),
            name="train",
            exist_ok=True,
            verbose=True,
            device=device,
            workers=workers,
            save=True,
            save_period=10,
            augment=True,
            # Augmentation parameters
            hsv_h=self.hsv_h,
            hsv_s=self.hsv_s,
            hsv_v=self.hsv_v,
            degrees=self.degrees,
            translate=self.translate,
            scale=self.scale,
            flipud=self.flipud,
            fliplr=self.fliplr,
            mosaic=self.mosaic,
            mixup=self.mixup,
        )
        
        logger.info("✅ Training completed!")
        
        return {
            "success": True,
            "output_dir": str(self.output_dir / "train"),
        }
    
    def export(self, formats: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Export model to various formats
        
        Args:
            formats: List of export formats (onnx, coreml, openvino, tensorrt, tflite)
            
        Returns:
            Export results dictionary
        """
        if not self.model:
            raise RuntimeError("Model not trained yet. Call train() first.")
        
        formats = formats or self.output_formats
        if not formats:
            logger.info("No export formats specified, skipping export")
            return {"exported": []}
        
        logger.info(f"📤 Exporting model to {len(formats)} formats...")
        
        exported = []
        failed = []
        
        for fmt in formats:
            try:
                logger.info(f"  Exporting to {fmt.upper()}...")
                self.model.export(format=fmt)
                exported.append(fmt)
                logger.info(f"  ✅ {fmt.upper()} export successful")
            except Exception as e:
                failed.append(fmt)
                logger.warning(f"  ⚠️ {fmt.upper()} export failed: {str(e)}")
                
                # Provide specific guidance for known issues
                if fmt == "tensorrt":
                    logger.warning("  💡 TensorRT requires specific GPU architecture (SM 75+)")
                elif fmt == "tflite":
                    logger.warning("  💡 TFLite may fail due to CuDNN version or onnx2tf issues")
        
        logger.info(f"✅ Export complete: {len(exported)} succeeded, {len(failed)} failed")
        
        return {
            "exported": exported,
            "failed": failed,
            "total": len(formats),
        }
    
    def prepare_kaggle_output(self, output_dir: Optional[Path] = None) -> None:
        """
        Prepare models for Kaggle output download
        
        Args:
            output_dir: Output directory (default: /kaggle/working/trained_models)
        """
        if not self.model:
            raise RuntimeError("Model not trained yet. Call train() first.")
        
        output_dir = output_dir or (self.working_dir / "trained_models")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info("📦 Preparing models for download...")
        
        # Source directory (where training outputs are)
        weights_dir = self.output_dir / "train" / "weights"
        
        if not weights_dir.exists():
            logger.warning(f"⚠️ Weights directory not found: {weights_dir}")
            return
        
        # Copy all model files
        copied_count = 0
        for file_path in weights_dir.iterdir():
            try:
                dst = output_dir / file_path.name
                
                if file_path.is_dir():
                    # Handle directories (e.g., .mlpackage)
                    if dst.exists():
                        shutil.rmtree(dst)
                    shutil.copytree(file_path, dst)
                else:
                    # Handle regular files
                    shutil.copy2(file_path, dst)
                
                logger.info(f"✅ Copied {file_path.name} to {output_dir}")
                copied_count += 1
                
            except Exception as e:
                logger.warning(f"⚠️ Failed to copy {file_path.name}: {e}")
        
        logger.info(f"✅ Prepared {copied_count} model files for download")
