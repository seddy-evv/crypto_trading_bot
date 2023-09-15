import numpy as np
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.engine.base import Engine
import numpy
from datetime import datetime, timedelta
from currencycom.client import Client, CandlesticksChartInervals
from currencycom.client import OrderSide, OrderType
from typing import Union


class Bot:
    trade_client: Client = None

    actual_prices: list = []
    last_order: dict = {}
    account_info: dict = {}
    login_correct: bool = False

    engine: Engine = create_engine("sqlite:///BTCUSDTstream.db")

    # api_key: str = ""
    # api_secret: str = ""
    symbol: str = ""
    qty: float = 0.0001

    # The value that divides the total interval into segments, min
    interval: CandlesticksChartInervals = CandlesticksChartInervals.MINUTE
    intervals = {CandlesticksChartInervals.MINUTE: 1,
                 CandlesticksChartInervals.FIVE_MINUTES: 5,
                 CandlesticksChartInervals.FIFTEEN_MINUTES: 15,
                 CandlesticksChartInervals.THIRTY_MINUTES: 30,
                 CandlesticksChartInervals.HOUR: 60,
                 CandlesticksChartInervals.FOUR_HOURS: 240,
                 CandlesticksChartInervals.DAY: 1440,
                 CandlesticksChartInervals.WEEK: 10080}

    # Total interval, min
    buy_interval: int = 0
    sell_interval: int = 0

    # Variable is used if variable buy_interval or variable
    # sell_interval is not specified, for sum the total interval
    min_delay: int = 0

    # If a value is specified, variable interval is not used.
    # The variable defines the interval of seconds between which
    # a request is made to the exchange.
    interval_in_sec: int = 0

    # The value determines the number of prices that are used
    # to calculate the coefficient.
    # Look back min = 2 !
    stack_buy: int = 0
    stack_sell: int = 0

    # Boundaries of buying and selling with percent.
    # buy 0.001 = 0.1%
    dip_limit: float = -0.002
    up_limit: float = 0
    # sell 0.001 = 0.1%
    profit_limit: float = 0.006
    loss_limit: float = 0

    # Boundaries of buying and selling with RSI coefficient.
    rsi_stack_buy: int = 0
    rsi_stack_sell: int = 0
    rsi_oversold: int = 30
    rsi_overbought: int = 70

    # The variable is used to display the coefficient on the form.
    current_rate: float = 0

    def __init__(self, **params) -> None:
        self.api_key = params.get("api_key", "")
        self.api_secret = params.get("api_secret", "")
        self.trade_client = Client(self.api_key, self.api_secret)

        # self.actual_prices = []
        # self.last_order = {}
        # self.account_info = {}
        # self.login_correct = False
        self.update_account_info()

    def update_account_info(self) -> None:
        """
        Get current account information and data about the
        user's balance in dollars and cryptocurrency.
        """
        account_info: dict
        try:
            account_info = self.trade_client.get_account_info()
        except Exception as e:
            self.write_logs("WARNING", "init", e)
            account_info = {}

        if account_info.get("canTrade", False):
            self.login_correct = True
            self.account_info = account_info
            self.write_logs("INFO", "init", "login correct")
        else:
            self.login_correct = False
            self.write_logs("WARNING", "init", "login incorrect")

    def start(self) -> str:
        """
        The preliminary stage at which the work of the crypto
        exchange is checked and the choice of the direction of
        trading: buying or selling.

        :rtype: str
        :return: crypto exchange status
        """
        exchange_working: bool = self._test_exchange()
        if exchange_working and self.last_order:
            try:
                self._sell()
            except Exception as e:
                self.write_logs("ERROR", "start sell part", e)
                return "not working"
            return "working"
        elif exchange_working and not self.last_order:
            try:
                self.last_order = self._buy()
            except Exception as e:
                self.write_logs("ERROR", "start buy part", e)
                return "not working"
            return "working"
        else:
            return "closed"

    def _test_exchange(self) -> bool:
        """
        Check the work of the crypto exchange and that the API returns data.

        :rtype: boolean
        :return: True if the crypto exchange is working and False otherwise.
        """
        frame: pd.DataFrame
        try:
            frame = pd.DataFrame(self.trade_client.get_agg_trades(self.symbol,
                                                                  limit=1))
        except Exception as e:
            self.write_logs("WARNING", "test exchange", e)
            frame = pd.DataFrame()
        if not frame.empty:
            return True
        else:
            return False

    def actualize_prices(self) -> None:
        """
        Actualize prices depending on the value of the coefficient stack_buy.
        """
        if self.interval_in_sec:
            for _ in range(self.stack_buy + 1):
                self._add_price(self.actual_prices)

    def _add_price(self, prices: list, delete: bool = False) -> None:
        """
        Get a price for a cryptocurrency and add it to the list.

        :param prices: price list
        :type prices: list
        :param delete: If the value is true, then the first price from
        the list will be removed.
        :type delete: boolean
        """
        req: dict
        try:
            req = self.trade_client.get_agg_trades(self.symbol, limit=1)
            prices.append(req[0])
            if delete:
                prices.pop(0)
        except Exception as e:
            self.write_logs("WARNING", "get price", e)

    def check_orders(self) -> Union[str, dict]:
        """
        Get previous orders from the database and if the last transaction
        was a purchase, return the order data.

        :rtype: str|dict
        :return: if the last order was for a purchase, return the date
        of the transaction otherwise an empty string.
        """
        last_ord: pd.DataFrame
        transact_time: pd.Series
        side: str
        try:
            last_ord = pd.read_sql("SELECT * FROM Orders WHERE Symbol = '{}' "
                                   "ORDER BY transactTime DESC LIMIT 1"
                                   .format(self.symbol), self.engine)

            transact_time = last_ord["transactTime"][0]
            side = last_ord["Side"][0]
            if side == "BUY":
                self.write_logs("INFO",
                                "check orders",
                                "last order is {}".format(transact_time))
                return {"transactTime": transact_time}
            else:
                self.write_logs("INFO", "check orders", "no purchase order")
                return ""
        except Exception as e:
            self.write_logs("INFO",
                            "check orders",
                            "no sql base - {}".format(e))
            return ""

    def _buy(self) -> dict:
        """
        Create a dataframe with prices and choose the function of creating a
        purchase order depending on the specified parameters.

        :rtype : dict
        :return: order
        """
        df: pd.DataFrame
        order: dict = {}
        try:
            if self.actual_prices and self.stack_buy:
                self._add_price(self.actual_prices, True)
                df = self._create_frame_req(self.actual_prices)
            elif self.actual_prices:
                self._add_price(self.actual_prices)
                df = self._create_frame_req(self.actual_prices)
            else:
                if self.buy_interval:
                    df = self._get_current_data(self.buy_interval)
                else:
                    df = self._get_current_data(self.min_delay)
            if not df.empty:
                if self.rsi_stack_buy:
                    order = self._buy_by_rsi(df)
                else:
                    order = self._buy_by_percent(df)
        except Exception as e:
            self.write_logs("WARNING", "buy", e)
        return order

    def _buy_by_rsi(self, df: pd.DataFrame) -> dict:
        """
        Create a purchase order if the RSI coefficient is less than the
        given value.

        :param df: DataFrame with prices
        :type df: DataFrame

        :rtype : dict
        :return: order
        """
        rsi: float
        order: dict

        buy_order: dict = {}
        rsi = self._get_rsi(df, self.rsi_stack_buy)
        self.current_rate = 0 if numpy.isnan(rsi) else rsi
        if rsi is not None and rsi < self.rsi_oversold:
            order = self._create_order(OrderSide.BUY, OrderType.MARKET)
            if order and order.get("transactTime"):
                self._write_order(order)
                self.min_delay = 0
                self.write_logs("INFO", "create buy order rsi", str(order))
                buy_order = order
        return buy_order

    def _buy_by_percent(self, df: pd.DataFrame) -> dict:
        """
        Create a buy order if the price has risen or fallen to certain values.
        df.Open.pct_change() - The change value of the course
        relative to the previous one in the sequence. To get
        the percentage, you need to multiply by 100.
        (df.Open.pct_change() + 1).cumprod() - Multiplies all
        the elements in a sequence, resulting in the percentage
        difference between the first and last values in the
        sequence.
        - means that the value has fallen,
        + means that it has increased.

        :param df: DataFrame with prices
        :type df: DataFrame

        :rtype : dict
        :return: order
        """
        order: dict

        buy_order: dict = {}
        ret: np.ndarray = (df.Open.pct_change() + 1).cumprod() - 1
        self.current_rate = 0 if numpy.isnan(ret[-1]) else ret[-1] * 100
        if (self.dip_limit and ret[-1] < self.dip_limit) or \
                (self.up_limit and ret[-1] > self.up_limit):
            order = self._create_order(OrderSide.BUY,
                                       OrderType.MARKET)
            if order and order.get("transactTime"):
                self._write_order(order)
                self.min_delay = 0
                self.write_logs("INFO", "create buy order percent", str(order))
                buy_order = order
        return buy_order

    def _sell(self) -> None:
        """
        Create a dataframe with prices and choose the method of creating a
        sales order depending on the specified parameters.

        """
        df: pd.DataFrame
        transact_time: datetime
        sincebuy: pd.Series

        if self.last_order and self.last_order.get("transactTime"):
            try:
                if (self.actual_prices and
                    len(self.actual_prices) < self.stack_sell) \
                        or (self.actual_prices and not self.stack_sell):
                    self._add_price(self.actual_prices)
                    df = self._create_frame_req(self.actual_prices)
                elif self.actual_prices:
                    self._add_price(self.actual_prices, True)
                    df = self._create_frame_req(self.actual_prices)
                else:
                    if self.sell_interval:
                        df = self._get_current_data(self.sell_interval)
                    else:
                        df = self._get_current_data(self.min_delay)
                if not df.empty:
                    # Fetching rows by date field if the condition is met.
                    # The sample is needed to analyze the rise or fall of
                    # prices from the time of purchase to the present
                    # but within the interval sell_interval.
                    transact_time = self.last_order["transactTime"]
                    sincebuy = df.loc[df.index > pd.to_datetime(transact_time,
                                                                unit="ms")]
                    if self.rsi_stack_buy:
                        self._sell_by_rsi(sincebuy)
                    else:
                        self._sell_by_percent(sincebuy)
            except Exception as e:
                self.write_logs("WARNING", "sell", e)
        else:
            self.last_order = {}

    def _sell_by_rsi(self, sincebuy: pd.Series) -> None:
        """
        Create a sell order if the RSI coefficient is greater than the
        given value.

        :param sincebuy: array of prices
        """
        order: dict

        rsi: float = self._get_rsi(sincebuy, self.rsi_stack_sell)
        self.current_rate = 0 if numpy.isnan(rsi) else rsi
        if rsi is not None and rsi > self.rsi_overbought:
            order = self._create_order(OrderSide.SELL, OrderType.MARKET)
            if order and order.get("transactTime"):
                self._write_order(order)
                self.last_order = {}
                self.write_logs("INFO", "create sell order rsi", str(order))

    def _sell_by_percent(self, sincebuy: pd.Series) -> None:
        """
        Create a sell order if the price has risen or fallen to certain values.

        :param sincebuy: array of prices
        """
        sincebuyret: np.ndarray
        order: dict

        if len(sincebuy) > 0:
            sincebuyret = (sincebuy.Open.pct_change() + 1).cumprod() - 1
            self.current_rate = 0 if numpy.isnan(sincebuyret[-1]) \
                else sincebuyret[-1] * 100
            if (self.profit_limit and sincebuyret[-1] > self.profit_limit) or \
                    (self.loss_limit and sincebuyret[-1] < self.loss_limit):
                order = self._create_order(OrderSide.SELL, OrderType.MARKET)
                if order and order.get("transactTime"):
                    self._write_order(order)
                    self.last_order = {}
                    self.write_logs("INFO",
                                    "create sell order percent",
                                    str(order))

    def _create_frame_req(self, prices: list) -> pd.DataFrame:
        """
        Create a dataframe with prices.

        :param prices: list with prices
        :type prices: list

        :rtype : DataFrame
        :return: DataFrame with prices.
        """
        frame: pd.DataFrame

        if prices:
            frame = pd.DataFrame(prices)
            frame = frame.loc[:, ["p", "T"]]
            frame.columns = ["Open", "Time"]
            frame.Time = pd.to_datetime(frame.Time, unit="ms")
            frame = frame.set_index("Time")
            frame.index = pd.to_datetime(frame.index, unit="ms")
            frame.Open = frame.Open.astype(float)
            frame['symbol'] = self.symbol
        else:
            frame = pd.DataFrame()
        return frame

    def _get_current_data(self, look_back: int) -> pd.DataFrame:
        """
        Get current data on prices for a certain period of time with a
        certain interval.

        :param look_back: period in min
        :type look_back: int

        :rtype : DataFrame
        :return: DataFrame with prices.
        """
        select_per: datetime
        klien: dict
        frame: pd.DataFrame

        try:
            if look_back:
                select_per = datetime.now() - timedelta(minutes=look_back)
                klien = self.trade_client.get_klines(self.symbol,
                                                     self.interval,
                                                     select_per)
                frame = pd.DataFrame(klien)
                frame.columns = ["Time", "Open", "High",
                                 "Low", "Close", "Volume"]
                frame = frame.set_index("Time")
                frame.index = pd.to_datetime(frame.index, unit="ms")
                frame = frame.astype(float)
                self.min_delay += self.intervals[self.interval]
            else:
                frame = pd.DataFrame()
                self.min_delay += self.intervals[self.interval]
        except Exception as e:
            self.write_logs("WARNING", "create frame", e)
            frame = pd.DataFrame()
        return frame

    @staticmethod
    def _get_rsi(closes: Union[pd.Series, pd.DataFrame], n: int = 0) -> float:
        """
        Calculate the rsi coefficient by the array of prices and
        the specified quantity for analysis.

        :param closes: array of prices
        :param n: number of analyzed prices
        :type n: int

        :rtype : float
        :return: coefficient RSI
        """
        prices: numpy.ndarray
        deltas: numpy.ndarray
        seed: numpy.ndarray
        up: float
        down: float
        rs: float
        rsi: float

        # calculate the difference between adjacent elements in cent,
        # + it has grown, - has fallen
        np_closes: numpy.ndarray = numpy.array(closes.Open)
        if n:
            prices = np_closes[- n + 1:]
        else:
            prices = np_closes
            n = len(np_closes)
        deltas = numpy.diff(prices)
        if any(deltas):
            seed = deltas[:n + 1]
            # seed[seed >= 0] - a list is formed with values
            # by condition from seed.
            up = seed[seed >= 0].sum() / n
            down = -seed[seed < 0].sum() / n
            if down:
                rs = up / down
                rsi = 100. - 100. / (1. + rs)
                return rsi
        return 0

    def _create_order(self, side: OrderSide, or_type: OrderType) -> dict:
        """
        Create an order to buy or sell cryptocurrency.

        :param side: order side - buy or sell
        :type side: OrderSide
        :param or_type: order type - limit, market or stop
        :type or_type: OrderType

        :rtype : dict
        :return: order
        """
        order: dict

        try:
            order = self.trade_client.new_order(symbol=self.symbol,
                                                side=side,
                                                order_type=or_type,
                                                quantity=self.qty)
            return order
        except Exception as e:
            self.write_logs("ERROR", "create order", e)
            return {}

    def _write_order(self, current_order: dict) -> None:
        """
        Write the successfully created sales or purchase order
        to the sql database.

        :param current_order: order
        :type current_order: dict
        """
        frame: pd.DataFrame = pd.DataFrame(current_order)
        # Selection of all rows in two columns of the frame.
        frame = frame.loc[:, ["symbol", "transactTime", "price", "origQty",
                              "executedQty", "side"]]
        frame.columns = ["Symbol", "transactTime", "Price", "OrigQty",
                         "ExecutedQty", "Side"]
        frame.transactTime = pd.to_datetime(frame.transactTime, unit="ms")
        frame.Price = frame.Price.astype(float)
        frame.OrigQty = frame.OrigQty.astype(float)
        frame.ExecutedQty = frame.ExecutedQty.astype(float)
        try:
            frame.to_sql("Orders", self.engine, if_exists="append",
                         index=False)
            self.update_account_info()
        except Exception as e:
            self.write_logs("ERROR", "write order", e)

    def test_attributes(self) -> None:
        """
        Method for debug testing.
        """
        attributes: list = [(self.symbol, type(self.symbol)),
                            (self.qty, type(self.qty)),
                            (self.interval, type(self.interval)),
                            (self.buy_interval, type(self.buy_interval)),
                            (self.sell_interval, type(self.sell_interval)),
                            (self.interval_in_sec, type(self.interval_in_sec)),
                            (self.stack_buy, type(self.stack_buy)),
                            (self.stack_sell, type(self.stack_sell)),
                            (self.dip_limit, type(self.dip_limit)),
                            (self.up_limit, type(self.up_limit)),
                            (self.profit_limit, type(self.profit_limit)),
                            (self.loss_limit, type(self.loss_limit)),
                            (self.rsi_stack_buy, type(self.rsi_stack_buy)),
                            (self.rsi_stack_sell, type(self.rsi_stack_sell)),
                            (self.rsi_oversold, type(self.rsi_oversold)),
                            (self.rsi_overbought, type(self.rsi_overbought))]
        self.write_logs("INFO", "attributes", attributes)

    @staticmethod
    def write_logs(type_log: str, chapter: str, message: Union[str, Exception, list]) -> None:
        date: str
        log: str

        try:
            with open("system.log", "a") as file:
                date = datetime.now().strftime("%Y-%m-%d %H:%M")
                log = "{} {} {} {}".format(type_log, date, chapter, message)
                file.write(log + "\n")
        except Exception as e:
            print(e)

    def sell_crypto(self, qty: float) -> bool:
        """
        Force sell cryptocurrency if needed.

        :param qty:
        :type qty: float

        :rtype: boolean
        :return: True if the cryptocurrency is successfully sold and False otherwise
        """
        order: dict

        try:
            order = self.trade_client.new_order(symbol=self.symbol,
                                                side=OrderSide.SELL,
                                                order_type=OrderType.MARKET,
                                                quantity=qty)
            self._write_order(order)
            self.write_logs("INFO", "sell crypto", str(order))
            return True
        except Exception as e:
            self.write_logs("ERROR", "sell crypto", e)
            return False
