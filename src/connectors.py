import aiohttp
from dataclasses import dataclass
from typing import Optional


@dataclass
class PricingInfo:
	url: str
	sku_id: str
	current_price: str
	recurrence_price: Optional[str]


async def get_connector_prices(session: aiohttp.ClientSession, bigId: str, locale: str):
	url = f'https://www.microsoft.com/msstoreapiprod/api/buybox?bigId={bigId}&locale={locale}'
	async with session.get(url, headers={'ms-cv': 'JamesTest', 'x-ms-test': 'JamesTest'}) as resp:
		data = await resp.json()
		sku_info_dict = data['skuInfo']
		for sku_id, sku_info in sku_info_dict.items():
			price = sku_info['price']
			pi = PricingInfo(url, sku_id, price['currentPrice'], price.get('recurrencePrice'))
			yield pi
