"""
Aegis AI Training Agent

Core agent functionality for distributed training:
- Firestore-based task queue monitoring
- Environment validation and dependency checking
- Dataset download and preparation
- Training execution with progress reporting
- Model upload and task completion
"""

import os
import sys
import time
import json
import psutil
import platform
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any, Callable, List
from datetime import datetime
import logging

# Aegis Vision imports
from .trainer import YOLOTrainer
from .agent_auth import AgentAuthenticator, AgentAuthenticationError

logger = logging.getLogger(__name__)


class AgentCapabilities:
    """System capabilities detection"""
    
    @staticmethod
    def detect() -> Dict[str, Any]:
        """Detect system capabilities"""
        capabilities = {
            "platform": platform.system(),
            "pythonVersion": platform.python_version(),
            "totalMemoryGB": round(psutil.virtual_memory().total / (1024**3), 2),
            "availableMemoryGB": round(psutil.virtual_memory().available / (1024**3), 2),
            "totalStorageGB": round(psutil.disk_usage('/').total / (1024**3), 2),
            "availableStorageGB": round(psutil.disk_usage('/').free / (1024**3), 2),
            "cpuCount": psutil.cpu_count(),
            "hasGPU": False,
            "hasMPS": False,
            "cudaVersion": None,
            "gpuInfo": [],
            "environment": AgentCapabilities._detect_environment(),
            "trainingFolder": str(Path.home() / ".aegis-vision" / "agent-work")
        }
        
        # Check for CUDA/GPU and MPS
        pytorch_available = False
        try:
            # Suppress warnings about newer GPUs not being fully supported
            import warnings
            warnings.filterwarnings('ignore', category=UserWarning, message='.*CUDA capability.*')
            warnings.filterwarnings('ignore', category=UserWarning, message='.*NumPy.*')
            
            import torch
            pytorch_available = True
            
            # Check CUDA
            if torch.cuda.is_available():
                capabilities["hasGPU"] = True
                capabilities["cudaVersion"] = torch.version.cuda
                capabilities["gpuInfo"] = [
                    {
                        "name": torch.cuda.get_device_name(i),
                        "memory": round(torch.cuda.get_device_properties(i).total_memory / (1024**3), 2)
                    }
                    for i in range(torch.cuda.device_count())
                ]
            
            # Check MPS (Apple Silicon)
            if hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
                capabilities["hasMPS"] = True
                capabilities["hasGPU"] = True  # MPS counts as GPU acceleration
                if not capabilities["gpuInfo"]:
                    capabilities["gpuInfo"] = [{
                        "name": "Apple Silicon (MPS)",
                        "memory": 0  # Shared memory, not separately reported
                    }]
        except ImportError:
            pass
        
        # If PyTorch not installed but running on Apple Silicon (Darwin + ARM64), indicate MPS potential
        if not pytorch_available and platform.system() == "Darwin":
            try:
                # Check if running on ARM64 (Apple Silicon)
                machine = platform.machine().lower()
                if 'arm' in machine or 'aarch64' in machine:
                    capabilities["hasMPS"] = True
                    capabilities["hasGPU"] = True
                    capabilities["gpuInfo"] = [{
                        "name": "Apple Silicon (MPS - PyTorch not installed)",
                        "memory": 0
                    }]
            except Exception:
                pass
        
        return capabilities
    
    @staticmethod
    def _detect_environment() -> Dict[str, Any]:
        """Detect Python environment type (conda, venv, or system)"""
        env_info = {
            "type": "system",  # default
            "name": None,
            "path": sys.prefix,
            "condaAvailable": False,
            "venvAvailable": True  # venv is built-in to Python 3.3+
        }
        
        # Check if in conda environment
        if os.environ.get('CONDA_DEFAULT_ENV'):
            env_info["type"] = "conda"
            env_info["name"] = os.environ.get('CONDA_DEFAULT_ENV')
            env_info["condaAvailable"] = True
        # Check if in venv
        elif hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
            env_info["type"] = "venv"
            env_info["name"] = Path(sys.prefix).name
        
        # Check if conda is available (even if not currently in conda env)
        try:
            result = subprocess.run(['conda', '--version'], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                env_info["condaAvailable"] = True
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass
        
        return env_info


class PackageManager:
    """Manage package installation and environment setup"""
    
    @staticmethod
    def check_package_installed(package_name: str) -> Dict[str, Any]:
        """Check if a package is installed and get its version"""
        result = {
            "installed": False,
            "version": None,
            "error": None
        }
        
        try:
            if package_name == "torch" or package_name == "pytorch":
                import torch
                result["installed"] = True
                result["version"] = torch.__version__
            elif package_name == "ultralytics":
                import ultralytics
                result["installed"] = True
                result["version"] = ultralytics.__version__
            else:
                # Generic package check
                import importlib
                mod = importlib.import_module(package_name)
                result["installed"] = True
                result["version"] = getattr(mod, '__version__', 'unknown')
        except ImportError as e:
            result["error"] = str(e)
        
        return result
    
    @staticmethod
    def install_package(package_name: str, env_type: str = "current", env_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Install a package in the specified environment.
        
        Args:
            package_name: Package to install (e.g., 'torch', 'ultralytics')
            env_type: 'current', 'conda', or 'venv'
            env_name: Name of conda env or path to venv
            
        Returns:
            Dict with success status, output, and error
        """
        result = {
            "success": False,
            "output": "",
            "error": None
        }
        
        try:
            if env_type == "conda" and env_name:
                # Install in conda environment
                cmd = ["conda", "run", "-n", env_name, "pip", "install", package_name]
            elif env_type == "venv" and env_name:
                # Install in venv
                pip_path = Path(env_name) / "bin" / "pip"
                if not pip_path.exists():
                    pip_path = Path(env_name) / "Scripts" / "pip.exe"  # Windows
                cmd = [str(pip_path), "install", package_name]
            else:
                # Install in current environment
                cmd = [sys.executable, "-m", "pip", "install", package_name]
            
            logger.info(f"Installing {package_name} with command: {' '.join(cmd)}")
            
            process = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minutes timeout
            )
            
            result["output"] = process.stdout
            result["success"] = process.returncode == 0
            
            if not result["success"]:
                result["error"] = process.stderr
                logger.error(f"Failed to install {package_name}: {process.stderr}")
            else:
                logger.info(f"Successfully installed {package_name}")
                
        except subprocess.TimeoutExpired:
            result["error"] = "Installation timeout (5 minutes exceeded)"
            logger.error(f"Installation timeout for {package_name}")
        except Exception as e:
            result["error"] = str(e)
            logger.error(f"Installation error for {package_name}: {e}")
        
        return result
    
    @staticmethod
    def create_conda_env(env_name: str, python_version: str = "3.10") -> Dict[str, Any]:
        """Create a new conda environment"""
        result = {
            "success": False,
            "output": "",
            "error": None
        }
        
        try:
            cmd = ["conda", "create", "-n", env_name, f"python={python_version}", "-y"]
            logger.info(f"Creating conda environment: {env_name}")
            
            process = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            result["output"] = process.stdout
            result["success"] = process.returncode == 0
            
            if not result["success"]:
                result["error"] = process.stderr
                logger.error(f"Failed to create conda env: {process.stderr}")
            else:
                logger.info(f"Successfully created conda environment: {env_name}")
                
        except Exception as e:
            result["error"] = str(e)
            logger.error(f"Error creating conda env: {e}")
        
        return result
    
    @staticmethod
    def create_venv(venv_path: str, python_executable: str = sys.executable) -> Dict[str, Any]:
        """Create a new virtual environment"""
        result = {
            "success": False,
            "output": "",
            "error": None
        }
        
        try:
            cmd = [python_executable, "-m", "venv", venv_path]
            logger.info(f"Creating venv at: {venv_path}")
            
            process = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120
            )
            
            result["output"] = process.stdout
            result["success"] = process.returncode == 0
            
            if not result["success"]:
                result["error"] = process.stderr
                logger.error(f"Failed to create venv: {process.stderr}")
            else:
                logger.info(f"Successfully created venv at: {venv_path}")
                
        except Exception as e:
            result["error"] = str(e)
            logger.error(f"Error creating venv: {e}")
        
        return result


class PlatformResolver:
    """Intelligent platform detection and PyTorch setup"""
    
    @staticmethod
    def detect_hardware() -> Dict[str, Any]:
        """Detect available hardware acceleration"""
        import torch
        
        hardware_info = {
            "platform": platform.system(),
            "architecture": platform.machine(),
            "has_cuda": False,
            "has_mps": False,
            "has_metal": False,
            "cuda_version": None,
            "recommended_torch_index": None,
            "recommended_install_cmd": None
        }
        
        # Check CUDA
        if torch.cuda.is_available():
            hardware_info["has_cuda"] = True
            hardware_info["cuda_version"] = torch.version.cuda
            hardware_info["recommended_torch_index"] = "cu118"  # Default to CUDA 11.8
        # Check MPS (Apple Silicon)
        elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
            hardware_info["has_mps"] = True
            hardware_info["recommended_torch_index"] = "cpu"  # MPS works with CPU-built PyTorch
        # Check METAL (older macOS)
        elif platform.system() == "Darwin":
            hardware_info["has_metal"] = True
            hardware_info["recommended_torch_index"] = "cpu"
        else:
            hardware_info["recommended_torch_index"] = "cpu"
        
        return hardware_info
    
    @staticmethod
    def resolve_pytorch_install(env_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Intelligently resolve PyTorch installation for the current platform.
        
        Returns dict with success status, device type, and installation info
        """
        logger.info("🔍 Resolving PyTorch for platform...")
        
        system = platform.system()
        machine = platform.machine().lower()
        
        result = {
            "success": False,
            "device": None,
            "pytorch_installed": False,
            "package_spec": None,
            "install_cmd": None,
            "reason": None
        }
        
        # Check if PyTorch is already installed
        pkg_check = PackageManager.check_package_installed("torch")
        if pkg_check["installed"]:
            logger.info(f"✅ PyTorch already installed: {pkg_check['version']}")
            result["pytorch_installed"] = True
            
            # Detect which device is available
            try:
                import torch
                if torch.cuda.is_available():
                    result["device"] = "cuda"
                    result["reason"] = "CUDA available"
                elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
                    result["device"] = "mps"
                    result["reason"] = "Apple MPS available"
                else:
                    result["device"] = "cpu"
                    result["reason"] = "Using CPU fallback"
                result["success"] = True
                return result
            except Exception as e:
                logger.warning(f"Failed to detect device: {e}")
                result["device"] = "cpu"
                result["success"] = True
                return result
        
        # PyTorch not installed - determine best variant for platform
        logger.info(f"📦 PyTorch not installed. Platform: {system} ({machine})")
        
        if system == "Darwin":
            # macOS
            if 'arm' in machine or 'aarch64' in machine:
                # Apple Silicon - use CPU build with MPS support
                logger.info("🍎 Apple Silicon detected - installing PyTorch with MPS support")
                result["package_spec"] = "torch torchvision torchaudio"
                result["install_cmd"] = f"{sys.executable} -m pip install torch torchvision torchaudio"
                result["device"] = "mps"
                result["reason"] = "Installing CPU variant with MPS acceleration"
            else:
                # Intel macOS
                logger.info("🍎 Intel macOS detected")
                result["package_spec"] = "torch torchvision torchaudio"
                result["install_cmd"] = f"{sys.executable} -m pip install torch torchvision torchaudio"
                result["device"] = "cpu"
                result["reason"] = "Installing CPU variant"
        
        elif system == "Linux":
            # Check for NVIDIA GPU
            try:
                result_nvidia = subprocess.run(
                    ['nvidia-smi'], 
                    capture_output=True, 
                    timeout=5
                )
                if result_nvidia.returncode == 0:
                    logger.info("🖥️  NVIDIA GPU detected - installing PyTorch with CUDA")
                    result["package_spec"] = "torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118"
                    result["install_cmd"] = f"{sys.executable} -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118"
                    result["device"] = "cuda"
                    result["reason"] = "NVIDIA GPU with CUDA 11.8"
                else:
                    raise FileNotFoundError
            except (FileNotFoundError, subprocess.TimeoutExpired):
                logger.info("💻 No NVIDIA GPU detected - using CPU")
                result["package_spec"] = "torch torchvision torchaudio"
                result["install_cmd"] = f"{sys.executable} -m pip install torch torchvision torchaudio"
                result["device"] = "cpu"
                result["reason"] = "CPU only"
        
        elif system == "Windows":
            # Check for NVIDIA GPU
            try:
                result_nvidia = subprocess.run(
                    ['nvidia-smi'], 
                    capture_output=True, 
                    timeout=5
                )
                if result_nvidia.returncode == 0:
                    logger.info("🖥️  NVIDIA GPU detected - installing PyTorch with CUDA")
                    result["package_spec"] = "torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118"
                    result["install_cmd"] = f"{sys.executable} -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118"
                    result["device"] = "cuda"
                    result["reason"] = "NVIDIA GPU with CUDA 11.8"
                else:
                    raise FileNotFoundError
            except (FileNotFoundError, subprocess.TimeoutExpired):
                logger.info("💻 No NVIDIA GPU detected - using CPU")
                result["package_spec"] = "torch torchvision torchaudio"
                result["install_cmd"] = f"{sys.executable} -m pip install torch torchvision torchaudio"
                result["device"] = "cpu"
                result["reason"] = "CPU only"
        
        else:
            # Unknown platform - fallback to CPU
            logger.warning(f"⚠️  Unknown platform: {system} - using CPU")
            result["package_spec"] = "torch torchvision torchaudio"
            result["install_cmd"] = f"{sys.executable} -m pip install torch torchvision torchaudio"
            result["device"] = "cpu"
            result["reason"] = "Unknown platform - CPU fallback"
        
        result["success"] = bool(result["install_cmd"])
        return result
    
    @staticmethod
    def install_pytorch_for_platform() -> Dict[str, Any]:
        """Install PyTorch appropriate for this platform"""
        resolution = PlatformResolver.resolve_pytorch_install()
        
        if resolution["pytorch_installed"]:
            logger.info(f"✅ PyTorch ready: device={resolution['device']}")
            return {
                "success": True,
                "device": resolution["device"],
                "reason": resolution["reason"]
            }
        
        if not resolution["install_cmd"]:
            return {
                "success": False,
                "error": "Could not determine PyTorch installation command"
            }
        
        logger.info(f"📦 Installing PyTorch: {resolution['reason']}")
        logger.info(f"   Command: {resolution['install_cmd']}")
        
        try:
            result = subprocess.run(
                resolution["install_cmd"],
                shell=True,
                capture_output=True,
                text=True,
                check=True,
                timeout=600  # 10 minutes timeout
            )
            
            logger.info(f"✅ PyTorch installed successfully for device: {resolution['device']}")
            return {
                "success": True,
                "device": resolution["device"],
                "reason": resolution["reason"]
            }
        
        except subprocess.TimeoutExpired:
            logger.error("❌ PyTorch installation timed out (10 minutes)")
            return {
                "success": False,
                "error": "Installation timeout",
                "device": resolution["device"]
            }
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ PyTorch installation failed: {e.stderr}")
            return {
                "success": False,
                "error": e.stderr or str(e),
                "device": resolution["device"]
            }
        except Exception as e:
            logger.error(f"❌ PyTorch installation error: {e}")
            return {
                "success": False,
                "error": str(e),
                "device": resolution["device"]
            }


class TrainingAgent:
    """
    Training agent that executes remote training tasks.
    
    The agent:
    1. Authenticates with Firebase using API key
    2. Registers itself in Firestore /agents/{agentId}
    3. Listens for tasks in /training_tasks collection
    4. Claims and executes tasks
    5. Reports progress and results back to Firestore
    """
    
    def __init__(
        self,
        authenticator: Optional[AgentAuthenticator] = None,
        work_dir: Optional[Path] = None
    ):
        """
        Initialize training agent.
        
        Args:
            authenticator: AgentAuthenticator instance (creates default if None)
            work_dir: Working directory for downloads and training
        """
        self.authenticator = authenticator or AgentAuthenticator()
        self.work_dir = work_dir or Path.home() / ".aegis-vision" / "agent-work"
        self.work_dir.mkdir(parents=True, exist_ok=True)
        
        self.agent_id = self.authenticator.get_agent_id()
        self.firestore_project = self.authenticator.get_firestore_project()
        
        # Firebase Admin SDK for all Firestore operations
        # Uses on_snapshot() for real-time listeners (cost-efficient, <1s latency)
        self.app: Optional[Any] = None
        self.db: Optional[Any] = None  # Admin SDK Firestore client
        
        # Agent state
        self.capabilities = AgentCapabilities.detect()
        self.running = False
        self.current_task: Optional[str] = None
        self.task_listener = None
        self.command_listener = None
        self.package_manager = PackageManager()
        self.detected_device = None # Initialize detected_device
        self.seen_task_ids: set = set()  # Track tasks already processed to prevent duplicates
        
        # Token management for Firestore Client
        self.id_token = None
        self.refresh_token = None
        self.token_expiry = 0
        
        logger.info(f"Agent initialized: {self.agent_id}")
        logger.info(f"Work directory: {self.work_dir}")
    
    def initialize_firebase(self) -> None:
        """Initialize Firestore using custom token from Cloud Function
        
        The authentication flow:
        1. API key (permanent, user-controlled) → stored in agent-config.json
        2. Custom token (1-hour expiry) → auto-refreshed by AgentAuthenticator
        3. ID token (1-hour expiry) → auto-refreshed using refresh token
        4. OAuth2 credentials → recreated with refreshed ID token
        
        The user only needs to create the API key once in the web UI.
        All token refreshes happen automatically without user intervention.
        """
        try:
            # Get custom token from Cloud Function (uses permanent API key)
            custom_token = self.authenticator.authenticate()
            logger.info("Successfully obtained Firebase custom token")
            
            # Initialize Firestore client with custom token
            # We use google-cloud-firestore which supports on_snapshot()
            from google.cloud import firestore
            from google.oauth2 import credentials as oauth_credentials
            import requests
            import time
            
            # Exchange custom token for ID token + refresh token
            logger.info("Exchanging custom token for OAuth2 credentials...")
            
            api_key = os.environ.get(
                'FIREBASE_API_KEY',
                'AIzaSyBQl6-_h7qZ9Y2MGM_QQOX1ylydToydTSY'
            )
            
            url = "https://identitytoolkit.googleapis.com/v1/accounts:signInWithCustomToken"
            response = requests.post(url, json={
                'token': custom_token,
                'returnSecureToken': True
            }, params={'key': api_key}, timeout=30)
            
            if response.status_code != 200:
                raise Exception(f"Token exchange failed: {response.text}")
            
            data = response.json()
            self.id_token = data['idToken']
            self.refresh_token = data.get('refreshToken')  # Save for auto-refresh
            
            # ID tokens expire after 1 hour
            expires_in = int(data.get('expiresIn', 3600))
            self.token_expiry = time.time() + expires_in
            
            # Create OAuth2 credentials from ID token
            creds = oauth_credentials.Credentials(token=self.id_token)
            
            # Create Firestore client with custom credentials
            self.db = firestore.Client(
                project=self.firestore_project,
                credentials=creds
            )
            
            logger.info("✅ Firestore initialized successfully")
            logger.info("   Package: google-cloud-firestore")
            logger.info("   Authentication: API key (permanent) → Custom token → ID token")
            logger.info("   Token Refresh: Automatic using refresh token")
            logger.info("   Features: Real-time listeners (on_snapshot)")
            logger.info("   Cost: ~$0.047/agent/month | Latency: <1 second")
            
        except Exception as e:
            logger.error(f"Failed to initialize Firestore: {e}")
            raise AgentAuthenticationError(f"Firestore initialization failed: {e}")
    
    def register_agent(self) -> None:
        """Register agent in Firestore with startup validation"""
        try:
            # Validate training scripts before registering
            scripts_valid = self._validate_training_scripts()
            
            # Detect platform and hardware info
            hardware_info = PlatformResolver.detect_hardware()
            
            # Check if agent document already exists
            agent_ref = self.db.collection("agents").document(self.agent_id)
            existing_doc = agent_ref.get()
            
            if existing_doc.exists:
                # Agent re-registering (restart) - only update dynamic fields
                logger.info(f"Agent {self.agent_id} already registered, updating status...")
                agent_doc = {
                    "status": "online",
                    "lastSeen": "SERVER_TIMESTAMP",
                    "capabilities": self.capabilities,
                    "hardwareInfo": hardware_info,
                    "currentTask": None,
                    "heartbeat": "SERVER_TIMESTAMP",
                    "scriptsValid": scripts_valid,
                    "lastValidationAt": "SERVER_TIMESTAMP"
                }
            else:
                # First-time registration - include all fields
                logger.info(f"Registering new agent: {self.agent_id}")
                agent_doc = {
                    "agentId": self.agent_id,
                    "agentName": self.authenticator.config.get("agentName", f"Agent {self.agent_id[:8]}"),
                    "ownerUid": self.authenticator.config.get("ownerUid", ""),
                    "status": "online",
                    "lastSeen": "SERVER_TIMESTAMP",
                    "capabilities": self.capabilities,
                    "hardwareInfo": hardware_info,
                    "currentTask": None,
                    "heartbeat": "SERVER_TIMESTAMP",
                    "registeredAt": "SERVER_TIMESTAMP",  # Only set on first registration
                    "scriptsValid": scripts_valid,
                    "lastValidationAt": "SERVER_TIMESTAMP"
                }
            
            agent_ref.set(agent_doc, merge=True)
            
            logger.info(f"Agent registered successfully: {self.agent_id}")
            logger.info(f"  Hardware: {hardware_info.get('platform')} ({hardware_info.get('architecture')})")
            if hardware_info.get('has_cuda'):
                logger.info(f"  CUDA: {hardware_info.get('cuda_version')}")
            if hardware_info.get('has_mps'):
                logger.info("  MPS: Available (Apple Silicon)")
            
            if scripts_valid:
                logger.info("✅ Training scripts validated successfully")
            else:
                logger.warning("⚠️  Training scripts validation failed - agent will not accept tasks")
            
            # Clean up orphaned tasks from previous run
            self._recover_orphaned_tasks()
            
        except Exception as e:
            logger.error(f"Failed to register agent: {e}")
            raise
    
    def _validate_training_scripts(self) -> bool:
        """
        Validate that training scripts exist and are executable
        
        Returns:
            True if scripts are valid, False otherwise
        """
        try:
            from pathlib import Path
            
            # Check for training_script.py
            script_path = Path(__file__).parent / "training_script.py"
            
            if not script_path.exists():
                logger.error(f"❌ Training script not found: {script_path}")
                return False
            
            # Check if file is readable
            if not script_path.is_file():
                logger.error(f"❌ Training script is not a file: {script_path}")
                return False
            
            # Try to read the script to ensure it's valid
            try:
                with open(script_path, 'r') as f:
                    content = f.read()
                    
                # Basic validation - check for main function
                if 'def main()' not in content:
                    logger.error("❌ Training script missing main() function")
                    return False
                    
                # Check for required imports
                required_imports = ['aegis_vision', 'YOLOTrainer']
                for imp in required_imports:
                    if imp not in content:
                        logger.warning(f"⚠️  Training script missing import: {imp}")
                
                logger.info(f"✅ Training script validated: {script_path}")
                logger.info(f"   Size: {len(content)} bytes")
                return True
                
            except Exception as e:
                logger.error(f"❌ Failed to read training script: {e}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Training script validation failed: {e}")
            return False
    
    def _recover_orphaned_tasks(self) -> None:
        """
        Recover tasks that were interrupted when agent crashed or stopped.
        Mark them as failed so they don't show as active.
        """
        try:
            logger.info("🔍 Checking for orphaned tasks from previous run...")
            
            # Find tasks assigned to this agent that are not in terminal state
            # NOTE: REST API client uses simplified query syntax without FieldFilter
            
            # Check for tasks in 'assigned' or 'running' state assigned to this agent
            active_statuses = ['assigned', 'running']
            
            for status in active_statuses:
                tasks_ref = self.db.collection("training_tasks").where(
                    "assignedTo", "==", self.agent_id
                ).where(
                    "status", "==", status
                )
                
                orphaned_tasks = list(tasks_ref.stream())
                
                if orphaned_tasks:
                    logger.warning(f"⚠️  Found {len(orphaned_tasks)} orphaned task(s) in '{status}' state")
                    
                    for task_doc in orphaned_tasks:
                        task_id = task_doc.id
                        task_data = task_doc.to_dict()
                        
                        logger.warning(f"⚠️  Recovering orphaned task: {task_id}")
                        logger.info(f"   Original status: {status}")
                        logger.info(f"   Created at: {task_data.get('createdAt', 'unknown')}")
                        
                        # Mark as failed with recovery message
                        try:
                            self.db.collection("training_tasks").document(task_id).update({
                                "status": "failed",
                                "error": "Agent interrupted - task was orphaned during agent restart",
                                "failedAt": "SERVER_TIMESTAMP",
                                "recoveredBy": self.agent_id,
                                "originalStatus": status,
                                "recoveryReason": "agent_restart"
                            })
                            
                            # Add log entry
                            self._append_log(
                                task_id, 
                                "warning", 
                                f"⚠️  Task recovered after agent restart - marked as failed. Original status: {status}"
                            )
                            
                            logger.info(f"✅ Task {task_id} marked as failed (orphaned recovery)")
                            
                        except Exception as e:
                            logger.error(f"❌ Failed to recover task {task_id}: {e}")
            
            # Also check local persistent state file if it exists
            self._clean_local_task_state()
            
            logger.info("✅ Orphaned task recovery complete")
            
        except Exception as e:
            logger.error(f"❌ Orphaned task recovery failed: {e}")
            # Don't raise - this is not critical for agent startup
    
    def _clean_local_task_state(self) -> None:
        """
        Clean up local persistent task state file.
        Remove any tasks that are in active state since agent just started.
        """
        try:
            state_file = self.work_dir / "task_state.json"
            
            if not state_file.exists():
                logger.info("ℹ️  No local task state file found - clean start")
                return
            
            logger.info(f"🔍 Checking local task state: {state_file}")
            
            import json
            
            with open(state_file, 'r') as f:
                state_data = json.load(f)
            
            active_tasks = state_data.get('active_tasks', [])
            
            if active_tasks:
                logger.warning(f"⚠️  Found {len(active_tasks)} task(s) in local state")
                
                # Clear active tasks since agent just started
                state_data['active_tasks'] = []
                state_data['last_cleanup'] = datetime.now().isoformat()
                state_data['cleanup_reason'] = 'agent_restart'
                
                # Archive old active tasks
                if 'archived_tasks' not in state_data:
                    state_data['archived_tasks'] = []
                
                for task_id in active_tasks:
                    state_data['archived_tasks'].append({
                        'task_id': task_id,
                        'archived_at': datetime.now().isoformat(),
                        'reason': 'agent_restart'
                    })
                    logger.info(f"   Archived task from local state: {task_id}")
                
                # Write updated state
                with open(state_file, 'w') as f:
                    json.dump(state_data, f, indent=2)
                
                logger.info("✅ Local task state cleaned up")
            else:
                logger.info("✅ Local task state is clean - no active tasks")
                
        except Exception as e:
            logger.warning(f"⚠️  Failed to clean local task state: {e}")
            # Don't raise - this is not critical
    
    def update_heartbeat(self) -> None:
        """Update agent heartbeat and refresh token if needed"""
        try:
            # Check if token needs refresh (5 minutes before expiry)
            import time
            if time.time() >= (self.token_expiry - 300):  # 5 minutes before expiry
                self._refresh_firebase_token()
            
            heartbeat_data = {
                "heartbeat": "SERVER_TIMESTAMP",
                "lastSeen": "SERVER_TIMESTAMP",
                "status": "training" if self.current_task else "online"
            }
            
            # Include detected device if available
            if self.detected_device:
                heartbeat_data["currentDevice"] = self.detected_device
            
            self.db.collection("agents").document(self.agent_id).update(heartbeat_data)
        except Exception as e:
            logger.warning(f"Failed to update heartbeat: {e}")
    
    def _refresh_firebase_token(self) -> None:
        """Refresh Firebase ID token using refresh token
        
        This is called automatically before the token expires.
        Uses the permanent API key to get a new custom token if refresh fails.
        """
        try:
            import requests
            import time
            from google.oauth2 import credentials as oauth_credentials
            
            logger.info("🔄 Refreshing Firebase token...")
            
            if self.refresh_token:
                # Try to refresh using refresh token first
                api_key = os.environ.get(
                    'FIREBASE_API_KEY',
                    'AIzaSyBQl6-_h7qZ9Y2MGM_QQOX1ylydToydTSY'
                )
                
                url = "https://securetoken.googleapis.com/v1/token"
                response = requests.post(url, json={
                    'grant_type': 'refresh_token',
                    'refresh_token': self.refresh_token
                }, params={'key': api_key}, timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    self.id_token = data['id_token']
                    self.refresh_token = data['refresh_token']
                    
                    expires_in = int(data.get('expires_in', 3600))
                    self.token_expiry = time.time() + expires_in
                    
                    # Update Firestore client credentials
                    from google.cloud import firestore
                    creds = oauth_credentials.Credentials(token=self.id_token)
                    self.db = firestore.Client(
                        project=self.firestore_project,
                        credentials=creds
                    )
                    
                    logger.info("✅ Token refreshed successfully")
                    return
            
            # Fallback: Re-exchange custom token (which uses permanent API key)
            logger.info("Using fallback: re-exchanging custom token...")
            custom_token = self.authenticator.authenticate()
            
            api_key = os.environ.get(
                'FIREBASE_API_KEY',
                'AIzaSyBQl6-_h7qZ9Y2MGM_QQOX1ylydToydTSY'
            )
            
            url = "https://identitytoolkit.googleapis.com/v1/accounts:signInWithCustomToken"
            response = requests.post(url, json={
                'token': custom_token,
                'returnSecureToken': True
            }, params={'key': api_key}, timeout=30)
            
            if response.status_code != 200:
                raise Exception(f"Token exchange failed: {response.text}")
            
            data = response.json()
            self.id_token = data['idToken']
            self.refresh_token = data.get('refreshToken')
            
            expires_in = int(data.get('expiresIn', 3600))
            self.token_expiry = time.time() + expires_in
            
            # Update Firestore client credentials
            from google.cloud import firestore
            creds = oauth_credentials.Credentials(token=self.id_token)
            self.db = firestore.Client(
                project=self.firestore_project,
                credentials=creds
            )
            
            logger.info("✅ Token refreshed successfully (via custom token)")
            
        except Exception as e:
            logger.error(f"❌ Failed to refresh token: {e}")
            logger.error("Agent will continue but may lose Firestore access")
    
    def listen_for_tasks(self, callback: Callable[[Dict[str, Any]], None]) -> None:
        """
        Listen for pending training tasks using real-time listeners.
        Only listens for tasks that are unassigned or assigned to this agent.
        
        Args:
            callback: Function to call when a task is available
        """
        def on_snapshot(doc_snapshot, changes, read_time):
            for change in changes:
                if change.type.name in ['ADDED', 'MODIFIED']:
                    task_data = change.document.to_dict()
                    task_id = change.document.id
                    
                    # Check if task is pending and either unassigned or assigned to this agent
                    if task_data.get('status') == 'pending':
                        assigned_to = task_data.get('assignedTo')
                        
                        # Only process if unassigned OR assigned to this agent
                        if not assigned_to or assigned_to == self.agent_id:
                            if self._can_handle_task(task_data):
                                logger.info(f"📋 Found pending task: {task_id}")
                                callback({**task_data, 'taskId': task_id})
                        else:
                            logger.debug(f"Skipping task {task_id} - assigned to different agent: {assigned_to}")
        
        # Query for pending tasks (includes both unassigned and tasks assigned to this agent)
        from google.cloud.firestore_v1 import FieldFilter
        query = self.db.collection("training_tasks").where(filter=FieldFilter("status", "==", "pending"))
        
        # Start listening
        self.task_listener = query.on_snapshot(on_snapshot)
        logger.info("✅ Started listening for training tasks (real-time)")
    
    def _can_handle_task(self, task: Dict[str, Any]) -> bool:
        """Check if agent can handle the task based on requirements"""
        config = task.get('config', {})
        
        # Check storage requirements (rough estimate: dataset + model)
        required_storage_gb = config.get('requiredStorageGB', 10)
        if self.capabilities['availableStorageGB'] < required_storage_gb:
            logger.warning(f"Insufficient storage: need {required_storage_gb}GB, have {self.capabilities['availableStorageGB']}GB")
            return False
        
        # Check memory requirements
        required_memory_gb = config.get('requiredMemoryGB', 8)
        if self.capabilities['totalMemoryGB'] < required_memory_gb:
            logger.warning(f"Insufficient memory: need {required_memory_gb}GB, have {self.capabilities['totalMemoryGB']}GB")
            return False
        
        # Check GPU requirements
        if config.get('requiresGPU', False) and not self.capabilities['hasGPU']:
            logger.warning("Task requires GPU but agent has none")
            return False
        
        return True
    
    def claim_task(self, task_id: str) -> bool:
        """
        Attempt to claim a task atomically.
        Uses optimistic locking: read current status, then update only if still pending.
        
        Only claims tasks that are:
        1. In 'pending' status, AND
        2. Either unassigned OR already assigned to this agent
        
        Args:
            task_id: Task ID to claim
            
        Returns:
            True if successfully claimed, False otherwise
        """
        try:
            task_ref = self.db.collection("training_tasks").document(task_id)
            
            # Read current task state
            snapshot = task_ref.get()
            if not snapshot.exists:
                logger.warning(f"Task {task_id} not found")
                return False
            
            task_data = snapshot.to_dict()
            
            # Check status
            if task_data.get('status') != 'pending':
                logger.debug(f"Task {task_id} no longer pending (status: {task_data.get('status')})")
                return False
            
            # Check assignment - only claim if unassigned or assigned to this agent
            assigned_to = task_data.get('assignedTo')
            if assigned_to and assigned_to != self.agent_id:
                logger.debug(f"Task {task_id} is assigned to different agent: {assigned_to}")
                return False
            
            # Attempt to claim (optimistic update)
            # If another agent claims between read and write, Firestore security rules
            # will prevent the update or we'll detect it in the verification below
            task_ref.update({
                'status': 'assigned',
                'assignedTo': self.agent_id,
                'assignedAt': "SERVER_TIMESTAMP"
            })
            
            # Verify we actually got it (double-check)
            updated_snapshot = task_ref.get()
            if updated_snapshot.exists:
                updated_data = updated_snapshot.to_dict()
                if updated_data.get('assignedTo') == self.agent_id:
                    logger.info(f"✅ Successfully claimed task: {task_id}")
                    self.current_task = task_id
                    
                    # Update agent status
                    self.db.collection("agents").document(self.agent_id).update({
                        "currentTask": {
                            "taskId": task_id,
                            "status": "assigned",
                            "startedAt": "SERVER_TIMESTAMP"
                        }
                    })
                    return True
                else:
                    logger.debug(f"Task {task_id} claimed by another agent: {updated_data.get('assignedTo')}")
                    return False
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to claim task {task_id}: {e}")
            return False
    
    def listen_for_commands(self) -> None:
        """
        Listen for package management and configuration commands using real-time listeners.
        """
        def on_command_snapshot(doc_snapshot, changes, read_time):
            for change in changes:
                if change.type.name in ['ADDED', 'MODIFIED']:
                    command_data = change.document.to_dict()
                    command_id = change.document.id
                    
                    # Check if command is pending
                    if command_data.get('status') == 'pending':
                        logger.info(f"📦 Received command: {command_id} - {command_data.get('type')}")
                        self._handle_command(command_id, command_data)
        
        # Listen for commands addressed to this agent
        from google.cloud.firestore_v1 import FieldFilter
        query = self.db.collection("agent_commands") \
            .where(filter=FieldFilter("agentId", "==", self.agent_id)) \
            .where(filter=FieldFilter("status", "==", "pending"))
        
        # Start listening
        self.command_listener = query.on_snapshot(on_command_snapshot)
        logger.info("✅ Started listening for agent commands (real-time)")
    
    def _handle_command(self, command_id: str, command_data: Dict[str, Any]) -> None:
        """Handle a package management or configuration command"""
        try:
            command_type = command_data.get('type')
            params = command_data.get('params', {})
            
            # Update command status to processing
            self._update_command_status(command_id, "processing")
            
            result = None
            if command_type == "check_package":
                result = self.package_manager.check_package_installed(params.get('package'))
            elif command_type == "install_package":
                result = self.package_manager.install_package(
                    params.get('package'),
                    params.get('envType', 'current'),
                    params.get('envName')
                )
            elif command_type == "create_conda_env":
                result = self.package_manager.create_conda_env(
                    params.get('envName'),
                    params.get('pythonVersion', '3.10')
                )
            elif command_type == "create_venv":
                result = self.package_manager.create_venv(
                    params.get('venvPath'),
                    params.get('pythonExecutable', sys.executable)
                )
            elif command_type == "refresh_capabilities":
                # Re-detect capabilities
                self.capabilities = AgentCapabilities.detect()
                result = {"success": True, "capabilities": self.capabilities}
                # Update agent document with new capabilities
                self.db.collection("agents").document(self.agent_id).update({
                    "capabilities": self.capabilities
                })
            else:
                result = {"success": False, "error": f"Unknown command type: {command_type}"}
            
            # Update command with result
            self._update_command_status(command_id, "completed", result)
            logger.info(f"Command {command_id} completed successfully")
            
        except Exception as e:
            logger.error(f"Failed to handle command {command_id}: {e}")
            self._update_command_status(command_id, "failed", {"error": str(e)})
    
    def _update_command_status(self, command_id: str, status: str, result: Optional[Dict[str, Any]] = None) -> None:
        """Update command status in Firestore"""
        try:
            update_data = {
                "status": status,
                "updatedAt": "SERVER_TIMESTAMP"
            }
            if result:
                update_data["result"] = result
            
            self.db.collection("agent_commands").document(command_id).update(update_data)
        except Exception as e:
            logger.error(f"Failed to update command status: {e}")
    
    def execute_task(self, task_id: str) -> None:
        """
        Execute a training task.
        
        Args:
            task_id: Task ID to execute
        """
        try:
            # Get task details
            task_doc = self.db.collection("training_tasks").document(task_id).get()
            if not task_doc.exists:
                raise ValueError(f"Task {task_id} not found")
            
            task_data = task_doc.to_dict()
            config = task_data['config']
            
            logger.info(f"Starting task execution: {task_id}")
            self._append_log(task_id, "info", f"Task claimed by agent {self.agent_id}")
            
            # DEBUG: Log what we received from Firestore
            self._append_log(task_id, "info", f"🔍 DEBUG: Received config from Firestore with keys: {list(config.keys())}")
            self._append_log(task_id, "info", f"🔍 DEBUG: config['epochs'] = {config.get('epochs', 'NOT FOUND')}")
            
            # Update status to running with additional metadata
            self._update_task_status(task_id, "running", {
                "assignedTo": self.agent_id,
                "agentName": self.authenticator.config.get("agentName", f"Agent {self.agent_id[:8]}"),
                "startedAt": "SERVER_TIMESTAMP",
                "trainingType": config.get('trainingType', 'agent_training'),  # agent_training vs kaggle
                "modelVariant": config.get('model', config.get('model_variant', 'yolo11n')),
                "totalEpochs": config.get('epochs', 100),
                "platform": self.capabilities.get('platform', 'unknown'),
                "device": self.detected_device or 'cpu',
            })
            
            # Validate environment
            self._append_log(task_id, "info", "Validating environment...")
            self._validate_environment(task_id, config)
            
            # Prepare dataset
            self._append_log(task_id, "info", "Preparing dataset...")
            dataset_dir = self._prepare_dataset(task_id, config)
            
            # Execute training using training script
            self._append_log(task_id, "info", "Starting training...")
            model_path = self._run_training_script(task_id, config, dataset_dir)
            
            # Upload model
            self._append_log(task_id, "info", "Uploading trained model...")
            model_url = self._upload_model(task_id, model_path)
            
            # Mark as completed with final metadata
            self._update_task_status(task_id, "completed", {
                "modelUrl": model_url,
                "completedAt": "SERVER_TIMESTAMP",
                "assignedTo": self.agent_id,
                "agentName": self.authenticator.config.get("agentName", f"Agent {self.agent_id[:8]}"),
                "trainingType": config.get('trainingType', 'agent_training'),
            })
            
            self._append_log(task_id, "info", f"Task completed successfully! Model: {model_url}")
            logger.info(f"Task {task_id} completed successfully")
            
        except Exception as e:
            logger.error(f"Task {task_id} failed: {e}")
            self._append_log(task_id, "error", f"Task failed: {str(e)}")
            
            # Update with error status and metadata
            self._update_task_status(task_id, "failed", {
                "error": str(e),
                "assignedTo": self.agent_id,
                "agentName": self.authenticator.config.get("agentName", f"Agent {self.agent_id[:8]}"),
                "failedAt": "SERVER_TIMESTAMP",
                "trainingType": self.current_task_config.get('trainingType', 'agent_training') if hasattr(self, 'current_task_config') else 'agent_training',
            })
        
        finally:
            # Clear current task
            self.current_task = None
            
            # Remove from seen tasks to allow retry if it becomes pending again
            if task_id in self.seen_task_ids:
                self.seen_task_ids.remove(task_id)
            
            self.db.collection("agents").document(self.agent_id).update({
                "currentTask": None,
                "status": "online"
            })
    
    def _validate_environment(self, task_id: str, config: Dict[str, Any]) -> None:
        """Validate that environment meets requirements"""
        # 1. Proactively resolve and install PyTorch for this platform
        logger.info("🔧 Step 1: Validating PyTorch installation...")
        self._append_log(task_id, "info", "🔧 Step 1/3: Validating PyTorch installation...")
        
        pytorch_result = PlatformResolver.install_pytorch_for_platform()
        
        if not pytorch_result["success"]:
            error_msg = pytorch_result.get("error", "Unknown PyTorch installation error")
            logger.error(f"❌ PyTorch setup failed: {error_msg}")
            self._append_log(task_id, "error", f"❌ PyTorch setup failed: {error_msg}")
            raise RuntimeError(f"PyTorch installation failed: {error_msg}")
        
        device_type = pytorch_result.get("device", "cpu")
        reason = pytorch_result.get("reason", "")
        logger.info(f"✅ PyTorch ready: device={device_type} ({reason})")
        self._append_log(task_id, "info", f"✅ PyTorch ready: device={device_type}")
        self._append_log(task_id, "info", f"   Reason: {reason}")
        
        # Store detected device for later use in training
        self.detected_device = device_type
        
        # 2. Check YOLO installation
        logger.info("🔧 Step 2: Validating Ultralytics installation...")
        self._append_log(task_id, "info", "🔧 Step 2/3: Validating Ultralytics installation...")
        
        try:
            from ultralytics import YOLO
            logger.info("✅ Ultralytics (YOLO) is installed")
            self._append_log(task_id, "info", "✅ Ultralytics (YOLO) is installed")
        except ImportError:
            logger.error("❌ ultralytics not installed")
            self._append_log(task_id, "error", "❌ Ultralytics not installed. Run: pip install ultralytics")
            raise RuntimeError("ultralytics not installed. Run: pip install ultralytics")
        
        # 3. Check disk space
        logger.info("🔧 Step 3: Validating disk space...")
        self._append_log(task_id, "info", "🔧 Step 3/3: Validating disk space...")
        
        free_space_gb = psutil.disk_usage(str(self.work_dir)).free / (1024**3)
        required_space = config.get('requiredStorageGB', 10)
        
        if free_space_gb < required_space:
            error_msg = f"Insufficient disk space: {free_space_gb:.1f}GB available, {required_space}GB required"
            logger.error(error_msg)
            self._append_log(task_id, "error", f"❌ {error_msg}")
            raise RuntimeError(error_msg)
        
        logger.info(f"✅ Disk space OK: {free_space_gb:.1f}GB available (need {required_space}GB)")
        self._append_log(task_id, "info", f"✅ Disk space OK: {free_space_gb:.1f}GB available")
        self._append_log(task_id, "info", "✅ Environment validation complete! Ready to train.")
        logger.info("✅ Environment validation complete")
    
    def _find_dataset_yaml(self, directory: Path) -> Optional[Path]:
        """
        Find dataset.yaml file in the directory or its subdirectories.
        
        Args:
            directory: Directory to search in
            
        Returns:
            Path to dataset.yaml if found, None otherwise
        """
        # Check root directory first
        yaml_path = directory / "dataset.yaml"
        if yaml_path.exists():
            return yaml_path
        
        # Check subdirectories (common for Kaggle datasets)
        for subdir in directory.iterdir():
            if subdir.is_dir():
                yaml_path = subdir / "dataset.yaml"
                if yaml_path.exists():
                    return yaml_path
                
                # Check one more level deep
                for subsubdir in subdir.iterdir():
                    if subsubdir.is_dir():
                        yaml_path = subsubdir / "dataset.yaml"
                        if yaml_path.exists():
                            return yaml_path
        
        return None
    
    def _prepare_dataset(self, task_id: str, config: Dict[str, Any]) -> Path:
        """Prepare dataset for training"""
        dataset_source = config.get('datasetSource', 'local')
        
        if dataset_source == 'local':
            dataset_path = Path(config.get('datasetPath', ''))
            if not dataset_path.exists():
                raise ValueError(f"Local dataset not found: {dataset_path}")
            return dataset_path
        
        elif dataset_source == 'kaggle':
            # Download dataset from Kaggle
            dataset_id = config.get('datasetPath')
            if not dataset_id:
                raise ValueError("Kaggle dataset ID not provided")
            
            # Create dataset cache directory
            datasets_dir = self.work_dir / "datasets"
            datasets_dir.mkdir(parents=True, exist_ok=True)
            
            # Use dataset name as folder (replace / with -)
            dataset_folder = dataset_id.replace('/', '-')
            dataset_cache_dir = datasets_dir / dataset_folder
            
            # Check if already downloaded
            if dataset_cache_dir.exists() and any(dataset_cache_dir.iterdir()):
                self._append_log(task_id, "info", f"Using cached dataset: {dataset_id}")
                return dataset_cache_dir
            
            # Download from Kaggle
            self._append_log(task_id, "info", f"Downloading dataset from Kaggle: {dataset_id}")
            dataset_cache_dir.mkdir(parents=True, exist_ok=True)
            
            try:
                import subprocess
                import os
                
                # Set up Kaggle credentials from config (if provided)
                env = os.environ.copy()
                kaggle_username = config.get('kaggleUsername', config.get('kaggle_username'))
                kaggle_api_key = config.get('kaggleApiKey', config.get('kaggle_api_key'))
                
                if kaggle_username and kaggle_api_key:
                    env['KAGGLE_USERNAME'] = kaggle_username
                    env['KAGGLE_KEY'] = kaggle_api_key
                    self._append_log(task_id, "info", f"✅ Using Kaggle credentials from task config (user: {kaggle_username})")
                else:
                    # Kaggle credentials not provided in task config
                    # Check if ~/.kaggle/kaggle.json exists as fallback
                    kaggle_config_dir = Path.home() / ".kaggle"
                    kaggle_json = kaggle_config_dir / "kaggle.json"
                    
                    if not kaggle_json.exists():
                        error_msg = (
                            "Kaggle credentials not found.\n\n"
                            "The task was submitted without Kaggle credentials, and no fallback credentials "
                            "were found in ~/.kaggle/kaggle.json\n\n"
                            "To fix this:\n"
                            "1. In the Aegis AI web app, go to Settings → Kaggle Credentials\n"
                            "2. Configure your Kaggle username and API key\n"
                            "3. Resubmit the training task\n\n"
                            "The credentials will be automatically included in the task config."
                        )
                        self._append_log(task_id, "error", error_msg)
                        raise ValueError(error_msg)
                    
                    self._append_log(task_id, "info", f"✅ Using Kaggle credentials from {kaggle_json}")
                
                # Use Kaggle API to download
                result = subprocess.run(
                    ['kaggle', 'datasets', 'download', '-d', dataset_id, '-p', str(dataset_cache_dir), '--unzip'],
                    capture_output=True,
                    text=True,
                    check=True,
                    env=env  # Pass environment with credentials
                )
                
                self._append_log(task_id, "info", f"Successfully downloaded dataset: {dataset_id}")
                return dataset_cache_dir
                
            except subprocess.CalledProcessError as e:
                error_msg = f"Failed to download Kaggle dataset: {e.stderr}"
                self._append_log(task_id, "error", error_msg)
                raise ValueError(error_msg)
            except FileNotFoundError:
                error_msg = "Kaggle CLI not installed. Please install: pip install kaggle"
                self._append_log(task_id, "error", error_msg)
                raise ValueError(error_msg)
        
        elif dataset_source == 'url':
            # Download dataset from URL
            dataset_url = config.get('datasetUrl')
            if not dataset_url:
                raise ValueError("Dataset URL not provided")
            
            download_dir = self.work_dir / task_id / "dataset"
            download_dir.mkdir(parents=True, exist_ok=True)
            
            # TODO: Implement dataset download
            # For now, assume dataset is a zip file
            self._append_log(task_id, "info", f"Downloading dataset from {dataset_url}")
            
            # Use wget or requests to download
            import requests
            response = requests.get(dataset_url, stream=True)
            response.raise_for_status()
            
            zip_path = download_dir / "dataset.zip"
            with open(zip_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            # Extract
            import zipfile
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(download_dir)
            
            return download_dir
        
        else:
            raise ValueError(f"Unknown dataset source: {dataset_source}")
    
    def _run_training_script(
        self, 
        task_id: str, 
        config: Dict[str, Any], 
        dataset_dir: Path
    ) -> Path:
        """Run training using the training script (same as Kaggle)"""
        import subprocess
        import json
        import os
        from pathlib import Path as PathlibPath
        
        # Create task working directory
        task_work_dir = self.work_dir / task_id
        task_work_dir.mkdir(parents=True, exist_ok=True)
        
        # Create input directory structure (mimic Kaggle)
        input_dir = task_work_dir / "input"
        input_dir.mkdir(exist_ok=True)
        
        # Symlink dataset to input directory
        dataset_link = input_dir / dataset_dir.name
        if not dataset_link.exists():
            dataset_link.symlink_to(dataset_dir, target_is_directory=True)
        
        # Create working directory
        working_dir = task_work_dir / "working"
        working_dir.mkdir(exist_ok=True)
        
        # Prepare training config
        # Use config values directly, log warning if critical fields missing
        if 'epochs' not in config:
            self._append_log(task_id, "warning", f"⚠️  'epochs' not in config, using default: 100")
        
        training_config = {
            'model_variant': config.get('model', config.get('model_variant', 'yolo11n')),
            'epochs': config.get('epochs', 100),
            'batch_size': config.get('batchSize', config.get('batch_size', 16)),
            'img_size': config.get('imgsz', config.get('img_size', 640)),
            'output_formats': config.get('outputFormats', config.get('output_formats', ['onnx'])),
            # Wandb configuration (API key will be passed via env var)
            'wandb_enabled': config.get('wandbEnabled', config.get('wandb_enabled', False)),
            'wandb_project': config.get('wandbProject', config.get('wandb_project', 'aegis-ai')),
            'wandb_entity': config.get('wandbEntity', config.get('wandb_entity', None)),
            'wandb_api_key': config.get('wandbApiKey', config.get('wandb_api_key', None)),
            # Kaggle upload configuration (credentials will be passed via env var)
            'kaggle_upload_enabled': config.get('kaggleUploadEnabled', config.get('kaggle_upload_enabled', False)),
            'kaggle_username': config.get('kaggleUsername', config.get('kaggle_username', None)),
            'kaggle_api_key': config.get('kaggleApiKey', config.get('kaggle_api_key', None)),
            'kaggle_model_slug': config.get('kaggleModelSlug', config.get('kaggle_model_slug', None)),
            'trainingType': config.get('trainingType', 'agent_training'),
            # Pass all optimization parameters
            'learning_rate': config.get('learning_rate', 0.01),
            'momentum': config.get('momentum', 0.937),
            'weight_decay': config.get('weight_decay', 0.0005),
            'warmup_epochs': config.get('warmup_epochs', 3),
            'early_stopping': config.get('early_stopping', {'patience': 50}),
            # Augmentation parameters
            'hsv_h': config.get('hsv_h', 0.015),
            'hsv_s': config.get('hsv_s', 0.7),
            'hsv_v': config.get('hsv_v', 0.4),
            'degrees': config.get('degrees', 0.0),
            'translate': config.get('translate', 0.1),
            'scale': config.get('scale', 0.5),
            'flipud': config.get('flipud', 0.0),
            'fliplr': config.get('fliplr', 0.5),
            'mosaic': config.get('mosaic', 1.0),
            'mixup': config.get('mixup', 0.0),
        }
        
        self._append_log(task_id, "info", f"📊 Training config: model={training_config['model_variant']}, epochs={training_config['epochs']}, batch_size={training_config['batch_size']}")
        
        # Write config to file (for local agents)
        config_file = input_dir / "training_config.json"
        with open(config_file, 'w') as f:
            json.dump(training_config, f, indent=2)
        
        self._append_log(task_id, "info", f"📝 Wrote training config to {config_file}")
        self._append_log(task_id, "info", f"🔍 DEBUG: Config file contains epochs={training_config['epochs']}")
        
        # Get training script path
        script_path = PathlibPath(__file__).parent / "training_script.py"
        if not script_path.exists():
            raise RuntimeError(f"Training script not found: {script_path}")
        
        self._append_log(task_id, "info", f"Using training script: {script_path}")
        self._append_log(task_id, "info", f"Dataset directory: {input_dir}")
        self._append_log(task_id, "info", f"Working directory: {working_dir}")
        
        # Set environment variables for agent mode
        env = os.environ.copy()
        env['AEGIS_AGENT_MODE'] = '1'
        env['AEGIS_INPUT_DIR'] = str(input_dir)
        env['AEGIS_WORKING_DIR'] = str(working_dir)
        
        # Fix for CUDA architecture errors on newer GPUs (H100, H200, etc.)
        # This prevents "nvrtc: error: invalid value for --gpu-architecture" errors
        if 'TORCH_CUDA_ARCH_LIST' not in env:
            env['TORCH_CUDA_ARCH_LIST'] = '7.0 7.5 8.0 8.6 8.9 9.0+PTX'
            self._append_log(task_id, "info", "🔧 Set TORCH_CUDA_ARCH_LIST for broad GPU compatibility")
        
        # ✅ NEW: Pass config via environment variable (for remote agents)
        # This allows the training script to work without file-based config sharing
        env['AEGIS_TRAINING_CONFIG'] = json.dumps(training_config)
        self._append_log(task_id, "info", "✅ Training config embedded in environment variable")
        
        # Pass detected device to training script
        if self.detected_device:
            env['AEGIS_DEVICE'] = self.detected_device
            self._append_log(task_id, "info", f"Using device: {self.detected_device}")
        else:
            env['AEGIS_DEVICE'] = 'cpu'  # Fallback
            self._append_log(task_id, "info", "Using device: cpu (fallback)")
        
        # Pass Wandb API key if enabled
        if training_config.get('wandb_enabled') and training_config.get('wandb_api_key'):
            env['WANDB_API_KEY'] = training_config['wandb_api_key']
            self._append_log(task_id, "info", "✅ Wandb API key configured")
        
        # Pass Kaggle credentials if upload enabled
        if training_config.get('kaggle_upload_enabled'):
            if training_config.get('kaggle_username') and training_config.get('kaggle_api_key'):
                env['KAGGLE_USERNAME'] = training_config['kaggle_username']
                env['KAGGLE_KEY'] = training_config['kaggle_api_key']
                self._append_log(task_id, "info", "✅ Kaggle credentials configured")
        
        # Run training script
        try:
            process = subprocess.Popen(
                [sys.executable, str(script_path)],
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            
            # Stream output and log progress
            for line in process.stdout:
                line = line.strip()
                if line:
                    print(line)  # Print to agent logs
                    # Log important lines to Firestore
                    if any(marker in line for marker in ['🚀', '✅', '❌', '📊', 'Epoch']):
                        self._append_log(task_id, "info", line)
            
            process.wait()
            
            if process.returncode != 0:
                raise RuntimeError(f"Training script failed with exit code {process.returncode}")
            
            self._append_log(task_id, "info", "Training script completed successfully")
            
        except Exception as e:
            self._append_log(task_id, "error", f"Training script error: {str(e)}")
            raise
        
        # Find the trained model
        # The trainer saves models to trained_models directory
        trained_models_dir = working_dir / "trained_models"
        
        # Look for best.pt in trained_models
        best_model = trained_models_dir / "best.pt"
        
        if best_model.exists():
            self._append_log(task_id, "info", f"Found trained model: {best_model}")
            return best_model
        
        # Fallback: Check in yolo training runs directory
        yolo_dataset_dir = working_dir / "yolo_dataset"
        runs_dir = yolo_dataset_dir / "runs" / "detect" / "train"
        best_model = runs_dir / "weights" / "best.pt"
        
        if best_model.exists():
            self._append_log(task_id, "info", f"Found trained model in runs: {best_model}")
            return best_model
        
        # Alternative: Check if runs is at working_dir level
        best_model = working_dir / "runs" / "detect" / "train" / "weights" / "best.pt"
        if best_model.exists():
            self._append_log(task_id, "info", f"Found trained model in runs: {best_model}")
            return best_model
        
        # List available files for debugging
        available_files = []
        if trained_models_dir.exists():
            available_files.extend([str(f.relative_to(working_dir)) for f in trained_models_dir.glob("*")])
        if runs_dir.exists():
            available_files.extend([str(f.relative_to(working_dir)) for f in runs_dir.glob("**/*") if f.is_file()])
        
        error_msg = f"Training completed but best model not found. Checked: {trained_models_dir}, {runs_dir}"
        if available_files:
            error_msg += f"\nAvailable files: {', '.join(available_files[:10])}"
        
        self._append_log(task_id, "error", error_msg)
        raise RuntimeError(error_msg)
    
    def _upload_model(self, task_id: str, model_path: Path) -> str:
        """Upload trained model to storage"""
        # TODO: Implement Firebase Storage upload
        # For now, return local path
        return str(model_path)
    
    def _update_task_status(
        self, 
        task_id: str, 
        status: str, 
        extra_fields: Optional[Dict[str, Any]] = None
    ) -> None:
        """Update task status in Firestore"""
        update_data = {"status": status}
        if extra_fields:
            update_data.update(extra_fields)
        
        try:
            self.db.collection("training_tasks").document(task_id).update(update_data)
            logger.info(f"✅ Task {task_id} status updated to: {status}")
        except Exception as e:
            logger.error(f"❌ Failed to update task {task_id} status to {status}: {e}")
            raise
    
    def _append_log(self, task_id: str, level: str, message: str) -> None:
        """Append log entry to task"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "message": message
        }
        
        # TODO: Implement array append for REST API
        # self.db.collection("training_tasks").document(task_id).update({
        #     "logs": ArrayUnion([log_entry])
        # })
        
        # Also log locally
        log_func = logger.info if level == "info" else logger.error
        log_func(f"[{task_id}] {message}")
    
    def start(self) -> None:
        """Start the agent daemon"""
        logger.info(f"Starting agent: {self.agent_id}")
        
        try:
            # Initialize Firebase Admin SDK
            self.initialize_firebase()
            
            # Register agent
            self.register_agent()
            
            # Start listening for tasks and commands (real-time)
            self.running = True
            
            def handle_task(task_data):
                task_id = task_data['taskId']
                if self.claim_task(task_id):
                    self.execute_task(task_id)
            
            self.listen_for_tasks(handle_task)
            self.listen_for_commands()
            
            # Heartbeat loop (real-time listeners active)
            logger.info("⚡ Real-time mode: 30-second heartbeat")
            logger.info("Agent started successfully. Press Ctrl+C to stop.")
            
            while self.running:
                self.update_heartbeat()
                time.sleep(30)  # Heartbeat every 30 seconds
                
        except KeyboardInterrupt:
            logger.info("Shutting down agent...")
            self.stop()
        except Exception as e:
            logger.error(f"Agent error: {e}")
            self.stop()
            raise
    
    def stop(self) -> None:
        """Stop the agent daemon"""
        self.running = False
        
        # Update agent status to offline
        if self.db:
            try:
                self.db.collection("agents").document(self.agent_id).update({
                    "status": "offline",
                    "lastSeen": "SERVER_TIMESTAMP"
                })
            except Exception as e:
                logger.warning(f"Failed to update agent status: {e}")
        
        # Stop listeners (polling threads)
        if self.task_listener and hasattr(self.task_listener, 'join'):
            # It's a thread, wait for it to finish
            pass  # Thread will exit when self.running = False
        if self.command_listener and hasattr(self.command_listener, 'join'):
            # It's a thread, wait for it to finish
            pass  # Thread will exit when self.running = False
        
        logger.info("Agent stopped")

