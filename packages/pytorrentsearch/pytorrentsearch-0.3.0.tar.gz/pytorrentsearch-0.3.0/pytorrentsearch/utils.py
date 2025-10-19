def status(message: str):
    from sys import stderr

    print(f"[*] {message}", file=stderr)


def request(url: str, timeout=10):
    from urllib.request import Request, urlopen

    req = Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36"  # noqa: E501
        },
    )
    res = urlopen(req, timeout=timeout)
    return res


def get_url_content(url: str, timeout=10):
    return request(url, timeout=timeout).read().decode("utf8")


def multi_iterator_pooler(*iterators):
    import queue
    from threading import Thread
    from time import sleep

    q = queue.Queue(maxsize=len(iterators))
    threads = []

    def worker(iterator):
        while True:
            q.put(next(iterator))

    for iterator in iterators:
        threads.append(Thread(target=worker, args=[iterator]))
    for thread in threads:
        thread.start()
    while True:
        if not q.empty():
            obj = q.get()
            q.task_done()
            yield obj
        keep_going = False
        for thread in threads:
            if thread.is_alive():
                keep_going = True
        if keep_going:
            sleep(0.1)


def min_wait(seconds):
    from time import sleep, time

    last_time = time()
    yield None
    while True:
        timediff = time() - last_time
        if timediff < seconds:
            sleep(seconds - timediff)
        yield None
