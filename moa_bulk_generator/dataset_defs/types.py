from typing import TypedDict, NotRequired


# TODO add seed key
class DatasetDict(TypedDict):
    generator: str
    classification_functions: list[int]
    drift_points: NotRequired[list[int]]
    drift_widths: NotRequired[list[int]]
    num_of_samples: int
    seed_value: int


class GeneratorInfoDict(TypedDict):
    fullName: str
    functions: list[int]
