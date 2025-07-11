from django.test import TestCase
from django.urls import reverse
from unittest.mock import patch, MagicMock

class CompareViewTest(TestCase):
    @patch('compareFund.views.compare_fund')
    @patch('compareFund.views.YFinanceService.getSearchData')
    def test_compare_view_success(self, mock_getSearchData, mock_compare_fund):
        # Simula que ambos fondos existen
        mock_getSearchData.side_effect = [True, True]
        # Simula la respuesta de compare_fund
        mock_df = MagicMock()
        mock_df.empty = False
        mock_df.to_html.return_value = "<table></table>"
        mock_compare_fund.return_value = (mock_df, {}, {}, { 'F1': 10, 'F2': 20 }, { 'F1': 5, 'F2': 7 })

        #response = self.client.get(reverse('compareFund:compare_view'), {'fund1': 'F1', 'fund2': 'F2'})
        response = self.client.get('/compareFund/', {'fund1': 'F1', 'fund2': 'F2'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('comparison_table', response.context)
        self.assertIsNone(response.context['error'])

    @patch('compareFund.views.YFinanceService.getSearchData')
    def test_compare_view_fund_not_found(self, mock_getSearchData):
        # Simula que el primer fondo no existe
        mock_getSearchData.side_effect = [None, True]
        #response = self.client.get(reverse('compareFund:compare_view'), {'fund1': 'F1', 'fund2': 'F2'})
        response = self.client.get('/compareFund/', {'fund1': 'F1', 'fund2': 'F2'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('error', response.context)
        self.assertIn("No se encontró el fondo", response.context['error'])