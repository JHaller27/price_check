from utils import *

import requests
from dataclasses import dataclass
from typing import Optional
import re
from scrape import get_price
import asyncio


@dataclass
class PricingInfo:
	url: str
	sku_id: str
	current_price: str
	recurrence_price: Optional[str]


def get_connector_prices(bigId: str, locale: str):
	url = f'https://www.microsoft.com/msstoreapiprod/api/buybox?bigId={bigId}&locale={locale}'
	resp = retry(lambda: requests.get(url, headers={'ms-cv': 'JamesTest', 'x-ms-test': 'JamesTest'}), lambda r: r.ok, 3)
	if resp is None:
		return None

	data = resp.json()
	sku_info_dict = data['skuInfo']
	for sku_id, sku_info in sku_info_dict.items():
		price = sku_info['price']
		pi = PricingInfo(url, sku_id, price['currentPrice'], price.get('recurrencePrice'))
		yield pi


LOCALE_REGEX = re.compile(r'\w{2}(-\w+)*-\w{2}')
BIGID_REGEX = re.compile(r'[bcdfghjklmnpqrstvwxyzBCDFGHJKLMNPQRSTVWXYZ\d]{12}')


def get_params_from_livesite(url: str) -> tuple[str, str]:
	locale_match = LOCALE_REGEX.search(url)
	if locale_match is None:
		locale = input('Manually enter locale> ')
	else:
		locale = locale_match.group(0)

	bigid_match = BIGID_REGEX.search(url)
	if bigid_match is None:
		bigid = input('Manually enter bigid> ')
	else:
		bigid = bigid_match.group(0)

	return bigid, locale


async def main():
	while True:
		live_url = input('livesite url> ')

		livesite_task = asyncio.create_task(get_price(live_url))

		bigId, locale = get_params_from_livesite(live_url)
		pricing_list = [p for p in get_connector_prices(bigId, locale)]

		livesite_price = await livesite_task
		for p in pricing_list:
			if p.current_price == livesite_price:
				print(f'Match found for {bigId} {locale}')
				break
		else:
			print(f'No match found for {bigId} {locale}')
			print('    Livesite:  ', livesite_price)
			print('    Connectors:', end=' ')
			first = True
			for p in pricing_list:
				if first:
					first = False
				else:
					print('               ')
				print(p.current_price)


if __name__ == '__main__':
	asyncio.run(main())
