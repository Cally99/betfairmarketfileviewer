from betfairlightweight import StreamListener


class CustomListener(StreamListener):
    def __init__(
        self,
        conflation: float,
        pre_play: bool,
        in_play: bool,
        seconds_to_start: int,
    ):
        super(StreamListener, self).__init__(None)
        self.output_queue = None
        self.lightweight = True
        self.debug = False
        self.update_clk = False
        self.conflation = conflation
        self._last_publish_time = 0
        self._pre_play = pre_play
        self._in_play = in_play
        self._seconds_to_start = seconds_to_start

    def snap(self, market_ids: list = None) -> list:
        if self.stream_type:
            for market_id in market_ids:
                cache = self.stream._caches.get(market_id)
                if cache is None:
                    continue
                # if market is not open (closed/suspended) send regardless
                if cache._definition_status == "OPEN":
                    if self._pre_play and self._in_play:
                        pass
                    else:
                        in_play = cache._definition_in_play
                        if in_play and not self._in_play:
                            continue
                        if not in_play and not self._pre_play:
                            continue
                    diff = (cache.publish_time - self._last_publish_time) / 1e3
                    if diff < self.conflation:
                        continue

                self._last_publish_time = cache.publish_time
                return [cache.create_resource(self.stream.unique_id, snap=True)]
        return []
