from currencycom.client import CandlesticksChartInervals
from bot.crypto_bot import Bot
import tkinter as tk
from tkinter import ttk


class Frames:

    crypto_bot = None
    id = None
    sleep_interval = 0
    match_inervals = {'1m': CandlesticksChartInervals.MINUTE,
                      '5m': CandlesticksChartInervals.FIVE_MINUTES,
                      '15m': CandlesticksChartInervals.FIFTEEN_MINUTES,
                      '30m': CandlesticksChartInervals.THIRTY_MINUTES,
                      '1h': CandlesticksChartInervals.HOUR,
                      '4h': CandlesticksChartInervals.FOUR_HOURS,
                      '1d': CandlesticksChartInervals.DAY,
                      '1w': CandlesticksChartInervals.WEEK}

    def __init__(self, window_frame):

        self.window = window_frame
        self.window.title("Cryptocurrency trading bot")

        # Initial form
        self.frm_form = tk.Frame(relief=tk.SUNKEN, borderwidth=3)
        self.frm_form.pack()

        self.lbl_api_key = tk.Label(master=self.frm_form, text="Api key:")
        self.ent_api_key = tk.Entry(master=self.frm_form, width=50, show="*")
        self.lbl_api_sec = tk.Label(master=self.frm_form, text="Api secret:")
        self.ent_api_sec = tk.Entry(master=self.frm_form, width=50, show="*")
        self.lbl_warning = tk.Label(master=self.frm_form,
                                    text="Api key or Api secret is not "
                                         "correct. Try again")

        self.lbl_api_key.grid(row=0, column=0, sticky="e")
        self.ent_api_key.grid(row=0, column=1)
        self.lbl_api_sec.grid(row=1, column=0, sticky="e")
        self.ent_api_sec.grid(row=1, column=1)

        self.frm_buttons = tk.Frame()
        self.frm_buttons.pack(fill=tk.X, ipadx=5, ipady=5)
        self.btn_enter = tk.Button(master=self.frm_buttons, text="Enter",
                                   command=self.check_currency)
        self.btn_enter.pack(side=tk.RIGHT, ipadx=10)

        # Settings form
        self.setting_form = tk.Frame(relief=tk.SUNKEN, borderwidth=3)

        self.lbl_balance = tk.Label(master=self.setting_form, text="Balance:")
        self.lbl_balance_cont = tk.Label(master=self.setting_form, text="")
        self.lbl_currency = tk.Label(master=self.setting_form,
                                     text="Choose currency:")
        self.currency = ttk.Combobox(master=self.setting_form, width=50,
                                     values=[
                                         "BTC",
                                         "ETH",
                                         "LTC",
                                         "DOGE",
                                         "SHIB",
                                         "ANT",
                                         "XRP"])
        self.currency.current(0)
        self.lbl_qty = tk.Label(master=self.setting_form, text="Quantity:")
        self.ent_qty = tk.Entry(master=self.setting_form, width=50,
                                validate="key")
        self.ent_qty['validatecommand'] = (self.ent_qty.
                                           register(self.test_val_float),
                                           '%P', '%d')
        self.lbl_info = tk.Label(master=self.setting_form,
                                 text="Specify an interval greater"
                                      " or equal 1 min:")
        self.lbl_min = tk.Label(master=self.setting_form,
                                text="Choose interval:")
        self.ent_min = ttk.Combobox(master=self.setting_form,
                                    width=50,
                                    values=['1m',
                                            '5m',
                                            '15m',
                                            '30m',
                                            '1h',
                                            '4h',
                                            '1d',
                                            '1w'])
        self.ent_min.current(0)
        self.lbl_min_buy = tk.Label(master=self.setting_form,
                                    text="Purchase range, min:")
        self.ent_min_buy = tk.Entry(master=self.setting_form,
                                    width=50, validate="key")
        self.ent_min_buy['validatecommand'] = (self.ent_min_buy.
                                               register(self.test_val),
                                               '%P', '%d')
        self.lbl_min_sell = tk.Label(master=self.setting_form,
                                     text="Selling range, min:")
        self.ent_min_sell = tk.Entry(master=self.setting_form,
                                     width=50, validate="key")
        self.ent_min_sell['validatecommand'] = (self.ent_min_sell.
                                                register(self.test_val),
                                                '%P', '%d')
        self.lbl_info_sec = tk.Label(master=self.setting_form,
                                     text="or an interval less 1 min.:")
        self.lbl_sec = tk.Label(master=self.setting_form,
                                text="Interval, sec.:")
        self.ent_sec = tk.Entry(master=self.setting_form,
                                width=50, validate="key")
        self.ent_sec['validatecommand'] = (self.ent_sec.
                                           register(self.test_val),
                                           '%P', '%d')
        self.lbl_sec_buy = tk.Label(master=self.setting_form,
                                    text="Number of purchase intervals:")
        self.ent_sec_buy = tk.Entry(master=self.setting_form,
                                    width=50, validate="key")
        self.ent_sec_buy['validatecommand'] = (self.ent_sec_buy.
                                               register(self.test_val),
                                               '%P', '%d')
        self.lbl_sec_sell = tk.Label(master=self.setting_form,
                                     text="Number of sales intervals:")
        self.ent_sec_sell = tk.Entry(master=self.setting_form,
                                     width=50, validate="key")
        self.ent_sec_sell['validatecommand'] = (self.ent_sec_sell.
                                                register(self.test_val),
                                                '%P', '%d')
        self.lbl_boundaries = tk.Label(master=self.setting_form,
                                       text="Specify the boundaries of buying"
                                            " and selling with percent:")
        self.lbl_dip_limit = tk.Label(master=self.setting_form,
                                      text="Dip threshold,-%:")
        self.ent_dip_limit = tk.Entry(master=self.setting_form,
                                      width=50, validate="key")
        self.ent_dip_limit['validatecommand'] = (self.ent_dip_limit.
                                                 register(self.test_val_float),
                                                 '%P', '%d')
        self.lbl_up_limit = tk.Label(master=self.setting_form,
                                     text="Upward trend threshold,%:")
        self.ent_up_limit = tk.Entry(master=self.setting_form,
                                     width=50, validate="key")
        self.ent_up_limit['validatecommand'] = \
            (self.ent_up_limit.register(self.test_val_float), '%P', '%d')
        self.lbl_profit_limit = tk.Label(master=self.setting_form,
                                         text="Profit threshold,%:")
        self.ent_profit_limit = tk.Entry(master=self.setting_form,
                                         width=50, validate="key")
        self.ent_profit_limit['validatecommand'] = \
            (self.ent_profit_limit.register(self.test_val_float), '%P', '%d')
        self.lbl_loss_limit = tk.Label(master=self.setting_form,
                                       text="Stop loss threshold,-%:")
        self.ent_loss_limit = tk.Entry(master=self.setting_form,
                                       width=50, validate="key")
        self.ent_loss_limit['validatecommand'] = \
            (self.ent_loss_limit.register(self.test_val_float), '%P', '%d')
        self.lbl_RSI = tk.Label(master=self.setting_form,
                                text="or RSI coefficient:")
        self.lbl_buy_stack = tk.Label(master=self.setting_form,
                                      text="Purchase stack:")
        self.ent_buy_stack = tk.Entry(master=self.setting_form,
                                      width=50, validate="key")
        self.ent_buy_stack['validatecommand'] = (self.ent_buy_stack.
                                                 register(self.test_val),
                                                 '%P', '%d')
        self.lbl_sell_stack = tk.Label(master=self.setting_form,
                                       text="Selling stack:")
        self.ent_sell_stack = tk.Entry(master=self.setting_form,
                                       width=50, validate="key")
        self.ent_sell_stack['validatecommand'] = (self.ent_sell_stack.
                                                  register(self.test_val),
                                                  '%P', '%d')
        self.lbl_oversold = tk.Label(master=self.setting_form,
                                     text="Oversold,%:")
        self.ent_oversold = tk.Entry(master=self.setting_form,
                                     width=50, validate="key")
        self.ent_oversold['validatecommand'] = (self.ent_oversold.
                                                register(self.test_val),
                                                '%P', '%d')
        self.lbl_overbought = tk.Label(master=self.setting_form,
                                       text="Overbought,%:")
        self.ent_overbought = tk.Entry(master=self.setting_form,
                                       width=50, validate="key")
        self.ent_overbought['validatecommand'] = (self.ent_overbought.
                                                  register(self.test_val),
                                                  '%P', '%d')

        self.lbl_balance.grid(row=0, column=0, sticky="e")
        self.lbl_balance_cont.grid(row=0, column=1)
        self.lbl_currency.grid(row=1, column=0, sticky="e")
        self.currency.grid(row=1, column=1)
        self.currency.current(0)
        self.lbl_qty.grid(row=2, column=0, sticky="e")
        self.ent_qty.grid(row=2, column=1)
        self.lbl_info.grid(row=3, column=1, sticky="e")
        self.lbl_min.grid(row=4, column=0, sticky="e")
        self.ent_min.grid(row=4, column=1)
        self.lbl_min_buy.grid(row=5, column=0, sticky="e")
        self.ent_min_buy.grid(row=5, column=1)
        self.lbl_min_sell.grid(row=6, column=0, sticky="e")
        self.ent_min_sell.grid(row=6, column=1)
        self.lbl_info_sec.grid(row=7, column=1, sticky="e")
        self.lbl_sec.grid(row=8, column=0, sticky="e")
        self.ent_sec.grid(row=8, column=1)
        self.lbl_sec_buy.grid(row=9, column=0, sticky="e")
        self.ent_sec_buy.grid(row=9, column=1)
        self.lbl_sec_sell.grid(row=10, column=0, sticky="e")
        self.ent_sec_sell.grid(row=10, column=1)
        self.lbl_boundaries.grid(row=11, column=1, sticky="e")
        self.lbl_dip_limit.grid(row=12, column=0, sticky="e")
        self.ent_dip_limit.grid(row=12, column=1)
        self.lbl_up_limit.grid(row=13, column=0, sticky="e")
        self.ent_up_limit.grid(row=13, column=1)
        self.lbl_profit_limit.grid(row=14, column=0, sticky="e")
        self.ent_profit_limit.grid(row=14, column=1)
        self.lbl_loss_limit.grid(row=15, column=0, sticky="e")
        self.ent_loss_limit.grid(row=15, column=1)
        self.lbl_RSI.grid(row=16, column=1, sticky="e")
        self.lbl_buy_stack.grid(row=17, column=0, sticky="e")
        self.ent_buy_stack.grid(row=17, column=1)
        self.lbl_sell_stack.grid(row=18, column=0, sticky="e")
        self.ent_sell_stack.grid(row=18, column=1)
        self.lbl_oversold.grid(row=19, column=0, sticky="e")
        self.ent_oversold.grid(row=19, column=1)
        self.lbl_overbought.grid(row=20, column=0, sticky="e")
        self.ent_overbought.grid(row=20, column=1)

        self.frm_buttons_set = tk.Frame()
        self.btn_start = tk.Button(master=self.frm_buttons_set,
                                   text="Start trading",
                                   command=self.start_trading)
        self.btn_start.pack(side=tk.RIGHT, ipadx=10)
        self.btn_sell = tk.Button(master=self.frm_buttons_set,
                                  text="Sell crypto",
                                  command=self.instant_sell_crypto)
        self.btn_sell.pack(side=tk.LEFT, ipadx=10)

        # Status Form
        self.status_form = tk.Frame(relief=tk.SUNKEN, borderwidth=3)
        self.lbl_balance_status = tk.Label(master=self.status_form,
                                           text="Balance:")
        self.lbl_balance_cont_status = tk.Label(master=self.status_form,
                                                text="")
        self.lbl_bot_status = tk.Label(master=self.status_form,
                                       text="Bot status:")
        self.lbl_bot_cont_status = tk.Label(master=self.status_form,
                                            text="")
        self.lbl_exchange_status = tk.Label(master=self.status_form,
                                            text="Exchange status:")
        self.lbl_exchange_cont_status = tk.Label(master=self.status_form,
                                                 text="")
        self.lbl_order_status = tk.Label(master=self.status_form,
                                         text="Order status:")
        self.lbl_order_cont_status = tk.Label(master=self.status_form,
                                              text="")
        self.lbl_rate_status = tk.Label(master=self.status_form,
                                        text="Current rate:")
        self.lbl_rate_cont_status = tk.Label(master=self.status_form,
                                             text="")
        self.frm_buttons_status = tk.Frame()
        self.btn_stop = tk.Button(master=self.frm_buttons_status,
                                  text="Stop",
                                  command=self.stop_bot)
        self.btn_stop.pack(side=tk.RIGHT, ipadx=10)
        self.btn_start = tk.Button(master=self.frm_buttons_status,
                                   text="Start",
                                   command=self.start_bot)
        self.btn_start.pack(side=tk.RIGHT, ipadx=10)

    def check_currency(self):
        """
        'Enter' button handler.
        """
        params = {"api_key": self.ent_api_key.get(),
                  "api_secret": self.ent_api_sec.get()}

        self.crypto_bot = Bot(**params)
        if not self.crypto_bot.login_correct:
            self.lbl_warning.grid(row=2, column=1, sticky="e")
        else:
            self.frm_buttons.destroy()
            self.frm_form.destroy()
            self.setting_form.pack()

            self.frm_buttons_set.pack(fill=tk.X, ipadx=5, ipady=5)
            acc_info = self.crypto_bot.account_info
            if self.crypto_bot.account_info.get("balances", False):
                balance = ", ".join(["{} = {}".format(bl["asset"], bl["free"])
                                     for bl in acc_info["balances"]])
                self.lbl_balance_cont["text"] = balance

    def start_trading(self):
        """
        'Start trading' button handler
        """
        exc = []
        self.crypto_bot.symbol = self.currency.get() + "/USD"

        quantity = self.get_value(self.ent_qty.get(), "float", exc)
        if quantity:
            self.crypto_bot.qty = quantity
        interval = self.ent_min.get()
        self.crypto_bot.interval = self.match_inervals[interval]
        buy_interval = self.get_value(self.ent_min_buy.get(), "int", exc)
        if buy_interval:
            self.crypto_bot.buy_interval = buy_interval
        sell_interval = self.get_value(self.ent_min_sell.get(), "int", exc)
        if sell_interval:
            self.crypto_bot.sell_interval = sell_interval
        interval_in_sec = self.get_value(self.ent_sec.get(), "int", exc)
        if interval_in_sec:
            self.crypto_bot.interval_in_sec = interval_in_sec
        stack_buy = self.get_value(self.ent_sec_buy.get(), "int", exc)
        if stack_buy:
            self.crypto_bot.stack_buy = stack_buy
        stack_sell = self.get_value(self.ent_sec_sell.get(), "int", exc)
        if stack_sell:
            self.crypto_bot.stack_sell = stack_sell
        dip_limit = self.get_value(self.ent_dip_limit.get(), "float", exc)
        if dip_limit:
            self.crypto_bot.dip_limit = - dip_limit / 100
        up_limit = self.get_value(self.ent_up_limit.get(), "float", exc)
        if up_limit:
            self.crypto_bot.up_limit = up_limit / 100
        profit_limt = self.get_value(self.ent_profit_limit.get(), "float", exc)
        if profit_limt:
            self.crypto_bot.profit_limit = profit_limt / 100
        loss_limit = self.get_value(self.ent_loss_limit.get(), "float", exc)
        if loss_limit:
            self.crypto_bot.loss_limit = - loss_limit / 100
        rsi_stack_buy = self.get_value(self.ent_buy_stack.get(), "int", exc)
        if rsi_stack_buy:
            self.crypto_bot.rsi_stack_buy = rsi_stack_buy
        rsi_stack_sell = self.get_value(self.ent_sell_stack.get(), "int", exc)
        if rsi_stack_sell:
            self.crypto_bot.rsi_stack_sell = rsi_stack_sell
        rsi_oversold = self.get_value(self.ent_oversold.get(), "int", exc)
        if rsi_oversold:
            self.crypto_bot.rsi_oversold = rsi_oversold
        rsi_overbought = self.get_value(self.ent_overbought.get(), "int", exc)
        if rsi_overbought:
            self.crypto_bot.rsi_overbought = rsi_overbought

        if self.crypto_bot.interval_in_sec:
            self.sleep_interval = self.crypto_bot.interval_in_sec * 1000
        else:
            interval = self.crypto_bot.interval
            intervals = self.crypto_bot.intervals
            self.sleep_interval = intervals[interval] * 60 * 1000
        self.crypto_bot.last_order = self.crypto_bot.check_orders()
        if self.crypto_bot.last_order:
            self.lbl_order_cont_status["text"] = "SELL"
        else:
            self.lbl_order_cont_status["text"] = "BUY"
        if self.crypto_bot.account_info.get("balances", False):
            acc_info = self.crypto_bot.account_info
            balance = ", ".join(["{} = {}".format(bl["asset"], bl["free"])
                                 for bl in acc_info["balances"]])
            self.lbl_balance_cont_status["text"] = balance

        self.crypto_bot.write_logs("INFO", "init setting frame", exc)

        self.crypto_bot.test_attributes()
        self.crypto_bot.actualize_prices()

        self.setting_form.destroy()
        self.frm_buttons_set.destroy()
        self.status_form.pack()

        self.frm_buttons_status.pack(fill=tk.X, ipadx=5, ipady=5)
        self.lbl_balance_status.grid(row=0, column=0, sticky="e")
        self.lbl_balance_cont_status.grid(row=0, column=1)
        self.lbl_bot_status.grid(row=1, column=0, sticky="e")
        self.lbl_bot_cont_status.grid(row=1, column=1)
        self.lbl_bot_cont_status["text"] = "working"
        self.lbl_exchange_status.grid(row=2, column=0, sticky="e")
        self.lbl_exchange_cont_status.grid(row=2, column=1)
        self.lbl_order_status.grid(row=3, column=0, sticky="e")
        self.lbl_order_cont_status.grid(row=3, column=1)
        self.lbl_rate_status.grid(row=4, column=0, sticky="e")
        self.lbl_rate_cont_status.grid(row=4, column=1)

        self.id = self.window.after(self.sleep_interval, self.callback)
        print(type(self.id))
    def instant_sell_crypto(self):
        """
        'Sell crypto' button handler
        """
        self.crypto_bot.symbol = self.currency.get() + "/USD"
        try:
            quantity = float(self.ent_qty.get())
        except Exception as e:
            self.crypto_bot.write_logs("WARNING", "instant sell crypto", e)
            quantity = 0
        if quantity:
            self.crypto_bot.sell_crypto(quantity)
            self.crypto_bot.update_account_info()
            if self.crypto_bot.account_info.get("balances", False):
                acc_info = self.crypto_bot.account_info
                balance = ", ".join(["{} = {}".format(bl["asset"], bl["free"])
                                     for bl in acc_info["balances"]])
                self.lbl_balance_cont["text"] = balance

    @staticmethod
    def test_val_float(in_str, acttyp):
        """
        Function for validating values of type float
        :return: True or False
        """
        if acttyp == '1':
            if not in_str.replace(".", "", 1).isdigit():
                return False
            return True

    @staticmethod
    def test_val(in_str, acttyp):
        """
        Function for validating values of type int
        :return: True or False
        """
        if acttyp == '1':
            if not in_str.isdigit():
                return False
            return True

    @staticmethod
    def get_value(str_value, value_type, exceptions):
        """
        Сonvert string value to number.

        :param str_value: value
        :type str_value: string
        :param value_type: value type
        :type value_type: string
        :param exceptions: list with exception
        :type exceptions: list

        :rtype: int|float
        :return: number value or 0
        """
        if value_type == "float":
            try:
                value = float(str_value)
                if value:
                    return value
            except Exception as e:
                exceptions.append(str(e) + "\n")
                return 0
        elif value_type == "int":
            try:
                value = int(str_value)
                if value:
                    return value
            except Exception as e:
                exceptions.append(str(e) + "\n")
                return 0

    def callback(self):
        """
        Function that works as an infinite loop.
        """
        self.lbl_exchange_cont_status["text"] = self.crypto_bot.start()
        if self.crypto_bot.rsi_stack_buy:
            status = "RSI coefficient is {0:.2f}%".format(
                self.crypto_bot.current_rate)
            self.lbl_rate_cont_status["text"] = status
        else:
            status = "Boundary coefficient is {0:.2f}%".format(
                self.crypto_bot.current_rate)
            self.lbl_rate_cont_status["text"] = status
        previous_status = self.lbl_order_cont_status["text"]
        if self.crypto_bot.last_order:
            self.lbl_order_cont_status["text"] = "SELL"
        else:
            self.lbl_order_cont_status["text"] = "BUY"
        current_status = self.lbl_order_cont_status["text"]
        if previous_status != current_status:
            self.crypto_bot.update_account_info()
            if self.crypto_bot.account_info.get("balances", False):
                acc_info = self.crypto_bot.account_info
                balance = ", ".join(["{} = {}".format(bl["asset"], bl["free"])
                                     for bl in acc_info["balances"]])
                self.lbl_balance_cont_status["text"] = balance

        self.window.update()
        self.id = self.window.after(self.sleep_interval, self.callback)

    def stop_bot(self):
        """
        'Stop' button handler
        """
        self.lbl_bot_cont_status["text"] = "not working"
        self.id = self.window.after_cancel(self.id)

    def start_bot(self):
        """
        'Start' button handler
        """
        self.lbl_bot_cont_status["text"] = "working"
        self.id = self.window.after(self.sleep_interval, self.callback)
