"""Tests for TvDatafeedLive, Seis, and Consumer classes."""

from __future__ import annotations

from unittest.mock import MagicMock, Mock, patch

import pandas as pd
import pytest
from tvDatafeed import Consumer, Interval, Seis, TvDatafeedLive


class TestTvDatafeedLive:
    """Test TvDatafeedLive initialization and basic functionality."""

    def test_init_anonymous(self):
        """Test TvDatafeedLive initialization without credentials."""
        tvl = TvDatafeedLive()
        assert tvl.token is None
        assert hasattr(tvl, '_lock')

    def test_init_with_credentials(self, mock_requests_post, tmp_path):
        """Test TvDatafeedLive initialization with credentials."""
        with patch('tvDatafeed.datafeed.TvDatafeed._is_token_valid', return_value=True):
            tvl = TvDatafeedLive(
                username="test",
                password="pass",
                token_cache_file=tmp_path / ".tv_token.json"
            )
            assert tvl.token == "test_token_123"

    def test_inherits_from_tvdatafeed(self):
        """Test that TvDatafeedLive inherits from TvDatafeed."""
        tvl = TvDatafeedLive()
        assert hasattr(tvl, 'get_hist')
        assert hasattr(tvl, 'search_symbol')


class TestSeis:
    """Test Seis class."""

    def test_seis_creation(self, mock_create_connection):
        """Test Seis object creation."""
        tvl = TvDatafeedLive()
        seis = Seis("AAPL", "NASDAQ", Interval.in_1_hour)
        seis.tvdatafeed = tvl

        assert seis.symbol == "AAPL"
        assert seis.exchange == "NASDAQ"
        assert seis.interval == Interval.in_1_hour
        assert seis.tvdatafeed == tvl

    def test_seis_get_hist(self, mock_create_connection):
        """Test Seis get_hist method."""
        tvl = TvDatafeedLive()
        seis = Seis("AAPL", "NASDAQ", Interval.in_daily)
        seis.tvdatafeed = tvl

        # This will attempt to get historical data
        result = seis.get_hist(n_bars=10)
        # May return None with mocked WebSocket

    def test_seis_new_consumer(self, mock_create_connection):
        """Test creating a consumer for a seis."""
        tvl = TvDatafeedLive()
        seis = Seis("AAPL", "NASDAQ", Interval.in_1_hour)
        seis.tvdatafeed = tvl

        def callback(seis_obj, data):
            pass

        # Manually add to internal tracker to bypass validation
        tvl._sat.append(seis, update_dt=pd.Timestamp.now())

        consumer = seis.new_consumer(callback)
        assert isinstance(consumer, Consumer)

    def test_seis_del_consumer(self, mock_create_connection):
        """Test deleting a consumer from seis."""
        tvl = TvDatafeedLive()
        seis = Seis("AAPL", "NASDAQ", Interval.in_1_hour)
        seis.tvdatafeed = tvl

        def callback(seis_obj, data):
            pass

        # Manually add to internal tracker
        tvl._sat.append(seis, update_dt=pd.Timestamp.now())

        consumer = seis.new_consumer(callback)
        seis.del_consumer(consumer)


class TestConsumer:
    """Test Consumer class."""

    def test_consumer_creation(self, mock_create_connection):
        """Test Consumer object creation."""
        tvl = TvDatafeedLive()
        seis = Seis("AAPL", "NASDAQ", Interval.in_1_hour)
        seis.tvdatafeed = tvl

        def callback(seis_obj, data):
            pass

        consumer = Consumer(seis, callback)
        assert consumer.seis == seis
        assert consumer.callback == callback

    def test_consumer_callback_execution(self, mock_create_connection, sample_ohlcv_data):
        """Test that consumer callback is executed."""
        tvl = TvDatafeedLive()
        seis = Seis("AAPL", "NASDAQ", Interval.in_1_hour)
        seis.tvdatafeed = tvl

        callback_called = []

        def callback(seis_obj, data):
            callback_called.append((seis_obj, data))

        consumer = Consumer(seis, callback)
        consumer.callback(seis, sample_ohlcv_data)

        assert len(callback_called) == 1
        assert callback_called[0][0] == seis
        assert isinstance(callback_called[0][1], pd.DataFrame)

    def test_consumer_del_consumer(self, mock_create_connection):
        """Test Consumer.del_consumer method."""
        tvl = TvDatafeedLive()
        seis = Seis("AAPL", "NASDAQ", Interval.in_1_hour)
        seis.tvdatafeed = tvl

        def callback(seis_obj, data):
            pass

        # Manually add to internal tracker
        tvl._sat.append(seis, update_dt=pd.Timestamp.now())

        consumer = Consumer(seis, callback)
        seis.add_consumer(consumer)

        consumer.del_consumer()


class TestLiveDataFlow:
    """Test live data flow between components."""

    def test_new_seis_from_tvdatafeedlive(self, mock_create_connection, mock_requests_get, sample_ohlcv_data):
        """Test creating a new seis from TvDatafeedLive."""
        # Mock symbol search to return valid result
        mock_requests_get.return_value.text = '[]'
        mock_requests_get.return_value.json.return_value = [
            {"symbol": "ETHUSDT", "exchange": "BINANCE"}
        ]

        tvl = TvDatafeedLive()

        # Mock get_hist to return sample data
        with patch.object(tvl, 'get_hist', return_value=sample_ohlcv_data):
            seis = tvl.new_seis("ETHUSDT", "BINANCE", Interval.in_1_hour)

        assert isinstance(seis, Seis)
        assert seis.symbol == "ETHUSDT"
        assert seis.exchange == "BINANCE"
        assert seis.interval == Interval.in_1_hour

    def test_new_consumer_from_tvdatafeedlive(self, mock_create_connection, mock_requests_get, sample_ohlcv_data):
        """Test creating a consumer from TvDatafeedLive."""
        # Mock symbol search
        mock_requests_get.return_value.text = '[]'
        mock_requests_get.return_value.json.return_value = [
            {"symbol": "AAPL", "exchange": "NASDAQ"}
        ]

        tvl = TvDatafeedLive()

        # Mock get_hist
        with patch.object(tvl, 'get_hist', return_value=sample_ohlcv_data):
            seis = tvl.new_seis("AAPL", "NASDAQ", Interval.in_daily)

        def callback(seis_obj, data):
            pass

        consumer = tvl.new_consumer(seis, callback)
        assert isinstance(consumer, Consumer)

    def test_del_seis_from_tvdatafeedlive(self, mock_create_connection, mock_requests_get, sample_ohlcv_data):
        """Test deleting a seis from TvDatafeedLive."""
        # Mock symbol search
        mock_requests_get.return_value.text = '[]'
        mock_requests_get.return_value.json.return_value = [
            {"symbol": "AAPL", "exchange": "NASDAQ"}
        ]

        tvl = TvDatafeedLive()

        # Mock get_hist
        with patch.object(tvl, 'get_hist', return_value=sample_ohlcv_data):
            seis = tvl.new_seis("AAPL", "NASDAQ", Interval.in_daily)

        tvl.del_seis(seis)
        # Should not raise an error

    def test_del_consumer_from_tvdatafeedlive(self, mock_create_connection, mock_requests_get, sample_ohlcv_data):
        """Test deleting a consumer from TvDatafeedLive."""
        # Mock symbol search
        mock_requests_get.return_value.text = '[]'
        mock_requests_get.return_value.json.return_value = [
            {"symbol": "AAPL", "exchange": "NASDAQ"}
        ]

        tvl = TvDatafeedLive()

        # Mock get_hist
        with patch.object(tvl, 'get_hist', return_value=sample_ohlcv_data):
            seis = tvl.new_seis("AAPL", "NASDAQ", Interval.in_daily)

        def callback(seis_obj, data):
            pass

        consumer = tvl.new_consumer(seis, callback)
        tvl.del_consumer(consumer)


class TestMultipleSeisAndConsumers:
    """Test multiple seis and consumers."""

    def test_multiple_seis(self, mock_create_connection, mock_requests_get, sample_ohlcv_data):
        """Test creating multiple seis objects."""
        # Mock symbol search
        mock_requests_get.return_value.text = '[]'
        mock_requests_get.return_value.json.return_value = [
            {"symbol": "AAPL", "exchange": "NASDAQ"}
        ]

        tvl = TvDatafeedLive()

        # Mock get_hist
        with patch.object(tvl, 'get_hist', return_value=sample_ohlcv_data):
            seis1 = tvl.new_seis("AAPL", "NASDAQ", Interval.in_1_hour)

            # Update mock for second symbol
            mock_requests_get.return_value.json.return_value = [
                {"symbol": "MSFT", "exchange": "NASDAQ"}
            ]
            seis2 = tvl.new_seis("MSFT", "NASDAQ", Interval.in_daily)

        assert seis1.symbol != seis2.symbol
        assert seis1 != seis2

    def test_multiple_consumers_one_seis(self, mock_create_connection, mock_requests_get, sample_ohlcv_data):
        """Test multiple consumers for one seis."""
        # Mock symbol search
        mock_requests_get.return_value.text = '[]'
        mock_requests_get.return_value.json.return_value = [
            {"symbol": "AAPL", "exchange": "NASDAQ"}
        ]

        tvl = TvDatafeedLive()

        # Mock get_hist
        with patch.object(tvl, 'get_hist', return_value=sample_ohlcv_data):
            seis = tvl.new_seis("AAPL", "NASDAQ", Interval.in_1_hour)

        def callback1(seis_obj, data):
            pass

        def callback2(seis_obj, data):
            pass

        consumer1 = tvl.new_consumer(seis, callback1)
        consumer2 = tvl.new_consumer(seis, callback2)

        consumers = seis.get_consumers()
        assert consumer1 in consumers
        assert consumer2 in consumers
        assert len(consumers) == 2

    def test_same_symbol_different_intervals(self, mock_create_connection, mock_requests_get, sample_ohlcv_data):
        """Test same symbol with different intervals."""
        # Mock symbol search
        mock_requests_get.return_value.text = '[]'
        mock_requests_get.return_value.json.return_value = [
            {"symbol": "AAPL", "exchange": "NASDAQ"}
        ]

        tvl = TvDatafeedLive()

        # Mock get_hist
        with patch.object(tvl, 'get_hist', return_value=sample_ohlcv_data):
            seis1h = tvl.new_seis("AAPL", "NASDAQ", Interval.in_1_hour)
            seis1d = tvl.new_seis("AAPL", "NASDAQ", Interval.in_daily)

        assert seis1h.symbol == seis1d.symbol
        assert seis1h.interval != seis1d.interval
        assert seis1h != seis1d
