# Copyright 2025 Baleine Jay
# Licensed under the Phicode Non-Commercial License (https://banes-lab.com/licensing)
# Commercial use requires a paid license. See link for details.
import sys
import os
from ...phicode_logger import logger
from ....config.config import SECURITY_NAME, RUST_NAME

def handle_security_install():
    try:
        from ....installers.phirust_installer import install_phirust_binary
        from ....installers.phimmuno_installer import install_phimmuno_binary
        install_phirust_binary()
        install_phimmuno_binary()
        logger.info("🔒 Security binaries installed successfully")
    except ImportError:
        logger.error("Security installer not available")
    except Exception as e:
        logger.error(f"Security installation failed: {e}")
    sys.exit(0)

def handle_security_status():
    try:
        from ....installers.phirust_installer import get_binary_path as get_phirust_path
        from ....installers.phimmuno_installer import get_binary_path as get_phimmuno_path

        phirust_installed = os.path.exists(get_phirust_path())
        phimmuno_installed = os.path.exists(get_phimmuno_path())

        logger.info("🔒 Security Status:")
        logger.info(f"  {RUST_NAME} Transpiler: {'✅ Installed' if phirust_installed else '❌ Not installed'}")
        logger.info(f"  {SECURITY_NAME} Engine: {'✅ Installed' if phimmuno_installed else '❌ Not installed'}")

        if phirust_installed and phimmuno_installed:
            logger.info("🛡️ Full security suite available")
        else:
            logger.info("💡 Run: phicode --security-install")
    except ImportError:
        logger.error("Security status checker not available")
    sys.exit(0)

def handle_benchmark(argv):
    try:
        from ....benchsuite import run_benchmarks
        original_argv = sys.argv
        sys.argv = ['phicode'] + argv
        try:
            run_benchmarks()
        finally:
            sys.argv = original_argv
    except ImportError:
        logger.error("Benchsuite module not available")
    sys.exit(0)

def handle_api_server(argv):
    try:
        port_idx = argv.index("--api-port") + 1 if "--api-port" in argv else None
        api_port = int(argv[port_idx]) if port_idx and port_idx < len(argv) else 8000
    except (ValueError, IndexError):
        api_port = 8000

    from ....api.cli import main as api_main
    sys.argv = ['phicode-api', '--port', str(api_port)]
    api_main()
    sys.exit(0)

def handle_config_generate():
    from ...mod.phicode_config_generator import generate_default_config
    generate_default_config()
    logger.info("Default configuration generated")
    logger.info("💡 Edit the config file to customize symbols and settings")
    sys.exit(0)

def handle_config_reset():
    from ...mod.phicode_config_generator import reset_config
    if reset_config():
        logger.info("Configuration reset successfully")
    else:
        logger.info("No configuration to reset")
    sys.exit(0)