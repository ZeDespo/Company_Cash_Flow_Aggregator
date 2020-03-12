from django.http import HttpRequest, JsonResponse
from typing import Dict, List

from . import SECScraper
from .models import Companies, CashFlowData


def add_company(request: HttpRequest) -> JsonResponse:
    """
    If the company does not exist within the database, add it to the companies table,
    then pull their cashflow data and add them to the cash_flow table.
    :param request: A POST request with the following parameters:
        {
            'stock_symbols': List[str]  # The stock symbols of the companies to add to the database.
        }
    :return: The following JSON:
        {
            'entry_statuses': [
                {
                    'stock_symbol': str          # The stock symbol of the company passed to the endpoint,
                    'company_in_database': bool  # Indicates whether the company was already in the database.
                    'valid_ticker': bool         # Indicates whether the company exists,
                }, ...
            ]
        }
    """
    response = {'entry_statuses': []}
    stock_symbol = request.GET['stock_symbol']
    # for stock_symbol in request.POST.getlist('stock_symbols'):
    s_response = {'stock_symbol': stock_symbol, 'company_in_database': False, 'valid_ticker': False}
    if not _row_exists(Companies, {'stock_symbol': stock_symbol}):
        cash_flow_data = _scrape(stock_symbol)
        if len(cash_flow_data) > 0:
            s_response['valid_ticker'] = True
            company_object = Companies.objects.create(stock_symbol=stock_symbol)
            for row in cash_flow_data:
                CashFlowData.objects.create(stock_symbol=company_object, filing=row[0], first_previous_year=row[1],
                                            second_previous_year=row[2], third_previous_year=row[3],
                                            is_header=row[4])
    else:
        s_response['company_in_database'], s_response['valid_ticker'] = True, True
    response['entry_statuses'].append(s_response)
    return JsonResponse(response)


def detailed_company_view(request: HttpRequest) -> JsonResponse:
    """

    :param request: A GET request with the following parameters:
        {
            'stock_symbol': str  # The stock symbol of a company in the database.
        }
    :return: The following JSON:
        {
            'cash_flow': [
                {
                    'header': str  # The header for the child data
                    'statements': [
                        {
                            'filing': str               # The information regarding the cash flow.
                            'first_previous_year: int   # The cash flow, in millions
                            'second_previous_year: int  # The cash flow, in millions
                            'third_previous_year: int   # The cash flow, in millions
                        }
                    ]
                }
            ],
            'error': str  # Is not None when the stock symbol does not exist in the database
        }
    """
    stock_symbol = request.GET['stock_symbol']
    response = {'cash_flow': [], 'error': None}
    if _row_exists(Companies, {'stock_symbol': stock_symbol}):
        rows = CashFlowData.objects.filter(stock_symbol=stock_symbol)
        i = -1
        for row in rows:
            if row.is_header:
                response['cash_flow'].append({'header': row.filing, 'statements': []})
                i += 1
            else:
                parsed_row = {
                    'filing': row.filing,
                    'first_previous_year': row.first_previous_year,
                    'second_previous_year': row.second_previous_year,
                    'third_previous_year': row.third_previous_year
                }
                response['cash_flow'][i]['statements'].append(parsed_row)
    else:
        response['error'] = '{} does not exist within the database.'.format(stock_symbol)
    return JsonResponse(response)

def list_all_companies(request: HttpRequest) -> JsonResponse:
    """
    Return all of the companies in the database.
    :param request: A GET request with no parameters.
    :return: The following JSON:
        {
            'companies': [
                stock_symbol_1: str  # The stock symbol for the company
                ...
            ]
        }
    """
    companies = Companies.objects.values_list('stock_symbol', flat=True)
    return JsonResponse({'companies': [c for c in companies]})


def update_company_data(request: HttpRequest) -> JsonResponse:
    """
    If the company exists in the database, update the entry from the web with the most up-to-date
    cash flow data.
    :param request: A POST request with the following parameters:
        {
            'stock_symbols': List[str]  # The stock symbols of the companies to update.
        }
    :return: The following JSON:
        {
            'entry_statuses': [
                {
                    'stock_symbol': str      # The stock symbol of the company passed to the endpoint,
                    'update_success': bool   # Indicates whether the company was already in the database.
                    'valid_ticker': bool     # Indicates whether the company exists on sec.gov,
                }, ...
            ]
        }
    """
    response = {'entry_statuses': []}
    for stock_symbol in request.POST.getlist('stock_symbols'):
        s_response = {'stock_symbol': stock_symbol, 'update_success': False, 'valid_ticker': True}
        if _row_exists(Companies, {'stock_symbol': stock_symbol}):
            cash_flow_data = _scrape(stock_symbol)
            if len(cash_flow_data) > 0:
                company_object = Companies.objects.get(stock_symbol=stock_symbol)
                CashFlowData.objects.filter(stock_symbol=company_object).delete()
                for row in cash_flow_data:
                    CashFlowData.objects.create(stock_symbol=company_object, filing=row[0], first_previous_year=row[1],
                                                second_previous_year=row[2], third_previous_year=row[3],
                                                is_header=row[4])
            else:
                s_response['valid_ticker'] = False
        response['entry_statuses'].append(s_response)
    return JsonResponse(response)


def _row_exists(model: Companies or CashFlowData, value_to_search: Dict[str, int or str]) -> bool:
    """
    Helper function to check if something in the database exists.
    Although Django's get_or_create does this function's job without the boilerplate code, there are circumstances
    where the program must check for validation before beginning a write.
    :param model: Some Django model
    :param value_to_search: The column-value pair to check in the database
    :return: True if the row exists. False if it does not.
    """
    try:
        model.objects.get(**value_to_search)
    except model.DoesNotExist:
        return False
    return True


def _scrape(stock_symbol: str) -> List[List[str and (int or None)]]:
    """
    Charged with calling the SECScraper to scrape the consolidated statements of cashflows, if the document exists at
    all.
    :param stock_symbol: The stock symbols of the company
    :return: A list of lists, formatted to hold the filing entry (str), the three previous years of cash flow
        data (ints), and whether or not the given row is a header providing description to "child" rows (bool).
    """
    sec = SECScraper(stock_symbol)
    to_insert = []
    url_10k = sec.find_company_10k_link()
    if url_10k:
        table_page = sec.get_cash_flows_table(url_10k)
        to_insert = sec.parse_cash_flows_table(table_page)
    return to_insert
