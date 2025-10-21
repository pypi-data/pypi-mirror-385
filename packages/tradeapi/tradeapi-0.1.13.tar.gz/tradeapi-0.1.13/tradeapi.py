import grpc
from google.protobuf.json_format import MessageToDict
from datetime import datetime, timezone, timedelta

import pandas as pd

from finamgrpc.tradeapi.v1.auth.auth_service_pb2_grpc import AuthServiceStub
from finamgrpc.tradeapi.v1.assets.assets_service_pb2_grpc import AssetsServiceStub
from finamgrpc.tradeapi.v1.marketdata.marketdata_service_pb2_grpc import MarketDataServiceStub
from finamgrpc.tradeapi.v1.accounts.accounts_service_pb2_grpc import AccountsServiceStub
from finamgrpc.tradeapi.v1.orders.orders_service_pb2_grpc import OrdersServiceStub

from finamgrpc.tradeapi.v1.auth import auth_service_pb2
from finamgrpc.tradeapi.v1.assets import assets_service_pb2
from finamgrpc.tradeapi.v1.marketdata import marketdata_service_pb2
from finamgrpc.tradeapi.v1.accounts import accounts_service_pb2
from finamgrpc.tradeapi.v1.orders import orders_service_pb2

from finamgrpc.tradeapi.v1 import side_pb2

from google.protobuf.timestamp_pb2 import Timestamp
from google.type.interval_pb2 import Interval
from google.type.decimal_pb2 import Decimal
import asyncio
import threading
import time 

class FinamApi:
    """
    FinamApi provides methods to authenticate, fetch market data,
    account information, and manage orders via Finam's gRPC Trade API.
    """
    def __init__(self, token):
        """
        Initialize the API client:
        - Establish a secure gRPC channel
        - Authenticate and retrieve a JWT token
        - Fetch account details, assets list, and exchange list
        - Build an order status lookup table

        Args:
            token (str): API secret for authentication
        """
        self.token = token
        self.channel = grpc.secure_channel(
            'api.finam.ru:443', grpc.ssl_channel_credentials()
        )
        self.auth()

        # Fetch token details and account info
        re_tkn = auth_service_pb2.TokenDetailsRequest(token=self.jwc_token)
        acc = self.auth_stub.TokenDetails(
            re_tkn,
            metadata=(self.metadata,)
        )
        self.account_inf = acc

        # Load assets into DataFrame
        assets_stub = AssetsServiceStub(self.channel)
        assets_request = assets_service_pb2.AssetsRequest()
        assets = assets_stub.Assets(assets_request, metadata=(self.metadata,))

        data = []
        for asset in assets.assets:
            data.append({
                "symbol": asset.symbol,
                "id": asset.id,
                "ticker": asset.ticker,
                "mic": asset.mic,
                "isin": asset.isin,
                "type": asset.type,
                "name": asset.name,
            })
        self.assets = pd.DataFrame(data)

        # Load exchanges into DataFrame
        exchange_request = assets_service_pb2.ExchangesRequest()
        exchanges = assets_stub.Exchanges(exchange_request, metadata=(self.metadata,))
        exc = exchanges.exchanges
        data = [MessageToDict(e, preserving_proto_field_name=True) for e in exc]
        self.exchanges = pd.DataFrame(data=data)

        # Map numeric order statuses to human-readable strings
        self.status_order = {
            0: "Неопределенное значение",
            1: "NEW",
            2: "PARTIALLY_FILLED",
            3: "FILLED",
            4: "DONE_FOR_DAY",
            5: "CANCELED",
            6: "REPLACED",
            7: "PENDING_CANCEL",
            9: "REJECTED",
            10: "SUSPENDED",
            11: "PENDING_NEW",
            13: "EXPIRED",
            16: "FAILED",
            17: "FORWARDING",
            18: "WAIT",
            19: "DENIED_BY_BROKER",
            20: "REJECTED_BY_EXCHANGE",
            21: "WATCHING",
            22: "EXECUTED",
            23: "DISABLED",
            24: "LINK_WAIT",
            27: "SL_GUARD_TIME",
            28: "SL_EXECUTED",
            29: "SL_FORWARDING",
            30: "TP_GUARD_TIME",
            31: "TP_EXECUTED",
            32: "TP_CORRECTION",
            33: "TP_FORWARDING",
            34: "TP_CORR_GUARD_TIME",
        }

        self._q_lock = threading.Lock()
        self._q_snapshots = {}                      # {symbol: {"ver": int, "data": {...}}}
        self._q_threads = {}                        # {symbol: Thread}
        self._q_stops = {}  

    def auth(self):
        """
        Authenticate with the Finam API using the provided secret.
        Stores the JWT token and metadata header for future calls.
        """
        self.auth_stub = AuthServiceStub(self.channel)
        request = auth_service_pb2.AuthRequest(secret=self.token)
        response = self.auth_stub.Auth(request)
        self.jwc_token = response.token
        self.metadata = ('authorization', self.jwc_token)

    def account(self, account_id):
        """
        Retrieve detailed information for a specified account.

        Args:
            account_id (str): The ID of the account to fetch

        Returns:
            GetAccountResponse: Protobuf response with account details
        """
        acc_stub = AccountsServiceStub(self.channel)
        request = accounts_service_pb2.GetAccountRequest(
            account_id=account_id
        )
        response = acc_stub.GetAccount(
            request, metadata=(self.metadata,)
        )
        msg = MessageToDict(response)
        try: 
            pos = msg['positions']
            if len(pos) != 0: 
                df = pd.DataFrame([self.flatten_dict(j) for j in pos])
                msg['positions'] = df 
            else: 
                msg['positions'] = pd.DataFrame()
        except: 
            msg['positions'] = pd.DataFrame()
        return msg
    
        

    def acc_trades(self, account_id, interval: list):
        """
        Fetch trades executed on an account within a date range.

        Args:
            account_id (str): Account ID
            interval (list): Two-element list with start and end dates (YYYY-MM-DD)

        Returns:
            pd.DataFrame: Trades with numeric columns converted to floats
        """
        acc_stub = AccountsServiceStub(self.channel)
        interval_v = self.make_interval_from_strings(
            interval[0], interval[1]
        )
        request = accounts_service_pb2.TradesRequest(
            account_id=account_id,
            interval=interval_v
        )
        response = acc_stub.Trades(
            request, metadata=(self.metadata,)
        )
        data = MessageToDict(response)
        if 'trades' in data.keys():
            df = pd.DataFrame(data['trades'])
            for col in ['price', 'size']:
                df[col] = df[col].apply(
                    lambda x: float(x['value'])
                )
        else: 
            df = pd.DataFrame()
        return df

    def transactions(self, account_id, interval: list):
        """
        Fetch cash/balance transactions for an account within a date range.

        Args:
            account_id (str): Account ID
            interval (list): Two-element list with start and end dates (YYYY-MM-DD)

        Returns:
            pd.DataFrame: Transactions flattened into a table
        """
        acc_stub = AccountsServiceStub(self.channel)
        interval_v = self.make_interval_from_strings(
            interval[0], interval[1]
        )
        request = accounts_service_pb2.TransactionsRequest(
            account_id=account_id,
            interval=interval_v
        )
        response = acc_stub.Transactions(
            request, metadata=(self.metadata,)
        )
        data = MessageToDict(response)
        data = [self.flatten_dict(j) for j in data['transactions']]
        df = pd.DataFrame(data)
        return df

    def option_chain(self, symbol):
        """
        Retrieve the option chain for a given underlying symbol.

        Args:
            symbol (str): Underlying asset symbol

        Returns:
            OptionsChainResponse: Protobuf response with option chain data
        """
        option_stub = AssetsServiceStub(self.channel)
        request = assets_service_pb2.OptionsChainRequest(
            underlying_symbol=symbol
        )
        return option_stub.OptionsChain(
            request, metadata=(self.metadata,)
        )

    def orderbook(self, symbol):
        """
        Fetch the current order book (bids and offers) for a symbol.

        Args:
            symbol (str): Asset symbol

        Returns:
            dict: DataFrames for 'bid' and 'offer', sorted by price
        """
        orderbook_stub = MarketDataServiceStub(self.channel)
        request = marketdata_service_pb2.OrderBookRequest(
            symbol=symbol
        )
        ob = orderbook_stub.OrderBook(
            request, metadata=(self.metadata,)
        )
        bid, offer = [], []
        for row in ob.orderbook.rows:
            vol = float(row.buy_size.value) if row.buy_size.value else float(row.sell_size.value)
            entry = {"price": float(row.price.value), "volume": vol}
            if row.buy_size.value:
                entry["side"] = 'BID'
                bid.append(entry)
            else:
                entry["side"] = 'OFFER'
                offer.append(entry)
        df_bid = pd.DataFrame(bid).sort_values(
            'price', ascending=False, ignore_index=True
        )
        df_off = pd.DataFrame(offer).sort_values(
            'price', ignore_index=True
        )
        return {'bid': df_bid, 'offer': df_off}

    def Quotes(self, symbol):
        """
        Fetch the latest quote for a symbol and normalize to a DataFrame.

        Args:
            symbol (str)

        Returns:
            pd.DataFrame: Single-row with price, size, timestamp in Moscow time
        """
        stub = MarketDataServiceStub(self.channel)
        req = marketdata_service_pb2.QuoteRequest(symbol=symbol)
        quote = stub.LastQuote(req, metadata=(self.metadata,))
        d = MessageToDict(quote.quote, preserving_proto_field_name=True)
        flat = self.flatten_dict(d)
        df = pd.DataFrame([flat])
        df['timestamp'] = pd.to_datetime(
            df['timestamp'], utc=True
        ).dt.tz_convert('Europe/Moscow')
        return df

    def Trades(self, symbol):
        """
        Fetch the latest batch of trades for a symbol and normalize.

        Args:
            symbol (str)

        Returns:
            pd.DataFrame: Recent trades with timestamp in Moscow time
        """
        stub = MarketDataServiceStub(self.channel)
        req = marketdata_service_pb2.LatestTradesRequest(symbol=symbol)
        trades = stub.LatestTrades(req, metadata=(self.metadata,))
        rows = []
        for tr in trades.trades:
            d = MessageToDict(tr, preserving_proto_field_name=True)
            rows.append(self.flatten_dict(d))
        df = pd.DataFrame(rows)
        #df['timestamp'] = pd.to_datetime(
        #   df['timestamp'], utc=True
        #).dt.tz_convert('Europe/Moscow')
        return df

    def Bars(self, symbol, interval: list, timeframe="TIME_FRAME_H1"):
        """
        Fetch historical bar data (candlesticks) for a symbol over a date range.

        Args:
            symbol (str)
            interval (list): [start_str, end_str]
            timeframe (str): e.g., "TIME_FRAME_H1"

        Returns:
            pd.DataFrame: Bars with OHLCV and timestamp in Moscow time
        """
        stub = MarketDataServiceStub(self.channel)
        interval_v = self.make_interval_from_strings(
            interval[0], interval[1]
        )
        req = marketdata_service_pb2.BarsRequest(
            symbol=symbol,
            interval=interval_v,
            timeframe=timeframe
        )
        bars = stub.Bars(req, metadata=(self.metadata,))
        data = []
        for br in bars.bars:
            data.append(self.flatten_dict(MessageToDict(br)))
        df = pd.DataFrame(data)
        df['timestamp'] = pd.to_datetime(
            df['timestamp'], utc=True
        ).dt.tz_convert('Europe/Moscow')
        return df

    def flatten_dict(self, d, parent_key='', sep='_'):
        """
        Recursively flatten nested dicts, converting {'value':...} to plain values.

        Args:
            d (dict): Nested dictionary
            parent_key (str): Prefix for keys
            sep (str): Separator between nested keys

        Returns:
            dict: Flattened dictionary
        """
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                if set(v.keys()) == {'value'}:
                    try:
                        items.append((new_key, float(v['value'])))
                    except ValueError:
                        items.append((new_key, v['value']))
                else:
                    items.extend(
                        self.flatten_dict(v, new_key, sep).items()
                    )
            else:
                items.append((new_key, v))
        return dict(items)

    def make_interval_from_strings(self, start_str, end_str, fmt='%Y-%m-%d'):
        """
        Convert two date strings into a protobuf Interval (UTC).

        Args:
            start_str (str): Start date
            end_str (str): End date
            fmt (str): Date format

        Returns:
            Interval: Protobuf interval with UTC timestamps
        """
        dt_start = datetime.strptime(start_str, fmt).replace(
            tzinfo=timezone.utc
        )
        dt_end = datetime.strptime(end_str, fmt).replace(
            tzinfo=timezone.utc
        )
        ts_start, ts_end = Timestamp(), Timestamp()
        ts_start.FromDatetime(dt_start)
        ts_end.FromDatetime(dt_end)
        return Interval(start_time=ts_start, end_time=ts_end)

    def place_order(self, symbol, account_id, quantity, limit_price=None, 
                    side=0, type=orders_service_pb2.ORDER_TYPE_MARKET):
        """
        Place a new order (market or limit) and return its details.

        Args:
            symbol (str)
            account_id (str)
            quantity (float)
            limit_price (float, optional)
            side (int): 0=buy, 1=sell
            type (enum): Order type constant

        Returns:
            dict: {'order_id', 'status', 'time'} with time in Moscow
        """
        qty = Decimal(value=str(quantity))
        pr = Decimal(value=str(limit_price)) if limit_price else None
        sd = side_pb2.SIDE_BUY if side == 0 else side_pb2.SIDE_SELL
        stub = OrdersServiceStub(self.channel)
        req = orders_service_pb2.Order(
            symbol=symbol, account_id=account_id,
            quantity=qty, limit_price=pr,
            side=sd, type=type
        )
        resp = stub.PlaceOrder(req, metadata=(self.metadata,))
        ts = resp.transact_at
        dt_utc = datetime.fromtimestamp(
            ts.seconds + ts.nanos / 1e9,
            tz=timezone.utc
        )
        msk_tz = timezone(timedelta(hours=3))
        return {
            'order_id': resp.order_id,
            'status': self.status_order[resp.status],
            'time': dt_utc.astimezone(msk_tz)
        }

    def cancel_order(self, order_id, account_id):
        """
        Cancel an existing order and return its updated status.

        Args:
            order_id (str)
            account_id (str)

        Returns:
            dict: {'order_id', 'status', 'time'} with time in Moscow
        """
        stub = OrdersServiceStub(self.channel)
        req = orders_service_pb2.CancelOrderRequest(
            order_id=order_id, account_id=account_id
        )
        res = stub.CancelOrder(req, metadata=(self.metadata,))
        ts = res.transact_at
        dt_utc = datetime.fromtimestamp(
            ts.seconds + ts.nanos / 1e9, tz=timezone.utc
        )
        return {
            'order_id': res.order_id,
            'status': self.status_order[res.status],
            'time': dt_utc.astimezone(timezone(timedelta(hours=3)))
        }

    def orders_info(self, account_id):
        """
        Fetch all orders for an account (active and historical).

        Args:
            account_id (str)

        Returns:
            pd.DataFrame: Orders with transactAt in Moscow time
        """
        stub = OrdersServiceStub(self.channel)
        req = orders_service_pb2.OrdersRequest(account_id=account_id)
        info = stub.GetOrders(req, metadata=(self.metadata,))
        if len(info.orders) > 0: 
            rows = [self.flatten_dict(MessageToDict(o)) for o in info.orders]
            df = pd.DataFrame(rows)
            df['transactAt'] = pd.to_datetime(
                df['transactAt'], utc=True
            ).dt.tz_convert('Europe/Moscow')
            return df
        else: 
            print('No Orders Info')

    def order_info(self, account_id, order_id):
        """
        Retrieve detailed info for a specific order.

        Args:
            account_id (str)
            order_id (str)

        Returns:
            dict: Flattened order info with human-readable status
        """
        stub = OrdersServiceStub(self.channel)
        req = orders_service_pb2.GetOrderRequest(
            account_id=account_id, order_id=order_id
        )
        res = stub.GetOrder(req, metadata=(self.metadata,))
        ord_dict = MessageToDict(res.order)
        ord_dict['status'] = self.status_order[res.status]
        return self.flatten_dict(ord_dict)

    def stream_trades(self, symbol):
        """
        Open a streaming RPC for live trades on a symbol. Iterate over the returned generator to receive updates.

        Args:
            symbol (str)

        Returns:
            generator: Yields protobuf Trade messages
        """
        stub = MarketDataServiceStub(self.channel)
        req = marketdata_service_pb2.SubscribeLatestTradesRequest(symbol=symbol)
        return stub.SubscribeLatestTrades(req, metadata=(self.metadata,))
    
    def assets_params(self,symbol,account_id): 
        stub = AssetsServiceStub(self.channel)
        req = assets_service_pb2.GetAssetParamsRequest(symbol = symbol, account_id = account_id)
        res = stub.GetAssetParams(req, metadata=(self.metadata,))
        res_dict = MessageToDict(res)
        res_dict = self.flatten_dict(res_dict)
        return res_dict 
    
    def assets_info(self,symbol,account_id):
        stub = AssetsServiceStub(self.channel)
        req = assets_service_pb2.GetAssetRequest(symbol = symbol, account_id = account_id)
        res = stub.GetAsset(req, metadata=(self.metadata,))
        res_dict = MessageToDict(res)
        res_dict = self.flatten_dict(res_dict)
        return res_dict
    
    def schedule(self,symbol): 
        stub = AssetsServiceStub(self.channel)
        req = assets_service_pb2.ScheduleRequest(symbol = symbol)
        res = stub.Schedule(req, metadata=(self.metadata,))
        res_dict = MessageToDict(res)
        res_dict = self.flatten_dict(res_dict)
        return res_dict

    def ensure_quote_stream(self,symbol: str):
        if symbol in self._q_threads and self._q_threads[symbol].is_alive():
            return  # already running

        stop_evt = threading.Event()
        self._q_stops[symbol] = stop_evt

        def _runner():
            backoff = 1.0
            while not stop_evt.is_set():
                try:
                    for ev in self.stream_trades(symbol):
                        if not ev.trades:
                            continue
                        t = ev.trades[-1]  # last trade in the batch
                        snap = {
                            "symbol": ev.symbol,
                            "trade_id": t.trade_id,
                            "side": t.side,
                            "price": float(t.price.value),
                            "size": float(t.size.value),
                            "ts": t.timestamp.seconds + t.timestamp.nanos / 1e9,
                        }
                        with self._q_lock:
                            rec = self._q_snapshots.get(symbol, {"ver": 0, "data": {}})
                            rec["ver"] += 1
                            rec["data"] = snap
                            self._q_snapshots[symbol] = rec
                        backoff = 1.0  # reset backoff after a good read
                    # stream ended gracefully -> short sleep then reconnect
                    time.sleep(1.0)
                except grpc.RpcError as e:
                    # handle UNAUTHENTICATED by refreshing your JWT (if you have a method for it)
                    if e.code() == grpc.StatusCode.UNAUTHENTICATED:
                        try:
                            # self.refresh_jwt()   # implement if you have it
                            pass
                        except Exception:
                            pass
                        backoff = 1.0
                    # backoff for other errors
                    time.sleep(min(30.0, backoff))
                    backoff = min(30.0, backoff * 2)

        th = threading.Thread(target=_runner, name=f"quote:{symbol}", daemon=True)
        th.start()
        self._q_threads[symbol] = th

    def get_quote_snapshot(self,symbol: str) -> dict | None:
        with self._q_lock:
            snap = self._q_snapshots.get(symbol)
            # returns like {"ver": 17, "data": {"symbol": "...", "bid": 99.1, "ask": 99.2, "last": 99.2, "ts": ...}}
            return None if snap is None else {"ver": snap["ver"], "data": dict(snap["data"])}

    def stop_quote_stream(self,symbol: str):
        """
        Gracefully stop the background quote stream for a given symbol.
        """
        evt = self._q_stops.get(symbol)
        th = self._q_threads.get(symbol)

        if evt:
            evt.set()               # signal the runner loop to stop
        if th and th.is_alive():
            th.join(timeout=2.0)    # wait a moment for it to finish

        # clean up dicts
        self._q_stops.pop(symbol, None)
        self._q_threads.pop(symbol, None)
        self._q_snapshots.pop(symbol, None)


