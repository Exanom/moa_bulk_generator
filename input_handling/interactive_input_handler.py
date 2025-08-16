from ..dataset_defs import DatasetObject
from .utils import handle_input, clear_console
from .types import CommandDict
from typing import Dict
import uuid

class InteractiveInputHanlder():
    _datasets: list[DatasetObject]
    _commands: Dict[int,CommandDict] 
    _running: bool

    def __init__(self, datasets: list[DatasetObject]):
        self._datasets = datasets
        self._commands = {
            1: {'name':'Add datset', 'action': self._add_dataset},
            2:{'name':'Remove dataset', 'action':self._remove_dataset},
            3:{'name':'Write to file', 'action':self._write_to_file},
            4:{'name':'Clear list','action':self._clear_list},
            5:{'name':'Generate datasets', 'action':self._generate},
            6:{'name':'Exit', 'action':self._exit}
        }
        self._running = False
        
    def run(self) -> list[DatasetObject]:
        self._running = True
        command_keys = [str(x) for x in self._commands.keys()]

        clear_console()
        while(self._running):
             self._print_headline()
             self._print_commads()
             inp = handle_input('Input command:', command_keys, command_keys[-1])
             clear_console()
             self._commands[int(inp)]['action']()
             
        
        return self._datasets


    def _print_headline(self):
        print('INTERACTIVE MOA BULK GENERATOR')
        print('==========================')
        print('Datasets to generate:')
        for i, d in enumerate(self._datasets):
                print(f'\t{i+1}.{d.to_string()}')
        print('==========================')
    
    def _print_commads(self):
         print('Commands:')
         for key, command in self._commands.items():
              print(f'\t{key} - {command['name']}')

    #TODO do this
    def _add_dataset(self):
         pass
    
    def _remove_dataset(self):
         if(len(self._datasets) < 1):
              return
         self._print_headline()

         indices = [str(x) for x in range(1, len(self._datasets)+1)]
         to_delete = handle_input('Specify index of the dataset to delete:',indices,indices[0])
         self._datasets.pop(int(to_delete)-1)
    
    def _write_to_file(self):
        path = handle_input('File path to save: ', None)
        dat = DatasetObject()
        dat.from_base_values('Agrawal',[1,2],[5],[1],number_of_samples=10)
        self._datasets.append(dat)
        try:
            with open(path, 'w') as f:
                 for dataset in self._datasets:
                      f.write(dataset.to_string() +'\n')
        except Exception as e:
            filename = f'{uuid.uuid4()}.txt'
            
            print(e)
            save = handle_input(f'An error has occured during file write. Write datasets to {filename}?(Y/N)')
            if(save == 'y'):
                with open(filename, 'w') as f:
                    for dataset in self._datasets:
                        f.write(dataset.to_string() + '\n')
            self._datasets = []
            self._running = False
         

    def _clear_list(self):
         self._datasets = []
    
    def _generate(self):
         self._running = False
         print('Generating...')
    
    def _exit(self):    
         self._datasets = []
         self._running = False
         print('Exiting...')

        