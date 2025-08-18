from .core.phicode_cli import parse_args
from .core.phicode_runtime import run
from .version import __version__

def main():
    args, remaining_args = parse_args()
    run(args, remaining_args)


if __name__ == "__main__":
    main()
