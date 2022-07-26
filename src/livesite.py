from utils import *

import aiohttp
import re
from bs4 import BeautifulSoup
from dataclasses import dataclass
from typing import Optional


@dataclass
class PricingInfo:
	url: str
	price: str
	promobar_message: Optional[str]


async def try_get_html(session: aiohttp.ClientSession, url: str) -> Optional[BeautifulSoup]:
	async with session.get(url) as resp:
		if resp.status != 200:
			return None
		text = await resp.text()
		return BeautifulSoup(await resp.text(), features='html.parser')


async def get_html(session: aiohttp.ClientSession, url: str) -> Optional[BeautifulSoup]:
	for _ in range(3):
		soup = await try_get_html(session, url)
		if soup is not None:
			return soup

	return None


def get_price(soup: BeautifulSoup) -> Optional[str]:
	price_container = soup.find("div", {'class': 'pi-price-text', 'id': re.compile('ProductPrice_productPrice_')})
	if price_container is None:
		return None

	price_el = price_container.span
	if price_el is None:
		price_el = price_container.h3
		if price_el is None:
			return None

	return price_el.text


def get_promo_price(soup: BeautifulSoup) -> Optional[str]:
	bar_containers = soup.find_all("div", {'class': 'pi-promotion-bar'})
	for bar_container in bar_containers:
		if bar_container is None:
			continue

		message = bar_container.find("div", {'class': 'message'})
		if message is None:
			continue

		message = message.div

		price_el = message.span
		return price_el.text


async def get_pricing(session: aiohttp.ClientSession, url: str) -> Optional[PricingInfo]:
	soup = await get_html(session, url)

	if soup is None:
		return None

	price = get_price(soup)
	promo_price = get_promo_price(soup)

	return PricingInfo(url, clean_string(price), clean_string(promo_price))
