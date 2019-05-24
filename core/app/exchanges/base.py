from multiprocessing.dummy import Pool as ThreadPool


class BaseExchange:
    pool = 4
    timeframes: list
    fetch_candles: callable

    def fill(self, ctx, pair: str) -> bool:
        pool = ThreadPool(self.pool)

        def worker(tf: str):
            with ctx:
                result = self.fetch_candles(pair, tf)
            return result

        results = pool.map(worker, self.timeframes)
        pool.close()
        pool.join()

        status = all(results)
        return status
