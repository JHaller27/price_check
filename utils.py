import re


def retry(run_fn, check_fn, retry_count):
	for _ in range(retry_count):
		resp = run_fn()
		if check_fn(resp):
			return resp
	return None


LOCALE_REGEX = re.compile(r'\w{2}(-\w+)*-\w{2}')
BIGID_REGEX = re.compile(r'[bcdfghjklmnpqrstvwxyzBCDFGHJKLMNPQRSTVWXYZ\d]{12}')


def get_params_from_livesite(url: str) -> tuple[str, str]:
	locale_match = LOCALE_REGEX.search(url)
	if locale_match is None:
		locale = input('Manually enter locale> ')
	else:
		locale = locale_match.group(0)

	bigid_match = BIGID_REGEX.search(url)
	if bigid_match is None:
		bigid = input('Manually enter bigid> ')
	else:
		bigid = bigid_match.group(0)

	return bigid, locale

