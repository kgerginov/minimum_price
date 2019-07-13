from typing import List

from bs4 import BeautifulSoup


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


def should_skip_element(element: BeautifulSoup) -> bool:
    attributes = element.get_attribute_list('class')
    if element.get('data-no-tax-price') is None:
        return True

    if 'hidden' in attributes:
        return True

    if not is_number(element.get('data-no-tax-price')):
        return True

    return False
