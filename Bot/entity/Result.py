from dataclasses import dataclass


@dataclass
class Result:
    value: object
    result: bool
    error_message: str