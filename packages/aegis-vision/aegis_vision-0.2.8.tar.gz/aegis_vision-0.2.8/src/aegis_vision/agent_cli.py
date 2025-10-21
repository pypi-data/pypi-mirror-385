"""
Aegis Agent CLI

Command-line interface for managing and running training agents.
"""

import sys
import argparse
import logging
from pathlib import Path
from typing import Optional

# Lazy imports to avoid requiring firebase_admin for all commands
def _import_agent_modules():
    """Lazy import of agent modules that require firebase_admin"""
    try:
        from .agent import TrainingAgent, AgentCapabilities
        from .agent_auth import AgentAuthenticator, AgentAuthenticationError
        return TrainingAgent, AgentCapabilities, AgentAuthenticator, AgentAuthenticationError
    except ImportError as e:
        if 'firebase_admin' in str(e) or 'google.cloud.firestore' in str(e):
            print("❌ Error: Required dependencies not found")
            print()
            print("Please reinstall aegis-vision:")
            print("  pip install --upgrade aegis-vision")
            print()
            print("If the error persists, try:")
            print("  pip install firebase-admin google-cloud-firestore")
            sys.exit(1)
        else:
            raise


def setup_logging(verbose: bool = False) -> None:
    """Configure logging"""
    level = logging.DEBUG if verbose else logging.INFO
    
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )


def cmd_login(args) -> int:
    """Interactive login command (like huggingface-cli login)"""
    try:
        _, _, AgentAuthenticator, _ = _import_agent_modules()
        
        print("🔐 Aegis AI Agent Login")
        print()
        print("To get your API key:")
        print("  1. Open Aegis AI application")
        print("  2. Go to: Model Training → Settings → Training Agents")
        print("  3. Click 'Add Agent' and copy the API key")
        print()
        
        # Get API key from user (visible input for easy verification)
        api_key = input("Enter your API key: ").strip()
        
        if not api_key:
            print("❌ API key is required")
            return 1
        
        # Validate API key format
        if not api_key.startswith('ak_'):
            print("❌ Invalid API key format. API keys should start with 'ak_'")
            return 1
        
        # Validate API key and retrieve owner info
        print()
        print("🔍 Validating API key...")
        import requests
        
        # Test API key by exchanging for token
        try:
            url = f"{args.cloud_function_url}/auth/agent/token"
            headers = {
                'Authorization': f"Bearer {api_key}",
                'Content-Type': 'application/json'
            }
            response = requests.post(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            if not data.get('success'):
                print(f"❌ API key validation failed: {data.get('message', 'Unknown error')}")
                return 1
            
            # Extract agent ID and owner info from response
            # IMPORTANT: Use the agent ID returned by the Cloud Function, not a generated one
            agent_id = data.get('agentId')
            if not agent_id:
                print("❌ API key validation failed: No agent ID returned")
                return 1
            
            owner_uid = data.get('ownerUid')
            owner_email = data.get('ownerEmail')
            owner_name = data.get('ownerName')
            
            print(f"✅ API key validated")
            print(f"   Agent ID: {agent_id}")
            if owner_uid:
                print(f"   Owner UID: {owner_uid}")
            if owner_email or owner_name:
                print(f"   Owner: {owner_name or ''} ({owner_email or 'no email'})")
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Failed to validate API key: {e}")
            return 1
        except Exception as e:
            print(f"❌ Validation error: {e}")
            return 1
        
        # Get machine/host name for identification
        import socket
        default_hostname = socket.gethostname()
        print()
        machine_name = input(f"Enter machine name (press Enter for '{default_hostname}'): ").strip()
        if not machine_name:
            machine_name = default_hostname
        
        # Create config file with owner info
        config_path = AgentAuthenticator.create_config_file(
            agent_id=agent_id,
            api_key=api_key,
            config_path=Path(args.config) if args.config else None,
            agent_name=machine_name,
            cloud_function_url=args.cloud_function_url,
            firestore_project=args.firestore_project,
            owner_uid=owner_uid,
            owner_email=owner_email,
            owner_name=owner_name
        )
        
        print()
        print(f"✅ Login successful!")
        print(f"   Configuration saved to: {config_path}")
        print(f"   Agent ID: {agent_id}")
        print(f"   Machine Name: {machine_name}")
        print()
        print("Next steps:")
        print("  1. Start the agent: aegis-agent start")
        print("  2. The agent will appear online in the Aegis AI application")
        print("  3. Submit training tasks from the application")
        
        return 0
        
    except KeyboardInterrupt:
        print("\n❌ Login cancelled")
        return 1
    except Exception as e:
        print(f"❌ Login failed: {e}")
        return 1


def cmd_init(args) -> int:
    """Initialize agent configuration"""
    try:
        _, _, AgentAuthenticator, _ = _import_agent_modules()
        
        if not args.api_key:
            print("Error: --api-key is required")
            print("Get your API key from the Aegis AI application:")
            print("  Model Training → Settings → Training Agents → Add Agent")
            print()
            print("Tip: Use 'aegis-agent login' for interactive setup")
            return 1
        
        # Generate agent ID if not provided
        if not args.agent_id:
            import uuid
            agent_id = f"agent-{uuid.uuid4().hex[:16]}"
        else:
            agent_id = args.agent_id
        
        # Create config file
        config_path = AgentAuthenticator.create_config_file(
            agent_id=agent_id,
            api_key=args.api_key,
            config_path=Path(args.config) if args.config else None,
            agent_name=args.name,
            cloud_function_url=args.cloud_function_url,
            firestore_project=args.firestore_project
        )
        
        print(f"✅ Agent configuration created: {config_path}")
        print(f"   Agent ID: {agent_id}")
        print(f"   Agent Name: {args.name or f'Agent {agent_id[:8]}'}")
        print()
        print("Next steps:")
        print("  1. Start the agent: aegis-agent start")
        print("  2. The agent will appear online in the Aegis AI application")
        print("  3. Submit training tasks from the application")
        
        return 0
        
    except Exception as e:
        print(f"❌ Failed to initialize agent: {e}")
        return 1


def cmd_start(args) -> int:
    """Start the agent daemon"""
    try:
        TrainingAgent, _, AgentAuthenticator, AgentAuthenticationError = _import_agent_modules()
        setup_logging(args.verbose)
        
        # Check environment compatibility BEFORE starting agent
        if not args.skip_env_check:
            from .environment_check import check_environment_interactive
            
            print()
            env_ok = check_environment_interactive()
            print()
            
            if not env_ok:
                print("❌ Environment check failed. Please fix the issues above.")
                print()
                print("💡 You can skip this check with --skip-env-check (not recommended)")
                return 1
        
        # Load authenticator
        config_path = Path(args.config) if args.config else None
        authenticator = AgentAuthenticator(config_path)
        
        # Create and start agent
        work_dir = Path(args.work_dir) if args.work_dir else None
        agent = TrainingAgent(authenticator, work_dir)
        
        print(f"🚀 Starting Aegis AI Training Agent")
        print(f"   Agent ID: {agent.agent_id}")
        print(f"   Work Directory: {agent.work_dir}")
        print()
        
        # Show capabilities
        caps = agent.capabilities
        print("📊 System Capabilities:")
        print(f"   Platform: {caps['platform']}")
        print(f"   Memory: {caps['totalMemoryGB']}GB total, {caps['availableMemoryGB']}GB available")
        print(f"   Storage: {caps['availableStorageGB']}GB available")
        print(f"   CPU Cores: {caps['cpuCount']}")
        print(f"   GPU: {'Yes' if caps['hasGPU'] else 'No'}")
        if caps['hasGPU']:
            print(f"   CUDA: {caps['cudaVersion']}")
            for i, gpu in enumerate(caps['gpuInfo']):
                print(f"   GPU {i}: {gpu['name']} ({gpu['memory']}GB)")
        print()
        
        # Start agent
        agent.start()
        
        return 0
        
    except AgentAuthenticationError as e:
        print(f"❌ Authentication failed: {e}")
        print()
        print("Make sure you have run 'aegis-agent init' first.")
        return 1
    except KeyboardInterrupt:
        print("\n👋 Agent stopped by user")
        return 0
    except Exception as e:
        print(f"❌ Agent error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


def cmd_status(args) -> int:
    """Show agent status"""
    try:
        _, AgentCapabilities, AgentAuthenticator, _ = _import_agent_modules()
        
        config_path = Path(args.config) if args.config else None
        authenticator = AgentAuthenticator(config_path)
        
        print(f"📊 Agent Status")
        print(f"   Agent ID: {authenticator.get_agent_id()}")
        print(f"   Config: {authenticator.config_path}")
        print(f"   Firestore Project: {authenticator.get_firestore_project()}")
        print()
        
        # Show capabilities
        caps = AgentCapabilities.detect()
        print("💻 System Capabilities:")
        print(f"   Platform: {caps['platform']}")
        print(f"   Python: {caps['pythonVersion']}")
        print(f"   Memory: {caps['availableMemoryGB']}GB / {caps['totalMemoryGB']}GB")
        print(f"   Storage: {caps['availableStorageGB']}GB / {caps['totalStorageGB']}GB")
        print(f"   CPU: {caps['cpuCount']} cores")
        print(f"   GPU: {'Yes (' + caps['cudaVersion'] + ')' if caps['hasGPU'] else 'No'}")
        
        # Test authentication
        print()
        print("🔐 Testing authentication...")
        try:
            token = authenticator.authenticate()
            print("   ✅ Authentication successful")
        except Exception as e:
            print(f"   ❌ Authentication failed: {e}")
            return 1
        
        return 0
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1


def cmd_info(args) -> int:
    """Show system information"""
    _, AgentCapabilities, _, _ = _import_agent_modules()
    caps = AgentCapabilities.detect()
    
    print("📊 System Information")
    print()
    print(f"Platform: {caps['platform']}")
    print(f"Python Version: {caps['pythonVersion']}")
    print()
    print("Memory:")
    print(f"  Total: {caps['totalMemoryGB']:.2f} GB")
    print(f"  Available: {caps['availableMemoryGB']:.2f} GB")
    print()
    print("Storage:")
    print(f"  Total: {caps['totalStorageGB']:.2f} GB")
    print(f"  Available: {caps['availableStorageGB']:.2f} GB")
    print()
    print(f"CPU Cores: {caps['cpuCount']}")
    print()
    
    if caps['hasGPU']:
        print("GPU Information:")
        print(f"  CUDA Version: {caps['cudaVersion']}")
        for i, gpu in enumerate(caps['gpuInfo']):
            print(f"  GPU {i}:")
            print(f"    Name: {gpu['name']}")
            print(f"    Memory: {gpu['memory']:.2f} GB")
    else:
        print("GPU: Not available")
    
    return 0


def cmd_check_env(args) -> int:
    """Check environment compatibility"""
    from .environment_check import check_environment_interactive
    
    print()
    env_ok = check_environment_interactive()
    print()
    
    if env_ok:
        print("✅ Environment is ready for Aegis AI training.")
        return 0
    else:
        print("❌ Environment has issues that need to be addressed.")
        return 1


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description='Aegis AI Training Agent - Distributed model training',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive login (recommended)
  aegis-agent login
  
  # Or initialize with API key directly
  aegis-agent init --api-key ak_xxxxxxxxxxxxx --name "My Training Server"
  
  # Start agent daemon
  aegis-agent start
  
  # Check agent status
  aegis-agent status
  
  # Show system capabilities
  aegis-agent info
"""
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # login command
    login_parser = subparsers.add_parser('login', help='Interactive login (like huggingface-cli login)')
    login_parser.add_argument('--config', help='Config file path (default: ~/.aegis-ai/agent-config.json)')
    login_parser.add_argument(
        '--cloud-function-url',
        default='https://us-central1-aegis-vision-464501.cloudfunctions.net/aegis-vision-admin-api',
        help='Cloud Function URL'
    )
    login_parser.add_argument(
        '--firestore-project',
        default='aegis-vision-464501',
        help='Firestore project ID'
    )
    
    # init command
    init_parser = subparsers.add_parser('init', help='Initialize agent configuration (non-interactive)')
    init_parser.add_argument('--api-key', required=True, help='API key from Aegis AI')
    init_parser.add_argument('--agent-id', help='Agent ID (auto-generated if not provided)')
    init_parser.add_argument('--name', help='Human-readable agent name')
    init_parser.add_argument('--config', help='Config file path (default: ~/.aegis-ai/agent-config.json)')
    init_parser.add_argument(
        '--cloud-function-url',
        default='https://us-central1-aegis-vision-464501.cloudfunctions.net/aegis-vision-admin-api',
        help='Cloud Function URL'
    )
    init_parser.add_argument(
        '--firestore-project',
        default='aegis-vision-464501',
        help='Firestore project ID'
    )
    
    # start command
    start_parser = subparsers.add_parser('start', help='Start agent daemon')
    start_parser.add_argument('--config', help='Config file path')
    start_parser.add_argument('--work-dir', help='Working directory for training')
    start_parser.add_argument('-v', '--verbose', action='store_true', help='Verbose logging')
    start_parser.add_argument(
        '--skip-env-check',
        action='store_true',
        help='Skip environment compatibility check (not recommended)'
    )
    
    # status command
    status_parser = subparsers.add_parser('status', help='Show agent status')
    status_parser.add_argument('--config', help='Config file path')
    
    # info command
    info_parser = subparsers.add_parser('info', help='Show system information')
    
    # check-env command
    check_env_parser = subparsers.add_parser(
        'check-env',
        help='Check environment compatibility and suggest fixes'
    )
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Route to command handler
    if args.command == 'login':
        return cmd_login(args)
    elif args.command == 'init':
        return cmd_init(args)
    elif args.command == 'start':
        return cmd_start(args)
    elif args.command == 'status':
        return cmd_status(args)
    elif args.command == 'info':
        return cmd_info(args)
    elif args.command == 'check-env':
        return cmd_check_env(args)
    else:
        print(f"Unknown command: {args.command}")
        return 1


if __name__ == '__main__':
    sys.exit(main())

