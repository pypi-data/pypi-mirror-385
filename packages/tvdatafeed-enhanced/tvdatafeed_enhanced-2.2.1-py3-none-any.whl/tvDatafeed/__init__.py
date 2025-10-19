"""TvDatafeed - TradingView historical and live data downloader.

A Python library for downloading historical and real-time market data
from TradingView. Supports both basic historical data retrieval and
advanced live streaming with callback architecture.

Example:
    Basic usage:
        >>> from tvDatafeed import TvDatafeed, Interval
        >>> tv = TvDatafeed(username='user', password='pass')
        >>> data = tv.get_hist('AAPL', 'NASDAQ', Interval.in_1_hour, n_bars=100)

    Live streaming:
        >>> from tvDatafeed import TvDatafeedLive, Interval
        >>> def callback(seis, data):
        ...     print(f"New bar: {data}")
        >>> tvl = TvDatafeedLive(username='user', password='pass')
        >>> seis = tvl.new_seis('ETHUSDT', 'BINANCE', Interval.in_1_hour)
        >>> consumer = seis.new_consumer(callback)
"""

from __future__ import annotations

from .consumer import Consumer
from .datafeed import TvDatafeedLive
from .main import Interval, TvDatafeed
from .seis import Seis

__version__ = "2.2.1"
__all__ = [
    "TvDatafeed",
    "TvDatafeedLive",
    "Interval",
    "Seis",
    "Consumer",
]
