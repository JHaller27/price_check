import json


with open('./data/promobarbigids.json') as fp:
	obj = json.load(fp)
promobar_map = {k.lower(): v for k, v in obj.items()}

def get_promobar_id(big_id: str):
	return promobar_map.get(big_id.lower())


if __name__ == '__main__':
	from utils import input_lines
	from rich import print

	big_ids = input_lines()
	if len(big_ids) == 1:
		print(get_promobar_id(big_ids[0]))
	else:
		from rich.table import Table

		tbl = Table('BigId', 'PromobarBigId')
		for big_id in big_ids:
			tbl.add_row(big_id, str(get_promobar_id(big_id)))
		print(tbl)
