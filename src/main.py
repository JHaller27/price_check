from utils import get_params_from_livesite
from scrape import get_price
from connectors import PricingInfo, get_connector_prices

import asyncio
from dataclasses import dataclass
from typing import Optional


@dataclass
class Result:
	live_url: str
	live_price: str
	connector_url: str
	connector_prices: list[PricingInfo]

	def get_first_diff(self) -> Optional[PricingInfo]:
		for c in self.connector_prices:
			if self.live_price != c.current_price:
				return c
		return None


async def compare(live_url: str) -> Result:
	livesite_task = asyncio.create_task(get_price(live_url))

	bigId, locale = get_params_from_livesite(live_url)
	pricing_list = [p for p in get_connector_prices(bigId, locale)]

	livesite_price = await livesite_task
	return Result(live_url, livesite_price, pricing_list[0].url, [p for p in pricing_list])


def get_urls():
	urls = []
	while True:
		try:
			live_url = input()
			if live_url == '':
				return urls
			urls.append(live_url)

		except EOFError:
			return urls


async def main():
	urls = get_urls()

	print("Gathering results...")
	results: list[Result] = await asyncio.gather(*[compare(url) for url in urls])

	diffs = [r for r in results if r.get_first_diff() is not None]

	if len(diffs) == 0:
		print("No diffs!")
		return

	for d in diffs:
		print('Live site:', d.live_url)
		print('   ', d.live_price)
		print('Connector:', d.connector_url)
		c = d.get_first_diff()
		print('   ', c.current_price, f'({c.sku_id})')
		print()


if __name__ == '__main__':
	asyncio.run(main())
