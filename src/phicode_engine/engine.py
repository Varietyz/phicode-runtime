import os
from .core.interpreter.cli.phicode_cli import parse_args
from .core.interpreter.phicode_exit_handlers import handle_early_exit_flags
from .core.runtime.phicode_runtime import run
from .core.phicode_logger import logger

def main():
    args = None
    try:
        args = parse_args()
        if handle_early_exit_flags(args):
            return

        is_switched = os.environ.get('PHICODE_ALREADY_SWITCHED', '0') == '1'

        if not is_switched:
            if args.bypass:
                logger.warning("   🔓 SECURITY BYPASS ENABLED")
                logger.warning("Threat detection is DISABLED for this execution.")
            else:
                logger.warning("   ⚠️  SECURITY WARNING ⚠️")
                logger.warning("This engine executes code on your machine.")
                logger.warning("Only provide input from trusted sources.")
                logger.warning("🔍 All code is screened for dangerous patterns before execution.")

        if args.debug:
            logger.setLevel("DEBUG")
            logger.debug("Debug mode enabled via centralized args")

        run(args)

    except KeyboardInterrupt:
        logger.info("Execution interrupted by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        if args and args.debug:
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    main()