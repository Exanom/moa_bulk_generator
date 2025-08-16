import argparse
import sys
from . import MOABulkGenerator








def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="MOA Bulk Generator.")
    p.add_argument("--datasets", "-d", type=str, help="Specify the txt file containing the datasets to generate.")
    p.add_argument("--interactive","-i", action="store_true", help="Run interactive configuration.")
    p.add_argument('--config',type=str,help='Speicify configuration json file other than default')
    p.add_argument("--out", type=str, help="Specify output directory other than default.")
    p.add_argument("--dry-run", action="store_true", help="Check validity of the datasets within the dataset txt file, without generating them.")
    return p

def main():
    parser = build_arg_parser()
    args = parser.parse_args()
    
    if(not args.interactive and not args.datasets):
        parser.print_help(sys.stderr)
        sys.exit(0) 
    else:
        moa = MOABulkGenerator(interactive=args.interactive, datasets_file=args.datasets, out_path=args.out, config_path=args.config)
        moa.run()


if __name__ == "__main__":
    main()
