def retry(run_fn, check_fn, retry_count):
    for _ in range(retry_count):
        resp = run_fn()
        if check_fn(resp):
            return resp
    return None

