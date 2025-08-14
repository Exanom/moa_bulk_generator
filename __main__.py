import argparse
import sys
import json
from moa_handling.MOAHandler import MOAHandler
from input_handling.FileInputHandler import FileInputHanlder



class MOABulkGenerator():
    _moa_handler: MOAHandler = None
    _interactive: bool
    _dataset_file_path: str
    _validation_mode: bool
    _out_path: str


    def __init__(self, interacitve:bool = True, datasets_file:str = '', out_path:str = 'results',  validation_mode: bool = False):
        self._interactive = interacitve
        self._dataset_file_path = datasets_file
        self._validation_mode = validation_mode
        if(out_path is not None):
            self._out_path = out_path
        else: 
            self._out_path = 'results'

        java_executable, moa_path = self._load_config()
        self._moa_handler = MOAHandler(java_executable, moa_path)
        
    def run(self):
        datasets = []
        if(not self._interactive):
            file_handler = FileInputHanlder(self._dataset_file_path)
            datasets = file_handler.load_validate_file()
        
        self._moa_handler.generate(datasets, self._out_path)

    def _load_config(self) -> tuple[str,str]:
        config = None
        config_path = 'config/config.json'
        moa_path = None
        java_executable = None

        with open(config_path) as f:
            config = json.load(f)
        if('MOA_path' not in config.keys()):
            raise Exception("Config file must have a vaild MOA_path parameter")
        if('JAVA_executable' not in config.keys()):
            raise Exception("Config file must have a vaild JAVA_executable parameter")
        moa_path = config['MOA_path']
        java_executable = config['JAVA_executable']

        return (java_executable, moa_path)




def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="MOA Bulk Generator.")
    group = p.add_mutually_exclusive_group(required=False)
    group.add_argument("--datasets", "-d", type=str, help="Specify the txt file containing the datasets to generate.")
    group.add_argument("--interactive","-i", action="store_true", help="Run interactive configuration.")
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
        if(args.interactive):
            print(args.out)
            moa = MOABulkGenerator(interacitve=True, out_path=args.out)
        else:
            moa = MOABulkGenerator(interacitve=False, datasets_file=args.datasets, out_path=args.out)
        moa.run()


if __name__ == "__main__":
    main()
