
from .core.phicode_args import parse_args, handle_early_exit_flags
from .core.phicode_runtime import run
from .core.phicode_logger import logger

def main():
    try:
        args = parse_args()
        if handle_early_exit_flags(args):
            return

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