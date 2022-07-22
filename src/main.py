from utils import get_params_from_livesite
from scrape import get_price
from connectors import PricingInfo, get_connector_prices

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
	live_price: str
	connector_url: str
	connector_prices: list[PricingInfo]

	@cached_property
	def first_match(self) -> Optional[PricingInfo]:
		for c in self.connector_prices:
			if self.live_price == c.current_price:
				return c
		return None


async def compare(live_url: str) -> Result:
	print('<', end='')
	async with aiohttp.ClientSession() as session:
		livesite_task = get_price(session, live_url)

		bigId, locale = get_params_from_livesite(live_url)
		pricing_list = [p async for p in get_connector_prices(session, bigId, locale)]

		livesite_price = await livesite_task
	print('>', end='')

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


def print_result(r: Result) -> None:
	print('Live site:', r.live_url)
	print('Connector:', r.connector_url)
	tbl = Table('Match', 'SkuId', 'Price', box=box.SIMPLE)
	tbl.add_row('', 'Live site', r.live_price)
	for c in r.connector_prices:
		tbl.add_row('[green]:heavy_check_mark:[/green]' if c.current_price == r.live_price else '[red]x[/red]', c.sku_id, c.current_price)
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
