from utils import *
from promobar import get_promobar_id

import aiohttp
from dataclasses import dataclass
from typing import Optional


@dataclass
class SkuPricing:
	sku_id: str
	current_price: str
	recurrence_price: Optional[str]


@dataclass
class PricingInfo:
	url: str
	sku_pricing: list[SkuPricing]
	promobar_message: Optional[str]


async def get_connector_json(session: aiohttp.ClientSession, url: str) -> dict:
	for _ in range(3):
		async with session.get(url, headers={'ms-cv': 'JamesTest', 'x-ms-test': 'JamesTest'}) as resp:
			if resp.status == 200:
				data = await resp.json()
				return data


async def get_connector_prices(session: aiohttp.ClientSession, big_id: str, locale: str) -> PricingInfo:
	# url = f'https://localhost:5001/api/buybox?bigId={big_id}&locale={locale}'
	url = f'https://microsoft.com/msstoreapiprod/api/buybox?bigId={big_id}&locale={locale}'

	promobar_big_id = get_promobar_id(big_id)
	if promobar_big_id is not None:
		url += f'&promobarbigId={promobar_big_id}'

	data = await get_connector_json(session, url)

	pi = PricingInfo(url, [], dict_deep_get(data, 'productInfo', 'promoBarPrice', 'message'))

	sku_info_dict = data.get('skuInfo')
	if sku_info_dict is None:
		return pi

	for sku_id, sku_info in sku_info_dict.items():
		price = sku_info['price']
		if price is None:
			pi.sku_pricing.append(SkuPricing(sku_id, 'Not found', None))
			return pi

		pi.sku_pricing.append(SkuPricing(sku_id, clean_string(price['currentPrice']), clean_string(price.get('recurrencePrice'))))

	return pi
