# from bot import crypto_bot
from bot.crypto_bot import Bot
import unittest
from unittest.mock import patch, Mock
from currencycom.client import Client


class TestBot(unittest.TestCase):
    def setUp(self) -> None:
        self.bot = Bot()

    @patch.object(Client, "get_account_info")
    def test_update_account_info(self, mock_get):

        mock_get.return_value = {
          "makerCommission": 15,
          "takerCommission": 15,
          "buyerCommission": 0,
          "sellerCommission": 0,
          "canTrade": True,
          "canWithdraw": True,
          "canDeposit": True,
          "updateTime": 123456789,
          "accountType": "SPOT",
          "balances": []
        }
        self.bot.update_account_info()
        self.assertEqual(self.bot.login_correct, True)
        mock_get.return_value = {}
        self.bot.update_account_info()
        self.assertEqual(self.bot.login_correct, False)

    @patch.object(Client, "get_agg_trades")
    def test_test_exchange(self, mock_get):
        mock_get.return_value = [
          {
            "a": 1582595833,
            "p": "8980.4",
            "q": "0.0",
            "T": 1580204505793,
            "m": False,
          }
        ]
        exchange = self.bot._test_exchange()
        self.assertEqual(exchange, True)
        mock_get.return_value = [{}]
        exchange = self.bot._test_exchange()
        self.assertEqual(exchange, False)


if __name__ == '__main__':
    unittest.main()

