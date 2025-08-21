import json
import os
from .moa_handling import MOAHandler
from .input_handling import FileInputHandler, InteractiveInputHandler


class MOABulkGenerator:
    """
    Main entry class into the library, handles and delegates all aspects of acquring datasets defintions and generating datasets.

    ------
    Format for string dataset definitons:\n
        {generator}_f_{functions separated by _}_p_{points seprated by _}_w_{widths separated by _}_s_{number of samples}
    When no concept drift is to occur, the shorthand version should be used:\n
        {generator}_f_{function}_s_{number of samples}
    ------
    Requirements for datasets:
        1.The specified generator is supported
        2.There is at least one classification function specified
        3. All specified classification functions are supported
        4. All specified drift point and drift width values are integers
        5. There is exactly one more classification functions specified, than the number of drift point and width values 
        6. The specified drift point values must be strictly rising
        7. No drift area(centered on a given drift point, and expanding to width/2 around it in both directions) overlaps with any other drift area
        8. No drift area overlaps with begining or end point of geneation
        9. The specified number of samples is bigger than zero
    ------
    """
    _moa_handler: MOAHandler = None
    _interactive: bool
    _dataset_file_path: str
    _out_path: str

    def __init__(
        self,
        interactive: bool = False,
        config: str ="config.json",
        datasets: str = None,
        out: str = "results",
    ):
        """
        MOABulkGenerator initialization. 

        Parameters:
            interactive (bool): Enables/Disables the interactive CLI mode.
            config_path (str): Path to a json file containing the path to execute a java program on user machine and the path to the main MOA directory. If no such file exists, one will be generated on first call.
            dataset_file (str): Path to a txt file containing defintions of the datasets to be generated in the form of strings. The format of the strings is specified below
            out_path (str): Directory where the generated datasets and log file will be saved
        
        ------
        Format for string dataset definitons:\n
            {generator}_f_{functions separated by _}_p_{points seprated by _}_w_{widths separated by _}_s_{number of samples}
        When no concept drift is to occur, the shorthand version should be used:\n
            {generator}_f_{function}_s_{number of samples}
        ------
        """

        self._interactive = interactive
        self._dataset_file_path = datasets

        if out is not None:
            self._out_path = out
        else:
            self._out_path = "results"
        if config is None:
            config = "config.json"

        java_executable, moa_path = self._load_config(config)
        self._moa_handler = MOAHandler(java_executable, moa_path)

    def run(self):
        """
        Handles the main functionalities of the script, including loading definitions of datasets, invoking the CLI and generating the datasets. 
        """
        print('MOA BULK GENERATOR')
        print('All command executions will be logged in log.txt file in the library directory')
        datasets = []
        if self._dataset_file_path:
            file_handler = FileInputHandler(self._dataset_file_path)
            datasets = file_handler.load_validate_file()

        if self._interactive:
            input_handler = InteractiveInputHandler(datasets)
            datasets = input_handler.run()

        self._moa_handler.generate(datasets, self._out_path)

    def _load_config(self, config_path: str) -> tuple[str, str]:
        config = None
        moa_path = None
        java_path = None

        if not os.path.isfile(config_path):
            tmp = {
                "MOA_path": "Path to the main moa directory that contains the bin directory",
                "Java_path": 'path to execute java program(normally just "java" should work)',
            }
            with open(config_path, "w") as f:
                json.dump(tmp, f, indent=4)
            raise Exception(
                f"Config file not found. New Config file created at {os.path.abspath(config_path)}. Input required data there"
            )
        with open(config_path) as f:
            config = json.load(f)
        if "MOA_path" not in config.keys():
            raise Exception("Config file must have a vaild MOA_path parameter")
        if "Java_path" not in config.keys():
            raise Exception("Config file must have a vaild Java_path parameter")
        moa_path = config["MOA_path"]
        java_path = config["Java_path"]

        return (java_path, moa_path)
