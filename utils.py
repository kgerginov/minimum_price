import csv
from typing import List

from constants import FieldNameConstants


def get_constant_class_values(constants_class) -> List[str]:
    return [
        value
        for key, value in vars(constants_class).items()
        if not key.startswith('__')
    ]


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


def parse_file_input_urls(path_to_file):
    result = []
    with open(path_to_file, 'r') as file:
        for line in file.readlines():
            result.append(line.rstrip())

    return result


def convert_data_to_csv(games: List[dict]):
    fieldnames = get_constant_class_values(FieldNameConstants)
    with open('game_prices.csv', 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames)
        writer.writeheader()
        writer.writerows(games)
