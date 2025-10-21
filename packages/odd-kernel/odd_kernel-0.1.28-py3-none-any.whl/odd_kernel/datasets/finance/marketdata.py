import pandas as pd
import yfinance as yf
from enum import Enum
from typing import List, Dict, Union

NANOSECONDS_PER_SECOND = 1_000_000_000


class DataType(Enum):
    """Available financial data fields."""

    OPEN = "Open"
    HIGH = "High"
    LOW = "Low"
    CLOSE = "Close"
    ADJ_CLOSE = "Adj Close"
    VOLUME = "Volume"

    @classmethod
    def parse(cls, value: str):
        """
        Parses a string (case-insensitive) into a DataField.
        Raises ValueError if the string does not match any field.
        """
        normalized = value.strip().lower()
        for field in cls:
            if field.value.lower() == normalized:
                return field
        raise ValueError(f"Unknown data field: {value}")


class TimeUnit(Enum):
    """Supported time units for interpolation resolution."""

    DAY = "D"
    MONTH = "M"
    YEAR = "Y"


class IndexType(Enum):
    STRING = "string"
    DATETIME = "datetime"
    EPOCH = "epoch"
    INDEX = "index"


class Period:
    """Represents a time resolution with unit and magnitude."""

    def __init__(self, value: int, unit: TimeUnit):
        if value <= 0:
            raise ValueError("Period value must be positive.")
        self.value = value
        self.unit = unit

    def to_pandas_freq(self) -> str:
        """Converts the period to a pandas-compatible frequency string."""
        return f"{self.value}{self.unit.value}"

    def __str__(self):
        return self.to_pandas_freq()


class MarketDataProvider:
    """
    Module to fetch and manage financial time series from Yahoo Finance.
    Provides summary, raw data, and interpolated data methods.
    """

    def __init__(self, max_cache_size=100, show_download_progress=False):
        self.dates_map = {}
        self.cache = {}
        self.max_cache_size = max_cache_size
        self.cache_keys = []
        self.show_download_progress = show_download_progress

    # ------------------------------------------------------------
    def _download(self, tickers: Union[str, List[str]]) -> dict:
        """Downloads and caches Yahoo Finance data for one or multiple tickers."""

        # Normalizar a lista
        if isinstance(tickers, str):
            tickers = [tickers]

        missing = []
        data_by_ticker = {}

        # Buscar los que ya estén cacheados
        for ticker in tickers:
            if ticker in self.cache:
                data_by_ticker[ticker] = self.cache[ticker]
            else:
                missing.append(ticker)

        # Descargar solo los faltantes
        if missing:
            data = yf.download(
                missing,
                start= "1800-12-31", 
                end= pd.Timestamp.today().strftime("%Y-%m-%d"),
                progress=self.show_download_progress,
                auto_adjust=False,
                multi_level_index=False,
            )

            if data.empty:
                raise ValueError(f"No data retrieved for '{missing}'.")

            # Si se descargaron varios tickers, Yahoo devuelve un DataFrame con columna 'Ticker'
            if isinstance(data.columns, pd.MultiIndex):
                data_types = set(DataType.parse(data_type) for data_type, _ in data.columns)
                for ticker in missing:
                    data_by_ticker[ticker] = {}
                    for data_type in data_types:
                        data_by_ticker[ticker][data_type] = data[(data_type.value, ticker)].dropna()
                    self._add_to_cache(ticker, data_by_ticker[ticker])
            else:
                # Only one ticker missing
                data_by_ticker[ticker] = {}
                data_types = set(DataType.parse(data_type) for data_type in data.columns)
                for data_type in data_types:
                    data_by_ticker[ticker][data_type] = data[data_type.value].dropna()
                self._add_to_cache(ticker, data_by_ticker[ticker])

        return data_by_ticker


    def _add_to_cache(self, key, data: dict):
        """Helper to manage cache insertion."""
        if self.max_cache_size <= len(self.cache_keys):
            key_to_pop = self.cache_keys[0]
            self.cache.pop(key_to_pop)
            self.cache_keys = self.cache_keys[1:]
        self.cache[key] = data
        self.cache_keys.append(key)

    # ------------------------------------------------------------
    def get_summary(self, tickers):
        """
        Returns a summary for each ticker:
        - name
        - min/max date
        - average resolution
        - available fields
        """
        summaries = []
        data_by_ticker = self._download(tickers)
        for ticker, data in data_by_ticker.items():
            # Take any data, for instance first key
            df = data[next(iter(data))]
            deltas = df.index.to_series().diff().dropna()
            resolution = deltas.mode()[0] if not deltas.empty else pd.Timedelta("NaT")
            # TODO: series are being returned!
            summaries.append(
                {
                    "name": ticker,
                    "date_min": df.index.min().date(),
                    "date_max": df.index.max().date(),
                    "resolution": str(resolution),
                    "fields": list(data.keys()),
                }
            )
        return pd.DataFrame(summaries)

    # ------------------------------------------------------------
    def get_raw(self, tickers: Union[str, List[str]], field: DataType):
        """Returns raw data for a given ticker and field."""
        data_by_ticker = self._download(tickers)
        return {ticker:data_by_ticker[ticker][field] for ticker in data_by_ticker.keys()}
        

    def get_interpolated(
        self,
        tickers: Union[str, List[str]],
        start: str,
        end: str,
        field: DataType,
        resolution: Period = None,
        index_type: IndexType = IndexType.DATETIME,
        extrapolate_left = False
    ):
        """
        Returns interpolated data for a given ticker, field, and resolution.
        Performs flat extrapolation to the left and right of the original data range if required.

        Parameters
        ----------
        tickers : Union[str, List[str]]
            Ticker symbols of the financial instrument.
        start : str
            Start date (inclusive) in 'YYYY-MM-DD' format.
        end : str
            End date (inclusive) in 'YYYY-MM-DD' format.
        field : DataField
            The financial data field to retrieve (e.g., CLOSE, OPEN).
        resolution : Period
            The target temporal resolution, e.g., Period(1, TimeUnit.DAY) or Period(3, TimeUnit.MONTHS). If None no interpolation is performed.
        index_type : IndexType, optional
            Defines the format of the time index in the output:
            - STRING → 'YYYY-MM-DD'
            - DATETIME → pandas datetime index (default)
            - EPOCH → seconds since 1970-01-01
            - INDEX → integer positions (0, 1, 2, …)
        extrapolate_left: Wether to perform flat extrapolation to the left or not. 

        Returns
        -------
        pd.DataFrame
            A DataFrame indexed according to `index_type`, containing interpolated and extrapolated values.
        """
        data_by_ticker = self.get_raw(tickers, field)
        if resolution is not None:
            freq = resolution.to_pandas_freq()

            # Create full time grid
            full_index = pd.date_range(start=start, end=end, freq=freq)

            # Interpolate + extrapolate flat
            interpolated_data = {}
            for ticker in data_by_ticker:
                interpolated_data[ticker] = data_by_ticker[ticker].reindex(full_index).interpolate(method="time").ffill()
                if extrapolate_left:
                    interpolated_data[ticker] = interpolated_data[ticker].bfill()
        else:
            interpolated_data = {}
            # Filter to end and start
            date_max = pd.to_datetime(end)
            date_min = pd.to_datetime(start)
            for ticker, data in data_by_ticker.items():
                mask = (date_min <= data.index) & (data.index <= date_max)
                interpolated_data[ticker] = data.loc[mask]

        # Format index according to index_type
        for ticker, interpolated in interpolated_data.items():
            if index_type == IndexType.STRING:
                interpolated_data[ticker].index = interpolated.index.strftime("%Y-%m-%d")
            elif index_type == IndexType.EPOCH:
                interpolated_data[ticker].index = (
                    interpolated.index.astype("int64") / NANOSECONDS_PER_SECOND
                )
            elif index_type == IndexType.INDEX:
                interpolated_data[ticker].index = range(len(interpolated))
            interpolated_data[ticker].index.name = "date"

        return interpolated_data

    def get_dataset(
        self,
        names: List[str],
        field: DataType,
        start: str,
        end: str,
        resolution: Period,
        index_type: IndexType = IndexType.DATETIME,
    ) -> Dict[str, pd.DataFrame]:
        """Returns interpolated data for the given tickers, field and resolution in a common time grid"""
        return {
            name: self.get_interpolated(name, start, end, field, resolution, index_type)
            for name in names
        }

## Update this list from https://en.wikipedia.org/wiki/List_of_S%26P_500_companies
# running in console
TICKERS_RETRIEVAL_SCRIPT = """
(() => {
   const rows = document.querySelectorAll("#constituents tbody tr");
   const tickers = Array.from(rows)
     .map(row => row.querySelector("td a")?.textContent.trim())
     .filter(Boolean);
   console.log("[\n  '" + tickers.join("', '") + "'\n]");
 })();
"""

AVAILABLE_TICKERS =  [
  'MMM', 'AOS', 'ABT', 'ABBV', 'ACN', 'ADBE', 'AMD', 'AES', 'AFL', 'A', 'APD', 'ABNB', 'AKAM', 'ALB', 'ARE', 'ALGN', 'ALLE', 'LNT', 'ALL', 'GOOGL', 'GOOG', 'MO', 'AMZN', 'AMCR', 'AEE', 'AEP', 'AXP', 'AIG', 'AMT', 'AWK', 'AMP', 'AME', 'AMGN', 'APH', 'ADI', 'AON', 'APA', 'APO', 'AAPL', 'AMAT', 'APP', 'APTV', 'ACGL', 'ADM', 'ANET', 'AJG', 'AIZ', 'T', 'ATO', 'ADSK', 'ADP', 'AZO', 'AVB', 'AVY', 'AXON', 'BKR', 'BALL', 'BAC', 'BAX', 'BDX', 'BBY', 'TECH', 'BIIB', 'BLK', 'BX', 'XYZ', 'BK', 'BA', 'BKNG', 'BSX', 'BMY', 'AVGO', 'BR', 'BRO', 'BLDR', 'BG', 'BXP', 'CHRW', 'CDNS', 'CPT', 'CPB', 'COF', 'CAH', 'KMX', 'CCL', 'CARR', 'CAT', 'CBOE', 'CBRE', 'CDW', 'COR', 'CNC', 'CNP', 'CF', 'CRL', 'SCHW', 'CHTR', 'CVX', 'CMG', 'CB', 'CHD', 'CI', 'CINF', 'CTAS', 'CSCO', 'C', 'CFG', 'CLX', 'CME', 'CMS', 'KO', 'CTSH', 'COIN', 'CL', 'CMCSA', 'CAG', 'COP', 'ED', 'STZ', 'CEG', 'COO', 'CPRT', 'GLW', 'CPAY', 'CTVA', 'CSGP', 'COST', 'CTRA', 'CRWD', 'CCI', 'CSX', 'CMI', 'CVS', 'DHR', 'DRI', 'DDOG', 'DVA', 'DAY', 'DECK', 'DE', 'DELL', 'DAL', 'DVN', 'DXCM', 'FANG', 'DLR', 'DG', 'DLTR', 'D', 'DPZ', 'DASH', 'DOV', 'DOW', 'DHI', 'DTE', 'DUK', 'DD', 'EMN', 'ETN', 'EBAY', 'ECL', 'EIX', 'EW', 'EA', 'ELV', 'EME', 'EMR', 'ETR', 'EOG', 'EPAM', 'EQT', 'EFX', 'EQIX', 'EQR', 'ERIE', 'ESS', 'EL', 'EG', 'EVRG', 'ES', 'EXC', 'EXE', 'EXPE', 'EXPD', 'EXR', 'XOM', 'FFIV', 'FDS', 'FICO', 'FAST', 'FRT', 'FDX', 'FIS', 'FITB', 'FSLR', 'FE', 'FI', 'F', 'FTNT', 'FTV', 'FOXA', 'FOX', 'BEN', 'FCX', 'GRMN', 'IT', 'GE', 'GEHC', 'GEV', 'GEN', 'GNRC', 'GD', 'GIS', 'GM', 'GPC', 'GILD', 'GPN', 'GL', 'GDDY', 'GS', 'HAL', 'HIG', 'HAS', 'HCA', 'DOC', 'HSIC', 'HSY', 'HPE', 'HLT', 'HOLX', 'HD', 'HON', 'HRL', 'HST', 'HWM', 'HPQ', 'HUBB', 'HUM', 'HBAN', 'HII', 'IBM', 'IEX', 'IDXX', 'ITW', 'INCY', 'IR', 'PODD', 'INTC', 'IBKR', 'ICE', 'IFF', 'IP', 'IPG', 'INTU', 'ISRG', 'IVZ', 'INVH', 'IQV', 'IRM', 'JBHT', 'JBL', 'JKHY', 'J', 'JNJ', 'JCI', 'JPM', 'K', 'KVUE', 'KDP', 'KEY', 'KEYS', 'KMB', 'KIM', 'KMI', 'KKR', 'KLAC', 'KHC', 'KR', 'LHX', 'LH', 'LRCX', 'LW', 'LVS', 'LDOS', 'LEN', 'LII', 'LLY', 'LIN', 'LYV', 'LKQ', 'LMT', 'L', 'LOW', 'LULU', 'LYB', 'MTB', 'MPC', 'MAR', 'MMC', 'MLM', 'MAS', 'MA', 'MTCH', 'MKC', 'MCD', 'MCK', 'MDT', 'MRK', 'META', 'MET', 'MTD', 'MGM', 'MCHP', 'MU', 'MSFT', 'MAA', 'MRNA', 'MHK', 'MOH', 'TAP', 'MDLZ', 'MPWR', 'MNST', 'MCO', 'MS', 'MOS', 'MSI', 'MSCI', 'NDAQ', 'NTAP', 'NFLX', 'NEM', 'NWSA', 'NWS', 'NEE', 'NKE', 'NI', 'NDSN', 'NSC', 'NTRS', 'NOC', 'NCLH', 'NRG', 'NUE', 'NVDA', 'NVR', 'NXPI', 'ORLY', 'OXY', 'ODFL', 'OMC', 'ON', 'OKE', 'ORCL', 'OTIS', 'PCAR', 'PKG', 'PLTR', 'PANW', 'PSKY', 'PH', 'PAYX', 'PAYC', 'PYPL', 'PNR', 'PEP', 'PFE', 'PCG', 'PM', 'PSX', 'PNW', 'PNC', 'POOL', 'PPG', 'PPL', 'PFG', 'PG', 'PGR', 'PLD', 'PRU', 'PEG', 'PTC', 'PSA', 'PHM', 'PWR', 'QCOM', 'DGX', 'RL', 'RJF', 'RTX', 'O', 'REG', 'REGN', 'RF', 'RSG', 'RMD', 'RVTY', 'HOOD', 'ROK', 'ROL', 'ROP', 'ROST', 'RCL', 'SPGI', 'CRM', 'SBAC', 'SLB', 'STX', 'SRE', 'NOW', 'SHW', 'SPG', 'SWKS', 'SJM', 'SW', 'SNA', 'SOLV', 'SO', 'LUV', 'SWK', 'SBUX', 'STT', 'STLD', 'STE', 'SYK', 'SMCI', 'SYF', 'SNPS', 'SYY', 'TMUS', 'TROW', 'TTWO', 'TPR', 'TRGP', 'TGT', 'TEL', 'TDY', 'TER', 'TSLA', 'TXN', 'TPL', 'TXT', 'TMO', 'TJX', 'TKO', 'TTD', 'TSCO', 'TT', 'TDG', 'TRV', 'TRMB', 'TFC', 'TYL', 'TSN', 'USB', 'UBER', 'UDR', 'ULTA', 'UNP', 'UAL', 'UPS', 'URI', 'UNH', 'UHS', 'VLO', 'VTR', 'VLTO', 'VRSN', 'VRSK', 'VZ', 'VRTX', 'VTRS', 'VICI', 'V', 'VST', 'VMC', 'WRB', 'GWW', 'WAB', 'WMT', 'DIS', 'WBD', 'WM', 'WAT', 'WEC', 'WFC', 'WELL', 'WST', 'WDC', 'WY', 'WSM', 'WMB', 'WTW', 'WDAY', 'WYNN', 'XEL', 'XYL', 'YUM', 'ZBRA', 'ZBH', 'ZTS'
]
