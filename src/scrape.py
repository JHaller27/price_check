from utils import *

import requests
import re
from bs4 import BeautifulSoup
from typing import Optional


def try_get_price(url: str) -> Optional[str]:
	resp = retry(lambda: requests.get(url), lambda r: r.ok, 3)
	if resp is None:
		return None

	soup = BeautifulSoup(resp.text, features='html.parser')

	price_container = soup.find("div", {'class': 'pi-price-text', 'id': re.compile('ProductPrice_productPrice_')})
	if price_container is None:
		return None

	price_el = price_container.span
	return price_el.text


async def get_price(url: str) -> str:
	return retry(lambda: try_get_price(url), lambda p: p is not None, 3)
