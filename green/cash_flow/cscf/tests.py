from django.db import transaction
from django.test import TestCase
from django.urls import reverse
import json
from .models import CashFlowData, Companies


class EndpointTestCase(TestCase):

    __slots__ = 'stock_symbols'

    def setUp(self):
        self.stock_symbols = ['AAPL', 'TSLA', 'MSFT', 'WMT']

    def test_add_company(self) -> None:
        """
        Simply tests if we can add all the companies.
        All of the stocks in self.stock_symbols have a 10k form to pull the cashflow data from.
        :return:
        """
        for s in self.stock_symbols:
            self._test_add_company(s)

    def test_detailed_view(self) -> None:
        """
        Fetch a 10-K from the SEC for some company and test if all the data is parsed and displayed properly.
        :return: None
        """
        stock = self.stock_symbols[0]
        self.assertEqual(stock, 'AAPL', msg='This test will only work with Apple data!')
        self._test_add_company(stock)
        response = self.client.get(path=reverse('detailed_company_view'), data={'stock_symbol': stock})
        response = json.loads(response.content)
        expected_json = {
            "header": "Statement of Cash Flows [Abstract]",
            "statements": [
                {
                    "filing": "Cash, cash equivalents and restricted cash, beginning balances",
                    "first_previous_year": 25913,
                    "second_previous_year": 20289,
                    "third_previous_year": 20484
                }
            ]
        }
        self.assertDictEqual(response['cash_flow'][0], expected_json)
        expected_json = {
            "header": "Supplemental cash flow disclosure",
            "statements": [
                {
                    "filing": "Cash paid for income taxes, net",
                    "first_previous_year": 15263,
                    "second_previous_year": 10417,
                    "third_previous_year": 11591
                },
                {
                    "filing": "Cash paid for interest",
                    "first_previous_year": 3423,
                    "second_previous_year": 3022,
                    "third_previous_year": 2092
                }
            ]
        }
        self.assertDictEqual(response['cash_flow'][-1], expected_json)

    def test_list_companies(self) -> None:
        """
        Test if all companies display properly.
        :return: None
        """
        with transaction.atomic():
            for s in self.stock_symbols:
                Companies.objects.create(stock_symbol=s)
        response = self.client.get(path=reverse('list_all_companies'))
        self.assertDictEqual(json.loads(response.content), {"companies": self.stock_symbols})

    def _test_add_company(self, stock_symbol: str) -> None:
        """
        Adds the company's stock symbol to the database. Since test_detailed_view needs data in the database to
        complete it's test, the add_company endpoint will not be tested independently.
        :return: None
        """
        self.client.get(path=reverse('add_companies'), data={'stock_symbol': stock_symbol})
        company = Companies.objects.get(stock_symbol=stock_symbol)
        assert company
        results = CashFlowData.objects.filter(stock_symbol=company)
        self.assertGreater(len(results), 0, msg="The CashFlowData table was not properly populated.")
