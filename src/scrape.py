import aiohttp
import re
from bs4 import BeautifulSoup
from typing import Optional


async def try_get_html(session: aiohttp.ClientSession, url: str) -> Optional[str]:
	async with session.get(url) as resp:
		if resp.status != 200:
			return None
		return await resp.text()


async def try_get_price(session: aiohttp.ClientSession, url: str) -> Optional[str]:
	text = None

	for _ in range(3):
		text = await try_get_html(session, url)
		if text is not None:
			break

	if text is None:
		return None

	soup = BeautifulSoup(text, features='html.parser')

	price_container = soup.find("div", {'class': 'pi-price-text', 'id': re.compile('ProductPrice_productPrice_')})
	if price_container is None:
		return None

	price_el = price_container.span
	return price_el.text


async def get_price(session: aiohttp.ClientSession, url: str) -> str:
	print('l', end='')
	retv = await try_get_price(session, url)
	print('L', end='')
	return retv
