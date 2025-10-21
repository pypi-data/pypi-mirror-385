import logging
from time import sleep
from typing import Any, Dict, List, Optional, Union
import pandas as pd

from coinmetrics.api_client import CoinMetricsClient

from cryptodatapy.extract.data_vendors.datavendor import DataVendor
from cryptodatapy.extract.datarequest import DataRequest
from cryptodatapy.transform.convertparams import ConvertParams
from cryptodatapy.transform.wrangle import WrangleData, WrangleInfo
from cryptodatapy.util.datacredentials import DataCredentials

# data credentials
data_cred = DataCredentials()

# CoinMetrics community API client:
client = CoinMetricsClient()


class CoinMetrics(DataVendor):
    """
    Retrieves data from Coin Metrics Python client API v4.
    """

    def __init__(
            self,
            categories: Union[str, List[str]] = "crypto",
            exchanges: Optional[List[str]] = None,
            indexes: Optional[List[str]] = None,
            assets: Optional[List[str]] = None,
            markets: Optional[List[str]] = None,
            market_types: List[str] = ["spot", "perpetual_future", "future", "option"],
            fields: Optional[List[str]] = None,
            frequencies: List[str] = ["tick", "block", "1s", "1min", "5min", "10min", "15min", "30min",
                                      "1h", "2h", "4h", "8h", "d", "w", "m", "q"],
            base_url: Optional[str] = data_cred.coinmetrics_base_url,
            api_endpoints: Optional[Dict[str, str]] = None,
            api_key: Optional[str] = data_cred.coinmetrics_api_key,
            max_obs_per_call: Optional[int] = None,
            rate_limit: Optional[Any] = None,
    ):
        """
        Constructor

        Parameters
        ----------
        categories: list or str, {'crypto', 'fx', 'rates', 'eqty', 'commodities', 'credit', 'macro', 'alt'}
            List or string of available categories, e.g. ['crypto', 'fx', 'alt'].
        exchanges: list, optional, default None
            List of available exchanges, e.g. ['Binance', 'Coinbase', 'Kraken', 'FTX', ...].
        indexes: list, optional, default None
            List of available indexes, e.g. ['mvda', 'bvin'].
        assets: list, optional, default None
            List of available assets, e.g. ['ftx': 'btc', 'eth', ...]
        markets: list, optional, default None
            List of available markets as base asset/quote currency pairs, e.g. [btcusdt', 'ethbtc', ...].
        market_types: list
            List of available market types/contracts, e.g. [spot', 'perpetual_futures', 'futures', 'options']
        fields: list, optional, default None
            List of available fields, e.g. ['open', 'high', 'low', 'close', 'volume'].
        frequencies: list
            List of available frequencies, e.g. ['tick', '1min', '5min', '10min', '15min', '30min', '1h', '2h', '4h',
        base_url: str, optional, default None
            Base url used for GET requests. If not provided, default is set to base_url stored in DataCredentials.
        api_endpoints: dict, optional, default None
            Dictionary with available API endpoints. If not provided, default is set to api_endpoints stored in
            DataCredentials.
        api_key: str, optional, default None
            Api key, e.g. 'dcf13983adf7dfa79a0dfa35adf'. If not provided, default is set to
            api_key stored in DataCredentials.
        max_obs_per_call: int, optional, default None
            Maximum number of observations returned per API call. If not provided, default is set to
            api_limit stored in DataCredentials.
        rate_limit: Any, optional, Default None
            Number of API calls made and left, by time frequency.
        """
        super().__init__(
            categories, exchanges, indexes, assets, markets, market_types,
            fields, frequencies, base_url, api_endpoints, api_key, max_obs_per_call, rate_limit
        )
        self.data_req = None
        self.data_resp = None
        self.data = pd.DataFrame()

    def req_meta(self, data_type: str) -> Dict[str, Any]:
        """
        Request metadata.

        Parameters
        ----------
        data_type: str, {'catalog_exchanges', 'catalog_indexes', 'catalog_assets', 'catalog_institutions',
                         'catalog_markets', 'catalog_metrics' }
            Type of data to request metadata for.

        Returns
        -------
        meta: Any
            Object with metadata.
        """
        try:
            self.data_resp = getattr(client, data_type)()

        except AssertionError as e:
            logging.warning(e)
            logging.warning(f"Failed to get metadata for {data_type}.")

        else:
            return self.data_resp

    def get_exchanges_info(self, as_list: bool = False) -> Union[List[str], pd.DataFrame]:
        """
        Get exchanges info.

        Parameters
        ----------
        as_list: bool, default False
            Returns exchanges info as list.

        Returns
        -------
        exch: list or pd.DataFrame
            List or dataframe with info on supported exchanges.
        """
        # req data
        self.req_meta(data_type='catalog_exchanges')
        # wrangle data resp
        self.exchanges = WrangleInfo(self.data_resp).cm_meta_resp(as_list=as_list, index_name='exchange')

        return self.exchanges

    def get_indexes_info(self, as_list: bool = False) -> Union[List[str], pd.DataFrame]:
        """
        Get indexes info.

        Parameters
        ----------
        as_list: bool, default False
            Returns indexes info as list.

        Returns
        -------
        indexes: list or pd.DataFrame
            List or dataframe with info on available indexes.
        """
        # req data
        self.req_meta(data_type='catalog_indexes')
        # wrangle data resp
        self.indexes = WrangleInfo(self.data_resp).cm_meta_resp(as_list=as_list, index_name='ticker')

        return self.indexes

    def get_assets_info(self, as_list: bool = False) -> Union[List[str], pd.DataFrame]:
        """
        Get assets info.

        Parameters
        ----------
        as_list: bool, default False
            Returns assets info as a list.

        Returns
        -------
        assets: list or pd.DataFrame
            List or dataframe with info on available assets.
        """
        # req data
        self.req_meta(data_type='catalog_assets')
        # wrangle data resp
        self.assets = WrangleInfo(self.data_resp).cm_meta_resp(as_list=as_list, index_name='ticker')

        return self.assets

    def get_markets_info(self, as_list: bool = False) -> Union[List[str], pd.DataFrame]:
        """
        Get markets info.

        Parameters
        ----------
        as_list: bool, default False
            Returns markets info as dict with exchange-markets key-values pair.

        Returns
        -------
        mkts: list or pd.DataFrame
            List or dataframe with info on available markets, by exchange.
        """
        # req data
        self.req_meta(data_type='catalog_markets')
        # wrangle data resp
        self.markets = WrangleInfo(self.data_resp).cm_meta_resp(as_list=as_list)

        return self.markets

    def get_onchain_fields_info(self, as_list: bool = False) -> Union[List[str], pd.DataFrame]:
        """
        Get on-chain fields info.

        Parameters
        ----------
        as_list: bool, default False
            Returns on-chain fields as list.

        Returns
        -------
        onchain_fields: list or pd.DataFrame
            List or dataframe of on-chain info.
        """
        # req data
        self.req_meta(data_type='catalog_metrics')
        # wrangle data resp
        onchain_fields = WrangleInfo(self.data_resp).cm_meta_resp(as_list=as_list, index_name='fields')

        return onchain_fields

    def get_fields_info(self, data_type: Optional[str] = None, as_list: bool = False) -> Union[List[str], pd.DataFrame]:
        """
        Get fields info. Can be filtered by data type.

        Parameters
        ----------
        data_type: str, optional, {'market', 'on-chain', 'off-chain'}, default None
            Type of data.
        as_list: bool, default False
            Returns available fields as list.

        Returns
        -------
        fields: list or pd.DataFrame
            List or dataframe with info on available fields.
        """
        # req data
        ohlcv_fields = ['price_open', 'price_close', 'price_high', 'price_low', 'vwap', 'volume', 'candle_usd_volume',
                        'candle_trades_count']  # get market fields
        onchain_fields = self.get_onchain_fields_info()  # get onchain fields

        # fields df
        if data_type == "market":
            self.fields = onchain_fields[onchain_fields.category == "Market"]
        else:
            self.fields = onchain_fields

        # fields list
        if as_list:
            if data_type == "market":
                self.fields = ohlcv_fields + list(self.fields.index)
            elif data_type == "on-chain":
                self.fields = list(self.fields.index)
            else:
                self.fields = ohlcv_fields + list(self.fields.index)

        return self.fields

    def get_onchain_tickers_list(self, data_req: DataRequest) -> List[str]:
        """
        Get list of available assets for fields in data request.

        Parameters
        ----------
        data_req: DataRequest
            Data request object with 'fields' parameter.

        Returns
        -------
        asset_list: list
            List of available assets for selected fields.
        """
        # convert data request parameters to Coin Metrics format
        self.data_req = ConvertParams(data_req).to_coinmetrics()

        # fields info
        self.get_fields_info()

        # fields dict
        fields_dict = {}
        for field in self.data_req.source_fields:
            if field in self.fields.index:
                df = self.fields.loc[field]  # get fields metadata
                # add to dict
                fields_dict[field] = df["frequencies"][0]["assets"]

        # asset list
        asset_list = list(set.intersection(*(set(val) for val in fields_dict.values())))

        # return asset list if dict not empty
        if len(fields_dict) != 0:
            return asset_list
        else:
            raise Exception("No fields were found. Check available fields and try again.")

    def get_rate_limit_info(self) -> None:
        """
        Get rate limit info.
        """
        return None

    def get_metadata(self) -> None:
        """
        Get CoinMetrics metadata.
        """
        if self.exchanges is None:
            self.get_exchanges_info(as_list=True)
        if self.indexes is None:
            self.get_indexes_info(as_list=True)
        if self.assets is None:
            self.get_assets_info(as_list=True)
        if self.markets is None:
            self.get_markets_info(as_list=True)
        if self.fields is None:
            self.get_fields_info(as_list=True)

    def req_data(self, data_req: DataRequest, data_type: str, params: Dict[str, Union[str, int]]) -> pd.DataFrame:
        """
        Sends data request to Python client.

        Parameters
        ----------
        data_req: DataRequest
            Parameters of data request in CryptoDataPy format.
        data_type: str
            Data type to retrieve.
        params: dict
            Dictionary containing parameter values for get request.

        Returns
        -------
        df: pd.DataFrame
            Dataframe with datetime, ticker/identifier, and field/col values.
        """
        # url
        url = self.base_url + data_type

        # data request
        self.data_resp = data_req.get_req(url=url, params=params)

        # raise error if data is None
        if self.data_resp is None:
            raise Exception("Failed to fetch data after multiple attempts.")
        # retrieve data
        else:
            # data
            data, next_page_url = self.data_resp.get('data', []), self.data_resp.get('next_page_url')

            # while loop
            while next_page_url:
                # wait to avoid exceeding rate limit
                sleep(data_req.pause)

                # request next page
                next_page_data_resp = data_req.get_req(url=next_page_url, params=None)
                next_page_data, next_page_url = next_page_data_resp.get('data', []), next_page_data_resp.get(
                    'next_page_url')

                # add data to list
                data.extend(next_page_data)

            # convert to df
            df = pd.DataFrame(data)

            return df

    def wrangle_data_resp(self, data_req: DataRequest, data_resp: pd.DataFrame()) -> pd.DataFrame():
        """
        Wrangle data response.

        Parameters
        ----------
        data_req: DataRequest
            Parameters of data request in CryptoDataPy format.
        data_resp: pd.DataFrame
            Data response from API.

        Returns
        -------
        df: pd.DataFrame - MultiIndex
            Wrangled dataframe with DatetimeIndex (level 0), ticker or institution (level 1), and market, on-chain or
            off-chain values for selected fields (cols), in tidy format.
        """
        # wrangle data resp
        df = WrangleData(data_req, data_resp).coinmetrics()

        return df

    def get_tidy_data(self, data_req: DataRequest, data_type: str, params: dict) -> pd.DataFrame:
        """
        Gets data and wrangles it into tidy data format.

        Parameters
        ----------
        data_req: DataRequest
            Parameters of data request in CryptoDataPy format.
        data_type: str, {'get_index_levels', 'get_institution_metrics', 'get_market_candles', 'get_asset_metrics',
                         'get_market_open_interest', 'get_market_funding_rates', 'get_market_trades',
                         'get_market_quotes'}
            Data type to retrieve.
        params: dict
            Dictionary containing parameter values for get request.

        Returns
        -------
        df: pd.DataFrame - MultiIndex
            Dataframe with DatetimeIndex (level 0), ticker (level 1) and values for fields/col, in tidy data format.
        """
        # get entire data history
        df = self.req_data(data_req, data_type, params)
        # wrangle df
        df = self.wrangle_data_resp(data_req, df)

        return df

    def check_tickers(self, data_req: DataRequest, data_type: str) -> DataRequest:
        """
        Checks tickers for data availability.

        Parameters
        ----------
        data_req: DataRequest
            Parameters of data request in CryptoDataPy format.
        data_type: str, {'indexes', 'institutions', market_candles', 'asset_metrics', 'open_interest', 'funding_rates',
                         'trades', quotes'}
            Data type to retrieve.

        Returns
        -------
        tickers: list
            List of available tickers.
        """
        # convert params
        self.data_req = ConvertParams(data_req).to_coinmetrics()

        # check indexes
        if data_type == 'indexes':
            self.get_indexes_info(as_list=True)
            # avail tickers
            self.data_req.source_tickers = [ticker for ticker in self.data_req.source_tickers
                                            if ticker.upper() in self.indexes]

        # check markets
        elif data_type == 'market_candles' or data_type == 'open_interest' or \
                data_type == 'funding_rates' or data_type == 'trades' or data_type == 'quotes':
            self.get_assets_info(as_list=True)
            # avail tickers
            self.data_req.source_markets = [market for ticker, market in
                                            zip(self.data_req.source_tickers, self.data_req.source_markets)
                                            if ticker in self.assets]

        # check assets
        elif data_type == 'asset_metrics':
            self.get_assets_info(as_list=True)
            # avail tickers
            self.data_req.source_tickers = [ticker for ticker in self.data_req.source_tickers
                                            if ticker in self.assets]

        # raise error if no tickers available
        if len(self.data_req.source_tickers) == 0:
            raise ValueError(
                f"{data_req.tickers} are not valid tickers for the requested data type."
                f" Use get_metadata to get a list of available indexes and assets."
            )

        return self.data_req

    def check_fields(self, data_req: DataRequest, data_type: str) -> DataRequest:
        """
        Checks fields for data availability.

        Parameters
        ----------
        data_req: DataRequest
            Parameters of data request in CryptoDataPy format.
        data_type: str, {'indexes', 'institutions', 'market_candles', 'asset_metrics', 'open_interest',
                        'funding_rates', 'trades', quotes'}
            Data type to retrieve.

        Returns
        -------
        fields: list
            List of avaialble fields.
        """
        # convert params
        self.data_req = ConvertParams(data_req).to_coinmetrics()

        # check on-chain metrics
        if data_type == 'asset_metrics':
            self.get_fields_info(data_type='on-chain', as_list=True)
            # avail fields
            self.data_req.source_fields = [field for field in self.data_req.source_fields
                                           if field in self.fields]

        # raise error if fields is empty
        if len(self.data_req.source_fields) == 0:
            raise ValueError(
                f"{data_req.fields} are not valid fields."
                f" Use the get_fields_info or get_inst_info methods to get available source fields."
            )

        return self.data_req

    def check_params(self, data_req: DataRequest, data_type: str) -> None:
        """
        Checks data request parameters.

        Parameters
        ----------
        data_req: DataRequest
            Parameters of data request in CryptoDataPy format.
        data_type: str, {'indexes', 'institutions', 'market_candles', 'asset_metrics', 'open_interest', 'funding_rates',
                         'trades', quotes'}
            Data type to retrieve.

        """
        # convert params
        self.data_req = ConvertParams(data_req).to_coinmetrics()

        # indexes
        if data_type == 'indexes':
            if self.data_req.source_freq not in ["1h", "1d"]:
                raise ValueError(
                    f"Indexes data is only available for hourly, daily, weekly, monthly and quarterly"
                    f" frequencies. Change data request frequency and try again."
                )

        # ohlcv
        elif data_type == 'market_candles':
            if self.data_req.source_freq not in ["1m", "1h", "1d"]:
                raise ValueError(
                    f"OHLCV data is only available for minute, hourly, daily, weekly, monthly and quarterly"
                    f" frequencies. Change data request frequency and try again."
                )

        # on-chain
        elif data_type == 'asset_metrics':
            if self.data_req.source_freq not in ["1b", "1d"]:
                raise ValueError(
                    f"On-chain data is only available for 'block' and 'd' frequencies."
                    f" Change data request frequency and try again."
                )

        # funding rate
        elif data_type == 'funding_rates':
            if self.data_req.mkt_type not in ["perpetual_future", "future", "option"]:
                raise ValueError(
                    f"Funding rates are only available for 'perpetual_future', 'future' and"
                    f" 'option' market types. Change 'mkt_type' in data request and try again."
                )

        # oi
        elif data_type == 'open_interest':
            if self.data_req.mkt_type not in ["perpetual_future", "future", "option"]:
                raise ValueError(
                    f"Open interest is only available for 'perpetual_future', 'future' and"
                    f" 'option' market types. Change 'mkt_type' in data request and try again."
                )

        # trades
        elif data_type == 'trades':
            if self.data_req.source_freq != "raw":
                raise ValueError(
                    f"{data_type} data is only available at the 'tick' frequency."
                    f" Change data request frequency and try again."
                )

        # quotes
        elif data_type == 'quotes':
            if self.data_req.source_freq not in ["raw", "1s", "1m", "1h", "1d"]:
                raise ValueError(
                    f"{data_type} data is only available at the 'tick', '1s', '1m', '1h' and '1d' frequencies."
                    f" Change data request frequency and try again."
                )

        return None

    def get_indexes(self, data_req: DataRequest) -> pd.DataFrame:
        """
        Get indexes data.

        Parameters
        ----------
        data_req: DataRequest
            Parameters of data request in CryptoDataPy format.

        Returns
        -------
        df: pd.DataFrame
            DataFrame with DatetimeIndex (level 0), tickers (level 1) and index values (cols).
        """
        # convert data request parameters to Coin Metrics format
        self.data_req = ConvertParams(data_req).to_coinmetrics()

        # check params
        self.check_params(data_req, data_type='indexes')

        # check tickers
        self.check_tickers(data_req, data_type='indexes')
        sleep(self.data_req.pause)

        # params
        params = {
            'indexes': ','.join(self.data_req.source_tickers),
            'frequency': self.data_req.source_freq,
            'start_time': self.data_req.source_start_date,
            'end_time': self.data_req.source_end_date,
            'pretty': True,
            'page_size': 10000,
        }

        # get tidy data
        df = self.get_tidy_data(data_req,
                                data_type='/timeseries/index-levels',
                                params=params)

        return df

    def get_ohlcv(self, data_req: DataRequest) -> pd.DataFrame:
        """
        Get OHLCV (candles) data.

        Parameters
        ----------
        data_req: DataRequest
            Parameters of data request in CryptoDataPy format.

        Returns
        -------
        df: pd.DataFrame - MultiIndex
            DataFrame with DatetimeIndex (level 0), ticker (level 1), and OHLCV values (cols).
        """
        # convert data request parameters to Coin Metrics format
        self.data_req = ConvertParams(data_req).to_coinmetrics()

        # check freq
        self.check_params(data_req, data_type='market_candles')

        # check tickers
        self.check_tickers(data_req, data_type='market_candles')
        sleep(self.data_req.pause)

        # params
        params = {
            'markets': ','.join(self.data_req.source_markets),
            'frequency': self.data_req.source_freq,
            'start_time': self.data_req.source_start_date,
            'end_time': self.data_req.source_end_date,
            'pretty': True,
            'page_size': 10000,
        }

        # get tidy data
        df = self.get_tidy_data(data_req,
                                data_type='/timeseries/market-candles',
                                params=params)

        return df

    def get_onchain(self, data_req: DataRequest) -> pd.DataFrame:
        """
        Get on-chain data.

        Parameters
        ----------
        data_req: DataRequest
            Parameters of data request in CryptoDataPy format.

        Returns
        -------
        df: pd.DataFrame - MultiIndex
            DataFrame with DatetimeIndex (level 0), ticker (level 1), and on-chain values (cols).
        """
        # convert data request parameters to Coin Metrics format
        self.data_req = ConvertParams(data_req).to_coinmetrics()

        # check params
        self.check_params(data_req, data_type='asset_metrics')

        # check tickers
        self.check_tickers(data_req, data_type='asset_metrics')
        sleep(self.data_req.pause)

        # check fields
        self.check_fields(data_req, data_type='asset_metrics')
        sleep(self.data_req.pause)

        # params
        params = {
            'assets': ','.join(self.data_req.source_tickers),
            'metrics': ','.join(self.data_req.source_fields),
            'frequency': self.data_req.source_freq,
            'start_time': self.data_req.source_start_date,
            'end_time': self.data_req.source_end_date,
            'pretty': True,
            'page_size': 10000,
            'ignore_forbidden_errors': True,
            'ignore_unsupported_errors': True

        }

        # get tidy data
        df = self.get_tidy_data(data_req,
                                data_type='/timeseries/asset-metrics',
                                params=params
                                )

        return df

    def get_open_interest(self, data_req: DataRequest) -> pd.DataFrame:
        """
        Get open interest data.

        Parameters
        ----------
        data_req: DataRequest
            Parameters of data request in CryptoDataPy format.

        Returns
        -------
        df: pd.DataFrame - MultiIndex
            DataFrame with DatetimeIndex (level 0), ticker (level 1), and open interest values (cols).
        """
        # convert data request parameters to Coin Metrics format
        self.data_req = ConvertParams(data_req).to_coinmetrics()

        # check params
        self.check_params(data_req, data_type='open_interest')

        # check tickers
        self.check_tickers(data_req, data_type='open_interest')
        sleep(self.data_req.pause)

        # params
        params = {
            'markets': ','.join(self.data_req.source_markets),
            'start_time': self.data_req.source_start_date,
            'end_time': self.data_req.source_end_date,
            'pretty': True,
            'page_size': 10000,
        }

        # get tidy data
        df = self.get_tidy_data(data_req,
                                data_type='/timeseries/market-openinterest',
                                params=params
                                )

        return df

    def get_funding_rates(self, data_req: DataRequest) -> pd.DataFrame:
        """
        Get funding rates data.

        Parameters
        ----------
        data_req: DataRequest
            Parameters of data request in CryptoDataPy format.

        Returns
        -------
        df: pd.DataFrame - MultiIndex
            DataFrame with DatetimeIndex (level 0), ticker (level 1), and funding rates values (cols).
        """
        # convert data request parameters to Coin Metrics format
        self.data_req = ConvertParams(data_req).to_coinmetrics()

        # check params
        self.check_params(data_req, data_type='funding_rates')

        # check tickers
        self.check_tickers(data_req, data_type='funding_rates')
        sleep(self.data_req.pause)

        # params
        params = {
            'markets': ','.join(self.data_req.source_markets),
            'start_time': self.data_req.source_start_date,
            'end_time': self.data_req.source_end_date,
            'pretty': True,
            'page_size': 10000,
        }

        # get tidy data
        df = self.get_tidy_data(data_req,
                                data_type='/timeseries/market-funding-rates',
                                params=params
                                )

        return df

    def get_trades(self, data_req: DataRequest) -> pd.DataFrame:
        """
        Get trades (transactions) data.

        Parameters
        ----------
        data_req: DataRequest
            Parameters of data request in CryptoDataPy format.

        Returns
        -------
        df: pd.DataFrame - MultiIndex
            DataFrame with DatetimeIndex (level 0), ticker (level 1), and bid/ask price and size values (cols).
        """
        # convert data request parameters to Coin Metrics format
        self.data_req = ConvertParams(data_req).to_coinmetrics()

        # check params
        self.check_params(data_req, data_type='trades')

        # check tickers
        self.check_tickers(data_req, data_type='trades')
        sleep(self.data_req.pause)

        # params
        params = {
            'markets': ','.join(self.data_req.source_markets),
            'start_time': self.data_req.source_start_date,
            'end_time': self.data_req.source_end_date,
            'pretty': True,
            'page_size': 10000,
        }

        # get tidy data
        df = self.get_tidy_data(data_req,
                                data_type='/timeseries/market-trades',
                                params=params
                                )

        return df

    def get_quotes(self, data_req: DataRequest) -> pd.DataFrame:
        """
        Get quotes (order book) data.

        Parameters
        ----------
        data_req: DataRequest
            Parameters of data request in CryptoDataPy format.

        Returns
        -------
        df: pd.DataFrame - MultiIndex
            DataFrame with DatetimeIndex (level 0), ticker (level 1), and bid/ask price and size values (cols).
        """
        # convert data request parameters to Coin Metrics format
        self.data_req = ConvertParams(data_req).to_coinmetrics()

        # check params
        self.check_params(data_req, data_type='quotes')

        # check tickers
        self.check_tickers(data_req, data_type='quotes')
        sleep(self.data_req.pause)

        # params
        params = {
            'markets': ','.join(self.data_req.source_markets),
            'granularity': self.data_req.source_freq,
            'start_time': self.data_req.source_start_date,
            'end_time': self.data_req.source_end_date,
            'pretty': True,
            'page_size': 10000,
        }

        # get tidy data
        df = self.get_tidy_data(data_req,
                                data_type='/timeseries/market-quotes',
                                params=params
                                )

        return df

    def get_data(self, data_req: DataRequest) -> pd.DataFrame:
        """
        Get market, on-chain and/or off-chain data.

        Parameters
        ----------
        data_req: DataRequest
            Parameters of data request in CryptoDataPy format.

        Returns
        -------
        df: pd.DataFrame - MultiIndex
            DataFrame with DatetimeIndex (level 0), ticker (level 1) and values for market, on-chain and/or off-chain
            fields (cols), in tidy format.
        """
        # convert data request parameters to Coin Metrics format
        self.data_req = ConvertParams(data_req).to_coinmetrics()

        # check if fields available
        self.get_fields_info(as_list=True)
        sleep(self.data_req.pause)

        if not all([field in self.fields for field in self.data_req.source_fields]):
            raise ValueError(
                "Some selected fields are not available. Check available fields with"
                " get_fields_info method and try again."
            )

        # field lists
        ohlcv_list = ['price_open', 'price_close', 'price_high', 'price_low', 'vwap', 'volume',
                      'candle_usd_volume', 'candle_trades_count']
        oc_list = [field for field in self.fields if field not in ohlcv_list]

        # get indexes data
        self.get_indexes_info(as_list=True)
        sleep(self.data_req.pause)
        if any([ticker.upper() in self.indexes for ticker in self.data_req.source_tickers]) and any(
                [field in ohlcv_list for field in self.data_req.source_fields]
        ):
            df = self.get_indexes(data_req)
            self.data = pd.concat([self.data, df])

        # get OHLCV data
        self.get_assets_info(as_list=True)
        sleep(self.data_req.pause)
        if any([ticker in self.assets for ticker in self.data_req.source_tickers]) and any(
                [field in ohlcv_list for field in self.data_req.source_fields]
        ):
            df1 = self.get_ohlcv(data_req)
            self.data = pd.concat([self.data, df1])

        # get on-chain data
        if any([ticker in self.assets for ticker in self.data_req.source_tickers]) and any(
                [field in oc_list for field in self.data_req.source_fields]
        ):
            df2 = self.get_onchain(data_req)
            self.data = pd.concat([self.data, df2], axis=1)

        # check if df empty
        if self.data.empty:
            raise Exception("No data returned."
                            " Check data request parameters and try again.")

        # filter df for desired fields and sort index by date
        fields = [field for field in data_req.fields if field in self.data.columns]
        self.data = self.data.loc[:, fields].sort_index()

        return self.data
