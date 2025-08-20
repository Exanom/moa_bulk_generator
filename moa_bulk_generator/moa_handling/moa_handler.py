import os
from ..dataset_defs import DatasetObject
import datetime
from ..input_handling.utils import handle_input
from .utils import execute_command, sigmoid
from scipy.io import arff as scipy_arff
import pandas as pd
import random

class MOAHandler:
    """
    A class containing all the functionality related to interacting with Java tool MOA.
    """
    _java_executable: str = None
    _MOA_path: str = None

    def __init__(self, java_path: str, moa_path: str):
        """
        MOAHandler initialization. After initializing, attempts to execute MOA command in order to validate provided values.

        Parameters:
            java_path (str): A path required to execute java program on user machine. By default just "java"  
            moa_path (str): A path to the main directory of the MOA tool(directory containing the /bin directory),
        """
        self._java_executable = java_path
        self._MOA_path = moa_path
        self._validate_MOA()

    def generate(self, datasets: list[DatasetObject], out_dir: str):
        """
        Creates and executes commands necessary to generate specified datasets using MOA tool.

        Parameters:
            datasets (list[DatasetObject]): List of datasets to generate
            out_dir (str): Directory where the generated datasets and log file will be saved
        """
        if not os.path.isdir(out_dir):
            to_create = handle_input(
                f"{os.path.abspath(out_dir)} does not exist. Create directory(Y/N):"
            )
            if to_create == "y":
                os.mkdir(out_dir)
            else:
                return

        dir_name = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
        out_dir = out_dir + "/" + dir_name
        os.mkdir(out_dir)

        start_time = datetime.datetime.now()
        for dataset in datasets:
            print(f"generating {dataset.to_string()} to {out_dir}...")
            self._generate_dataset(dataset, out_dir)
        run_time = datetime.datetime.now() - start_time
        with open(out_dir + "/log.txt", "w") as f:
            f.write(f"generation time: {format(run_time)} \n")
            f.write("datasets:\n")
            for dataset in datasets:
                f.write(dataset.to_string() + "\n")

    def _generate_dataset(self, dataset_object: DatasetObject, out_dir: str):
        command = (
            self._java_executable
            + " -cp "
            + self._MOA_path
            + "\\lib\\moa.jar -javaagent:"
            + self._MOA_path
            + "\\lib\\sizeofag-1.1.0.jar moa.DoTask"
        )
        generation_command = "WriteStreamToARFFFile "
        if len(dataset_object.classification_functions) == 1:
            generation_command += f"-s (generators.{dataset_object.get_generator_name()}) -f {str(dataset_object.classification_functions[0])})"
        else:
            generation_command += self._build_command(
                dataset_object.get_generator_name(),
                dataset_object.classification_functions,
                dataset_object.drift_points,
                dataset_object.drift_widths,
            )

        generation_command += f" -f {out_dir}/{dataset_object.to_string()}.arrf -m {str(dataset_object.num_of_samples)}"
        full_command = f'{command} "{generation_command}"'

        try:
            execute_command(full_command)
        except:
            raise Exception(f"Execution of command failed: \n{full_command}")
        
        #Handle switching CD
        if(dataset_object.check_switching_drift()):
            self._handle_switching_drift(dataset_object, f'{out_dir}/{dataset_object.to_string()}.arrf')

    def _handle_switching_drift(self, dataset_object: DatasetObject, dataset_file: str):
        dataset, meta = scipy_arff.loadarff(dataset_file)
        dataset = pd.DataFrame(dataset)

        classes = dataset.iloc[:,-1].unique()
        for i in range(len(dataset_object.drift_points)):
            if(dataset_object.classification_functions[i] == dataset_object.classification_functions[i+1]):
                if(i<len(dataset_object.drift_points)-1):
                    self._apply_label_drift(dataset,dataset_object.drift_points[i],dataset_object.drift_widths[i],classes,dataset_object.drift_points[i+1],dataset_object.drift_widths[i+1])
                else:
                    self._apply_label_drift(dataset,dataset_object.drift_points[i],dataset_object.drift_widths[i],classes)
        
        self._overwrite_arff_file(dataset, meta, dataset_file)
     
    def _apply_label_drift(self, dataset: pd.DataFrame, p:int, w:int, classes:list[any], p_next: int|None = None, w_next: int|None = None):
        if len(classes)>0:
            perm = classes.copy()
            while((perm == classes).all()):
                random.shuffle(perm)
            mapping = {classes[i]: perm[i] for i in range(len(classes))}

        for i, sample in enumerate(dataset.iloc[:,-1], start=1):
            prob = sigmoid(i, p, w)

            #handle early exit if the next drift is likely to take effect
            if(p_next):
                #probabilty that the sample was classified by the next classification function
                next_prob = sigmoid(i,p_next,w_next)
                #If our current drift already occured, and its probability is within the margin of the probability of the next drift, break
                if(prob > 0.99 and prob-next_prob<0.01):
                    break
            if random.random() < prob:
                dataset.iloc[i-1,-1] = mapping.get(sample)
            
    #Important to fit format of arff file generated by MOA
    def _overwrite_arff_file(self, data:pd.DataFrame, meta_data: scipy_arff.MetaData, path:str):
        types = meta_data.types()

        file_data = []
        with open(path) as f:
            file_data = f.readlines()
        data_index = file_data.index('@data\n')

        data_arr = []
        for sample in data.values:
            data_str = ''
            for j, value in enumerate(sample):
                if(types[j] == 'nominal'):
                    data_str += value.decode('utf-8')
                else:
                    data_str += str(value)
                data_str+=','  
            data_arr.append(data_str + '\n')  

        file_data[data_index+2:] = data_arr
        with open(path, 'w') as f:
           f.writelines(file_data)



    def _validate_MOA(self):
        command = (
            self._java_executable
            + " -cp "
            + self._MOA_path
            + "\\lib\\moa.jar -javaagent:"
            + self._MOA_path
            + "\\lib\\sizeofag-1.1.0.jar moa.DoTask"
        )
        try:
            execute_command(command)
        except Exception as e:
            raise Exception(
                f"MOA couldn't be called. Make sure the information within config gile is correct. Attempted command:\n{command}"
            )

    def _build_command(
        self,
        generator: str,
        classification_functions: list[int],
        drift_points: list[int],
        drift_widths: list[int],
    ) -> str:
        res = "-s (ConceptDriftStream "
        if len(drift_points) < 2:
            res += f"-s (generators.{generator} -f {str(classification_functions[0])}) -d (generators.{generator} -f {str(classification_functions[1])})"
        else:
            res += (
                self._build_command(
                    generator,
                    classification_functions[:-1],
                    drift_points[:-1],
                    drift_widths[:-1],
                )
                + f" -d (generators.{generator} -f {str(classification_functions[-1])})"
            )
        res += f" -p {drift_points[-1]} -w {drift_widths[-1]})"
        return res
