import argparse
from typing import List, Dict, Union

import requests

from bs4 import BeautifulSoup

from constants import FieldNameConstants, CurrencyConstants
from utils import (
    get_constant_class_values,
    parse_file_input_urls,
    convert_data_to_csv,
    is_number
)


def should_skip_element(element: BeautifulSoup) -> bool:
    attributes = element.get_attribute_list('class')
    if element.get('data-no-tax-price') is None:
        return True

    if 'hidden' in attributes:
        return True

    if not is_number(element.get('data-no-tax-price')):
        return True

    return False


def get_html_page(url: str, currency: str) -> BeautifulSoup:
    accepted_currencies = get_constant_class_values(CurrencyConstants)
    if currency not in accepted_currencies:
        raise Exception(f'Currency should be one from recognized types: {" ".join(accepted_currencies)}')

    response = requests.get(
        url=url,
        cookies={'currency': currency},
        timeout=5
    )

    if response.status_code != 200:
        raise Exception(f'Is site working? Got status code `{response.status_code}`.')

    return BeautifulSoup(response.text, features='html.parser')


def parse_min_price(url: str, currency: str):
    prices = []

    page = get_html_page(url=url, currency=currency)
    game_title: str = page.find('h1').get_text(strip=True)

    print(f'Getting lowest price in {currency} for: {game_title} / {url}...')

    for element in page.find_all('span'):
        if should_skip_element(element):
            continue

        price = float(element.get('data-no-tax-price'))
        prices.append(round(price, 2))

    result = {
        FieldNameConstants.URL: url,
        FieldNameConstants.GAME_NAME: game_title,
        FieldNameConstants.LOWEST_PRICE: min(prices) if prices else 'N/A',
        FieldNameConstants.CURRENCY: currency
    }

    return result


def main(path_to_urls_file: str, currency: str):
    all_results: List[Dict[str, Union[int, str]]] = []

    urls = parse_file_input_urls(path_to_urls_file)
    for url in urls:
        data = parse_min_price(url=url, currency=currency)
        all_results.append(data)

    convert_data_to_csv(all_results)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Get lowest prices for given Kinguin urls.')
    parser.add_argument(
        'file_name',
        type=str,
        metavar='file',
        help='path to file with urls.'
    )
    parser.add_argument(
        '-c', '--currency',
        default=CurrencyConstants.EURO,
        type=str,
        help='currency of fetched prices.'
    )

    args = parser.parse_args()

    main(
        path_to_urls_file=args.file_name,
        currency=args.currency
    )
