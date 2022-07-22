from utils import *

import requests
import re
from bs4 import BeautifulSoup


def try_get_price(url: str) -> str:
	resp = retry(lambda: requests.get(url), lambda r: r.ok, 3)
	if resp is None:
		return 'NotFound'

	soup = BeautifulSoup(resp.text, features='html.parser')

	price_container = soup.find("div", {'class': 'pi-price-text', 'id': re.compile('ProductPrice_productPrice_')})
	price_el = price_container.span
	return price_el.text


async def get_price(url: str) -> str:
	return retry(lambda: try_get_price(url), lambda p: p is not None, 3)


def main():
	url = 'https://www.microsoft.com/hu-hu/microsoft-365/p/excel/CFQ7TTC0HR4R'
	price = get_price(url)
	print(price)


if __name__ == '__main__':
	main()
