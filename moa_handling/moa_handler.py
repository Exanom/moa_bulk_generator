import subprocess
import os
from ..dataset_defs.dataset_object import DatasetObject
import datetime 
from ..input_handling.utils import handle_input

class MOAHandler():
    _java_executable:str  = None
    _MOA_path:str = None

    def __init__(self, java_executable:str, moa_path:str):
        self._java_executable = java_executable
        self._MOA_path = moa_path
        self._validate_MOA()

    def generate(self, datasets: list[DatasetObject], out_dir: str):
        if(not os.path.isdir(out_dir)):
            to_create = handle_input(f'{os.path.abspath(out_dir)} does not exist. Create directory(Y/N):')
            if(to_create == 'y'):
                os.mkdir(out_dir)
            else:
                return
        
        dir_name = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
        out_dir = out_dir + '/' +dir_name
        os.mkdir(out_dir)

        start_time = datetime.datetime.now()
        for dataset in datasets:
            print(f'generating {dataset.to_string()}...')
            self._generate_dataset(dataset,out_dir)
        run_time = datetime.datetime.now() - start_time
        with open(out_dir+'/log.txt', 'w') as f:
            f.write(f'generation time: {format(run_time)} \n' )
            f.write('datasets:\n')
            for dataset in datasets:
                f.write(dataset.to_string() +'\n')

    def _generate_dataset(self,dataset_object: DatasetObject, out_dir:str) -> bool:
        command = self._java_executable + ' -cp '+self._MOA_path+'\\lib\\moa.jar -javaagent:'+self._MOA_path+'\\lib\\sizeofag-1.1.0.jar moa.DoTask'
        generation_command = 'WriteStreamToARFFFile '
        if(len(dataset_object.classification_functions) == 1):
            generation_command += f'-s (generators.{dataset_object.get_generator_name()}) -f {str(dataset_object.classification_functions[0])})'
        else:
            generation_command += self._build_command(dataset_object.get_generator_name(),dataset_object.classification_functions, dataset_object.drift_points, dataset_object.drift_widths)

        generation_command += f' -f {out_dir}/{dataset_object.to_string()}.arrf -m {str(dataset_object.num_of_samples)}'
        full_command = f'{command} "{generation_command}"'
        
        try:
            subprocess.run(full_command,stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except:
            raise Exception(f'EXECUTION OF COMMAND FAILED: \n{full_command}')

    def _validate_MOA(self):
        command = self._java_executable + ' -cp '+self._MOA_path+'\\lib\\moa.jar -javaagent:'+self._MOA_path+'\\lib\\sizeofag-1.1.0.jar moa.DoTask'
        try:
            subprocess.run(command,stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception as e:
            raise Exception(f'MOA COULDN\'T BE CALLED. MAKE SURE THE INFORMATION WITHIN CONFIG FILE IS CORRECT. ATTEMPTED COMMAND:\n{command}')
        

    def _build_command(self, generator:str, classification_functions:list[int], drift_points:list[int], drift_widths:list[int]) -> str:
        res = '-s (ConceptDriftStream '
        if(len(drift_points) < 2):
            res += f'-s (generators.{generator} -f {str(classification_functions[0])}) -d (generators.{generator} -f {str(classification_functions[1])})'
        else:
            res += self._build_command(generator, classification_functions[:-1],drift_points[:-1],drift_widths[:-1]) + f' -d (generators.{generator} -f {str(classification_functions[-1])})'
        res += f' -p {drift_points[-1]} -w {drift_widths[-1]})'
        return res