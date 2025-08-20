from ..dataset_defs import DatasetObject
from .utils import handle_input, clear_console, handle_input_int
from .types import CommandDict
from typing import Dict
import uuid



class InteractiveInputHandler:
    """
    A class containing all the functionality related to interactive CLI of the script. Supports following functionalities:
        1. List datasets to generate
        2. Manually add datasets to generate
        3. Manually remove chosen datasets from generation
        4. Display information for a chosen dataset
        5. Write list of current datasets to a txt file
        6. Remove all datasets from the list
        7. Generate listed datasets
    """
    _datasets: list[DatasetObject]
    _commands: Dict[int, CommandDict]
    _running: bool

    def __init__(self, datasets: list[DatasetObject]):
        """
        InteractiveInputHandler initialization. 

        Parameters:
            datasets (list[DatasetObject]): A list of datasets to be initalized for the CLI. Can be empty
        """
        self._datasets = datasets
        self._commands = {
            "a": {"name": "Add datset", "action": self._add_dataset},
            "r": {"name": "Remove dataset", "action": self._remove_dataset},
            "i": {"name": "Inspect dataset", "action": self._inspect_dataset},
            "w": {"name": "Write to file", "action": self._write_to_file},
            "c": {"name": "Clear list", "action": self._clear_list},
            "g": {"name": "Generate datasets", "action": self._generate},
            "q": {"name": "Quit", "action": self._exit},
        }
        self._running = False

    def run(self) -> list[DatasetObject]:
        """
        Handles all the interation with the user. Provides the current state of the datasets and handles usage of predefined commands.

        Returns:
            list[DatasetObject]: A list containing all the datasets reflecting the end state of the user intearaction. Returns an empty list if user quits without generating
        """
        self._running = True

        clear_console()
        while self._running:
            self._print_headline()
            self._print_commads()
            inp = handle_input("Input command:", list(self._commands.keys()), "q")
            clear_console()
            self._commands[inp]["action"]()

        return self._datasets

    def _print_headline(self):
        print("INTERACTIVE MOA BULK GENERATOR")
        print('All command executions will be logged in log.txt file in the library directory')
        print("==========================")
        print("Datasets to generate:")
        for i, d in enumerate(self._datasets):
            print(f"\t{i+1}.{d.to_string()}")
        print("==========================")

    def _print_commads(self):
        print("Commands:")
        for key, command in self._commands.items():
            print(f"\t{key} - {command['name']}")

    def _add_dataset(self):
        self._print_headline()
        print("Generators:")
        generators = {}
        for i, generator in enumerate(DatasetObject.GENERATORS.keys()):
            print(f"\t{i+1} - {generator}")
            generators[str(i + 1)] = generator
        indices = [str(x) for x in generators.keys()]
        inp = handle_input("Choose generator: ", indices, indices[0])
        gen = generators[inp]

        functions = []
        functions_values = [str(x) for x in DatasetObject.GENERATORS[gen]["functions"]]
        print(f"Functions available for this {gen} generator: {functions_values}")
        fun1 = handle_input(
            "Choose first classification function: ",
            functions_values,
            functions_values[0],
        )
        functions.append(int(fun1))

        add_drift = handle_input("Introduce Concept Drift?(Y/N)")
        drift_points = []
        max_drift_point = 0
        drift_widths = []
        while add_drift == "y":
            fun2 = handle_input(
                "Choose the next classification function: ",
                functions_values,
                functions_values[0],
            )
            functions.append(int(fun2))

            if len(drift_points) > 0:
                max_drift_point = drift_points[-1]
            drift_point = handle_input_int(
                "Choose the central position in which drift will occur: ",
                min_val=max_drift_point,
            )
            drift_points.append(drift_point)

            drift_width = handle_input_int(
                "Choose the number of samples over which the drift will occur: ",
                min_val=0,
            )
            drift_widths.append(drift_width)

            add_drift = handle_input("Introduce another Concept Drift?(Y/N)")

        num_of_samples = handle_input_int(
            "Specify the number of samples to generate: ", min_val=max_drift_point
        )

        try:
            dataset = DatasetObject(
                generator=gen,
                classification_functions=functions,
                drits_points=drift_points,
                drift_widths=drift_widths,
                number_of_samples=num_of_samples,
            )
            clear_console()
            self._inspect_dataset(dataset)
            to_add = handle_input("Add this dataset to the list?(Y/N)")
            if to_add == "y":
                self._datasets.append(dataset)
            clear_console()

        except Exception as e:
            print(f"Dataset is invalid: {e}")
            handle_input("Press enter to continue...", None)
            clear_console()

    def _remove_dataset(self):
        if len(self._datasets) < 1:
            return
        self._print_headline()

        indices = [str(x) for x in range(1, len(self._datasets) + 1)]
        to_delete = handle_input(
            "Specify index of the dataset to delete:", indices, indices[0]
        )
        clear_console()
        self._datasets.pop(int(to_delete) - 1)

    def _inspect_dataset(self, dataset_in: DatasetObject | None = None):
        if dataset_in is not None:
            dataset = dataset_in
        else:
            if len(self._datasets) < 1:
                return
            self._print_headline()

            indices = [str(x) for x in range(1, len(self._datasets) + 1)]
            to_show = handle_input(
                "Specify index of the dataset to inspect:", indices, indices[0]
            )
            dataset = self._datasets[int(to_show) - 1]

        print(f"Name: {dataset.to_string()}")
        print(f'Generaot: {dataset.get_generator_name()}')
        if len(dataset.classification_functions) > 1:
            for i in range(len(dataset.drift_points)):
                print(f"Concept Drfit {i}:")
                print(
                    f"\t Classification functions: {dataset.classification_functions[i]}->{dataset.classification_functions[i+1]}"
                )
                print(f"\t Drift point: {dataset.drift_points[i]}")
                print(f"\t Drift width: {dataset.drift_widths[i]}")
        else:
            print(f"Classification function: {dataset.classification_functions[0]}")
        print(f"Number of samples: {dataset.num_of_samples}")

        if dataset_in is None:
            handle_input("Press enter to continue...", None)
            clear_console()

    def _write_to_file(self):
        path = handle_input("File path to save: ", None)
        try:
            with open(path, "w") as f:
                for dataset in self._datasets:
                    f.write(dataset.to_string() + "\n")
        except Exception as e:
            filename = f"{uuid.uuid4()}.txt"

            print(e)
            save = handle_input(
                f"An error has occured during file write. Write datasets to {filename}?(Y/N)"
            )
            if save == "y":
                with open(filename, "w") as f:  
                    for dataset in self._datasets:
                        f.write(dataset.to_string() + "\n")
            self._datasets = []
            self._running = False
        clear_console()

    def _clear_list(self):
        self._datasets = []

    def _generate(self):
        self._running = False
        print("Generating...")

    def _exit(self):
        self._datasets = []
        self._running = False
        print("Exiting...")
