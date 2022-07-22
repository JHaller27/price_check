from utils import get_params_from_livesite
from scrape import PricingInfo as LiveSitePricingInfo, get_pricing
from connectors import PricingInfo as ConnectorPricingInfo, get_connector_prices

import aiohttp
from functools import cached_property
import asyncio
from dataclasses import dataclass
from typing import Optional

from rich import print as rprint
from rich.table import Table
from rich import box


@dataclass
class Result:
	live_url: str
	live_price: LiveSitePricingInfo
	connector_url: str
	connector_prices: list[ConnectorPricingInfo]

	@cached_property
	def first_match(self) -> Optional[ConnectorPricingInfo]:
		for c in self.connector_prices:
			if self.live_price == c.current_price:
				return c
		return None


async def compare(live_url: str) -> Result:
	print('<', end='')
	async with aiohttp.ClientSession() as session:
		livesite_task = get_pricing(session, live_url)

		bigId, locale = get_params_from_livesite(live_url)
		pricing_list = [p async for p in get_connector_prices(session, bigId, locale)]

		livesite_price = await livesite_task
	print('>', end='')

	return Result(live_url, livesite_price, pricing_list[0].url, pricing_list)


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


def get_match_emoji(test: bool) -> str:
	return '[green]:heavy_check_mark:[/green]' if test else '[red]x[/red]'


def print_result(r: Result) -> None:
	print('Live site:', r.live_url)
	print('Connector:', r.connector_url)

	tbl = Table('Match', 'SkuId', 'Price', 'Promobar', box=box.SIMPLE)
	tbl.add_row('', 'Live site', r.live_price.price, r.live_price.promobarPrice)

	for c in r.connector_prices:
		tbl.add_row(get_match_emoji(c.current_price == r.live_price), c.sku_id, c.current_price, c.promobar_message or '-')

	rprint(tbl)


async def main():
	urls = get_urls()

	print("Gathering results...")
	results: list[Result] = await asyncio.gather(*[compare(url) for url in urls])

	for r in results:
		print()
		print_result(r)

	if len(results) == 0:
		rprint("[yellow]No results![/yellow]")
		return


if __name__ == '__main__':
	asyncio.run(main())
