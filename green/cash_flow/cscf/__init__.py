import re
import requests
from bs4 import BeautifulSoup
from typing import Optional, List
from urllib.parse import urlparse, parse_qs


class SECScraper:

    __slots__ = ('netloc', 'atoi', 'stock_symbol',)

    def __init__(self, stock_symbol: str):
        """
        This class will scrape https://sec.gov for consolidated statements of cash flows, given some company's stock
        symbol.
        :param stock_symbol: Some company's stock symbol.
        """
        self.netloc, self.stock_symbol = 'https://www.sec.gov', stock_symbol
        self.atoi = re.compile('[%s]' % '$(), ')  # To remove all special characters from numbers in tables.

    def find_company_10k_link(self, start: Optional[int] = 0) -> str:
        """
        Recursive function which finds the 10-K filing of some company, by searching the company on the SEC's website
        and iterating through the pages.
        :param start: The index to keep track which page the function is on. Starts at 0 and increments by 100 with
        each subsequent call.
        :return: An empty string if the 10-K form was not found, else, a URL that points to the 10-K filing data
        """
        url = "{}/cgi-bin/browse-edgar?CIK={}&start={}&count=100".format(self.netloc, self.stock_symbol, start)
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        if start == 0:  # This is the first call, check if company exists in the SEC website.
            if soup.body.find_all(text='No matching CIK.'):
                return ''
        interactive_data = soup.find_all('tr', class_='blueRow')
        if interactive_data:
            for row in interactive_data:
                if row.find('td', text='10-K'):
                    return self.netloc + row.find('a', id='interactiveDataBtn')['href']
        else:  # The "start" variable grew too large. No 10-K found.
            return ''
        return self.find_company_10k_link(start + 100)

    def get_cash_flows_table(self, url: str) -> bytes or None:
        """
        Given some url pointing to a company's most recent 10-K filing, grab the table that holds the data
        regarding consolidated statements of cash flows.
        :param url: The url that points to the 10-K filing data.
        :return: None if there is no consolidated statements of cash flows table, else, returns the page that holds the
        data.
        """
        q_params = parse_qs(urlparse(url).query)
        cik, accession_number = q_params['cik'][0], q_params['accession_number'][0].replace('-', '')
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        cash_flow_table_link = soup.find('a', text='CONSOLIDATED STATEMENTS OF CASH FLOWS')
        if cash_flow_table_link:
            javascript_load_url = cash_flow_table_link['href']
            index = re.findall(r'\d+', javascript_load_url)[0]
            table_url = '{}/Archives/edgar/data/{}/{}/R{}.htm'.format(self.netloc, cik, accession_number, index)
            response = requests.get(table_url)
            return response.content

    def parse_cash_flows_table(self, page: bytes) -> List[List[str and (int or None)]]:
        """
        Parse the consolidated statements of cash flows table, extracting all of the rows and cleaning the
        items that hold numerical values.
        :param page: The web page that holds the table.
        :return: A list of lists, formatted to hold the filing entry (str), the three previous years of cash flow
        data (ints), and whether or not the given row is a header providing description to "child" rows (bool).
        """
        soup = BeautifulSoup(page, 'html.parser')
        table_rows = soup.find('table').find_all('tr')
        formatted_rows = []
        for i, row in enumerate(table_rows):
            if i < 2:  # Skip the top of the table.
                continue
            values = row.find_all('td')  # Get all column values in the row.
            f_row: List[str and int] = [values[0].text]  # [str, int or None, int or None, int or None, bool]
            for j in range(1, len(values)):
                if values[j]['class'][0] == 'text':  # Null value.
                    val = None
                else:  # Parse the number. Remove special characters and convert the string to an int
                    number = values[j].text
                    negative = True if '(' in number else False
                    val = int(self.atoi.sub('', number))
                    if negative:
                        val *= -1
                f_row.append(val)
            if values[0].find('strong'):  # This row is not a filing. It is a header within the table's rows.
                f_row[0] = f_row[0].replace(":", "")  # Headers often have a trailing : attached. Need to remove.
                f_row.append(True)
            else:
                f_row.append(False)
            formatted_rows.append(f_row)
        return formatted_rows
