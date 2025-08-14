import json
import os
from .moa_handling.moa_handler import MOAHandler
from .input_handling.file_input_handler import FileInputHanlder

class MOABulkGenerator():
    _moa_handler: MOAHandler = None
    _interactive: bool
    _dataset_file_path: str
    _validation_mode: bool
    _out_path: str


    def __init__(self, interactive:bool = True, config_path='config.json', datasets_file:str = '', out_path:str = 'results',  validation_mode: bool = False):
        self._interactive = interactive
        self._dataset_file_path = datasets_file
        self._validation_mode = validation_mode
        
        if(out_path is not None):
            self._out_path = out_path
        else: 
            self._out_path = 'results'
        if(config_path is None):
            config_path='config.json'

        java_executable, moa_path = self._load_config(config_path)
        self._moa_handler = MOAHandler(java_executable, moa_path)
        
    def run(self):
        datasets = []
        if(not self._interactive):
            file_handler = FileInputHanlder(self._dataset_file_path)
            datasets = file_handler.load_validate_file()
        
        self._moa_handler.generate(datasets, self._out_path)

    def _load_config(self,config_path:str) -> tuple[str,str]:
        config = None
        moa_path = None
        java_path = None

        if(not os.path.isfile(config_path)):
            tmp = {
                'MOA_path':'Path to the main moa directory that contains the bin directory',
                'Java_path':'path to execute java program(normally just "java" should work)'
            }
            with open(config_path, 'w') as f:
                json.dump(tmp,f)
            raise Exception(f'Config file not found. New Config file created at {os.path.abspath(config_path)}. Input required data there')
        with open(config_path) as f:
            config = json.load(f)
        if('MOA_path' not in config.keys()):
            raise Exception("Config file must have a vaild MOA_path parameter")
        if('Java_path' not in config.keys()):
            raise Exception("Config file must have a vaild Java_path parameter")
        moa_path = config['MOA_path']
        java_path = config['Java_path']

        return (java_path, moa_path)