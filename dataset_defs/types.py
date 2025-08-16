from typing import TypedDict, NotRequired


class DatasetDict(TypedDict):
    generator: str
    classification_functions: list[int]
    drift_points: NotRequired[list[int]]
    drift_widths: NotRequired[list[int]]
    num_of_samples: int
