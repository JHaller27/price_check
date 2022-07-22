from utils import *

import aiohttp
import json
from dataclasses import dataclass
from typing import Optional


with open('./data/promobarbigids.json') as fp:
	obj = json.load(fp)
promobar_map = {k.lower(): v for k, v in obj.items()}


@dataclass
class SkuPricing:
	sku_id: str
	current_price: str
	recurrence_price: Optional[str]
	promobar_message: Optional[str]


@dataclass
class PricingInfo:
	url: str
	sku_pricing: list[SkuPricing]


async def get_connector_prices(session: aiohttp.ClientSession, big_id: str, locale: str) -> PricingInfo:
	promobar_big_id = promobar_map.get(big_id.lower())
	url = f'https://www.microsoft.com/msstoreapiprod/api/buybox?bigId={big_id}&locale={locale}'
	if promobar_big_id is not None:
		url += f'&promobarbigId={promobar_big_id}'

	pi = PricingInfo(url, [])

	async with session.get(url, headers={'ms-cv': 'JamesTest', 'x-ms-test': 'JamesTest'}) as resp:
		data = await resp.json()
		sku_info_dict = data['skuInfo']
		for sku_id, sku_info in sku_info_dict.items():
			price = sku_info['price']
			pi.sku_pricing.append(SkuPricing(sku_id, price['currentPrice'], price.get('recurrencePrice'), dict_deep_get(data, 'productInfo', 'promoBarPrice', 'message')))

	return pi
