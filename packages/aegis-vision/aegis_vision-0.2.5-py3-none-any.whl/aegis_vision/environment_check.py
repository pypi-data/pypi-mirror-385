"""
Environment validation and auto-fix for Aegis Vision agents.

Checks for common compatibility issues and provides automated fixes.
"""

import sys
import subprocess
import importlib.metadata
from typing import Dict, List, Optional, Tuple
from pathlib import Path


class EnvironmentIssue:
    """Represents an environment compatibility issue"""
    
    def __init__(
        self,
        severity: str,  # 'error', 'warning', 'info'
        title: str,
        description: str,
        packages_affected: List[str],
        fix_command: Optional[str] = None,
        fix_description: Optional[str] = None,
        alternative_solution: Optional[str] = None
    ):
        self.severity = severity
        self.title = title
        self.description = description
        self.packages_affected = packages_affected
        self.fix_command = fix_command
        self.fix_description = fix_description
        self.alternative_solution = alternative_solution


class EnvironmentChecker:
    """Check and validate the Python environment for compatibility issues"""
    
    @staticmethod
    def check_numpy_compatibility() -> Optional[EnvironmentIssue]:
        """
        Check if NumPy version is compatible with compiled modules.
        
        Many packages (onnxruntime, opencv-python, scipy, etc.) are compiled
        against NumPy 1.x and will fail or show warnings with NumPy 2.x.
        
        Additionally, opencv-python 4.12.0+ REQUIRES NumPy 2.x for Python >= 3.9,
        so we must pin opencv-python < 4.12.0 to allow NumPy 1.x usage.
        """
        try:
            import numpy as np
            numpy_version = np.__version__
            
            # Check if NumPy 2.x
            major_version = int(numpy_version.split('.')[0])
            
            if major_version >= 2:
                # Find which packages are compiled against NumPy 1.x
                problematic_packages = []
                
                # Check packages known to have NumPy 1.x compiled extensions
                packages_to_check = [
                    ('onnxruntime', 'ONNX Runtime (ML inference)'),
                    ('cv2', 'OpenCV (computer vision)'),
                    ('scipy', 'SciPy (scientific computing)'),
                    ('torch', 'PyTorch (deep learning)'),
                    ('ultralytics', 'Ultralytics (YOLO training)'),
                ]
                
                for pkg_name, description in packages_to_check:
                    try:
                        importlib.import_module(pkg_name)
                        problematic_packages.append(description)
                    except ImportError:
                        pass  # Package not installed
                
                # Also check opencv-python version
                opencv_issue = ""
                try:
                    import cv2
                    cv2_version = cv2.__version__
                    # Extract opencv-python version (format: 4.x.y.z)
                    if cv2_version.startswith('4.12.') or cv2_version.startswith('4.13.'):
                        opencv_issue = (
                            "\n\nAdditionally, opencv-python 4.12.0+ REQUIRES NumPy 2.x for Python >= 3.9. "
                            "You must downgrade opencv-python to < 4.12.0 AND NumPy to < 2.0."
                        )
                except ImportError:
                    pass
                
                if problematic_packages:
                    return EnvironmentIssue(
                        severity='error',
                        title='NumPy 2.x Incompatibility',
                        description=(
                            f'NumPy {numpy_version} is installed, but the following packages '
                            'were compiled with NumPy 1.x and may crash or malfunction:\n'
                            + '\n'.join(f'  • {pkg}' for pkg in problematic_packages) +
                            opencv_issue +
                            '\n\nThis is a known compatibility issue. See: '
                            'https://numpy.org/doc/stable/numpy_2_0_migration_guide.html'
                        ),
                        packages_affected=problematic_packages,
                        fix_command='pip install "numpy<2.0" "opencv-python<4.12.0"',
                        fix_description='Downgrade NumPy to 1.x and opencv-python to <4.12.0',
                        alternative_solution=(
                            'Use a Docker image with NumPy 1.x pre-installed, such as:\n'
                            '  • nvcr.io/nvidia/pytorch:24.08-py3 (NumPy 1.26.4)\n'
                            '  • nvcr.io/nvidia/pytorch:24.12-py3 (NumPy 1.26.4)\n'
                            '  • python:3.10-slim with manual NumPy 1.x installation'
                        )
                    )
        except ImportError:
            # NumPy not installed - will be caught by other checks
            pass
        
        return None
    
    @staticmethod
    def check_pytorch_cuda_compatibility() -> Optional[EnvironmentIssue]:
        """
        Check if PyTorch supports the available GPU architecture.
        
        Newer GPUs (Blackwell/GB10 - sm_121) require PyTorch nightly builds.
        """
        try:
            import torch
            
            if not torch.cuda.is_available():
                return None  # No GPU, no issue
            
            # Get GPU compute capability
            try:
                props = torch.cuda.get_device_properties(0)
                gpu_name = torch.cuda.get_device_name(0)
                compute_capability = f"sm_{props.major}{props.minor}"
                
                # Check if PyTorch version supports this GPU
                # PyTorch stable supports up to sm_90 (Hopper)
                # Blackwell (sm_121) requires nightly
                if props.major >= 12 or (props.major == 12 and props.minor >= 1):
                    return EnvironmentIssue(
                        severity='warning',
                        title='GPU Architecture Not Fully Supported',
                        description=(
                            f'GPU: {gpu_name} (compute capability {compute_capability})\n'
                            f'PyTorch Version: {torch.__version__}\n\n'
                            'Your GPU uses a newer architecture that may not be fully supported '
                            'by the current PyTorch installation. This may result in:\n'
                            '  • Performance degradation (CPU fallback)\n'
                            '  • Missing optimizations\n'
                            '  • Compatibility warnings\n\n'
                            'Note: Training will still work using forward compatibility mode, '
                            'but upgrading to PyTorch nightly is recommended for best performance.'
                        ),
                        packages_affected=['PyTorch'],
                        fix_command=(
                            'pip install --upgrade --pre torch torchvision torchaudio '
                            '--index-url https://download.pytorch.org/whl/nightly/cu126'
                        ),
                        fix_description='Upgrade to PyTorch nightly with latest GPU support',
                        alternative_solution=(
                            'Use NVIDIA NGC PyTorch container with latest GPU support:\n'
                            '  docker pull nvcr.io/nvidia/pytorch:25.01-py3'
                        )
                    )
            except Exception:
                pass  # Unable to check GPU properties
        except ImportError:
            # PyTorch not installed
            pass
        
        return None
    
    @staticmethod
    def check_all() -> List[EnvironmentIssue]:
        """Run all environment checks and return list of issues"""
        issues = []
        
        # Run all checks
        checks = [
            EnvironmentChecker.check_numpy_compatibility,
            EnvironmentChecker.check_pytorch_cuda_compatibility,
        ]
        
        for check in checks:
            issue = check()
            if issue:
                issues.append(issue)
        
        return issues
    
    @staticmethod
    def apply_fix(issue: EnvironmentIssue) -> Tuple[bool, str]:
        """
        Apply the automatic fix for an issue.
        
        Returns:
            (success: bool, message: str)
        """
        if not issue.fix_command:
            return False, "No automatic fix available"
        
        try:
            # Execute fix command
            result = subprocess.run(
                issue.fix_command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=300  # 5 minutes
            )
            
            if result.returncode == 0:
                return True, "Fix applied successfully"
            else:
                return False, f"Fix failed: {result.stderr}"
        except subprocess.TimeoutExpired:
            return False, "Fix timed out (5 minutes)"
        except Exception as e:
            return False, f"Fix error: {e}"


def print_issue(issue: EnvironmentIssue, index: Optional[int] = None) -> None:
    """Pretty print an environment issue"""
    
    # Severity emoji
    severity_emoji = {
        'error': '❌',
        'warning': '⚠️',
        'info': 'ℹ️'
    }
    emoji = severity_emoji.get(issue.severity, '•')
    
    # Header
    if index is not None:
        print(f"\n{emoji} Issue #{index}: {issue.title}")
    else:
        print(f"\n{emoji} {issue.title}")
    
    print("─" * 70)
    
    # Description
    print(f"\n{issue.description}")
    
    # Packages affected
    if issue.packages_affected:
        print(f"\n📦 Affected packages:")
        for pkg in issue.packages_affected:
            print(f"   • {pkg}")
    
    # Fix option
    if issue.fix_command:
        print(f"\n✅ Automatic fix available:")
        print(f"   {issue.fix_description}")
        print(f"\n   Command:")
        print(f"   {issue.fix_command}")
    
    # Alternative
    if issue.alternative_solution:
        print(f"\n🐳 Alternative (Docker-based):")
        for line in issue.alternative_solution.split('\n'):
            print(f"   {line}")


def check_environment_interactive() -> bool:
    """
    Check environment and prompt user for fixes.
    
    Returns:
        True if environment is OK or fixes were applied
        False if user declined fixes or environment has errors
    """
    print("🔍 Checking environment compatibility...")
    print()
    
    issues = EnvironmentChecker.check_all()
    
    if not issues:
        print("✅ Environment check passed! All systems ready.")
        return True
    
    # Show all issues
    print(f"⚠️  Found {len(issues)} environment issue(s):\n")
    
    for i, issue in enumerate(issues, 1):
        print_issue(issue, i)
    
    print("\n" + "=" * 70)
    
    # Count errors vs warnings
    errors = [iss for iss in issues if iss.severity == 'error']
    warnings = [iss for iss in issues if iss.severity == 'warning']
    
    if errors:
        print(f"\n❌ Found {len(errors)} critical error(s) that must be fixed.")
    if warnings:
        print(f"⚠️  Found {len(warnings)} warning(s) that should be addressed.")
    
    print()
    
    # Prompt for fixes
    fixable_issues = [iss for iss in issues if iss.fix_command]
    
    if not fixable_issues:
        print("💡 Please apply the suggested solutions manually.")
        return len(errors) == 0  # OK if only warnings
    
    # Ask user if they want automatic fixes
    print("🔧 Automatic fixes are available.")
    print()
    
    try:
        response = input("Apply automatic fixes now? [y/N]: ").strip().lower()
        
        if response not in ['y', 'yes']:
            print()
            print("❌ Fixes declined. Please fix manually or use a compatible Docker image.")
            print()
            for issue in fixable_issues:
                if issue.alternative_solution:
                    print(f"💡 {issue.title}:")
                    print(issue.alternative_solution)
                    print()
            return False
        
        # Apply fixes
        print()
        print("🔧 Applying fixes...")
        print()
        
        all_success = True
        for i, issue in enumerate(fixable_issues, 1):
            print(f"[{i}/{len(fixable_issues)}] Fixing: {issue.title}")
            print(f"      Command: {issue.fix_command}")
            
            success, message = EnvironmentChecker.apply_fix(issue)
            
            if success:
                print(f"      ✅ {message}")
            else:
                print(f"      ❌ {message}")
                all_success = False
            print()
        
        if all_success:
            print("=" * 70)
            print("✅ All fixes applied successfully!")
            print("🔄 Please restart the agent for changes to take effect.")
            return True
        else:
            print("=" * 70)
            print("⚠️  Some fixes failed. Please review the errors above.")
            return False
            
    except KeyboardInterrupt:
        print("\n\n❌ Fixes cancelled by user.")
        return False
