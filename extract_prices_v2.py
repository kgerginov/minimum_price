import csv
import argparse
from typing import List, Dict, Union

import requests

from bs4 import BeautifulSoup

from constants import FieldNameConstants, CurrencyConstants
from utils import get_constant_class_values, should_skip_element


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


def parse_min_price(urls: List[str], currency: str):
    all_results: List[Dict[str, Union[int, str]]] = []

    for url in urls:
        prices_per_url = []

        page = get_html_page(url=url, currency=currency)
        game_title: str = page.find('h1').get_text().strip()

        print(f'Getting lowest price for: {game_title} / {url}...')

        for element in page.find_all('span'):
            if should_skip_element(element):
                continue

            price = float(element.get('data-no-tax-price'))
            prices_per_url.append(round(price, 2))

        all_results.append({
            FieldNameConstants.URL: url,
            FieldNameConstants.GAME_NAME: game_title,
            FieldNameConstants.LOWEST_PRICE: min(prices_per_url) if prices_per_url else 'N/A',
            FieldNameConstants.CURRENCY: currency
        })

    return all_results


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


def main(path_to_urls_file: str, currency: str):
    urls = parse_file_input_urls(path_to_urls_file)
    data = parse_min_price(urls=urls, currency=currency)
    convert_data_to_csv(data)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Get lowest prices for given Kinguin urls.')
    parser.add_argument(
        'file_name',
        type=str,
        metavar='file',
        help='path to file with urls.'
    )
    parser.add_argument(
        '--currency', '-c',
        default=CurrencyConstants.EURO,
        type=str,
        help='currency of fetched prices.'
    )

    args = parser.parse_args()

    main(
        path_to_urls_file=args.file_name,
        currency=args.currency
    )

