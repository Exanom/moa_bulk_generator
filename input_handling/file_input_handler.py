from ..dataset_defs import DatasetObject
from .utils import handle_input


class FileInputHandler:
    """
    A class containing all the functionality related to loading datasets definitions from txt file.
    """
    _dataset_path: str
    _dataset_strings: list[str]
    _dataset_objects: list[DatasetObject]

    def __init__(self, dataset_path: str):
        """
        FileInputHandler initialization. 

        Parameters:
            dataset_path (str): A path to a txt file containing the datasets definitions
        """
        self._dataset_path = dataset_path
        self._dataset_strings = []
        self._dataset_objects = []

    def load_validate_file(self) -> list[DatasetObject]:
        """
        Loads and parses the strings within the txt file. In case of any invalid entries, will require user input to decide course of action.

        Returns:
            list[DatasetObject]: A list of dataset definition objects based on the file contents. If there were no valid datasets defintions within the file, returns an empty list.
        """
        datasets = []
        with open(self._dataset_path) as f:
            datasets = f.read().splitlines()
        # remove empty strings
        self._dataset_strings = list(filter(None, datasets))

        errors = []
        for i, dataset in enumerate(self._dataset_strings):
            try:
                d_object = DatasetObject(dataste_string=dataset)
                self._dataset_objects.append(d_object)
            except Exception as e:
                errors.append(f"line {i+1}: {dataset} -> error: {e}")
        print("")

        if len(self._dataset_objects) > 0:
            print("Datasets to generate:")
            for i, d in enumerate(self._dataset_objects):
                print(f"\t{i}.{d.to_string()}")
        if len(errors) > 0:
            print("Script encoutered following errors in the dataset file:")
            for error in errors:
                print("\t" + error)

        if len(self._dataset_objects) < 1:
            print("No datasets to generate")
        to_generate = "y"
        if len(errors) > 0 and len(self._dataset_objects) > 0:
            to_generate = handle_input(
                f"Load the remaining({len(datasets)}) datasets?(Y/N)"
            )
        if to_generate == "n":
            self._dataset_objects = []

        return self._dataset_objects
