import argparse
import sys
from . import MOABulkGenerator
from .dataset_defs import DatasetObject


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="MOA Bulk Generator.")
    p.add_argument(
        "--datasets",
        "-d",
        type=str,
        help="Specify the txt file containing the datasets to generate.",
    )
    p.add_argument(
        "--interactive",
        "-i",
        action="store_true",
        help="Run interactive configuration.",
    )
    p.add_argument(
        "--validate",
        type=str,
        help="Validate the dataset definitions within the specified txt file without generating them.",
    )
    p.add_argument(
        "--config", type=str, help="Speicify configuration json file other than default"
    )
    p.add_argument(
        "--out", type=str, help="Specify output directory other than default."
    )
    p.add_argument(
        '--list',
        '-l',
        action="store_true",
        help='List information on supported generators'
    )
    return p


def main():
    parser = build_arg_parser()
    args = parser.parse_args()  
    if not args.interactive and not args.datasets and not args.list and not args.validate:
        parser.print_help(sys.stderr)
        sys.exit(0)
    elif(args.list):
        generatos = DatasetObject.GENERATORS
        print('Supported Generators:')
        for gen in generatos:
            print(f'name: {gen}')
            for key in generatos[gen]:
                print(f'\t {key}:{generatos[gen][key]}')
    elif(args.validate):
        datasets, errors = MOABulkGenerator.validate_datasets(args.validate)
        print('Valid datasets:')
        for dataset in datasets:
            print(f'\t {dataset.to_string()}')
        print('Errors:')
        for error in errors:
            print(f'\t {error}')
    else:
        moa = MOABulkGenerator(
            interactive=args.interactive,
            datasets=args.datasets,
            out=args.out,
            config=args.config,
        )
        moa.run()


if __name__ == "__main__":
    main()
