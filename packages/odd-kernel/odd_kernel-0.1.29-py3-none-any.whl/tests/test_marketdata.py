import pytest
import pandas as pd
from odd_kernel.datasets.finance.marketdata import MarketDataProvider, DataType, Period, TimeUnit, AVAILABLE_TICKERS


@pytest.fixture(scope="module")
def market_data_provider():
    """Create a MarketData instance to reuse across tests."""
    return MarketDataProvider()


@pytest.fixture(scope="module")
def ticker():
    """Use a stable ticker with long history."""
    return "AAPL"

@pytest.fixture(scope="module")
def tickers():
    """Use a stable ticker with long history."""
    return AVAILABLE_TICKERS[::50]


@pytest.fixture(scope="module")
def date_range():
    """Provide a small date range for tests"""
    return ("2020-12-31", "2025-12-31")


# ------------------------------------------------------------
# ENUMS AND BASIC CLASSES
# ------------------------------------------------------------

def test_period_to_pandas_freq():
    p = Period(3, TimeUnit.DAY)
    assert p.to_pandas_freq() == "3D"

    p2 = Period(1, TimeUnit.MONTH)
    assert str(p2) == "1M"


def test_period_invalid_value():
    with pytest.raises(ValueError):
        Period(0, TimeUnit.DAY)


# ------------------------------------------------------------
# DOWNLOAD AND SUMMARY
# ------------------------------------------------------------

def test_download_and_cache(market_data_provider, ticker):
    data_by_ticker_1 = market_data_provider._download(ticker)
    data_by_ticker_2 = market_data_provider._download(ticker)
    # Cached object should be the same
    assert data_by_ticker_1
    assert data_by_ticker_1[ticker] is data_by_ticker_2[ticker]
    assert all(data_type  in data_by_ticker_1[ticker] for data_type in DataType)

def test_download_and_cache_multi(market_data_provider, tickers):
    data_by_ticker_1 = market_data_provider._download(tickers)
    data_by_ticker_2 = market_data_provider._download(tickers)
    # Cached object should be the same
    assert data_by_ticker_1
    assert all(data_by_ticker_1[column] is data_by_ticker_2[column] for column in data_by_ticker_1)
    assert all(data_type in data_by_ticker_1[ticker] for ticker in tickers for data_type in DataType)


def test_get_summary(market_data_provider, ticker):
    summary = market_data_provider.get_summary([ticker])
    assert isinstance(summary, pd.DataFrame)
    assert "fields" in summary.columns
    assert ticker in summary["name"].values


# ------------------------------------------------------------
# RAW AND INTERPOLATED DATA
# ------------------------------------------------------------

def test_get_raw_close_field(market_data_provider, ticker):
    data_type = DataType.CLOSE
    data_by_ticker = market_data_provider.get_raw(ticker, data_type)
    assert isinstance(data_by_ticker, dict)
    assert all(isinstance(data, pd.Series) for data in data_by_ticker.values())
    assert all(data.index.is_monotonic_increasing for data in data_by_ticker.values())


def test_get_raw_invalid_field(market_data_provider, ticker):
    with pytest.raises(ValueError):
        market_data_provider.get_raw(ticker, DataType("Nonexistent"))


def test_get_interpolated_daily(market_data_provider, tickers, date_range):
    start, end = date_range
    p = Period(1, TimeUnit.DAY)
    interpolated_data_by_ticker = market_data_provider.get_interpolated(tickers, start, end, DataType.CLOSE, p)

    assert all(isinstance(interpolated_data, pd.Series) for interpolated_data in interpolated_data_by_ticker.values())
    assert all(interpolated_data.index.freq is not None or len(interpolated_data) > 0 for interpolated_data in interpolated_data_by_ticker.values())
    # Should cover entire date range
    assert all(interpolated_data.index.min() >= pd.Timestamp(start) for interpolated_data in interpolated_data_by_ticker.values())
    assert all(interpolated_data.index.max() <= pd.Timestamp(end) for interpolated_data in interpolated_data_by_ticker.values())


def test_interpolation_fills_missing_values(market_data_provider, tickers, date_range):
    """Ensure interpolation fills gaps correctly."""
    start, end = date_range
    period = Period(1, TimeUnit.DAY)
    data_type = DataType.CLOSE
    interpolated_data_by_ticker = market_data_provider.get_interpolated(tickers, start, end, data_type, period)
    assert all(interpolated_data_by_ticker[ticker].isna().sum() == 0 for ticker in tickers)
