from django.test import TestCase
from unittest.mock import patch, MagicMock
from .utils import search_fund_data

class SearchViewTest(TestCase):
    @patch('searchFund.views.search_fund_data')
    def test_search_view_success(self, mock_search_fund_data):
        # Búsqueda exitosa
        mock_results = [
            {'symbol': 'AMZN', 'name': 'Amazon', 'price': 150.0},
            {'symbol': 'AAPL', 'name': 'Apple', 'price': 200.0}
        ]
        mock_search_fund_data.return_value = mock_results
        response = self.client.get('/searchFund/', {'query': 'AMZN'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('results', response.context)
        self.assertEqual(response.context['results'], mock_results)
        self.assertIsNone(response.context['error'])

    @patch('searchFund.views.search_fund_data')
    def test_search_view_no_results(self, mock_search_fund_data):
        # Búsqueda sin resultados
        mock_search_fund_data.return_value = None
        response = self.client.get('/searchFund/', {'query': 'INVALID'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('error', response.context)
        self.assertIn('Ninguna API fue capaz', response.context['error'])

    def test_search_view_empty_query(self):
        # Test sin término de búsqueda
        response = self.client.get('/searchFund/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('error', response.context)
        self.assertIn('Por favor, introduce', response.context['error'])

class FundDetailsViewTest(TestCase):
    @patch('searchFund.views.perform_api_call')
    def test_fund_details_view_success(self, mock_perform_api_call):
        # Datos de un fondo
        mock_details = {'symbol': 'AMZN', 'name': 'Amazon'}
        mock_hist_data = {
            'dates': ['2023-01-01', '2023-12-31'],
            'prices': [100.0, 150.0],
            'open': [100.0, 150.0],
            'high': [110.0, 160.0],
            'low': [90.0, 140.0],
            'close': [105.0, 155.0],
            'volumes': [1000, 2000]
        }
        mock_perform_api_call.side_effect = [mock_details, mock_hist_data]
        
        response = self.client.get('/searchFund/details/AMZN/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('details', response.context)
        self.assertIn('line_data', response.context)

class SearchFundDataTest(TestCase):
    @patch('searchFund.utils.perform_api_call')
    def test_search_fund_data_success(self, mock_perform_api_call):
        # Respuesta exitosa de la API
        mock_perform_api_call.return_value = [
            {'symbol': 'AMZN', 'name': 'Amazon', 'price': 150.0}
        ]
        result = search_fund_data('AMZN')
        self.assertIsNotNone(result)
        self.assertEqual(result[0]['symbol'], 'AMZN')

    @patch('searchFund.utils.perform_api_call')
    def test_search_fund_data_no_results(self, mock_perform_api_call):
        # Respuesta sin resultados
        mock_perform_api_call.return_value = None
        result = search_fund_data('INVALID')
        self.assertIsNone(result)