import argparse
import sys
from rhesis import __version__

def main():
    parser = argparse.ArgumentParser(
        description="Rhesis SDK - Testing and validation tools for GenAI applications"
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version=f'rhesis-sdk {__version__}'
    )

    args = parser.parse_args()

    # Since we only have --help and --version,
    # if no arguments are provided, show help
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)

if __name__ == '__main__':
    main()
