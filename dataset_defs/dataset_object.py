import math
import re
from .types import DatasetDict


class DatasetObject:
    generator: str
    classification_functions: list[int]
    drift_points: list[int]
    drift_widths: list[int]
    num_of_samples: int
    GENERATORS = {
        "Agrawal": {"fullName": "AgrawalGenerator", "functions": list(range(1, 12))},
        "STAGGER": {"fullName": "STAGGERGenerator", "functions": list(range(1, 4))},
        "SEA": {"fullName": "SEAGenerator", "functions": list(range(1, 5))},
    }

    def __init__(
        self,
        *,
        generator: str | None = None,
        classification_functions: list[int] | None = None,
        drits_points: list[int] | None = None,
        drift_widths: list[int] | None = None,
        number_of_samples: int | None = None,
        dataste_string: str | None = None,
        dataset_dict: DatasetDict | None = None,
    ):
        self.generator = generator
        self.classification_functions = classification_functions
        self.drift_points = drits_points
        self.drift_widths = drift_widths
        self.num_of_samples = number_of_samples
        if dataste_string is not None:
            self._from_string(dataste_string)
        elif dataset_dict is not None:
            self._from_dict(dataset_dict)
        self._validate()

    def _from_string(self, generator_string: str):
        pattern = re.compile(
            r"^(?P<name>[^_]+)"  # generator name (no underscores)
            r"_f_(?P<f_vals>\d+(?:_\d+)*)"  # f values (one or more ints separated by _)
            r"(?:_p_(?P<p_vals>\d+(?:_\d+)*)_w_(?P<w_vals>\d+(?:_\d+)*))?"  # optional p and w blocks
            r"_s_(?P<s>\d+)$"  # final s integer
        )

        m = pattern.fullmatch(generator_string)
        if not m:
            raise Exception(f"Invalid string for pasrsing:: {generator_string}")

        self.generator = m.group("name")
        self.classification_functions = [int(x) for x in m.group("f_vals").split("_")]
        if m.group("p_vals"):
            self.drift_points = [int(x) for x in m.group("p_vals").split("_")]
            self.drift_widths = [int(x) for x in m.group("w_vals").split("_")]
        else:
            self.drift_points = []
            self.drift_widths = []
        self.num_of_samples = int(m.group("s"))

    def _from_dict(self, generation_dict: DatasetDict):
        if not isinstance(generation_dict, dict):
            raise Exception("Value passed to dataset object is not a dictionary")
        all_keys = {
            "generator",
            "classification_functions",
            "drift_points",
            "drift_widths",
            "num_of_samples",
        }
        shorthand_keys = {"generator", "classification_functions", "num_of_samples"}
        if (
            generation_dict.keys() != all_keys
            and generation_dict.keys() != shorthand_keys
        ):
            raise Exception(
                f"Dictionary passed to dataset object does not comply to the necessary structure. Accepted structures: \n {all_keys} \n {shorthand_keys}"
            )

        if not isinstance(generation_dict["classification_functions"], list):
            raise Exception("classification_functions field must be a list")
        if "drift_points" in generation_dict.keys() and not isinstance(
            generation_dict["drift_points"], list
        ):
            raise Exception("drift_points field must be a list")
        if "drift_widths" in generation_dict.keys() and not isinstance(
            generation_dict["drift_widths"], list
        ):
            raise Exception("drift_widths field must be a lis")

        self.generator = generation_dict["generator"]
        self.classification_functions = generation_dict["classification_functions"]
        if "drift_points" in generation_dict.keys():
            self.drift_points = generation_dict["drift_points"]
            self.drift_widths = generation_dict["drift_widths"]
        self.num_of_samples = int(generation_dict["num_of_samples"])

    def to_string(self) -> str:
        self._validate()
        res = self.generator + "_"

        res += "f_"
        for function in self.classification_functions:
            res += str(function) + "_"

        if len(self.drift_points):
            res += "p_"
            for point in self.drift_points:
                res += str(point) + "_"

        if len(self.drift_widths):
            res += "w_"
            for width in self.drift_widths:
                res += str(width) + "_"

        res += "s_" + str(self.num_of_samples)
        return res

    def get_generator_name(self) -> str:
        return DatasetObject.GENERATORS[self.generator]["fullName"]

    def _validate(self):
        if self.generator not in DatasetObject.GENERATORS.keys():
            raise Exception(
                f'Invalid generator type "{self.generator}". Supported generators: {DatasetObject.GENERATORS.keys()}'
            )
        if len(self.classification_functions) <= 0:
            raise Exception(f"Must provide at least one classification function")

        for funct in self.classification_functions:
            if not isinstance(funct, int):
                raise Exception("All classification function Values mustt be integers")
            if not funct in DatasetObject.GENERATORS[self.generator]["functions"]:
                raise Exception(
                    f"Provided classification function is not supported by this generator. Available functions: {DatasetObject.GENERATORS[self.generator]['functions']}"
                )
        for point in self.drift_points:
            if not isinstance(point, int):
                raise Exception("All drift point values mustt be integers")
        for width in self.drift_widths:
            if not isinstance(width, int):
                raise Exception("All drift width values mustt be integers")

        # Each concept drift requires two classification functions(which can overlap), so the number of functions must be one more than the number of drits
        if (len(self.drift_points) != len(self.drift_widths)) or (
            len(self.drift_points) != len(self.classification_functions) - 1
        ):
            raise Exception(
                "The number of classification functions and drifts mismatch. There must be one more classification function than the number of drift points"
            )
        # Make sure the drift points are strictly raising
        for i in range(1, len(self.drift_points)):
            if self.drift_points[i - 1] >= self.drift_points[i]:
                raise Exception("drift points values must be strictly raising")
        # Make sure there is no overlap in the drift area(and that width is over 0)
        drift_areas = []
        for i in range(len(self.drift_points)):
            if self.drift_widths[i] < 1:
                raise Exception("drift width values must be above 0")
            ofset = math.ceil(self.drift_widths[i] / 2)
            lower = self.drift_points[i] - ofset
            upper = self.drift_points[i] + ofset
            if lower < 1:
                raise Exception(
                    "One of the drift areas would begin before first sample"
                )
            if upper >= self.num_of_samples:
                raise Exception(
                    "One of the drift areas would end after the last sample"
                )
            if i > 0:
                if max(drift_areas) >= lower:
                    raise Exception(f"One of the drift areas would lead to an overlap")

            drift_areas.append(lower)
            drift_areas.append(upper)

        if self.num_of_samples <= 0:
            raise Exception("Must specify number of samples bigger than one")
