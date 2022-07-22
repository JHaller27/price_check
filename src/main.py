from utils import get_params_from_livesite
from scrape import PricingInfo as LiveSitePricingInfo, get_pricing
from connectors import PricingInfo as ConnectorPricingInfo, SkuPricing, get_connector_prices

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
	live_price: LiveSitePricingInfo
	connector_pricing: ConnectorPricingInfo

	@cached_property
	def first_matching_sku_price(self) -> Optional[SkuPricing]:
		for c in self.connector_pricing.sku_pricing:
			if self.live_price == c.current_price:
				return c
		return None


async def compare(live_url: str) -> Result:
	async with aiohttp.ClientSession() as session:
		livesite_task = get_pricing(session, live_url)

		bigId, locale = get_params_from_livesite(live_url)
		connector_pricing = await get_connector_prices(session, bigId, locale)
		livesite_price = await livesite_task

	return Result(livesite_price, connector_pricing)


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


def compare_promo_messages(livesite: str, connector: str) -> bool:
	if '/' not in connector:
		return connector == livesite

	parts = connector.split('/')
	return all([p in livesite for p in parts])


def print_result(r: Result) -> None:
	print('Live site:', r.live_price.url)
	print('Connector:', r.connector_pricing.url)

	# Print sku pricing table
	tbl = Table('Match', 'SkuId', 'Price', box=box.SIMPLE)
	tbl.add_row('', 'Live site', r.live_price.price)

	for c in r.connector_pricing.sku_pricing:
		tbl.add_row(get_match_emoji(c.current_price == r.live_price.price), c.sku_id, c.current_price)

	rprint(tbl)

	# Print promobar table
	if r.live_price.promobar_message is None:
		print('No promobar')
		return

	tbl = Table('Match', 'Who', 'Promobar pricing', box=box.SIMPLE)
	tbl.add_row('', 'Live site', r.live_price.promobar_message)
	tbl.add_row(get_match_emoji(compare_promo_messages(r.live_price.promobar_message, r.connector_pricing.promobar_message)), 'Connector', r.connector_pricing.promobar_message)

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
